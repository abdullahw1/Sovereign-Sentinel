"""
Forensic Auditor: Analyzes loan portfolio data and flags high-risk PIK loans.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Union, Optional, Dict

import pandas as pd
from pydantic import ValidationError

from app.models import LoanRecord, FlaggedLoan, LoanHistoricalRecord, AgentReasoningTrace
from app.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


class ForensicAuditor:
    """Analyzes loan portfolios and identifies high-risk PIK loans with AI reasoning."""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the Forensic Auditor.
        
        Args:
            openai_api_key: Optional OpenAI API key for agent reasoning
        """
        self.validation_errors: List[dict] = []
        self.openai_client = OpenAIClient(api_key=openai_api_key)
        self.historical_data: Dict[str, List[LoanHistoricalRecord]] = {}
    
    def load_historical_data(self, file_path: Union[str, Path]) -> None:
        """
        Load historical loan payment data for PIK toggle detection.
        
        Args:
            file_path: Path to historical data JSON file
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.warning(f"Historical data file not found: {file_path}")
            return
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            history_records = data.get('history', [])
            
            # Group by loan_id
            for record_data in history_records:
                try:
                    # Parse timestamp
                    if 'timestamp' in record_data and isinstance(record_data['timestamp'], str):
                        record_data['timestamp'] = datetime.fromisoformat(record_data['timestamp'].replace('Z', '+00:00'))
                    
                    record = LoanHistoricalRecord(**record_data)
                    
                    if record.loan_id not in self.historical_data:
                        self.historical_data[record.loan_id] = []
                    
                    self.historical_data[record.loan_id].append(record)
                    
                except (ValidationError, ValueError) as e:
                    logger.warning(f"Skipping invalid historical record: {e}")
                    continue
            
            # Sort each loan's history by timestamp
            for loan_id in self.historical_data:
                self.historical_data[loan_id].sort(key=lambda r: r.timestamp)
            
            logger.info(f"Loaded historical data for {len(self.historical_data)} loans")
            
        except Exception as e:
            logger.error(f"Failed to load historical data: {e}")
    
    
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
    
    def _detect_pik_toggle(self, loan: LoanRecord) -> tuple[bool, Optional[str], List[LoanHistoricalRecord]]:
        """
        Detect if a loan has toggled from Cash/Hybrid to PIK.
        
        Args:
            loan: Current loan record
            
        Returns:
            Tuple of (toggle_detected, previous_type, history)
        """
        if loan.loan_id not in self.historical_data:
            return False, None, []
        
        history = self.historical_data[loan.loan_id]
        
        # Check if current status is PIK
        if loan.interest_type != 'PIK':
            return False, None, history
        
        # Look for any non-PIK payment in history
        for record in history:
            if record.interest_type != 'PIK':
                return True, record.interest_type, history
        
        return False, None, history
    
    def _analyze_loan_with_ai(
        self,
        loan: LoanRecord,
        risky_sectors: List[str],
        correlated_event: str,
        pik_toggle_detected: bool,
        previous_type: Optional[str],
        history: List[LoanHistoricalRecord]
    ) -> tuple[str, str, float, List[AgentReasoningTrace]]:
        """
        Use OpenAI to analyze loan risk with multi-step reasoning.
        
        Args:
            loan: Loan to analyze
            risky_sectors: List of high-risk sectors
            correlated_event: Geopolitical event description
            pik_toggle_detected: Whether PIK toggle was detected
            previous_type: Previous interest type if toggle detected
            history: Historical payment records
            
        Returns:
            Tuple of (flag_reason, risk_level, confidence_score, reasoning_traces)
        """
        reasoning_traces = []
        
        # Step 1: Identify PIK status
        step1_system = "You are a financial forensic analyst. Analyze loan payment structures."
        step1_user = f"""Loan ID: {loan.loan_id}
Borrower: {loan.borrower}
Industry: {loan.industry}
Current Interest Type: {loan.interest_type}
Outstanding Balance: ${loan.outstanding_balance:,.2f}

Task: Identify if this is currently a PIK loan and explain the implications."""
        
        try:
            step1_response = self.openai_client.analyze_with_reasoning(
                system_prompt=step1_system,
                user_prompt=step1_user,
                temperature=0.3,
                max_tokens=300
            )
            
            reasoning_traces.append(AgentReasoningTrace(
                step=1,
                action="Identify PIK loans",
                observation=f"Loan {loan.loan_id} has interest_type={loan.interest_type}",
                reasoning=step1_response[:500]  # Truncate for storage
            ))
            
        except Exception as e:
            logger.error(f"Step 1 AI analysis failed: {e}")
            step1_response = f"Current status: {loan.interest_type} loan"
        
        # Step 2: Cross-reference with historical data
        history_summary = ""
        if history:
            history_summary = "\n".join([
                f"- {h.timestamp.strftime('%Y-%m-%d')}: {h.interest_type} (Balance: ${h.outstanding_balance:,.2f})"
                for h in history
            ])
        else:
            history_summary = "No historical data available"
        
        step2_system = "You are a financial forensic analyst. Analyze payment history patterns."
        step2_user = f"""Loan ID: {loan.loan_id}
