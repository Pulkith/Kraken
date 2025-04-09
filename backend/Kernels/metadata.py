import os
import requests
import json
from datetime import datetime, timedelta
import calendar
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NYTimesMetadataFetcher:
    def __init__(self):
        self.api_key = os.getenv('NYTIMES_API_KEY')
        if not self.api_key:
            raise ValueError("NYTimes API key not found in environment variables")
        
        self.base_url = "https://api.nytimes.com/svc/archive/v1"
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "News", "Metadata")
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def get_filename(self, year, month):
        """Generate filename for a specific year and month"""
        return os.path.join(self.output_dir, f"nytimes_{year}_{month:02d}.json")
    
    def fetch_archive(self, year, month):
        """Fetch NYTimes archive data for a specific year and month"""
        url = f"{self.base_url}/{year}/{month}.json?api-key={self.api_key}"
        
        logger.info(f"Fetching NYTimes archive data for {year}-{month:02d}")
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data for {year}-{month:02d}: {e}")
            return None
    
    def save_data(self, data, year, month):
        """Save fetched data to a JSON file"""
        if not data:
            return False
        
        filename = self.get_filename(year, month)
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f)
            logger.info(f"Saved data to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving data to {filename}: {e}")
            return False
    
    def get_previous_months(self, num_months=12):
        """Get the current month and previous months"""
        now = datetime.now()
        months = []
        
        for i in range(num_months):
            # Calculate the month that is i months ago
            date = now - timedelta(days=30*i)
            months.append((date.year, date.month))
        
        return months
    
    def run(self):
        """Main method to fetch and save NYTimes archive data"""
        # Get current month
        now = datetime.now()
        current_year, current_month = now.year, now.month
        
        # Check if we need to fetch previous months
        current_month_file = self.get_filename(current_year, current_month)
        
        if os.path.exists(current_month_file):
            # If current month file exists, only fetch and update current month
            logger.info(f"Current month file exists. Updating only current month data.")
            data = self.fetch_archive(current_year, current_month)
            self.save_data(data, current_year, current_month)
        else:
            # If current month file doesn't exist, fetch last 3 months
            logger.info(f"Current month file doesn't exist. Fetching last 12 months data.")
            months_to_fetch = self.get_previous_months(12)
            
            for year, month in months_to_fetch:
                data = self.fetch_archive(year, month)
                self.save_data(data, year, month)

def main():
    try:
        fetcher = NYTimesMetadataFetcher()
        fetcher.run()
    except Exception as e:
        logger.error(f"Error running NYTimes metadata fetcher: {e}")

if __name__ == "__main__":
    main()