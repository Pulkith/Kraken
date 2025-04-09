import json
import os
from datetime import datetime
from typing import List, Dict, Union

class FetchUtils:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_path = os.path.join(current_dir, "..", "News", "Metadata")
        all_data = self._get_all_articles()

        self.data_map = {}
        for article in all_data:
            article_url = article.get('web_url')
            if article_url:
                self.data_map[article_url] = article

    def get_all_articles_metadata(self, month: int = None, year: int = None) -> List[Dict]:
        """
        Fetch article metadata either for a specific month/year or all available articles
        
        Args:
            month (int, optional): Month (1-12)
            year (int, optional): Year (YYYY)
            
        Returns:
            List[Dict]: List of article metadata dictionaries
        """
        if month and year:
            return self._get_specific_month_articles(month, year)
        return self._get_all_articles()

    def _get_specific_month_articles(self, month: int, year: int) -> List[Dict]:
        """Get articles for a specific month and year"""
        filename = f"nytimes_{year}_{month:02d}.json"
        file_path = os.path.join(self.base_path, filename)
        
        if not os.path.exists(file_path):
            return []
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('response', {}).get('docs', [])
        except Exception as e:
            print(f"Error reading file {filename}: {str(e)}")
            return []

    def _get_all_articles(self) -> List[Dict]:
        """Get all articles from all available files"""
        all_articles = []
        
        for filename in os.listdir(self.base_path):
            if filename.startswith("nytimes_") and filename.endswith(".json"):
                file_path = os.path.join(self.base_path, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        articles = data.get('response', {}).get('docs', [])
                        all_articles.extend(articles)
                except Exception as e:
                    print(f"Error reading file {filename}: {str(e)}")
                    continue
        
        return all_articles
    def get_available_months(self) -> List[Dict[str, int]]:
        
        """
        Get a list of available months and years from the metadata files
        
        Returns:
            List[Dict[str, int]]: List of dictionaries containing month and year
        """
        available_dates = []
        
        for filename in os.listdir(self.base_path):
            if filename.startswith("nytimes_") and filename.endswith(".json"):
                try:
                    # Extract year and month from filename
                    year, month = map(int, filename.replace("nytimes_", "").replace(".json", "").split("_"))
                    available_dates.append({"year": year, "month": month})
                except:
                    continue
                    
        return sorted(available_dates, key=lambda x: (x["year"], x["month"]))
    
    def get_full_article_data(self, article_url: str):
        return self.data_map.get(article_url, None)

