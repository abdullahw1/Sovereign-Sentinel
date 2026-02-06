"""
Unit tests for You.com API client.
"""
import pytest
from datetime import datetime, timedelta
from app.you_client import YouAPIClient
from app.models import NewsArticle


class TestYouAPIClientCache:
    """Test caching functionality of You.com API client."""
    
    def test_cache_initialization(self):
        """Client should initialize with empty cache."""
        client = YouAPIClient(api_key="test_key")
        assert len(client.cache) == 0
    
    def test_cache_validity_check(self):
        """Test cache validity checking."""
        client = YouAPIClient(api_key="test_key")
        
        # Empty cache should be invalid
        assert not client._is_cache_valid("test_query")
        
        # Add to cache
        articles = [
            NewsArticle(
                title="Test",
                url="https://example.com",
                published_date=datetime.now(),
                snippet="Test snippet",
                relevance_score=0.5
            )
        ]
        client._save_to_cache("test_query", articles)
        
        # Should now be valid
        assert client._is_cache_valid("test_query")
    
    def test_cache_expiration(self):
        """Cache should expire after TTL."""
        client = YouAPIClient(api_key="test_key")
        
        articles = [
            NewsArticle(
                title="Test",
                url="https://example.com",
                published_date=datetime.now(),
                snippet="Test snippet",
                relevance_score=0.5
            )
        ]
        
        # Manually set cache with old timestamp
        old_time = datetime.now() - timedelta(seconds=client.cache_ttl.total_seconds() + 1)
        client.cache["test_query"] = (articles, old_time)
        
        # Should be invalid due to expiration
        assert not client._is_cache_valid("test_query")
    
    def test_get_from_cache(self):
        """Test retrieving from cache."""
        client = YouAPIClient(api_key="test_key")
        
        articles = [
            NewsArticle(
                title="Test",
                url="https://example.com",
                published_date=datetime.now(),
                snippet="Test snippet",
                relevance_score=0.5
            )
        ]
        
        client._save_to_cache("test_query", articles)
        
        cached = client._get_from_cache("test_query")
        assert cached is not None
        assert len(cached) == 1
        assert cached[0].title == "Test"


class TestDateParsing:
    """Test date parsing functionality."""
    
    def test_parse_iso_date(self):
        """Should parse ISO format dates."""
        client = YouAPIClient(api_key="test_key")
        
        iso_date = "2024-01-15T10:30:00Z"
        parsed = client._parse_date(iso_date)
        assert isinstance(parsed, datetime)
    
    def test_parse_empty_date(self):
        """Should return current time for empty date."""
        client = YouAPIClient(api_key="test_key")
        
        parsed = client._parse_date("")
        assert isinstance(parsed, datetime)
        # Should be very recent
        assert (datetime.now() - parsed).total_seconds() < 1
    
    def test_parse_invalid_date(self):
        """Should return current time for invalid date."""
        client = YouAPIClient(api_key="test_key")
        
        parsed = client._parse_date("invalid_date_string")
        assert isinstance(parsed, datetime)


class TestResponseParsing:
    """Test API response parsing."""
    
    def test_parse_empty_response(self):
        """Should handle empty response."""
        client = YouAPIClient(api_key="test_key")
        
        articles = client._parse_response({})
        assert articles == []
    
    def test_parse_response_with_hits(self):
        """Should parse response with 'results.news' field."""
        client = YouAPIClient(api_key="test_key")
        
        response = {
            "results": {
                "news": [
                    {
                        "title": "Test Article",
                        "url": "https://example.com",
                        "page_age": "2024-01-15T10:30:00Z",
                        "description": "Test snippet"
                    }
                ]
            }
        }
        
        articles = client._parse_response(response)
        assert len(articles) == 1
        assert articles[0].title == "Test Article"
        assert articles[0].relevance_score == 0.5
    
    def test_parse_response_with_results(self):
        """Should parse response with 'results.news' field."""
        client = YouAPIClient(api_key="test_key")
        
        response = {
            "results": {
                "news": [
                    {
                        "title": "Test Article",
                        "url": "https://example.com",
                        "page_age": "2024-01-15T10:30:00Z",
                        "description": "Test description"
                    }
                ]
            }
        }
        
        articles = client._parse_response(response)
        assert len(articles) == 1
        assert articles[0].title == "Test Article"
        assert articles[0].snippet == "Test description"
    
    def test_parse_response_with_invalid_article(self):
        """Should skip invalid articles and continue."""
        client = YouAPIClient(api_key="test_key")
        
        response = {
            "results": {
                "news": [
                    {
                        "title": "Valid Article",
                        "url": "https://example.com",
                        "page_age": "2024-01-15T10:30:00Z",
                        "description": "Valid snippet"
                    },
                    {
                        # Missing required fields - should be skipped
                        "invalid": "data"
                    },
                    {
                        "title": "Another Valid Article",
                        "url": "https://example2.com",
                        "page_age": "2024-01-15T11:00:00Z",
                        "description": "Another snippet"
                    }
                ]
            }
        }
        
        articles = client._parse_response(response)
        assert len(articles) == 2
        assert articles[0].title == "Valid Article"
        assert articles[1].title == "Another Valid Article"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
