"""
Data models for Sovereign Sentinel.
"""
from datetime import datetime
from typing import List, Literal, Optional
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


class FlaggedLoan(LoanRecord):
    """Represents a flagged high-risk loan."""
    flag_reason: str
    risk_level: Literal['low', 'medium', 'high', 'critical']
    correlated_event: str
    flagged_at: datetime
    
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
                "flag_reason": "PIK loan in high-risk sector",
                "risk_level": "critical",
                "correlated_event": "Middle East energy crisis",
                "flagged_at": "2024-01-15T10:30:00Z"
            }
        }
