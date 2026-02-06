"""
Unit tests for Forensic Auditor.
"""
import json
import pytest
from pathlib import Path
from datetime import datetime

from app.forensic_auditor import ForensicAuditor
from app.models import LoanRecord, FlaggedLoan


@pytest.fixture
def auditor():
    """Create a ForensicAuditor instance."""
    return ForensicAuditor()


@pytest.fixture
def sample_loans():
    """Create sample loan records."""
    return [
        LoanRecord(
            loanId="L001",
            borrower="Acme Energy",
            industry="energy",
            interestType="PIK",
            principalAmount=10000000,
            outstandingBalance=12500000,
            maturityDate=datetime(2025, 12, 31),
            covenants=["debt-to-equity < 2.0"]
        ),
        LoanRecord(
            loanId="L002",
            borrower="Global Mining",
            industry="mining",
            interestType="Cash",
            principalAmount=5000000,
            outstandingBalance=5200000,
            maturityDate=datetime(2024, 6, 30),
            covenants=[]
        ),
        LoanRecord(
            loanId="L003",
            borrower="LatAm Telecom",
            industry="currency",
            interestType="PIK",
            principalAmount=8000000,
            outstandingBalance=9500000,
            maturityDate=datetime(2025, 3, 15),
            covenants=["interest-coverage > 1.5"]
        )
    ]


class TestLedgerParsing:
    """Tests for ledger parsing functionality."""
    
    def test_parse_csv_ledger(self, auditor):
        """Test parsing a valid CSV ledger file."""
        csv_path = Path("data/test_ledger.csv")
        loans = auditor.parse_ledger(csv_path, format='csv')
        
        assert len(loans) == 5
        assert all(isinstance(loan, LoanRecord) for loan in loans)
        assert loans[0].loan_id == "L001"
        assert loans[0].borrower == "Acme Energy"
        assert loans[0].interest_type == "PIK"
    
    def test_parse_json_ledger(self, auditor):
        """Test parsing a valid JSON ledger file."""
        json_path = Path("data/test_ledger.json")
        loans = auditor.parse_ledger(json_path, format='json')
        
        assert len(loans) == 5
        assert all(isinstance(loan, LoanRecord) for loan in loans)
        assert loans[0].loan_id == "L001"
        assert loans[0].borrower == "Acme Energy"
        assert loans[0].interest_type == "PIK"
    
    def test_format_agnostic_parsing(self, auditor):
        """Test that CSV and JSON parsing produce equivalent results."""
        csv_path = Path("data/test_ledger.csv")
        json_path = Path("data/test_ledger.json")
        
        csv_loans = auditor.parse_ledger(csv_path, format='csv')
        json_loans = auditor.parse_ledger(json_path, format='json')
        
        assert len(csv_loans) == len(json_loans)
        
        # Compare key fields
        for csv_loan, json_loan in zip(csv_loans, json_loans):
            assert csv_loan.loan_id == json_loan.loan_id
            assert csv_loan.borrower == json_loan.borrower
            assert csv_loan.industry == json_loan.industry
            assert csv_loan.interest_type == json_loan.interest_type
            assert csv_loan.outstanding_balance == json_loan.outstanding_balance
    
    def test_invalid_file_path(self, auditor):
        """Test handling of non-existent file."""
        with pytest.raises(ValueError, match="Ledger file not found"):
            auditor.parse_ledger("nonexistent.csv")
    
    def test_unsupported_format(self, auditor):
        """Test handling of unsupported file format."""
        with pytest.raises(ValueError, match="Unsupported format"):
            auditor.parse_ledger("data/test_ledger.csv", format='xml')


