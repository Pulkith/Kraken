import os
import asyncio
from twikit import Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class TwikitAPI:
    def __init__(self, lang: str = 'en-US', cookies_file: str = 'cookies.json'):
        """
        Initializes the Twikit API client with the provided language and cookies file.
        
        Authentication is loaded automatically from environment variables:
          - X_USERNAME: your username
          - X_EMAIL: your email
          - X_PASSWORD: your password
        """
        self.lang = lang
        self.cookies_file = cookies_file
        self.client = Client(self.lang)
        self.username = os.getenv("X_USERNAME")
        self.email = os.getenv("X_EMAIL")
        self.password = os.getenv("X_PASSWORD")

        # Validate that credentials have been provided.
        if not all([self.username, self.email, self.password]):
            raise ValueError("Missing credentials. Please set X_USERNAME, X_EMAIL, and X_PASSWORD in your .env file.")
    
    async def login(self):
        """
        Log into the Twikit client using the credentials from the environment.
        """
        await self.client.login(
            auth_info_1=self.username,
            auth_info_2=self.email,
            password=self.password,
            cookies_file=self.cookies_file
        )
    
    async def search_tweets(self, search_query: str, result_type: str = "Latest", count=10):
        """
        Search for tweets based on the provided query and result type.
        
        Args:
            search_query (str): Query string to search tweets.
            result_type (str): Type of results to retrieve (e.g., "Latest").
        
        Returns:
            List: A list of tweet objects matching the search criteria.
        """
        tweets = await self.client.search_tweet(search_query, result_type, count=count)
        return tweets

    async def get_top_crypto(self, search_query: str = "Cyrpto", result_type: str = "Top", count=10):
        tweets = await self.client.search_tweet(search_query, result_type, count=count)
        return tweets

    async def get_trending_tweets(self, search_query: str, count = 10):
        tweets = await self.client.get_trends(search_query, count = count)
        return tweets
        """
        Get trending tweets based on the provided query and result type.

        Args:
            search_query (str): Query string to search tweets.
            result_type (str): Type of results to retrieve (e.g., "Latest").

        Returns:
            List: A list of tweet objects matching the search criteria.
        """

    async def request_and_return_results(self, search_query: str, result_type: str = "Latest", count = 10):
        """
        Logs into Twikit (if not already logged in), performs a tweet search,
        and returns the search results.
        
        Args:
            search_query (str): Query string to search tweets.
            result_type (str): Type of tweet results (default is "Latest").
        
        Returns:
            List: A list of tweet objects.
        """
        # Log in first
        await self.login()
        # Perform the tweet search
        tweets = await self.search_tweets(search_query, result_type, count=count)
        return tweets
    
    async def request_and_return_trending(self, search_query : str = 'news'):
        """
        Logs into Twikit (if not already logged in), performs a tweet search,
        and returns the search results.
        Args:
            search_query (str): Query string to search tweets.
            result_type (str): Type of tweet results (default is "Latest").
        Returns:
            List: A list of tweet objects.
        """
        # Log in first
        await self.login()
        # Perform the tweet search
        tweets = await self.get_trending_tweets(search_query)
        return tweets

    async def request_and_return_top_crypto(self, search_query: str = "Cyrpto", result_type: str = "Top", count=10):
        # Log in first
        await self.login()
        # Perform the tweet search
        tweets = await self.get_top_crypto(search_query, result_type, count=count)
        return tweets

# Example usage
async def main():
    api = TwikitAPI(lang='en-US', cookies_file='cookies.json')
    tweets = await api.request_and_return_results("Prompt", "Latest")
    for tweet in tweets:
        print(tweet.user.name, tweet.text, tweet.created_at)

if __name__ == "__main__":
    asyncio.run(main())