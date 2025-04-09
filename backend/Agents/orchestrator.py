# orchestrator.py

import os
import asyncio
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta, timezone
import json

from backend.API.AppData import AppData

# Assuming these classes are in the specified directories and importable
from backend.Agents.Foundations.OpenAIAPI import OpenAIAPI
from backend.Agents.Foundations.PerplexityAPI import PerplexityAPI
from backend.Agents.Foundations.XDigest import TwikitAPI
from backend.Kernels.vectorization import RunVectorization # Renamed file from prompt

from backend.Kernels.FetchUtils import FetchUtils
from backend.Agents.prompts import (
    SELECT_DIVERSE_ARTICLES,
    DEEP_RESEARCH,
    COMPOSE_STORY,
    SELECT_DIVERSE_X_POSTS,
    INSIGHTS_PROMPT
)

# --- Configuration ---
# Consider moving these to a config file or environment variables
NUM_INITIAL_ARTICLES = 20
NUM_FINAL_ARTICLES = 8
NUM_X_POSTS_TO_FETCH = 30 # Fetch more posts initially
NUM_X_POSTS_TO_SELECT = 10
PERPLEXITY_MODEL = "sonar" # Or your preferred Perplexity model
GPT_CHAT_MODEL = "gpt-4o" # Or your preferred chat model
GPT_SEARCH_MODEL = "gpt-4o" # Or your preferred search model

fetchTooler = FetchUtils()

