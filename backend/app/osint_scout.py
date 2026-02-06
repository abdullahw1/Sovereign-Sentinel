"""
OSINT Scout agent for geopolitical intelligence gathering.
"""
import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Literal, Optional
from pathlib import Path
from app.models import NewsArticle, RiskAssessment
from app.you_client import YouAPIClient
from app.config import settings

logger = logging.getLogger(__name__)


class OSINTScout:
    """Agent responsible for tracking global crises using You.com API."""
    
    # Predefined sectors to monitor
    MONITORED_SECTORS = [
        "Middle East energy",
        "Latin America currency volatility",
        "sovereign debt default",
        "geopolitical crisis"
    ]
    
    # Sentiment keywords for analysis
    SENTIMENT_KEYWORDS = {
        'critical': ['crisis', 'collapse', 'default', 'war', 'conflict', 'emergency', 'catastrophe'],
        'negative': ['risk', 'threat', 'concern', 'decline', 'fall', 'drop', 'volatility', 'instability'],
        'neutral': ['stable', 'steady', 'unchanged', 'monitor', 'watch'],
        'positive': ['growth', 'recovery', 'improvement', 'stability', 'agreement', 'resolution']
    }
    
    def __init__(self, you_client: YouAPIClient, storage_path: str = "data"):
        self.you_client = you_client
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.latest_assessment: Optional[RiskAssessment] = None
        
    async def scan_geopolitical_events(self, sectors: List[str] = None) -> RiskAssessment:
        """
        Scan for geopolitical events across specified sectors.
        
        Args:
            sectors: List of sectors to scan. If None, uses default MONITORED_SECTORS.
            
        Returns:
            RiskAssessment object with calculated risk score
        """
        if sectors is None:
            sectors = self.MONITORED_SECTORS
        
        logger.info(f"Starting geopolitical scan for sectors: {sectors}")
        
        all_articles: List[NewsArticle] = []
        affected_sectors: List[str] = []
        
        # Query each sector
        for sector in sectors:
            try:
                articles = await self.you_client.search_news(
                    query=f"{sector} crisis risk",
                    max_results=5
                )
                
                if articles:
                    all_articles.extend(articles)
                    affected_sectors.append(sector)
                    logger.info(f"Found {len(articles)} articles for sector: {sector}")
                    
            except Exception as e:
                logger.error(f"Error scanning sector {sector}: {e}")
                continue
        
        # Calculate risk score
        risk_score = self.calculate_global_risk_score(all_articles)
        
        # Determine sentiment
        sentiment = self._determine_sentiment(risk_score)
        
        # Create assessment
        assessment = RiskAssessment(
            timestamp=datetime.now(),
            global_risk_score=risk_score,
            affected_sectors=affected_sectors,
            source_articles=all_articles,
            sentiment=sentiment
        )
        
        # Persist assessment
        await self.persist_risk_score(assessment)
        
        # Store as latest
        self.latest_assessment = assessment
        
        logger.info(f"Scan complete. Risk Score: {risk_score:.2f}, Sentiment: {sentiment}")
        
        return assessment
    
    def calculate_global_risk_score(self, news_results: List[NewsArticle]) -> float:
        """
        Calculate Global Risk Score (0-100) based on news articles.
        
        The score is calculated using:
        - Sentiment analysis (keyword matching)
        - Recency weighting (newer articles weighted higher)
        - Relevance scores from API
        
        Args:
            news_results: List of NewsArticle objects
            
        Returns:
            Risk score between 0 and 100
        """
        if not news_results:
            return 0.0
        
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for article in news_results:
            # Calculate sentiment score (0-100)
            sentiment_score = self._analyze_sentiment(article)
            
            # Calculate recency weight (newer = higher weight)
            recency_weight = self._calculate_recency_weight(article.published_date)
            
            # Use relevance score from API
            relevance_weight = article.relevance_score
            
            # Combined weight
            weight = recency_weight * relevance_weight
            
            total_weighted_score += sentiment_score * weight
            total_weight += weight
        
        # Calculate final score
        if total_weight == 0:
            return 0.0
        
        risk_score = total_weighted_score / total_weight
        
        # Ensure score is within bounds [0, 100]
        risk_score = max(0.0, min(100.0, risk_score))
        
        return round(risk_score, 2)
    
    def _analyze_sentiment(self, article: NewsArticle) -> float:
        """
        Analyze sentiment of an article using keyword matching.
        
        Args:
            article: NewsArticle object
            
        Returns:
            Sentiment score (0-100)
        """
        text = f"{article.title} {article.snippet}".lower()
        
        # Count keyword matches
        critical_count = sum(1 for kw in self.SENTIMENT_KEYWORDS['critical'] if kw in text)
        negative_count = sum(1 for kw in self.SENTIMENT_KEYWORDS['negative'] if kw in text)
        neutral_count = sum(1 for kw in self.SENTIMENT_KEYWORDS['neutral'] if kw in text)
        positive_count = sum(1 for kw in self.SENTIMENT_KEYWORDS['positive'] if kw in text)
        
        # Calculate weighted score
        if critical_count > 0:
            return 90.0 + min(critical_count * 2, 10.0)  # 90-100
        elif negative_count > positive_count:
            return 60.0 + min(negative_count * 5, 30.0)  # 60-90
        elif neutral_count > 0 or (negative_count == positive_count):
            return 40.0 + min(neutral_count * 5, 20.0)  # 40-60
        else:
            return 10.0 + min(positive_count * 5, 30.0)  # 10-40
    
    def _calculate_recency_weight(self, published_date: datetime) -> float:
        """
        Calculate recency weight for an article.
        
        Args:
            published_date: When the article was published
            
        Returns:
            Weight between 0.1 and 1.0 (newer = higher)
        """
        now = datetime.now()
        
        # Handle timezone-aware vs naive datetime
        if published_date.tzinfo is not None and now.tzinfo is None:
            from datetime import timezone
            now = now.replace(tzinfo=timezone.utc)
        elif published_date.tzinfo is None and now.tzinfo is not None:
            now = now.replace(tzinfo=None)
        
        age = now - published_date
        age_hours = age.total_seconds() / 3600
        
        # Exponential decay: articles lose weight over time
        # 24 hours = 1.0, 48 hours = 0.7, 72 hours = 0.5, 1 week = 0.3
        if age_hours < 24:
            return 1.0
        elif age_hours < 48:
            return 0.7
        elif age_hours < 72:
            return 0.5
        elif age_hours < 168:  # 1 week
            return 0.3
        else:
            return 0.1
    
    def _determine_sentiment(
        self, 
        risk_score: float
    ) -> Literal['positive', 'neutral', 'negative', 'critical']:
        """
        Determine overall sentiment based on risk score.
        
        Args:
            risk_score: Global risk score (0-100)
            
        Returns:
            Sentiment category
        """
        if risk_score >= 80:
            return 'critical'
        elif risk_score >= 60:
            return 'negative'
        elif risk_score >= 40:
            return 'neutral'
        else:
            return 'positive'
    
    async def persist_risk_score(self, assessment: RiskAssessment) -> None:
        """
        Persist risk assessment to storage.
        
        Args:
            assessment: RiskAssessment object to persist
        """
        try:
            # Save to JSON file with timestamp
            filename = f"risk_assessment_{assessment.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.storage_path / filename
            
            with open(filepath, 'w') as f:
                json.dump(assessment.model_dump(mode='json'), f, indent=2, default=str)
            
            logger.info(f"Persisted risk assessment to {filepath}")
            
            # Also save as latest
            latest_path = self.storage_path / "latest_assessment.json"
            with open(latest_path, 'w') as f:
                json.dump(assessment.model_dump(mode='json'), f, indent=2, default=str)
            
        except Exception as e:
            logger.error(f"Failed to persist risk assessment: {e}")
            raise
    
    def get_latest_assessment(self) -> Optional[RiskAssessment]:
        """
        Retrieve the latest risk assessment.
        
        Returns:
            Latest RiskAssessment or None if not available
        """
        if self.latest_assessment:
            return self.latest_assessment
        
        # Try to load from file
        try:
            latest_path = self.storage_path / "latest_assessment.json"
            if latest_path.exists():
                with open(latest_path, 'r') as f:
                    data = json.load(f)
                    self.latest_assessment = RiskAssessment(**data)
                    return self.latest_assessment
        except Exception as e:
            logger.error(f"Failed to load latest assessment: {e}")
        
        return None
