import os
import asyncio
import httpx  # Import httpx instead of requests
from dotenv import load_dotenv
from typing import List, Dict, Any, Tuple, Optional # Added Tuple, Optional

# Load environment variables from a .env file
load_dotenv()

class PerplexityAPI:
    """
    An asynchronous class to interact with the Perplexity Chat Completions API using httpx.

    Methods:
    --------
    chat_completions(...) -> Tuple[str, List[Dict[str, Any]]]
        Asynchronously sends a chat completion request to the Perplexity API
        and returns the response text and citations. Raises exceptions on errors.

    Usage:
    ------
    async def main():
        async with AsyncPerplexityAPI() as api:
            try:
                response_text, citations = await api.chat_completions(...)
                print("Response Text:", response_text)
                print("Citations:", citations)
            except Exception as e:
                print(f"An API error occurred: {e}")

    asyncio.run(main())
    """
    def __init__(self):
        """Initializes the asynchronous API client."""
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY not found in .env file.")

        self.base_url = os.getenv("PERPLEXITY_BASE_URL", "https://api.perplexity.ai/chat/completions")

        # Common headers for requests
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json", # Good practice to include Accept header
        }

        # Initialize httpx AsyncClient for connection pooling
        self._client = httpx.AsyncClient(headers=self.headers, timeout=60.0) # Increased timeout for potentially long completions

    async def __aenter__(self):
        """Enter the async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context manager, closing the client."""
        await self.close()

    async def close(self):
        """Closes the underlying httpx async client."""
        if hasattr(self, '_client') and self._client is not None:
             await self._client.aclose()

    async def chat_completions(self,
                               model: str,
                               system_message: str,
                               user_message: str,
                               temperature: float = 1.0, # Default temperature if not provided
                               search_domain_filter_force_include: Optional[List[str]] = None,
                               search_domain_filter_force_exclude: Optional[List[str]] = None,
                               return_images: bool = False,
                               search_recency_filter: Optional[str] = None,
                               web_search_options: Optional[Dict[str, Any]] = None
                               ) -> Tuple[str, List[Dict[str, Any]]]: # Return tuple or raise exception
        """
        Asynchronously sends a chat completions request to Perplexity.

        Args:
            model (str): The model name (e.g., "sonar-small-chat", "sonar-medium-chat").
            system_message (str): System instructions.
            user_message (str): User's query.
            temperature (float): Randomness (0 to 2). Defaults to 1.0.
            search_domain_filter_force_include (Optional[List[str]]): Domains to force include.
            search_domain_filter_force_exclude (Optional[List[str]]): Domains to force exclude.
            return_images (bool): Whether to include images. Defaults to False.
            search_recency_filter (Optional[str]): Time filter (e.g., "day", "week").
            web_search_options (Optional[Dict[str, Any]]): Additional search options.

        Returns:
            Tuple[str, List[Dict[str, Any]]]: A tuple containing:
                - The response text content.
                - A list of citation dictionaries.

        Raises:
            httpx.HTTPStatusError: If the API returns an HTTP error status.
            httpx.RequestError: For network-related issues.
            KeyError: If the response JSON structure is unexpected.
            Exception: For other potential errors.
        """
        search_domain_filter = []
        if search_domain_filter_force_include:
            search_domain_filter.extend(search_domain_filter_force_include)
        if search_domain_filter_force_exclude:
            search_domain_filter.extend([f"-{domain}" if not domain.startswith("-") else domain
                                         for domain in search_domain_filter_force_exclude])

        payload: Dict[str, Any] = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            "temperature": temperature,
            "return_images": return_images,
        }

        # Add optional parameters only if they have values
        if search_domain_filter:
            payload["search_domain_filter"] = search_domain_filter
        if search_recency_filter is not None:
            payload["search_recency_filter"] = search_recency_filter
        if web_search_options is not None:
             payload["web_search_options"] = web_search_options
        # Add other optional params like max_tokens, top_p etc. here if needed

        try:
            # Make the asynchronous POST request
            # Note: We initialized the client with base_url, so only need path here ("" for the base endpoint)
            response = await self._client.post(self.base_url, json=payload) # Use "" as path since base_url is set

            # Raise an exception for bad status codes (4xx or 5xx)
            response.raise_for_status()

            # Parse the JSON response asynchronously
            response_json = response.json() # .json() is sync after await response

            # Extract content and citations, raising KeyError if structure is wrong
            response_text = response_json["choices"][0]["message"]["content"]

            # Citations might be optional or structured differently, adjust as needed.
            # Assuming 'citations' is a top-level key containing a list.
            # If citations aren't guaranteed, use .get()
            citations = response_json.get("citations", [])
            if not isinstance(citations, list):
                 print(f"Warning: Expected 'citations' to be a list, but got {type(citations)}. Treating as empty.")
                 citations = []


            return response_text, citations

        # Specific exceptions are caught first
        except httpx.HTTPStatusError as e:
            print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
            raise # Re-raise the exception to be handled by the caller
        except httpx.RequestError as e:
            print(f"Network Request Error: {e}")
            raise # Re-raise
        except (KeyError, IndexError) as e:
            print(f"Error parsing API response structure: {e}")
            # Include response details if possible and available
            try:
                 error_details = response.text if 'response' in locals() else "Response data unavailable."
                 print(f"Response Content: {error_details}")
            except Exception:
                 pass
            raise KeyError(f"Unexpected response structure from API: {e}") from e # Raise a more specific error
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise # Re-raise any other unexpected exceptions

