from sentence_transformers import SentenceTransformer
from backend.Kernels.FetchUtils import FetchUtils
import redis
import pickle
import os
import numpy as np
from datetime import datetime, timezone # Import datetime and timezone
import json

def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(np.dot(vec1, vec2) / (norm1 * norm2))

class RunVectorization:
    def __init__(self, vector_file: str = "backend/News/vectors.json", redis_host='localhost', redis_port=6379, redis_db=0):
        self.vector_file = vector_file
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
        self.model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')
        self.vector_file = vector_file
        # Pre-load the vectors at initialization if desired
        with open(self.vector_file, 'r') as f:
            self.all_data = json.load(f)
    
    def run_vectorization(self):
        print("Starting vectorization process...")
        
        # Get articles
        articles = FetchUtils().get_all_articles_metadata()
        print(f"Total articles to vectorize: {len(articles)}")
        
        total_finished = 0
        
        # Process each article
        for article in articles:
            # Skip if already vectorized (using URL as key)
            if article.get('web_url') and self.redis_client.exists(article['web_url']):
                total_finished += 1
                continue
                
            # Create text for vectorization
            full_keyword_string = ""
            if "keywords" in article:
                for keyword in article["keywords"]:
                    full_keyword_string += keyword["name"] + ", "
            
            full_text = f""" 
            {article.get('title', '')} 
            \n \
            {article.get('abstract', '')} \
            
            {article.get('lead_paragraph', '')}
            
            {article.get('snippet', '')}
            
            {full_keyword_string}
            """
            
            # Vectorize article
            vector = self.model.encode(full_text).tolist()
            
            # Store in Redis (URL as key, vector as value)
            if article.get('web_url'):
                # Store the vector
                self.redis_client.set(article['web_url'], pickle.dumps(vector))
                
                # Optionally store metadata separately
                metadata = {
                    'title': article.get('title', ''),
                    'abstract': article.get('abstract', ''),
                    'lead_paragraph': article.get('lead_paragraph', ''),
                    'snippet': article.get('snippet', ''),
                    'pub_date': article.get('pub_date', '')
                }
                self.redis_client.set(f"{article['web_url']}:metadata", pickle.dumps(metadata))
            
            total_finished += 1
            
            if total_finished % 100 == 0:
                print(f"Finished {total_finished} articles of {len(articles)}")
    
    def run_vectorization_shallow(self):
        print("Starting vectorization process...")
        
        current_month = 4
        current_year = 2025

        # Get articles
        articles = FetchUtils().get_all_articles_metadata(month=current_month, year=current_year)
        print(f"Total articles to vectorize: {len(articles)}")
        
        total_finished = 0
        
        all_data = []

        # Process each article
        for article in articles:
                
            # Create text for vectorization
            full_keyword_string = ""
            if "keywords" in article:
                for keyword in article["keywords"]:
                    full_keyword_string += keyword["name"] + ", "
            
            full_text = f""" 
            {article.get('title', '')} 
            \n \
            {article.get('abstract', '')} \
            
            {article.get('lead_paragraph', '')}
            
            {article.get('snippet', '')}
            
            {full_keyword_string}
            """
            
            # Vectorize article
            vector = self.model.encode(full_text).tolist()
            
            data = {
                "web_url": article.get('web_url', ''),
                "vector": list(vector),
                "metadata": {
                    'title': article.get('headline', ''),
                    'abstract': article.get('abstract', ''),
                    'lead_paragraph': article.get('lead_paragraph', ''),
                    'snippet': article.get('snippet', ''),
                    'pub_date': article.get('pub_date', '')
                }
            }

            all_data.append(data)
            
            total_finished += 1
            
            if total_finished % 100 == 0:
                print(f"Finished {total_finished} articles of {len(articles)}")

        # write to json file
        with open('backend/News/vectors.json', 'w') as f:
            json.dump(all_data, f)


    def get_vector(self, url):
        """Retrieve a vector by URL"""
        vector_data = self.redis_client.get(url)
        if vector_data:
            return pickle.loads(vector_data)
        return None
    
    def get_metadata(self, url):
        """Retrieve article metadata by URL"""
        metadata = self.redis_client.get(f"{url}:metadata")
        if metadata:
            return pickle.loads(metadata)
        return None
    
    def search_similar(self, query_text: str, top_k: int = 5, start_date: datetime = None, end_date: datetime = None):
        """
        Search for similar articles based on a query text, with optional date filtering.

        Args:
            query_text (str): The text to search for.
            top_k (int): The maximum number of results to return.
            start_date (datetime, optional): The earliest publication date (inclusive).
                                             Should be timezone-aware (e.g., UTC) for accurate comparison.
                                             If naive, comparison assumes system's local timezone or UTC
                                             depending on how pub_date is parsed. Defaults to None (no start limit).
            end_date (datetime, optional): The latest publication date (inclusive).
                                           Should be timezone-aware. Defaults to None (no end limit).

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each containing 'url', 'score', and 'metadata'.
        """
        try:
            query_vector = self.model.encode(query_text).tolist()
        except Exception as e:
            print(f"Error encoding query text: {e}")
            return []

        # Get all potential keys (URLs)
        all_urls = []
        try:
            # Use scan_iter for large databases to avoid blocking
            for key in self.redis_client.scan_iter('*'):
                 key_str = key.decode('utf-8')
                 # Check if it's likely a URL key (not a metadata key)
                 if not key_str.endswith(':metadata'):
                     all_urls.append(key_str)
        except Exception as e:
            print(f"Error scanning Redis keys: {e}")
            return []

        if not all_urls:
            print("No article URLs found in Redis.")
            return []

        print(f"Found {len(all_urls)} potential articles. Calculating similarity and filtering...")

        results = []
        processed_count = 0
        for url in all_urls:
            try:
                vector_data = self.redis_client.get(url)
                if not vector_data:
                    # print(f"Vector data not found for {url}") # Optional debug
                    continue

                # --- Date Filtering Logic ---
                apply_filter = start_date is not None or end_date is not None
                passes_date_filter = not apply_filter # Assume passes if no filter applied

                if apply_filter:
                    metadata = self.get_metadata(url)
                    if metadata and 'pub_date' in metadata:
                        pub_date_str = metadata.get('pub_date')
                        try:
                            # Attempt to parse the date string (NYT format often like '2024-05-01T00:12:20+0000')
                            article_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))

                            # Make dates comparable (ideally use timezone-aware)
                            # If input dates are naive, compare naively or assume UTC
                            # If input dates are aware, ensure article_date is also aware
                            if start_date and start_date.tzinfo is None and article_date.tzinfo is not None:
                                # Example: Convert article date to naive UTC if start_date is naive
                                article_date_compare = article_date.astimezone(timezone.utc).replace(tzinfo=None)
                            elif start_date and start_date.tzinfo is not None and article_date.tzinfo is None:
                                # Cannot reliably compare aware and naive, skip or assume timezone for article_date
                                print(f"Warning: Cannot compare aware start_date with naive article_date for {url}. Skipping date filter.")
                                passes_date_filter = True # Or False, depending on desired behavior
                            else:
                                # Either both aware or both naive
                                article_date_compare = article_date

                            date_ok = True
                            if start_date and article_date_compare < start_date:
                                date_ok = False
                            if end_date and article_date_compare > end_date:
                                date_ok = False

                            passes_date_filter = date_ok

                        except ValueError:
                            print(f"Warning: Could not parse date '{pub_date_str}' for filtering article: {url}")
                            passes_date_filter = False # Exclude if date cannot be parsed
                        except Exception as date_e:
                             print(f"Error comparing dates for {url}: {date_e}")
                             passes_date_filter = False # Exclude on error
                    else:
                        # print(f"Warning: Missing metadata or pub_date for filtering article: {url}") # Optional debug
                        passes_date_filter = False # Exclude if no date for filtering
                # --- End Date Filtering ---

                if passes_date_filter:
                    vector = pickle.loads(vector_data)
                    # Calculate cosine similarity
                    # Use numpy for potentially better performance/stability
                    query_norm = np.linalg.norm(query_vector)
                    vector_norm = np.linalg.norm(vector)
                    if query_norm == 0 or vector_norm == 0:
                        similarity = 0.0 # Avoid division by zero
                    else:
                        similarity = np.dot(query_vector, vector) / (query_norm * vector_norm)

                    # Append URL, score, and the metadata we already fetched (if filter was applied)
                    if not apply_filter: # Fetch metadata only if not already fetched for filtering
                        metadata = self.get_metadata(url)

                    results.append({'url': url, 'score': float(similarity), 'metadata': metadata})

                processed_count += 1
                if processed_count % 200 == 0: # Print progress
                    print(f"Processed {processed_count}/{len(all_urls)} articles...")


            except redis.exceptions.RedisError as r_err:
                print(f"Redis error processing URL {url}: {r_err}")
            except pickle.UnpicklingError as p_err:
                print(f"Error unpickling data for URL {url}: {p_err}")
            except Exception as e:
                print(f"Unexpected error processing URL {url}: {e}")


        print(f"Finished processing. Found {len(results)} articles matching filters.")

        # Sort by similarity (highest first)
        # Handle potential NaN or invalid scores if necessary
        results.sort(key=lambda x: x['score'] if np.isfinite(x['score']) else -np.inf, reverse=True)

        # Return top_k results
        return results[:top_k]

    def compute_embedding(self, text: str) -> np.ndarray:
        """
        Convert the query text into an embedding vector.
        This function is a placeholder. In practice you might use a language model,
        e.g., SentenceTransformers or another embedding model.
        """
        return self.model.encode(text)
        

    def search_similar_shallow(self, query_text: str, top_k: int = 5, start_date: datetime = None):
        """
        Search for the top_k news items that are semantically similar to the query_text,
        filtered by publication date (start_date). It first filters and sorts the data by pub_date,
        then computes the semantic similarity with the query embedding.
        """
        # If new vectors are expected to be updated, you might want to reload the file here.
        data = self.all_data

        # Filter by start_date if provided.
        filtered_data = []
        for item in data:
            pub_date_str = item.get("metadata", {}).get("pub_date")
            if not pub_date_str:
                continue  # Skip items without a pub_date.
            try:
                print("RUNNING")
                # Normalize ISO format by replacing Z with +00:00 if needed.
                pub_date = datetime.fromisoformat(pub_date_str.replace("Z", "+00:00"))
                pub_date = pub_date.replace(tzinfo=None)  # remove timezone for comparison
            except ValueError:
                print("ERROR")
                continue  # Skip items with invalid date formats.
            
            if start_date is None or pub_date >= start_date:
                filtered_data.append(item)

        # Sort filtered data by publication date (ascending order; adjust as needed).
        filtered_data.sort(
            key=lambda x: datetime.fromisoformat(
                x.get("metadata", {}).get("pub_date").replace("Z", "+00:00")
            )
        )
        
        print(len(filtered_data))

        # Compute the embedding for the query text.
        query_vector = self.compute_embedding(query_text)
        
        # Compute semantic similarity for each item.
        scored_items = []
        for item in filtered_data:
            # Assuming each item has a "vector" key with its semantic vector.
            vector = item.get("vector")
            if vector is None:
                continue  # Skip items without a semantic vector.
            article_vector = np.array(vector, dtype=float)
            similarity = cosine_similarity(query_vector, article_vector)
            scored_items.append((similarity, item))
        
        # Sort items by similarity score in descending order.
        scored_items.sort(key=lambda x: x[0], reverse=True)
        
        # Select the top_k items.
        top_results = [item for similarity, item in scored_items[:top_k]]
        return top_results


# if __name__ == "__main__":
#     vectorizer = RunVectorization()
#     vectorizer.run_vectorization_shallow()

if __name__ == "__main__":
    # Change the file path as needed.
    searcher = RunVectorization(vector_file="backend/News/vectors.json")
    
    # Optionally provide a start date, e.g. articles after April 1, 2025.
    start_date = datetime(2025, 4, 1)
    
    # Provide your query text.
    query = "Latest updates on election lawsuits"
    
    results = searcher.search_similar_shallow(query_text=query, top_k=5, start_date=start_date)
    
    # Print out the titles of the top results.
    for article in results:
        title = article.get("metadata", {}).get("title", {}).get("main", "No Title")
        pub_date = article.get("metadata", {}).get("pub_date", "No pub_date")
        print(f"Title: {title} | Publication Date: {pub_date}")