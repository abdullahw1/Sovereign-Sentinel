#!/usr/bin/env python3
"""
Test script to verify You.com API connection with real API key.
"""
import asyncio
from app.you_client import YouAPIClient
from app.config import settings

async def test_you_api():
    """Test You.com API connection."""
    print("Testing You.com API connection...")
    print(f"API Key: {settings.you_api_key[:15]}...")
    
    client = YouAPIClient(api_key=settings.you_api_key)
    
    try:
        # Test with a simple query
        articles = await client.search_news(
            query="Middle East energy crisis",
            max_results=3,
            use_cache=False
        )
        
        print(f"\n✓ Successfully retrieved {len(articles)} articles")
        
        for i, article in enumerate(articles, 1):
            print(f"\nArticle {i}:")
            print(f"  Title: {article.title}")
            print(f"  URL: {article.url}")
            print(f"  Published: {article.published_date}")
            print(f"  Relevance: {article.relevance_score}")
            print(f"  Snippet: {article.snippet[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"\n✗ API call failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("You.com API Connection Test")
    print("=" * 60)
    
    success = asyncio.run(test_you_api())
    
    if success:
        print("\n" + "=" * 60)
        print("✓ API connection successful!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("✗ API connection failed")
        print("=" * 60)
        exit(1)
