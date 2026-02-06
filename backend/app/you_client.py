"""
You.com API client with error handling and caching.
"""
import httpx
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from app.models import NewsArticle
from app.config import settings

logger = logging.getLogger(__name__)


class YouAPIClient:
    """Client for interacting with You.com Search API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://ydc-index.io/v1"
        self.cache: Dict[str, tuple[List[NewsArticle], datetime]] = {}
        self.cache_ttl = timedelta(seconds=settings.cache_ttl_seconds)
        
    def _is_cache_valid(self, query: str) -> bool:
        """Check if cached data for query is still valid."""
        if query not in self.cache:
            return False
        _, cached_time = self.cache[query]
        return datetime.now() - cached_time < self.cache_ttl
    
    def _get_from_cache(self, query: str) -> Optional[List[NewsArticle]]:
        """Retrieve cached results if valid."""
        if self._is_cache_valid(query):
            articles, _ = self.cache[query]
            logger.info(f"Using cached results for query: {query}")
            return articles
        return None
    
    def _save_to_cache(self, query: str, articles: List[NewsArticle]) -> None:
        """Save results to cache."""
        self.cache[query] = (articles, datetime.now())
        logger.info(f"Cached {len(articles)} articles for query: {query}")
    
    async def search_news(
        self, 
        query: str, 
        max_results: int = 10,
        use_cache: bool = True
    ) -> List[NewsArticle]:
        """
        Search for news articles using You.com API.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            use_cache: Whether to use cached results if available
            
        Returns:
            List of NewsArticle objects
            
        Raises:
            Exception: If API call fails and no cached data is available
        """
        # Check cache first
        if use_cache:
            cached_results = self._get_from_cache(query)
            if cached_results is not None:
                return cached_results[:max_results]
        
        # Make API request
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {
                    "X-API-Key": self.api_key
                }
                
                params = {
                    "query": query,
                    "count": max_results
                }
                
                logger.info(f"Searching You.com API for: {query}")
                response = await client.get(
                    f"{self.base_url}/search",
                    headers=headers,
                    params=params
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Parse response into NewsArticle objects
                articles = self._parse_response(data)
                
                # Cache the results
                self._save_to_cache(query, articles)
                
                logger.info(f"Retrieved {len(articles)} articles from You.com API")
                return articles[:max_results]
                
        except httpx.HTTPError as e:
            logger.error(f"You.com API HTTP error: {e}")
            # Try to return cached data even if expired
            if query in self.cache:
                articles, cached_time = self.cache[query]
                logger.warning(f"Using expired cache from {cached_time} due to API error")
                return articles[:max_results]
            raise Exception(f"You.com API error and no cached data available: {e}")
            
        except Exception as e:
            logger.error(f"Unexpected error calling You.com API: {e}")
            # Try to return cached data even if expired
            if query in self.cache:
                articles, cached_time = self.cache[query]
                logger.warning(f"Using expired cache from {cached_time} due to error")
                return articles[:max_results]
            raise Exception(f"Unexpected error and no cached data available: {e}")
    
    def _parse_response(self, data: Dict[str, Any]) -> List[NewsArticle]:
        """
        Parse You.com API response into NewsArticle objects.
        
        Args:
            data: Raw API response data
            
        Returns:
            List of NewsArticle objects
        """
        articles = []
        
        # You.com search API returns results in 'results.news' field
        results_data = data.get('results', {})
        news_results = results_data.get('news', [])
        
        for result in news_results:
            try:
                # Validate required fields exist
                if 'title' not in result or 'url' not in result:
                    logger.warning(f"Skipping article with missing required fields: {result}")
                    continue
                
                # Parse published date from 'page_age' field
                published_str = result.get('page_age', '')
                published_date = self._parse_date(published_str)
                
                article = NewsArticle(
                    title=result['title'],
                    url=result['url'],
                    published_date=published_date,
                    snippet=result.get('description', ''),
                    relevance_score=0.5  # You.com doesn't provide relevance score in news results
                )
                articles.append(article)
                
            except Exception as e:
                logger.warning(f"Failed to parse article: {e}")
                continue
        
        return articles
    
    def _parse_date(self, date_str: str) -> datetime:
        """
        Parse date string from various formats.
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            datetime object
        """
        if not date_str:
            return datetime.now()
        
        try:
            # Try ISO format first
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            pass
        
        try:
            # Try common formats
            from dateutil import parser
            return parser.parse(date_str)
        except:
            # Default to now if parsing fails
            logger.warning(f"Could not parse date: {date_str}, using current time")
            return datetime.now()
