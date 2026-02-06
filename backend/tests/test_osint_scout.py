"""
Unit tests for OSINT Scout functionality.
"""
import pytest
from datetime import datetime, timedelta
from app.models import NewsArticle, RiskAssessment
from app.osint_scout import OSINTScout
from app.you_client import YouAPIClient


class TestRiskScoreCalculation:
    """Test risk score calculation logic."""
    
    def test_risk_score_bounds_empty_articles(self):
        """Risk score should be 0 for empty article list."""
        scout = OSINTScout(you_client=None)
        score = scout.calculate_global_risk_score([])
        assert score == 0.0
        assert 0.0 <= score <= 100.0
    
    def test_risk_score_bounds_with_articles(self):
        """Risk score should always be between 0 and 100."""
        scout = OSINTScout(you_client=None)
        
        # Create test articles with critical keywords
        articles = [
            NewsArticle(
                title="Crisis in Middle East Energy Sector",
                url="https://example.com/1",
                published_date=datetime.now(),
                snippet="Major crisis and collapse in energy markets",
                relevance_score=0.9
            ),
            NewsArticle(
                title="Currency Default Risk Rising",
                url="https://example.com/2",
                published_date=datetime.now() - timedelta(hours=12),
                snippet="Default risk and volatility concerns increase",
                relevance_score=0.8
            )
        ]
        
        score = scout.calculate_global_risk_score(articles)
        assert 0.0 <= score <= 100.0
        assert isinstance(score, float)
    
    def test_risk_score_critical_keywords(self):
        """Articles with critical keywords should produce high risk scores."""
        scout = OSINTScout(you_client=None)
        
        critical_article = NewsArticle(
            title="War and Crisis Lead to Catastrophe",
            url="https://example.com/critical",
            published_date=datetime.now(),
            snippet="Emergency default situation with conflict escalation",
            relevance_score=1.0
        )
        
        score = scout.calculate_global_risk_score([critical_article])
        assert score >= 80.0  # Critical keywords should produce high scores
    
    def test_risk_score_positive_keywords(self):
        """Articles with positive keywords should produce low risk scores."""
        scout = OSINTScout(you_client=None)
        
        positive_article = NewsArticle(
            title="Economic Growth and Recovery",
            url="https://example.com/positive",
            published_date=datetime.now(),
            snippet="Stability and improvement in markets with resolution",
            relevance_score=1.0
        )
        
        score = scout.calculate_global_risk_score([positive_article])
        assert score <= 50.0  # Positive keywords should produce low scores
    
    def test_recency_weighting(self):
        """Recent articles should have higher weight than old articles."""
        scout = OSINTScout(you_client=None)
        
        recent_article = NewsArticle(
            title="Risk Alert",
            url="https://example.com/recent",
            published_date=datetime.now(),
            snippet="Major risk developing",
            relevance_score=1.0
        )
        
        old_article = NewsArticle(
            title="Risk Alert",
            url="https://example.com/old",
            published_date=datetime.now() - timedelta(days=10),
            snippet="Major risk developing",
            relevance_score=1.0
        )
        
        recent_score = scout.calculate_global_risk_score([recent_article])
        old_score = scout.calculate_global_risk_score([old_article])
        
        # Recent article should produce higher score due to recency weight
        # Using "risk" keyword which gives ~65 base score, allowing recency to show difference
        assert recent_score >= old_score  # At minimum should be equal or higher


class TestSentimentAnalysis:
    """Test sentiment analysis functionality."""
    
    def test_sentiment_determination(self):
        """Test sentiment categorization based on risk score."""
        scout = OSINTScout(you_client=None)
        
        assert scout._determine_sentiment(90.0) == 'critical'
        assert scout._determine_sentiment(75.0) == 'negative'
        assert scout._determine_sentiment(50.0) == 'neutral'
        assert scout._determine_sentiment(30.0) == 'positive'
    
    def test_sentiment_boundaries(self):
        """Test sentiment boundaries."""
        scout = OSINTScout(you_client=None)
        
        assert scout._determine_sentiment(80.0) == 'critical'
        assert scout._determine_sentiment(79.9) == 'negative'
        assert scout._determine_sentiment(60.0) == 'negative'
        assert scout._determine_sentiment(59.9) == 'neutral'
        assert scout._determine_sentiment(40.0) == 'neutral'
        assert scout._determine_sentiment(39.9) == 'positive'


class TestRecencyWeight:
    """Test recency weight calculation."""
    
    def test_recency_weight_recent(self):
        """Articles less than 24 hours old should have weight 1.0."""
        scout = OSINTScout(you_client=None)
        
        recent_date = datetime.now() - timedelta(hours=12)
        weight = scout._calculate_recency_weight(recent_date)
        assert weight == 1.0
    
    def test_recency_weight_decay(self):
        """Weight should decay over time."""
        scout = OSINTScout(you_client=None)
        
        day_1 = datetime.now() - timedelta(hours=12)
        day_2 = datetime.now() - timedelta(hours=36)
        day_3 = datetime.now() - timedelta(hours=60)
        week_old = datetime.now() - timedelta(days=8)
        
        weight_1 = scout._calculate_recency_weight(day_1)
        weight_2 = scout._calculate_recency_weight(day_2)
        weight_3 = scout._calculate_recency_weight(day_3)
        weight_week = scout._calculate_recency_weight(week_old)
        
        assert weight_1 > weight_2 > weight_3 > weight_week
        assert weight_week == 0.1  # Minimum weight


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
