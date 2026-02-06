#!/usr/bin/env python3
"""
Simple test script to verify the application works without real API keys.
"""
import asyncio
from datetime import datetime
from app.models import NewsArticle, RiskAssessment
from app.osint_scout import OSINTScout

def test_risk_calculation():
    """Test risk score calculation without API calls."""
    print("Testing OSINT Scout risk calculation...")
    
    # Create a mock scout (no API client needed for calculation)
    scout = OSINTScout(you_client=None)
    
    # Create sample articles
    articles = [
        NewsArticle(
            title="Middle East Energy Crisis Escalates",
            url="https://example.com/1",
            published_date=datetime.now(),
            snippet="Major crisis in energy sector with supply disruptions",
            relevance_score=0.9
        ),
        NewsArticle(
            title="Latin America Currency Volatility Increases",
            url="https://example.com/2",
            published_date=datetime.now(),
            snippet="Currency markets showing significant instability and risk",
            relevance_score=0.8
        ),
        NewsArticle(
            title="Sovereign Debt Default Concerns Rise",
            url="https://example.com/3",
            published_date=datetime.now(),
            snippet="Growing concerns about potential default on sovereign obligations",
            relevance_score=0.85
        )
    ]
    
    # Calculate risk score
    risk_score = scout.calculate_global_risk_score(articles)
    
    print(f"✓ Risk Score Calculated: {risk_score:.2f}/100")
    
    # Verify score is in valid range
    assert 0 <= risk_score <= 100, f"Risk score {risk_score} out of bounds!"
    print(f"✓ Risk score is within valid bounds [0, 100]")
    
    # Test sentiment determination
    sentiment = scout._determine_sentiment(risk_score)
    print(f"✓ Sentiment: {sentiment}")
    
    # Create assessment
    assessment = RiskAssessment(
        timestamp=datetime.now(),
        global_risk_score=risk_score,
        affected_sectors=["energy", "currency", "sovereign debt"],
        source_articles=articles,
        sentiment=sentiment
    )
    
    print(f"✓ Assessment created successfully")
    print(f"  - Timestamp: {assessment.timestamp}")
    print(f"  - Risk Score: {assessment.global_risk_score}")
    print(f"  - Sentiment: {assessment.sentiment}")
    print(f"  - Affected Sectors: {', '.join(assessment.affected_sectors)}")
    print(f"  - Articles: {len(assessment.source_articles)}")
    
    return True

def test_models():
    """Test data models."""
    print("\nTesting data models...")
    
    # Test NewsArticle
    article = NewsArticle(
        title="Test Article",
        url="https://example.com",
        published_date=datetime.now(),
        snippet="Test snippet",
        relevance_score=0.75
    )
    print(f"✓ NewsArticle model works")
    
    # Test RiskAssessment
    assessment = RiskAssessment(
        timestamp=datetime.now(),
        global_risk_score=65.5,
        affected_sectors=["test"],
        source_articles=[article],
        sentiment="negative"
    )
    print(f"✓ RiskAssessment model works")
    
    # Test JSON serialization
    json_data = assessment.model_dump(mode='json')
    print(f"✓ JSON serialization works")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Sovereign Sentinel - Application Test")
    print("=" * 60)
    
    try:
        test_models()
        test_risk_calculation()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        print("\nThe application is working correctly.")
        print("To run the server, use:")
        print("  source venv/bin/activate")
        print("  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
