import os
import asyncio # Import asyncio for running async code
import httpx    # Import httpx instead of requests
from dotenv import load_dotenv
from typing import Tuple, Dict, Any

# Load environment variables from a .env file
load_dotenv()

class OpenAIAPI:
    """
    An asynchronous class to interact with a ChatGPT conversational model
    and a GPT-powered web search tool using httpx.

    Methods:
    --------
    query_chatgpt(system_prompt: str, user_prompt: str, model: str = 'gpt-3.5-turbo', temperature: float = 0.7) -> str
        Asynchronously sends a conversation query to ChatGPT and returns the assistant response.

    query_search_tool(query: str, model: str = 'gpt-4o', temperature: float = 0.7,
                      user_location: Dict[str, str] = None, search_context_size: str = "medium") -> Tuple[str, Dict[str, Any]]
        Asynchronously sends a search query using the web search tool and returns the text result along with any URL citation annotations.

    Usage:
    ------
    async def main():
        async with AsyncOpenAIAPI() as api:
            # Make API calls
            chat_response = await api.query_chatgpt(...)
            search_text, citations = await api.query_search_tool(...)
            print(chat_response)
            print(search_text, citations)

    asyncio.run(main()) # Run the main async function
    """
    def __init__(self):
        """Initializes the asynchronous API client."""
        self.api_key = os.getenv("GPT_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Please set GPT_API_KEY in your .env file.")

        # Endpoints for ChatGPT and the search tool
        self.chat_base_url = os.getenv("CHAT_BASE_URL", "https://api.openai.com/v1/chat/completions")
        self.search_base_url = os.getenv("SEARCH_BASE_URL", "https://api.openai.com/v1/responses") # Assuming this endpoint is correct

        # Headers for authenticating the request.
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Initialize an httpx AsyncClient. It's good practice to reuse the client
        # for connection pooling and performance.
        self._client = httpx.AsyncClient(headers=self.headers, timeout=30.0) # Set a reasonable timeout

    async def __aenter__(self):
        """Enter the async context manager, return self."""
        # The client is already initialized in __init__
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context manager, ensuring the client is closed."""
        await self.close()

    async def close(self):
        """Closes the underlying httpx client."""
        await self._client.aclose() # Use aclose() for AsyncClient

    async def query_chatgpt(self, system_prompt: str, user_prompt: str, model: str = 'gpt-3.5-turbo', temperature: float = 0.7) -> str:
        """
        Asynchronously sends a conversation query to ChatGPT.

        Args:
            system_prompt (str): Instructions for the assistant.
            user_prompt (str): The user's query.
            model (str): The model to use.
            temperature (float): Sampling temperature.

        Returns:
            str: The generated assistant response.
        """
        payload = {
            "model": model,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }
        try:
            # Use await with the async client's post method
            response = await self._client.post(self.chat_base_url, json=payload)
            response.raise_for_status() # Check for HTTP errors
            data = response.json() # .json() is synchronous after await response
            # Assumes response format: data["choices"][0]["message"]["content"]
            chat_response = data["choices"][0]["message"]["content"]
            return chat_response
        except httpx.HTTPStatusError as e:
            # More specific error handling for HTTP errors
            return f"Error querying ChatGPT (HTTP {e.response.status_code}): {e.response.text}"
        except httpx.RequestError as e:
            # Handle network-related errors (timeouts, connection issues)
             return f"Error querying ChatGPT (Request Error): {e}"
        except Exception as e:
            # General exception catch
            return f"An unexpected error occurred querying ChatGPT: {e}"

    async def query_search_tool(self, query: str, model: str = 'gpt-4o', temperature: float = 0.7,
                                  user_location: Dict[str, str] = None, search_context_size: str = "medium") -> Tuple[str, Dict[str, Any]]:
        """
        Asynchronously sends a query to GPT's web search tool.

        Args:
            query (str): The search query input.
            model (str): The model to use (default is "gpt-4o" for search).
            temperature (float): Sampling temperature.
            user_location (Dict[str, str], optional): User location details.
            search_context_size (str): Search context size ("low", "medium", "high").

        Returns:
            Tuple[str, Dict[str, Any]]: A tuple containing the search result text and citation annotations.
        """
        payload = {
            "model": model,
            "temperature": temperature,
            "input": query,
            "tools": [ {
                "type": "web_search_preview",
                "search_context_size": search_context_size,
                # Only include user_location if it's provided and not None
                **({"user_location": user_location} if user_location else {})
            } ]
        }
        # Remove user_location from payload if it's None (cleaner way)
        # if user_location is None and "user_location" in payload["tools"][0]:
        #     del payload["tools"][0]["user_location"] # Alternative way

        try:
            # Use await with the async client's post method
            response = await self._client.post(self.search_base_url, json=payload)
            response.raise_for_status() # Check for HTTP errors
            data = response.json() # .json() is synchronous after await response

            # Extract the message item containing search output
            # Ensure 'output' exists and is iterable, default to empty list if not
            response_output = data.get("output", [])
            if not isinstance(response_output, list):
                 return f"Unexpected response format: 'output' is not a list. Response: {data}", {}

            message_item = next((item for item in response_output if item.get("type") == "message"), None)

            if not message_item:
                return f"No 'message' item found in the search tool response output. Response: {data}", {}

            # Safely access nested content
            content_list = message_item.get("content", [])
            if not content_list or not isinstance(content_list, list):
                 return f"No 'content' list found in the message item or it's not a list. Response: {data}", {}

            first_content = content_list[0]
            if not isinstance(first_content, dict):
                return f"First content item is not a dictionary. Response: {data}", {}

            response_text = first_content.get("text", "No text found in response.")
            annotations = first_content.get("annotations", [])

            # Parse annotations
            citations = {}
            if isinstance(annotations, list): # Ensure annotations is a list before iterating
                for idx, annot in enumerate(annotations):
                     if isinstance(annot, dict) and annot.get("type") == "url_citation":
                        citations[f"citation_{idx}"] = {
                            "url": annot.get("url", ""),
                            "title": annot.get("title", ""),
                            "start_index": annot.get("start_index"),
                            "end_index": annot.get("end_index")
                        }
            else:
                print(f"Warning: 'annotations' field was not a list: {annotations}")


            return response_text, citations

        except httpx.HTTPStatusError as e:
            return f"Error querying web search tool (HTTP {e.response.status_code}): {e.response.text}", {}
        except httpx.RequestError as e:
             return f"Error querying web search tool (Request Error): {e}", {}
        except (KeyError, IndexError, TypeError) as e:
             # Catch errors during response parsing
             return f"Error parsing search tool response: {e}. Response data: {data}", {}
        except Exception as e:
            # General exception catch
            return f"An unexpected error occurred querying web search tool: {e}", {}


# --- Example Usage ---
async def main():
    """Example asynchronous function to use the API class."""
    # Use async with to automatically manage the client lifecycle (open/close)
    async with AsyncOpenAIAPI() as api:
        print("Querying ChatGPT...")
        chat_response = await api.query_chatgpt(
            system_prompt="You are a helpful assistant.",
            user_prompt="Explain the difference between synchronous and asynchronous programming in Python."
        )
        print("\n--- ChatGPT Response ---")
        print(chat_response)
        print("-" * 25)

        print("\nQuerying Search Tool...")
        search_text, citations = await api.query_search_tool(
            query="What are the latest developments in AI?",
            user_location={"country": "US"}, # Example location
            search_context_size="medium"
        )
        print("\n--- Search Tool Response ---")
        print("Text:", search_text)
        print("\nCitations:", citations)
        print("-" * 25)

if __name__ == "__main__":
    # Run the main asynchronous function
    # In a script, you run the top-level async function like this:
    asyncio.run(main())

    # If you are in an environment where an event loop is already running
    # (like Jupyter notebooks), you might just use `await main()`