# --- Example Usage ---
async def main():
    """Example asynchronous function to use the API class."""
    print("Attempting to initialize Perplexity API client...")
    try:
        # Use async with for automatic client cleanup
        async with PerplexityAPI() as perplexity_api:
            print("Client initialized. Sending request...")
            # Set up test parameters
            model = "sonar-small-chat" # Or "sonar-medium-chat" etc.
            system_message = "You are an expert astrophysicist. Provide detailed but understandable explanations."
            user_message = "How many stars are estimated to be in the Milky Way galaxy, and what are the primary methods for estimation?"
            temperature = 0.3
            search_domain_filter_force_include = ["nasa.gov", "esa.int"]
            search_domain_filter_force_exclude = [] # No specific excludes
            return_images = False
            search_recency_filter = None # No recency filter
            web_search_options = None # No extra web options

            try:
                response_text, citations = await perplexity_api.chat_completions(
                    model=model,
                    system_message=system_message,
                    user_message=user_message,
                    temperature=temperature,
                    search_domain_filter_force_include=search_domain_filter_force_include,
                    search_domain_filter_force_exclude=search_domain_filter_force_exclude,
                    return_images=return_images,
                    search_recency_filter=search_recency_filter,
                    web_search_options=web_search_options
                )

                # Print the successful response
                print("\n--- Perplexity API Response ---")
                print("Text:\n", response_text)
                print("\nCitations:")
                if citations:
                     for i, citation in enumerate(citations):
                         print(f"  {i+1}. {citation.get('title', 'N/A')}: {citation.get('url', 'N/A')}")
                else:
                     print("  No citations provided.")
                print("-" * 30)

            except Exception as e:
                # Handle errors specifically from the API call
                print(f"\n--- Error during Perplexity API call ---")
                print(f"An error occurred: {e}")
                print("-" * 30)

    except ValueError as err:
        # Handle initialization errors (e.g., missing API key)
        print(f"Initialization Error: {err}")
    except Exception as e:
        # Catch any other unexpected errors during setup/cleanup
        print(f"An unexpected error occurred outside the API call: {e}")


if __name__ == "__main__":
    # Ensure .env file has PERPLEXITY_API_KEY
    if not os.getenv("PERPLEXITY_API_KEY"):
        print("Error: PERPLEXITY_API_KEY environment variable not set.")
        print("Please create a .env file with PERPLEXITY_API_KEY=your_api_key")
    else:
        # Run the main asynchronous function
        asyncio.run(main())