import os
import requests
from dotenv import load_dotenv
from typing import List, Dict, Any

# Load environment variables from your .env file
load_dotenv()

class MistralClient:
    """
    A client to communicate with the Mistral API for chat completions.

    The client uses the configuration defined in the .env file:
      - MISTRAL_API_KEY: Your Mistral API key.
      - MISTRAL_BASE_URL: The base URL for Mistral (default: https://api.mistral.ai/v1).

    Example usage:
      client = MistralClient()
      response = client.send_chat_request(
          model="mistral-tiny",
          messages=[
              {"role": "system", "content": "Be precise and concise."},
              {"role": "user", "content": "How many stars are in our galaxy?"}
          ],
          temperature=0.7,
          max_tokens=150
      )
      print(response)
    """

    def __init__(self, mistral_api_key: str = None) -> None:
        # Attempt to read from parameter first; fall back to environment variable.
        self.api_key = mistral_api_key or os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY not found. Please set it in your .env file or pass it to the client.")
        
        # Read the Mistral base URL; default to https://api.mistral.ai/v1 if not provided.
        self.base_url = os.getenv("MISTRAL_BASE_URL", "https://api.mistral.ai/v1")
        
        # Common HTTP request headers
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def send_chat_request(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Sends a chat completions request to the Mistral API.

        Args:
            model (str): The model name to use (e.g., "mistral-tiny").
            messages (List[Dict[str, str]]): A list of message objects that form the conversation.
            temperature (float): Sampling temperature (0 <= temperature < 2).
            **kwargs: Additional optional parameters such as max_tokens, top_p, etc.

        Returns:
            Dict[str, Any]: The JSON response from the API.
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        # Merge any additional parameters into the payload.
        payload.update(kwargs)

        url = f"{self.base_url}/chat/completions"
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()  # Raise an error for bad status codes.
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

# Example usage:
if __name__ == "__main__":
    # Instantiate the client (make sure your .env file contains MISTRAL_API_KEY and optionally MISTRAL_BASE_URL)
    try:
        mistral_client = MistralClient()
    except ValueError as e:
        print(e)
        exit(1)

    # Define a conversation similar to the sample communication format
    messages = [
        {"role": "system", "content": "Be precise and concise."},
        {"role": "user", "content": "How many stars are there in our galaxy?"}
    ]
    
    # Additional parameters can be provided as needed (e.g., max_tokens, top_p, etc.)
    response = mistral_client.send_chat_request(
        model="mistral-tiny",
        messages=messages,
        temperature=0.3,
    )
    
    print("Response from Mistral API:")
    print(response)