Current Status: {loan.interest_type}
PIK Toggle Detected: {pik_toggle_detected}
Previous Type: {previous_type or 'N/A'}

Payment History:
{history_summary}

Task: Analyze if the borrower switched payment types and what this indicates about financial distress."""
        
        try:
            step2_response = self.openai_client.analyze_with_reasoning(
                system_prompt=step2_system,
                user_prompt=step2_user,
                temperature=0.3,
                max_tokens=400
            )
            
            reasoning_traces.append(AgentReasoningTrace(
                step=2,
                action="Cross-reference with historical data",
                observation=f"Toggle detected: {pik_toggle_detected}, Previous: {previous_type}",
                reasoning=step2_response[:500]
            ))
            
        except Exception as e:
            logger.error(f"Step 2 AI analysis failed: {e}")
            step2_response = f"Toggle status: {pik_toggle_detected}"
        
        # Step 3: Flag toggle events
        step3_system = "You are a financial forensic analyst. Identify red flags in corporate debt."
        step3_user = f"""Loan Analysis:
- Borrower: {loan.borrower}
- Industry: {loan.industry}
- PIK Toggle: {pik_toggle_detected}
- Risky Sectors: {', '.join(risky_sectors)}
- Geopolitical Event: {correlated_event}

Task: Determine if this loan should be flagged as high-risk. Consider:
1. Is the industry in a risky sector?
2. Did the borrower toggle to PIK (sign of distress)?
3. Is there correlation with geopolitical events?

Respond with: FLAG or NO_FLAG, followed by brief reasoning."""
        
        try:
            step3_response = self.openai_client.analyze_with_reasoning(
                system_prompt=step3_system,
                user_prompt=step3_user,
                temperature=0.2,
                max_tokens=300
            )
            
            should_flag = "FLAG" in step3_response.upper().split('\n')[0]
            
            reasoning_traces.append(AgentReasoningTrace(
                step=3,
                action="Flag toggle events",
                observation=f"Should flag: {should_flag}",
                reasoning=step3_response[:500]
            ))
            
        except Exception as e:
            logger.error(f"Step 3 AI analysis failed: {e}")
            # Fallback to rule-based logic
            should_flag = (
                pik_toggle_detected and 
                loan.industry.lower() in [s.lower() for s in risky_sectors]
            )
            step3_response = f"Fallback logic: flag={should_flag}"
        
        # Step 4: Assess risk severity
        step4_system = "You are a financial risk analyst. Assess risk severity and confidence."
        step4_user = f"""Loan Risk Assessment:
- Outstanding Balance: ${loan.outstanding_balance:,.2f}
- PIK Toggle: {pik_toggle_detected}
- Industry: {loan.industry} (Risky: {loan.industry.lower() in [s.lower() for s in risky_sectors]})
- Geopolitical Context: {correlated_event}

Task: Provide:
1. Risk Level: low, medium, high, or critical
2. Confidence Score: 0-100
3. Brief justification

