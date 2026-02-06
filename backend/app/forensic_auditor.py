"""
Forensic Auditor: Analyzes loan portfolio data and flags high-risk PIK loans.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Union

import pandas as pd
from pydantic import ValidationError

from app.models import LoanRecord, FlaggedLoan

logger = logging.getLogger(__name__)


class ForensicAuditor:
    """Analyzes loan portfolios and identifies high-risk PIK loans."""
    
    def __init__(self):
        """Initialize the Forensic Auditor."""
        self.validation_errors: List[dict] = []
    
    def parse_ledger(self, file_path: Union[str, Path], format: str = None) -> List[LoanRecord]:
        """
        Parse a ledger file in CSV or JSON format.
        
        Args:
            file_path: Path to the ledger file
            format: File format ('csv' or 'json'). If None, inferred from extension.
            
        Returns:
            List of validated LoanRecord objects
            
        Raises:
            ValueError: If file format is unsupported or file doesn't exist
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise ValueError(f"Ledger file not found: {file_path}")
        
        # Infer format from extension if not provided
        if format is None:
            format = file_path.suffix.lower().lstrip('.')
        
        if format == 'csv':
            return self._parse_csv(file_path)
        elif format == 'json':
            return self._parse_json(file_path)
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'csv' or 'json'.")
    
    def _parse_csv(self, file_path: Path) -> List[LoanRecord]:
        """Parse CSV ledger file using pandas."""
        self.validation_errors = []
        loan_records = []
        
        try:
            df = pd.read_csv(file_path)
            
            # Convert column names to camelCase for Pydantic
            df.columns = df.columns.str.strip()
            
            for idx, row in df.iterrows():
                try:
                    # Convert row to dict and handle date parsing
                    loan_data = row.to_dict()
                    
                    # Parse maturity date if it's a string
                    if 'maturityDate' in loan_data and isinstance(loan_data['maturityDate'], str):
                        loan_data['maturityDate'] = pd.to_datetime(loan_data['maturityDate']).to_pydatetime()
                    
                    # Handle covenants field (may be string or list)
                    if 'covenants' in loan_data:
                        if pd.isna(loan_data['covenants']):
                            loan_data['covenants'] = []
                        elif isinstance(loan_data['covenants'], str):
                            # Split by semicolon or comma
                            loan_data['covenants'] = [c.strip() for c in loan_data['covenants'].split(';') if c.strip()]
                    
                    loan_record = LoanRecord(**loan_data)
                    loan_records.append(loan_record)
                    
                except (ValidationError, ValueError, TypeError) as e:
                    error_msg = f"Row {idx + 2}: {str(e)}"
                    logger.warning(f"Skipping invalid record - {error_msg}")
                    self.validation_errors.append({
                        'row': idx + 2,
                        'error': str(e),
                        'data': row.to_dict()
                    })
                    continue
            
            logger.info(f"Parsed {len(loan_records)} valid records from CSV (skipped {len(self.validation_errors)} invalid)")
            return loan_records
            
        except Exception as e:
            logger.error(f"Failed to parse CSV file: {e}")
            raise ValueError(f"CSV parsing error: {e}")
    
    def _parse_json(self, file_path: Path) -> List[LoanRecord]:
        """Parse JSON ledger file with validation."""
        self.validation_errors = []
        loan_records = []
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Handle both array of loans and object with loans array
            if isinstance(data, dict) and 'loans' in data:
                loans_data = data['loans']
            elif isinstance(data, list):
                loans_data = data
            else:
                raise ValueError("JSON must be an array of loans or object with 'loans' key")
            
            for idx, loan_data in enumerate(loans_data):
                try:
                    # Parse maturity date if it's a string
                    if 'maturityDate' in loan_data and isinstance(loan_data['maturityDate'], str):
                        loan_data['maturityDate'] = datetime.fromisoformat(loan_data['maturityDate'].replace('Z', '+00:00'))
                    
                    loan_record = LoanRecord(**loan_data)
                    loan_records.append(loan_record)
                    
                except (ValidationError, ValueError, TypeError) as e:
                    error_msg = f"Record {idx}: {str(e)}"
                    logger.warning(f"Skipping invalid record - {error_msg}")
                    self.validation_errors.append({
                        'index': idx,
                        'error': str(e),
                        'data': loan_data
                    })
                    continue
            
            logger.info(f"Parsed {len(loan_records)} valid records from JSON (skipped {len(self.validation_errors)} invalid)")
            return loan_records
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON file: {e}")
            raise ValueError(f"JSON parsing error: {e}")
        except Exception as e:
            logger.error(f"Failed to parse JSON file: {e}")
            raise ValueError(f"JSON parsing error: {e}")
    
    def flag_high_risk_loans(
        self, 
        loans: List[LoanRecord], 
        risky_sectors: List[str],
        correlated_event: str = "Geopolitical crisis"
    ) -> List[FlaggedLoan]:
        """
        Flag loans where interestType is PIK and industry is in risky sectors.
        
        Args:
            loans: List of loan records to analyze
            risky_sectors: List of high-risk industry sectors
            correlated_event: Description of the correlated geopolitical event
            
        Returns:
            List of flagged loans
        """
        flagged_loans = []
        
        for loan in loans:
            # Flagging logic: PIK loan in risky sector
            if loan.interest_type == 'PIK' and loan.industry.lower() in [s.lower() for s in risky_sectors]:
                # Determine risk level based on outstanding balance
                if loan.outstanding_balance >= 10_000_000:
                    risk_level = 'critical'
                elif loan.outstanding_balance >= 5_000_000:
                    risk_level = 'high'
                elif loan.outstanding_balance >= 1_000_000:
                    risk_level = 'medium'
                else:
                    risk_level = 'low'
                
                flagged_loan = FlaggedLoan(
                    **loan.model_dump(),
                    flag_reason=f"PIK loan in high-risk sector ({loan.industry})",
                    risk_level=risk_level,
                    correlated_event=correlated_event,
                    flagged_at=datetime.utcnow()
                )
                flagged_loans.append(flagged_loan)
        
        logger.info(f"Flagged {len(flagged_loans)} high-risk PIK loans out of {len(loans)} total loans")
        return flagged_loans
    
    def rank_by_exposure(self, flagged_loans: List[FlaggedLoan]) -> List[FlaggedLoan]:
        """
        Rank flagged loans by exposure amount (outstanding balance) in descending order.
        
        Args:
            flagged_loans: List of flagged loans
            
        Returns:
            Sorted list of flagged loans (highest exposure first)
        """
        ranked = sorted(flagged_loans, key=lambda loan: loan.outstanding_balance, reverse=True)
        logger.info(f"Ranked {len(ranked)} flagged loans by exposure")
        return ranked
    
    def analyze_portfolio(
        self,
        file_path: Union[str, Path],
        risky_sectors: List[str],
        correlated_event: str = "Geopolitical crisis",
        format: str = None
    ) -> dict:
        """
        Complete portfolio analysis workflow.
        
        Args:
            file_path: Path to ledger file
            risky_sectors: List of high-risk sectors
            correlated_event: Description of correlated event
            format: File format ('csv' or 'json')
            
        Returns:
            Dictionary with analysis results
        """
        # Parse ledger
        loans = self.parse_ledger(file_path, format)
        
        # Flag high-risk loans
        flagged = self.flag_high_risk_loans(loans, risky_sectors, correlated_event)
        
        # Rank by exposure
        ranked = self.rank_by_exposure(flagged)
        
        return {
            'total_loans': len(loans),
            'flagged_loans': len(flagged),
            'validation_errors': len(self.validation_errors),
            'ranked_flagged_loans': ranked,
            'errors': self.validation_errors
        }
