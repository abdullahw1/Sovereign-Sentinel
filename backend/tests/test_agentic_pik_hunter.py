"""
Test script for Agentic PIK Toggle Hunter.
"""
import json
import logging
from pathlib import Path
from app.forensic_auditor import ForensicAuditor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Test the agentic PIK toggle detection."""
    logger.info("=== Testing Agentic PIK Toggle Hunter ===\n")
    
    # Initialize auditor
    auditor = ForensicAuditor()
    
    # Analyze portfolio with AI
    result = auditor.analyze_portfolio(
        file_path="data/test_ledger.json",
        risky_sectors=["energy", "currency"],
        correlated_event="Middle East energy crisis and LatAm currency volatility",
        use_ai=True,
        historical_data_path="data/loan_history.json"
    )
    
    logger.info(f"\n=== Analysis Results ===")
    logger.info(f"Total loans: {result['total_loans']}")
    logger.info(f"Flagged loans: {result['flagged_loans']}")
    logger.info(f"PIK toggles detected: {result['pik_toggles_detected']}")
    logger.info(f"AI-powered: {result['ai_powered']}\n")
    
    # Display flagged loans with reasoning
    for i, loan in enumerate(result['ranked_flagged_loans'], 1):
        logger.info(f"\n--- Flagged Loan #{i} ---")
        logger.info(f"Loan ID: {loan.loan_id}")
        logger.info(f"Borrower: {loan.borrower}")
        logger.info(f"Industry: {loan.industry}")
        logger.info(f"Outstanding Balance: ${loan.outstanding_balance:,.2f}")
        logger.info(f"Risk Level: {loan.risk_level}")
        logger.info(f"Confidence Score: {loan.confidence_score:.1f}%")
        logger.info(f"PIK Toggle: {loan.pik_toggle_detected}")
        if loan.previous_interest_type:
            logger.info(f"Previous Type: {loan.previous_interest_type}")
        logger.info(f"Flag Reason: {loan.flag_reason}")
        
        # Display agent reasoning traces
        if loan.agent_reasoning:
            logger.info(f"\nAgent Reasoning Chain:")
            for trace in loan.agent_reasoning:
                logger.info(f"  Step {trace.step}: {trace.action}")
                logger.info(f"    Observation: {trace.observation}")
                logger.info(f"    Reasoning: {trace.reasoning[:200]}...")
    
    # Save detailed results
    output_file = "data/agentic_analysis_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            'summary': {
                'total_loans': result['total_loans'],
                'flagged_loans': result['flagged_loans'],
                'pik_toggles_detected': result['pik_toggles_detected']
            },
            'flagged_loans': [loan.model_dump(mode='json') for loan in result['ranked_flagged_loans']]
        }, f, indent=2, default=str)
    
    logger.info(f"\n\nDetailed results saved to: {output_file}")


if __name__ == "__main__":
    main()
