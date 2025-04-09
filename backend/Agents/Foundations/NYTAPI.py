import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class NYTAPI:
    def __init__(self):
        # Get the NYT API key from the environment
        self.api_key = os.getenv("NYTIMES_API_KEY")
        if not self.api_key:
            raise ValueError("NYT_API_KEY not found in your .env file.")
        
        # Base URLs for the NYT APIs
        self.top_stories_base_url = "https://api.nytimes.com/svc/topstories/v2/"
        self.article_search_url = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
    
    def get_top_stories(self, category: str):
        """
        Get top stories for a given category.
        
        The endpoint URL format is:
          https://api.nytimes.com/svc/topstories/v2/{category}.json?api-key=yourkey
          
        Args:
            category (str): The category to search for (e.g., "arts", "business", etc.).
        
        Returns:
            list: A list of story objects under the "results" key.
        """
        url = f"{self.top_stories_base_url}{category}.json?api-key={self.api_key}"
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()
        return data.get("results", [])
    
    def search_articles(self, query: str, first_published_date: str = None):
        """
        Search for articles using the NYT Article Search API.
        
        The endpoint URL is:
          https://api.nytimes.com/svc/search/v2/articlesearch.json
        
        Query Parameters:
            - q: the search text to look up in the article's headline, body, or byline.
            - begin_date and end_date: (optional) filter results by a specific date.
              The dates must be in YYYYMMDD format.
        
        Args:
            query (str): The search query.
            first_published_date (str, optional): The date (YYYYMMDD) to filter articles by first publication.
            
        Returns:
            list: A list of article objects found in the "docs" field of the response.
        """
        params = {
            "q": query,
            "api-key": self.api_key
        }
        
        # If a published date is provided, limit the search to that exact day.
        if first_published_date:
            params["begin_date"] = first_published_date
            params["end_date"] = first_published_date
        
        response = requests.get(self.article_search_url, params=params)
        response.raise_for_status()
        data = response.json()
        # For the Article Search API, the articles are found under the "docs" key.
        return data.get("response", {}).get("docs", [])

# Example usage:
if __name__ == "__main__":
    nyt_client = NYTAPI()
    
    # Example: Get top stories in the "arts" category
    try:
        top_stories = nyt_client.get_top_stories("business")
        print("Top Stories in Arts:")
        for story in top_stories:
            print("-", story.get("title"))
    except Exception as e:
        print("Error retrieving top stories:", e)
    
    # Example: Search articles related to "climate change" published on April 10, 2025
    try:
        articles = nyt_client.search_articles("climate change", first_published_date="20250410")
        print("\nArticle Search Results for 'climate change':")
        for article in articles:
            headline = article.get("headline", {}).get("main", "No headline")
            print("-", headline)
    except Exception as e:
        print("Error searching articles:", e)