class NewsOrchestrator:
    def __init__(self):
        print("Initializing Orchestrator...")
        try:
            self.vector_search = RunVectorization()
            self.openai_api = OpenAIAPI()
            self.perplexity_api = PerplexityAPI()
            # Ensure X_USERNAME, X_EMAIL, X_PASSWORD are in your .env file for TwikitAPI
            self.twikit_api = TwikitAPI(lang='en-US', cookies_file='cookies.json')
            print("Orchestrator Initialized Successfully.")
        except ValueError as e:
            print(f"ERROR: Orchestrator initialization failed: {e}")
            print("Please ensure all required API keys (GPT, Perplexity) and X credentials are set in your .env file.")
            raise
        except ImportError as e:
            print(f"ERROR: Failed to import necessary modules: {e}")
            print("Please check your file structure and ensure all class files (OpenAIAPI, PerplexityAPI, XDigest, RunVectorization) exist and are importable.")
            raise
        except Exception as e:
            print(f"ERROR: An unexpected error occurred during Orchestrator initialization: {e}")
            raise

    async def _filter_articles_by_date(self, articles: List[Dict[str, Any]], days: int = 1) -> List[Dict[str, Any]]:
        """Filters articles published within the last 'days'."""
        filtered_articles = []
        cutoff_date = datetime.now() - timedelta(days=days)
        print(f"Filtering articles published after: {cutoff_date.isoformat()}")

        for article in articles:
            metadata = article.get('metadata', {})
            if not metadata:
                print(f"Warning: Article missing metadata: {article.get('url')}")
                continue

            pub_date_str = metadata.get('pub_date')
            if not pub_date_str:
                print(f"Warning: Article missing publication date: {article.get('url')}")
                continue

            try:
                # Handle different possible ISO formats (with/without timezone)
                pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
                # Make cutoff_date timezone-aware (assuming UTC for comparison if article date is aware)
                aware_cutoff_date = cutoff_date.replace(tzinfo=pub_date.tzinfo)

                if pub_date >= aware_cutoff_date:
                    # Add the original article metadata back for easier access
                    article_data = metadata.copy()
                    article_data['web_url'] = article.get('url') # Ensure URL is top-level
                    article_data['similarity_score'] = article.get('score') # Keep score if needed
                    filtered_articles.append(article_data)
                # else:
                    # print(f"Article too old: {pub_date_str} for {article.get('url')}")

            except ValueError:
                print(f"Warning: Could not parse date '{pub_date_str}' for article: {article.get('url')}")
            except Exception as e:
                print(f"Error processing date for article {article.get('url')}: {e}")

        print(f"Found {len(filtered_articles)} articles published within the last {days} day(s).")
        return filtered_articles

    async def _select_diverse_articles_gpt(self, articles: List[Dict[str, Any]], topic: str, focus) -> List[Dict[str, Any]]:
        """Uses GPT to select diverse articles from a list."""
        if not articles:
            return []
        if len(articles) <= NUM_FINAL_ARTICLES:
            return articles # Return all if fewer than needed

        print(f"Selecting {NUM_FINAL_ARTICLES} diverse articles from {len(articles)} candidates using GPT...")

        article_list_text = ""

        true_focus = (focus if focus is not None else "General")

        for i, article in enumerate(articles):
            headline = article["metadata"]["title"]["main"]
            abstract = article["metadata"]["abstract"]
            article_list_text += f"{i}. Headline: {headline}\n   Abstract: {abstract}\n\n"

        prompt = SELECT_DIVERSE_ARTICLES.format(
            num_articles=len(articles),
            num_select=NUM_FINAL_ARTICLES,
            topic=topic,
            article_list_text=article_list_text.strip(),
            focus=true_focus
        )

        try:
            # Using system prompt might be better for instruction following
            system_prompt = "You are an AI assistant tasked with selecting diverse news articles based on their headlines and abstracts."
            response = await self.openai_api.query_chatgpt(
                system_prompt=system_prompt,
                user_prompt=prompt,
                model=GPT_CHAT_MODEL,
                temperature=0.2 # Low temp for deterministic index selection
            )

            # Extract indices (expecting format "0,3,5,...")
            match = re.search(r'[\d,]+', response)
            if not match:
                print(f"ERROR: Could not parse indices from GPT response for diverse articles: {response}")
                # Fallback: return the first NUM_FINAL_ARTICLES
                return articles[:NUM_FINAL_ARTICLES]

            indices_str = match.group(0)
            selected_indices = [int(idx.strip()) for idx in indices_str.split(',') if idx.strip().isdigit()]

            selected_articles = [articles[i] for i in selected_indices if 0 <= i < len(articles)]
            print(f"Selected diverse article indices: {selected_indices}")
            return selected_articles

        except Exception as e:
            print(f"ERROR: Failed to select diverse articles using GPT: {e}")
            # Fallback: return the first NUM_FINAL_ARTICLES
            return articles[:NUM_FINAL_ARTICLES]

    async def _research_article(self, article: Dict[str, Any]) -> Tuple[str, Dict, str, Dict]:
        """Performs research using Perplexity and GPT Web concurrently."""
        headline = article.get('headline', {}).get('main', 'No Headline')
        abstract = article.get('abstract', 'No Abstract')
        query = DEEP_RESEARCH.format(headline=headline, abstract=abstract, source="NYT")
        article_url = article.get('web_url', 'N/A')
        print(f"Starting research for: {headline} ({article_url})")

        # Define tasks for concurrent execution
        perplexity_task = asyncio.create_task(
            self.perplexity_api.chat_completions(
                model=PERPLEXITY_MODEL,
                system_message="Provide factual, unbiased research based on the user query.",
                user_message=query,
                temperature=0.5, # Allow some variability in research
                search_domain_filter_force_include=[],
                search_domain_filter_force_exclude=[],
                return_images=False,
                search_recency_filter="week", # Focus on recent info
                web_search_options={"search_context_size": "medium"}
            )
        )

        gpt_web_task = asyncio.create_task(
            self.openai_api.query_search_tool(
                query=query,
                model=GPT_SEARCH_MODEL,
                temperature=0.5,
                # user_location could be added here if needed
                search_context_size="medium"
            )
        )

        # Await both tasks
        perplexity_result, gpt_web_result = await asyncio.gather(
            perplexity_task, gpt_web_task, return_exceptions=True
        )

        # Process Perplexity results
        pplx_text = "Perplexity research failed."
        pplx_citations = {}
        if isinstance(perplexity_result, Exception):
            print(f"ERROR: Perplexity research failed for '{headline}': {perplexity_result}")
        elif isinstance(perplexity_result, dict) and "error" in perplexity_result:
             print(f"ERROR: Perplexity API error for '{headline}': {perplexity_result.get('error')}")
             pplx_text = f"Perplexity research failed: {perplexity_result.get('error')}"
        elif isinstance(perplexity_result, tuple) and len(perplexity_result) == 2:
            pplx_text, pplx_citations = perplexity_result
            print(f"Perplexity research successful for: {headline}")
        else:
             print(f"ERROR: Unexpected Perplexity result format for '{headline}': {perplexity_result}")


        # Process GPT Web results
        gpt_web_text = "GPT Web research failed."
        gpt_web_citations = {}
        if isinstance(gpt_web_result, Exception):
            print(f"ERROR: GPT Web research failed for '{headline}': {gpt_web_result}")
        elif isinstance(gpt_web_result, tuple) and len(gpt_web_result) == 2:
             gpt_web_text, gpt_web_citations = gpt_web_result
             # Check if the text indicates an error internally
             if "Error querying web search tool:" in gpt_web_text:
                 print(f"ERROR: GPT Web API error for '{headline}': {gpt_web_text}")
             else:
                 print(f"GPT Web research successful for: {headline}")
        else:
            print(f"ERROR: Unexpected GPT Web result format for '{headline}': {gpt_web_result}")


        return pplx_text, pplx_citations, gpt_web_text, gpt_web_citations

    def _extract_urls(self, citations: Any) -> List[str]:
        if isinstance(citations, list):
            return [url for url in citations if isinstance(url, str)]
        elif isinstance(citations, dict):
            return [entry.get('url', '') for entry in citations.values() if isinstance(entry, dict) and entry.get('url')]
        return []

    async def _compose_story_gpt(self, article: Dict[str, Any], research_results: Dict[str, Any]) -> str:
        """Uses GPT to synthesize research into a story."""
        headline = article.get('headline', {}).get('main', 'No Headline')
        article_url = article.get('web_url', 'N/A')
        
        print(f"Composing story for: {headline} ({article_url})")

        perplexity_urls = self._extract_urls(research_results.get('perplexity_citations'))
        gpt_web_urls = self._extract_urls(research_results.get('gpt_web_citations'))

        combined_research = f"""
        Original Article Abstract:
        {article.get('abstract', 'N/A')}

        Perplexity Research Summary:
        {research_results.get('perplexity_text', 'N/A')}

        GPT Web Research Summary:
        {research_results.get('gpt_web_text', 'N/A')}

        Supporting Sources (URLs):
        Perplexity Sources: {', '.join(perplexity_urls)}
        GPT Web Sources: {', '.join(gpt_web_urls)}
        """

        prompt = COMPOSE_STORY.format(
            headline=headline,
            research=combined_research.strip()
        )

        try:
            system_prompt = "You are an expert news anchor AI. Synthesize the provided information into a concise, unbiased, 5-sentence news report."
            composed_story = await self.openai_api.query_chatgpt(
                system_prompt=system_prompt,
                user_prompt=prompt,
                model=GPT_CHAT_MODEL,
                temperature=0.6 # Balance creativity and factuality
            )
            print(f"Story composed successfully for: {headline}")
            return composed_story
        except Exception as e:
            print(f"ERROR: Failed to compose story using GPT for '{headline}': {e}")
            return f"Error composing story for {headline}."

    async def _generate_insights(self, article_content) -> dict:
        prompt = INSIGHTS_PROMPT.format(
            summary=article_content
        )
        try:
            system_prompt = "You are an unbiased expert financial analyst."
            composed_story = await self.openai_api.query_chatgpt(
                system_prompt=system_prompt,
                user_prompt=prompt,
                model=GPT_CHAT_MODEL,
                temperature=0.6 # Balance creativity and factuality
            )
            print(composed_story)
            print(f"Insights generated successfully")
            json_converted = json.loads(composed_story.replace('`', ''))
            return json_converted
        except Exception as e:
            print(f"ERROR: Failed to compose story using GPT for '': {e}")
            return f"Error composing story for."


    async def _get_and_select_x_posts(self, headline: str) -> List[Dict[str, Any]]:
        """Fetches latest X posts and selects diverse/impactful ones using GPT."""
        print(f"Fetching and selecting X posts related to: {headline}")
        raw_tweets = []
        selected_posts_data = []

        # Step 6: Query X posts
        try:
            # Use headline as a search query, maybe add source? Be careful with query length/complexity
            # Consider filtering by time as well if the API supports it.
            search_query = f'"{headline}"' # Search for exact headline phrase
            # Adding source might make query too specific: OR url:"{article_url}" ? (Depends on API)
            print(f"Searching X with query: {search_query}")
            raw_tweets = await self.twikit_api.request_and_return_results(
                search_query=search_query,
                result_type="Latest", # Get most recent relevant posts
                count=NUM_X_POSTS_TO_FETCH
                )
            print(f"Fetched {len(raw_tweets)} raw posts from X for: {headline}")
            if not raw_tweets:
                return [] # No posts found
        except ValueError as e:
            print(f"Warning: TwikitAPI credentials error: {e}. Skipping X post fetching.")
            return []
        except Exception as e:
            print(f"ERROR: Failed to fetch X posts for '{headline}': {e}")
            return [] # Proceed without X posts if fetching fails


        # Step 7: Use LLM to select diverse/impactful posts
        if not raw_tweets:
            return []

        post_list_text = ""
        tweet_data_map = {} # To easily retrieve full tweet data later
        for i, tweet in enumerate(raw_tweets):
             # Basic filtering for relevance/quality before sending to LLM
            if not tweet.text or tweet.text.strip().lower().startswith("rt @"): # Skip retweets or empty
                 continue
            # Could add more filters: min length, language detection etc.
            post_list_text += f"{i}. {tweet.user.screen_name}: {tweet.text}\n\n"
            tweet_data_map[i] = {
                'id': tweet.id,
                'text': tweet.text,
                'created_at': tweet.created_at if tweet.created_at else None,
                'user_name': tweet.user.name,
                'user_screen_name': tweet.user.screen_name,
                'url': f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}" # Construct URL
            }

        if not post_list_text or not tweet_data_map:
            print(f"No suitable posts found for LLM selection for: {headline}")
            return []


        prompt = SELECT_DIVERSE_X_POSTS.format(
            num_posts=len(tweet_data_map), # Count actual posts sent
            num_select=NUM_X_POSTS_TO_SELECT,
            headline=headline,
            post_list_text=post_list_text.strip()
        )

        try:
            system_prompt = "You are an AI assistant analyzing social media posts to find the most impactful and diverse reactions to a news story."
            response = await self.openai_api.query_chatgpt(
                system_prompt=system_prompt,
                user_prompt=prompt,
                model=GPT_CHAT_MODEL,
                temperature=0.3 # Lower temp for better index selection
            )

            # Extract indices
            match = re.search(r'[\d,]+', response)
            if not match:
                print(f"ERROR: Could not parse indices from GPT response for X posts selection: {response}")
                # Fallback: return first N suitable posts
                selected_indices = list(tweet_data_map.keys())[:NUM_X_POSTS_TO_SELECT]
            else:
                indices_str = match.group(0)
                selected_indices = [int(idx.strip()) for idx in indices_str.split(',') if idx.strip().isdigit()]

            # Retrieve full data for selected posts
            selected_posts_data = [tweet_data_map[i] for i in selected_indices if i in tweet_data_map]
            print(f"Selected {len(selected_posts_data)} diverse/impactful X posts for: {headline}")

        except Exception as e:
            print(f"ERROR: Failed to select diverse X posts using GPT for '{headline}': {e}")
            # Fallback: return first N suitable posts if GPT fails
            selected_posts_data = list(tweet_data_map.values())[:NUM_X_POSTS_TO_SELECT]


        return selected_posts_data


    async def generate_generic_news(self, topic: str = "business", focus=None) -> List[Dict[str, Any]]:
        """
        Generates a curated list of news articles for a generic topic.
        """

        AppData.data["emit_function"](AppData.data["socketio"], {"type": "status", "status": "Starting Genertion"});
        print(f"\n--- Starting Generic News Generation for Topic: {topic} ---")
        final_results = []

        AppData.data["emit_function"](AppData.data["socketio"], {"type": "status", "status": f"Connecting to Blockchain"});

        AppData.data["emit_function"](AppData.data["socketio"], {"type": "status", "status": "Updating News Index"});

        # 1. Query relevant articles using vector search WITH date filter
        print(f"\nStep 1: Searching for relevant articles for '{topic}' in Redis (filtered for last 24h)...")
        try:
            # Calculate date range for the last 24 hours (using UTC)
            end_dt = datetime.now(timezone.utc)

            back_days = (2 if focus is None else 10)

            start_dt = (datetime.now(timezone.utc) - timedelta(days=back_days)).replace(tzinfo=None)

            print(f"Date filter range: {start_dt.isoformat()} to {end_dt.isoformat()}")

            # Call search_similar with date filters and desired final count for candidates
            # We ask for NUM_INITIAL_ARTICLES directly, assuming the date filter is applied inside.

            AppData.data["emit_function"](AppData.data["socketio"], {"type": "status", "status": "Searching News Index"});

            query_text = (topic if focus is None else focus)

            recent_articles = self.vector_search.search_similar_shallow(
                query_text=query_text,
                top_k=NUM_INITIAL_ARTICLES, # Request the number needed for diversity selection
                start_date=start_dt
                # end_date=end_dt
            )
            print(f"Found {len(recent_articles)} relevant articles via vector search within the date range.")
            AppData.data["emit_function"](AppData.data["socketio"], {"type": "status", "status": f"Found {len(recent_articles)} Possible Articles"});

            # <<<< REMOVED the subsequent call to self._filter_articles_by_date >>>>
            # <<<< REMOVED the check if len(recent_articles) > NUM_INITIAL_ARTICLES >>>>
            # The result from search_similar is now assumed to be date-filtered and limited by top_k.

        except Exception as e:
            print(f"ERROR in Step 1 (Article Search/Filter): {e}")
            # Optionally log the full traceback
            import traceback
            traceback.print_exc()
            return [] # Cannot proceed without articles

        if not recent_articles:
            print("No recent articles found for the topic matching the criteria. Exiting.")
            return []

        # 2. Select diverse articles using GPT (Input is now 'recent_articles')
        print(f"\nStep 2: Selecting {NUM_FINAL_ARTICLES} diverse articles from {len(recent_articles)} candidates...")
        AppData.data["emit_function"](AppData.data["socketio"], {"type": "status", "status": f"Personalizing Candidate News"});
        # Pass the already filtered recent_articles list
        diverse_articles = await self._select_diverse_articles_gpt(recent_articles, topic, focus)
        if not diverse_articles:
            print("Failed to select diverse articles. Exiting.")
            return []
        print(f"Selected {len(diverse_articles)} articles for deep research.")
        AppData.data["emit_function"](AppData.data["socketio"], {"type": "status", "status": f"Using {len(diverse_articles)} Relevant Articles"});
        for i, art in enumerate(diverse_articles):
             # Ensure metadata exists before trying to access nested keys
             main_headline = art["metadata"]["title"]["main"]
             url = art.get('web_url', 'N/A') # URL is now top-level in the search_similar result
             print(f"  {i+1}. {main_headline} ({url})")


        # 3, 4, 5: Research and Compose (concurrently per article)
        print("\nSteps 3, 4, 5: Performing research and composing stories...")
        AppData.data["emit_function"](AppData.data["socketio"], {"type": "status", "status": f"Conducting Deep Research"});
        research_compose_tasks = []
        cur_count = 0 # To track the current article number
        for article in diverse_articles:
             # *** IMPORTANT: Ensure the article dict passed to _process_single_article
             # *** now matches the structure returned by the updated search_similar
             # *** which includes 'url', 'score', and 'metadata' at the top level.
             # *** The _process_single_article function needs to expect this structure.
            research_compose_tasks.append(asyncio.create_task(self._process_single_article(article, cur_count))) # Pass the dict directly
            cur_count += 1

        # Wait for all article processing to complete
        processed_article_results = await asyncio.gather(*research_compose_tasks, return_exceptions=True) # Added return_exceptions

        AppData.data["emit_function"](AppData.data["socketio"], {"type": "status", "status": f"Composing Articles"});

        # Filter out potential exceptions/errors from processing
        successful_processed_articles = [res for res in processed_article_results if isinstance(res, dict)]
        failed_tasks = [res for res in processed_article_results if isinstance(res, Exception) or res is None]
        if failed_tasks:
             print(f"Warning: {len(failed_tasks)} article(s) failed during research/composition.")
             # Optionally log details of failures

        AppData.data["emit_function"](AppData.data["socketio"], {"type": "status", "status": f"Searching X"});
        # 6, 7: Fetch and Select X Posts (concurrently per article)
        print("\nSteps 6, 7: Fetching and selecting X posts...")
        # x_post_tasks = []
        # # Use the successfully processed articles for fetching X posts
        # processed_articles_dict = {res['web_url']: res for res in diverse_articles} # Map by URL

        # # Iterate through the original diverse_articles list to maintain order for results
        # for article in diverse_articles:
        #      url = article.get('web_url')
        #      # Fetch posts only if the article was successfully processed earlier
        #      if url and url in processed_articles_dict:
        #          # Ensure metadata and headline are present before accessing
        #          headline = article["metadata"]["title"]["main"]
        #          x_post_tasks.append(asyncio.create_task(self._get_and_select_x_posts(headline, url)))
        #      else:
        #          # Append a placeholder for articles that failed processing or lacked URL
        #          x_post_tasks.append(asyncio.create_task(asyncio.sleep(0, result=[])))

        x_query = (topic if focus is None else focus)

        x_post_results = await self._get_and_select_x_posts(x_query)


        # Wait for all X post processing to complete
        # x_post_results = await asyncio.gather(*x_post_tasks, return_exceptions=True) # Added return_exceptions


        AppData.data["emit_function"](AppData.data["socketio"], {"type": "status", "status": f"Compiling Results"});
        # 8. Combine Results
        print("\nStep 8: Compiling final results...")
        # # Iterate through the successfully processed articles
        for i, article_data in enumerate(successful_processed_articles):
        #      # Find the corresponding X post result. This assumes the order of
        #      # successful_processed_articles matches the order of tasks created based on diverse_articles
        #      # where processing was successful. A more robust way might involve mapping via URL.
        #      original_index = -1
        #      for idx, da in enumerate(diverse_articles):
        #          if da.get('url') == article_data.get('web_url'):
        #             original_index = idx
        #             break

        #      if original_index != -1 and original_index < len(x_post_results):
        #         x_result = x_post_results[original_index]
        #         if isinstance(x_result, Exception):
        #             print(f"Warning: X post fetching failed for {article_data.get('web_url')}: {x_result}")
        #             article_data['x_posts'] = [] # Assign empty list on error
        #         elif isinstance(x_result, list):
        #              article_data['x_posts'] = x_result
        #         else:
        #              print(f"Warning: Unexpected X post result type for {article_data.get('web_url')}")
        #              article_data['x_posts'] = []

        #      else:
        #          print(f"Warning: Could not map X posts results for {article_data.get('web_url')}")
        #          article_data['x_posts'] = [] # Assign empty list if mapping fails


             final_results.append(article_data)
        final_results.append({
            'x_posts': x_post_results
        })
        AppData.data["emit_function"](AppData.data["socketio"], {"type": "new_data_x", "info": x_post_results});

        print(f"\n--- Generic News Generation Complete for Topic: {topic} ---")
        print(f"Generated {len(final_results)} final news items.")
        return final_results

    async def _process_single_article(self, article_search_result: Dict[str, Any], index: int) -> Dict[str, Any] | None:
        """
        Helper to manage research and composition for one article based on search_similar result structure.

        Args:
            article_search_result (Dict): A dictionary containing 'url', 'score', and 'metadata'.
        """
        # --- Adapt to the new input structure ---
        article_metadata = article_search_result.get('metadata')
        url = article_search_result.get('web_url', 'N/A')

        if not article_metadata:
            print(f"ERROR: Metadata missing for article URL: {url}. Cannot process.")
            return None

        headline_data = article_metadata.get('title', {})
        headline = headline_data.get('main', 'No Headline')
        abstract = article_metadata.get('abstract', 'No Abstract')
        # --- End adaptation ---

        try:
            # Steps 3 & 4: Research concurrently (pass headline/abstract)
            # Construct a temporary dict matching the old expected structure for _research_article if needed,
            # or update _research_article to take headline/abstract directly.
            # Let's assume _research_article can handle the metadata dict or parts of it.
            # Passing the whole metadata dict might be simplest if _research_article is adapted.
            temp_article_info = {
                'headline': headline_data, # Pass the headline dict
                'abstract': abstract,
                'web_url': url
                }
            pplx_text, pplx_citations, gpt_web_text, gpt_web_citations = await self._research_article(temp_article_info)

            research_results = {
                'perplexity_text': pplx_text,
                'perplexity_citations': pplx_citations,
                'gpt_web_text': gpt_web_text,
                'gpt_web_citations': gpt_web_citations,
            }

            # Step 5: Compose story (pass headline/abstract/research)
            # Adapt _compose_story_gpt if needed, or pass required info
            temp_compose_info = {
                 'headline': headline_data, # Pass the headline dict
                 'abstract': abstract,
                 'web_url': url
            }

            composed_story = await self._compose_story_gpt(temp_compose_info, research_results)

            # Extract images from metadata
            images = [media.get('url') for media in article_metadata.get('multimedia', []) if media.get('type') == 'image' and media.get('url')]
            images = [f"https://www.nytimes.com/{img}" if img.startswith("images/") else img for img in images]

            # Combine all sources
            all_sources = {}
            for i in range(len(pplx_citations)):
                all_sources[f"perplexity_{i}"] = pplx_citations[i]
            all_sources.update({f"gpt_web_{k}": v for k, v in gpt_web_citations.items()})

            insights = await self._generate_insights(composed_story)

            # Prepare final structure for this article
            article_output = {
                'headline': headline, # Use the main headline string
                'content': composed_story,
                'insights': insights,
                'abstract': abstract,
                'images': images,
                'date_published': article_metadata.get('pub_date', 'N/A'),
                'all_sources': all_sources,
                'lead_source': url,
                'web_url': url,
                'index': index,
                'all_data': fetchTooler.get_full_article_data(url),
            }

            AppData.data["emit_function"](AppData.data["socketio"], {"type": "new_data", "info": article_output});

            return article_output

        except Exception as e:
            print(f"FATAL ERROR processing article '{headline}' ({url}): {e}")
            import traceback
            traceback.print_exc() # Print full traceback for debugging
            return None # Indicate failure

        except Exception as e:
            print(f"FATAL ERROR processing article '{headline}' ({url}): {e}")
            # Optionally log the full error trace
            return None # Indicate failure for this article

    def generate_specific_news(self, query: str) -> None:
        """
        Placeholder for generating news based on a specific query or URL.
        (Currently returns None as requested).
        """
        print(f"\n--- Specific News Generation (Placeholder) ---")
        print(f"Received specific query: {query}")
        print("This function is not yet implemented.")
        return None

# --- Example Usage ---
async def run_example():
    try:
        orchestrator = NewsOrchestrator()
        # Example for generic news
        print("\nStarting Generic News Generation Example...")
        business_news = await orchestrator.generate_generic_news(topic="technology") # Changed topic for variety
        print(f"\nGenerated {len(business_news)} business news items.")

        if business_news:
            print("\n--- Example Output (First Item) ---")
            import json
            print(json.dumps(business_news, indent=2, default=str)) # Use default=str for datetime objects if any remain
            print("------------------------------------")

        # Example for specific news (placeholder)
        # print("\nStarting Specific News Generation Example...")
        # specific_result = orchestrator.generate_specific_news(query="Details about the latest Apple event")
        # print(f"Specific news result: {specific_result}")

    except Exception as e:
        print(f"\nAn error occurred during the example run: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Ensure you have an event loop running if using asyncio in scripts
    # In a Jupyter notebook, this might run directly.
    # If running as a script, use asyncio.run()
    print("Running Orchestrator Example...")
    asyncio.run(run_example())
    print("Orchestrator Example Finished.")