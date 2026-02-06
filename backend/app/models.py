"""
Data models for Sovereign Sentinel.
"""
from datetime import datetime
from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field


class NewsArticle(BaseModel):
    """Represents a news article from You.com API."""
    title: str
    url: str
    published_date: datetime
    snippet: str
    relevance_score: float = Field(ge=0.0, le=1.0, default=0.5)


class RiskAssessment(BaseModel):
    """Represents a geopolitical risk assessment."""
    timestamp: datetime
    global_risk_score: float = Field(ge=0.0, le=100.0)
    affected_sectors: List[str]
    source_articles: List[NewsArticle]
    sentiment: Literal['positive', 'neutral', 'negative', 'critical']
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2024-01-15T10:30:00Z",
                "global_risk_score": 75.5,
                "affected_sectors": ["energy", "currency"],
                "source_articles": [],
                "sentiment": "critical"
            }
        }


class LoanRecord(BaseModel):
    """Represents a loan record from the ledger."""
    loan_id: str = Field(alias="loanId")
    borrower: str
    industry: str
    interest_type: Literal['PIK', 'Cash', 'Hybrid'] = Field(alias="interestType")
    principal_amount: float = Field(alias="principalAmount")
    outstanding_balance: float = Field(alias="outstandingBalance")
    maturity_date: datetime = Field(alias="maturityDate")
    covenants: List[str] = Field(default_factory=list)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "loanId": "L001",
                "borrower": "Acme Energy",
                "industry": "energy",
                "interestType": "PIK",
                "principalAmount": 10000000,
                "outstandingBalance": 12500000,
                "maturityDate": "2025-12-31T00:00:00Z",
                "covenants": ["debt-to-equity < 2.0"]
            }
        }


class LoanHistoricalRecord(BaseModel):
    """Represents historical payment data for a loan."""
    loan_id: str = Field(alias="loanId")
    timestamp: datetime
    interest_type: Literal['PIK', 'Cash', 'Hybrid'] = Field(alias="interestType")
    outstanding_balance: float = Field(alias="outstandingBalance")
    
    class Config:
        populate_by_name = True


class AgentReasoningTrace(BaseModel):
    """Represents agent reasoning steps for transparency."""
    step: int
    action: str
    observation: str
    reasoning: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class FlaggedLoan(LoanRecord):
    """Represents a flagged high-risk loan with agent reasoning."""
    flag_reason: str
    risk_level: Literal['low', 'medium', 'high', 'critical']
    correlated_event: str
    flagged_at: datetime
    confidence_score: float = Field(ge=0.0, le=100.0, default=50.0)
    agent_reasoning: List[AgentReasoningTrace] = Field(default_factory=list)
    pik_toggle_detected: bool = False
    previous_interest_type: Optional[str] = None
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "loanId": "L001",
                "borrower": "Acme Energy",
                "industry": "energy",
                "interestType": "PIK",
                "principalAmount": 10000000,
                "outstandingBalance": 12500000,
                "maturityDate": "2025-12-31T00:00:00Z",
                "covenants": [],
                "flag_reason": "PIK toggle detected: switched from Cash to PIK",
                "risk_level": "critical",
                "correlated_event": "Middle East energy crisis",
                "flagged_at": "2024-01-15T10:30:00Z",
                "confidence_score": 85.0,
                "agent_reasoning": [],
                "pik_toggle_detected": True,
                "previous_interest_type": "Cash"
            }
        }


class Alert(BaseModel):
    """Represents a system alert."""
    alert_id: str = Field(alias="alertId")
    timestamp: datetime
    severity: Literal['info', 'warning', 'critical']
    title: str
    message: str
    action_required: bool = Field(alias="actionRequired")
    recommended_hedge: float = Field(alias="recommendedHedge", default=0.0)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "alertId": "alert_001",
                "timestamp": "2024-01-15T10:30:00Z",
                "severity": "critical",
                "title": "High-Risk Correlation Detected",
                "message": "Middle East energy crisis correlates with PIK debt exposure",
                "actionRequired": True,
                "recommendedHedge": 15.0
            }
        }


class AudioAlertResult(BaseModel):
    """Result of audio alert generation."""
    alert_id: str = Field(alias="alertId")
    audio_url: str = Field(alias="audioUrl")
    audio_path: str = Field(alias="audioPath", default="")
    status: Literal['generated', 'failed']
    script: str
    duration: float
    error: Optional[str] = None
    
    class Config:
        populate_by_name = True


class AuthorizationResult(BaseModel):
    """Result of user authorization action."""
    authorized: bool
    timestamp: datetime
    alert_id: str = Field(alias="alertId")
    action: str
    
    class Config:
        populate_by_name = True


class TradeResult(BaseModel):
    """Result of a trade execution."""
    trade_id: str = Field(alias="tradeId")
    timestamp: datetime
    asset: str
    amount: float
    price: float
    total_cost: float = Field(alias="totalCost")
    status: Literal['pending', 'completed', 'failed']
    exchange_order_id: str = Field(alias="exchangeOrderId")
    
    class Config:
        populate_by_name = True


class PortfolioImpact(BaseModel):
    """Portfolio impact from a trade."""
    previous_btc_position: float = Field(alias="previousBtcPosition")
    new_btc_position: float = Field(alias="newBtcPosition")
    hedge_percentage: float = Field(alias="hedgePercentage")
    
    class Config:
        populate_by_name = True


class HedgeExecutionReport(BaseModel):
    """Complete hedge execution report with agent reasoning."""
    trade_id: str = Field(alias="tradeId")
    timestamp: datetime
    status: Literal['completed', 'failed', 'pending']
    asset: str
    amount: float
    price: float
    total_cost: float = Field(alias="totalCost")
    exchange_order_id: str = Field(alias="exchangeOrderId")
    portfolio_impact: PortfolioImpact = Field(alias="portfolioImpact")
    human_readable_report: str = Field(alias="humanReadableReport")
    agent_reasoning: List[Dict[str, Any]] = Field(alias="agentReasoning", default_factory=list)
    
    class Config:
        populate_by_name = True