Format: RISK_LEVEL: <level> | CONFIDENCE: <score> | REASON: <justification>"""
        
        try:
            step4_response = self.openai_client.analyze_with_reasoning(
                system_prompt=step4_system,
                user_prompt=step4_user,
                temperature=0.2,
                max_tokens=400
            )
            
            # Parse response
            risk_level = 'medium'
            confidence_score = 50.0
            
            if 'RISK_LEVEL:' in step4_response:
                risk_part = step4_response.split('RISK_LEVEL:')[1].split('|')[0].strip().lower()
                if risk_part in ['low', 'medium', 'high', 'critical']:
                    risk_level = risk_part
            
            if 'CONFIDENCE:' in step4_response:
                try:
                    conf_part = step4_response.split('CONFIDENCE:')[1].split('|')[0].strip()
                    confidence_score = float(conf_part)
                    confidence_score = max(0.0, min(100.0, confidence_score))
                except:
                    pass
            
            reasoning_traces.append(AgentReasoningTrace(
                step=4,
                action="Assess risk severity",
                observation=f"Risk: {risk_level}, Confidence: {confidence_score}",
                reasoning=step4_response[:500]
            ))
            
        except Exception as e:
            logger.error(f"Step 4 AI analysis failed: {e}")
            # Fallback risk assessment
            if loan.outstanding_balance >= 10_000_000:
                risk_level = 'critical'
                confidence_score = 70.0
            elif loan.outstanding_balance >= 5_000_000:
                risk_level = 'high'
                confidence_score = 65.0
            else:
                risk_level = 'medium'
                confidence_score = 60.0
        
        # Generate flag reason
        if pik_toggle_detected:
            flag_reason = f"PIK toggle detected: switched from {previous_type} to PIK in {loan.industry} sector"
        else:
            flag_reason = f"PIK loan in high-risk sector ({loan.industry})"
        
        return flag_reason, risk_level, confidence_score, reasoning_traces
    
    def flag_high_risk_loans_with_ai(
        self,
        loans: List[LoanRecord],
        risky_sectors: List[str],
        correlated_event: str = "Geopolitical crisis"
    ) -> List[FlaggedLoan]:
        """
        Flag loans using AI-powered PIK toggle detection and reasoning.
        
        This is the AGENTIC UPGRADE that replaces static flagging with OpenAI reasoning.
        
        Args:
            loans: List of loan records to analyze
            risky_sectors: List of high-risk industry sectors
            correlated_event: Description of the correlated geopolitical event
            
        Returns:
            List of flagged loans with AI reasoning traces
        """
        flagged_loans = []
        
        for loan in loans:
            # Step 1 & 2: Detect PIK toggle
            pik_toggle_detected, previous_type, history = self._detect_pik_toggle(loan)
            
            # Only flag PIK loans in risky sectors OR loans with PIK toggles
            should_analyze = (
                (loan.interest_type == 'PIK' and loan.industry.lower() in [s.lower() for s in risky_sectors]) or
                pik_toggle_detected
            )
            
            if not should_analyze:
                continue
            
            # Step 3 & 4: AI-powered risk assessment
            flag_reason, risk_level, confidence_score, reasoning_traces = self._analyze_loan_with_ai(
                loan=loan,
                risky_sectors=risky_sectors,
                correlated_event=correlated_event,
                pik_toggle_detected=pik_toggle_detected,
                previous_type=previous_type,
                history=history
            )
            
            flagged_loan = FlaggedLoan(
                **loan.model_dump(),
                flag_reason=flag_reason,
                risk_level=risk_level,
                correlated_event=correlated_event,
                flagged_at=datetime.utcnow(),
                confidence_score=confidence_score,
                agent_reasoning=reasoning_traces,
                pik_toggle_detected=pik_toggle_detected,
                previous_interest_type=previous_type
            )
            flagged_loans.append(flagged_loan)
        
        logger.info(f"AI-flagged {len(flagged_loans)} high-risk loans (toggles: {sum(1 for f in flagged_loans if f.pik_toggle_detected)})")
        return flagged_loans
    
    def analyze_portfolio(
        self,
        file_path: Union[str, Path],
        risky_sectors: List[str],
        correlated_event: str = "Geopolitical crisis",
        format: str = None,
        use_ai: bool = True,
        historical_data_path: Optional[Union[str, Path]] = None
    ) -> dict:
        """
        Complete portfolio analysis workflow.
        
        Args:
            file_path: Path to ledger file
            risky_sectors: List of high-risk sectors
            correlated_event: Description of correlated event
            format: File format ('csv' or 'json')
            use_ai: Whether to use AI-powered analysis (default: True)
            historical_data_path: Path to historical data for PIK toggle detection
            
        Returns:
            Dictionary with analysis results
        """
        # Load historical data if provided
        if historical_data_path:
            self.load_historical_data(historical_data_path)
        
        # Parse ledger
        loans = self.parse_ledger(file_path, format)
        
        # Flag high-risk loans (AI or rule-based)
        if use_ai:
            flagged = self.flag_high_risk_loans_with_ai(loans, risky_sectors, correlated_event)
        else:
            flagged = self.flag_high_risk_loans(loans, risky_sectors, correlated_event)
        
        # Rank by exposure
        ranked = self.rank_by_exposure(flagged)
        
        # Count PIK toggles
        toggle_count = sum(1 for f in flagged if f.pik_toggle_detected)
        
        return {
            'total_loans': len(loans),
            'flagged_loans': len(flagged),
            'pik_toggles_detected': toggle_count,
            'validation_errors': len(self.validation_errors),
            'ranked_flagged_loans': ranked,
            'errors': self.validation_errors,
            'ai_powered': use_ai
        }