class TestPIKFlagging:
    """Tests for PIK loan flagging logic."""
    
    def test_flag_pik_loans_in_risky_sectors(self, auditor, sample_loans):
        """Test flagging PIK loans in risky sectors."""
        risky_sectors = ["energy", "currency"]
        flagged = auditor.flag_high_risk_loans(sample_loans, risky_sectors, "Middle East crisis")
        
        # Should flag L001 (energy, PIK) and L003 (currency, PIK)
        assert len(flagged) == 2
        assert all(isinstance(loan, FlaggedLoan) for loan in flagged)
        assert flagged[0].loan_id == "L001"
        assert flagged[1].loan_id == "L003"
    
    def test_no_flagging_for_non_pik_loans(self, auditor, sample_loans):
        """Test that non-PIK loans are not flagged even in risky sectors."""
        risky_sectors = ["mining"]
        flagged = auditor.flag_high_risk_loans(sample_loans, risky_sectors, "Mining crisis")
        
        # L002 is in mining but is Cash type, should not be flagged
        assert len(flagged) == 0
    
    def test_no_flagging_for_safe_sectors(self, auditor, sample_loans):
        """Test that PIK loans in safe sectors are not flagged."""
        risky_sectors = ["technology"]
        flagged = auditor.flag_high_risk_loans(sample_loans, risky_sectors, "Tech crisis")
        
        # No PIK loans in technology sector
        assert len(flagged) == 0
    
    def test_flagged_loan_attributes(self, auditor, sample_loans):
        """Test that flagged loans have correct attributes."""
        risky_sectors = ["energy"]
        flagged = auditor.flag_high_risk_loans(sample_loans, risky_sectors, "Energy crisis")
        
        assert len(flagged) == 1
        loan = flagged[0]
        assert loan.flag_reason == "PIK loan in high-risk sector (energy)"
        assert loan.risk_level == "critical"  # Outstanding balance >= 10M
        assert loan.correlated_event == "Energy crisis"
        assert isinstance(loan.flagged_at, datetime)
    
    def test_risk_level_assignment(self, auditor):
        """Test risk level assignment based on outstanding balance."""
        loans = [
            LoanRecord(
                loanId="L1", borrower="A", industry="energy", interestType="PIK",
                principalAmount=1000000, outstandingBalance=15000000,
                maturityDate=datetime(2025, 12, 31), covenants=[]
            ),
            LoanRecord(
                loanId="L2", borrower="B", industry="energy", interestType="PIK",
                principalAmount=1000000, outstandingBalance=7000000,
                maturityDate=datetime(2025, 12, 31), covenants=[]
            ),
            LoanRecord(
                loanId="L3", borrower="C", industry="energy", interestType="PIK",
                principalAmount=1000000, outstandingBalance=3000000,
                maturityDate=datetime(2025, 12, 31), covenants=[]
            ),
            LoanRecord(
                loanId="L4", borrower="D", industry="energy", interestType="PIK",
                principalAmount=1000000, outstandingBalance=500000,
                maturityDate=datetime(2025, 12, 31), covenants=[]
            )
        ]
        
        flagged = auditor.flag_high_risk_loans(loans, ["energy"], "Crisis")
        
        assert flagged[0].risk_level == "critical"  # >= 10M
        assert flagged[1].risk_level == "high"      # >= 5M
        assert flagged[2].risk_level == "medium"    # >= 1M
        assert flagged[3].risk_level == "low"       # < 1M


class TestExposureRanking:
    """Tests for exposure ranking functionality."""
    
    def test_rank_by_outstanding_balance(self, auditor):
        """Test ranking flagged loans by outstanding balance."""
        flagged_loans = [
            FlaggedLoan(
                loanId="L1", borrower="A", industry="energy", interestType="PIK",
                principalAmount=1000000, outstandingBalance=5000000,
                maturityDate=datetime(2025, 12, 31), covenants=[],
                flag_reason="Test", risk_level="medium", correlated_event="Crisis",
                flagged_at=datetime.utcnow()
            ),
            FlaggedLoan(
                loanId="L2", borrower="B", industry="energy", interestType="PIK",
                principalAmount=1000000, outstandingBalance=15000000,
                maturityDate=datetime(2025, 12, 31), covenants=[],
                flag_reason="Test", risk_level="critical", correlated_event="Crisis",
                flagged_at=datetime.utcnow()
            ),
            FlaggedLoan(
                loanId="L3", borrower="C", industry="energy", interestType="PIK",
                principalAmount=1000000, outstandingBalance=8000000,
                maturityDate=datetime(2025, 12, 31), covenants=[],
                flag_reason="Test", risk_level="high", correlated_event="Crisis",
                flagged_at=datetime.utcnow()
            )
        ]
        
        ranked = auditor.rank_by_exposure(flagged_loans)
        
        assert len(ranked) == 3
        assert ranked[0].loan_id == "L2"  # 15M
        assert ranked[1].loan_id == "L3"  # 8M
        assert ranked[2].loan_id == "L1"  # 5M
        assert ranked[0].outstanding_balance >= ranked[1].outstanding_balance
        assert ranked[1].outstanding_balance >= ranked[2].outstanding_balance
    
    def test_rank_empty_list(self, auditor):
        """Test ranking an empty list."""
        ranked = auditor.rank_by_exposure([])
        assert ranked == []


class TestCompleteWorkflow:
    """Tests for complete portfolio analysis workflow."""
    
    def test_analyze_portfolio_csv(self, auditor):
        """Test complete analysis workflow with CSV file."""
        result = auditor.analyze_portfolio(
            "data/test_ledger.csv",
            risky_sectors=["energy", "currency"],
            correlated_event="Geopolitical crisis"
        )
        
        assert result['total_loans'] == 5
        assert result['flagged_loans'] == 3  # L001, L003, L005 (PIK in energy/currency)
        assert len(result['ranked_flagged_loans']) == 3
        
        # Check ranking order (by outstanding balance)
        ranked = result['ranked_flagged_loans']
        assert ranked[0].loan_id == "L005"  # 18M
        assert ranked[1].loan_id == "L001"  # 12.5M
        assert ranked[2].loan_id == "L003"  # 9.5M
    
    def test_analyze_portfolio_json(self, auditor):
        """Test complete analysis workflow with JSON file."""
        result = auditor.analyze_portfolio(
            "data/test_ledger.json",
            risky_sectors=["energy"],
            correlated_event="Energy crisis"
        )
        
        assert result['total_loans'] == 5
        assert result['flagged_loans'] == 2  # L001, L005 (PIK in energy)
        assert len(result['ranked_flagged_loans']) == 2
