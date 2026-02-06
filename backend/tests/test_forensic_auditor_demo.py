"""
Demo script to test Forensic Auditor functionality.
"""
from app.forensic_auditor import ForensicAuditor


def main():
    """Run a complete forensic audit demonstration."""
    print("=" * 60)
    print("FORENSIC AUDITOR DEMONSTRATION")
    print("=" * 60)
    
    auditor = ForensicAuditor()
    
    # Analyze CSV ledger
    print("\n1. Analyzing CSV Ledger...")
    print("-" * 60)
    result_csv = auditor.analyze_portfolio(
        "data/test_ledger.csv",
        risky_sectors=["energy", "currency"],
        correlated_event="Middle East energy crisis & LatAm currency volatility"
    )
    
    print(f"Total loans parsed: {result_csv['total_loans']}")
    print(f"Flagged PIK loans: {result_csv['flagged_loans']}")
    print(f"Validation errors: {result_csv['validation_errors']}")
    
    print("\nFlagged Loans (ranked by exposure):")
    for i, loan in enumerate(result_csv['ranked_flagged_loans'], 1):
        print(f"\n  {i}. {loan.loan_id} - {loan.borrower}")
        print(f"     Industry: {loan.industry}")
        print(f"     Outstanding Balance: ${loan.outstanding_balance:,.0f}")
        print(f"     Risk Level: {loan.risk_level.upper()}")
        print(f"     Flag Reason: {loan.flag_reason}")
        print(f"     Correlated Event: {loan.correlated_event}")
    
    # Analyze JSON ledger
    print("\n\n2. Analyzing JSON Ledger...")
    print("-" * 60)
    result_json = auditor.analyze_portfolio(
        "data/test_ledger.json",
        risky_sectors=["energy"],
        correlated_event="Middle East energy crisis"
    )
    
    print(f"Total loans parsed: {result_json['total_loans']}")
    print(f"Flagged PIK loans: {result_json['flagged_loans']}")
    
    print("\nFlagged Loans (ranked by exposure):")
    for i, loan in enumerate(result_json['ranked_flagged_loans'], 1):
        print(f"\n  {i}. {loan.loan_id} - {loan.borrower}")
        print(f"     Industry: {loan.industry}")
        print(f"     Outstanding Balance: ${loan.outstanding_balance:,.0f}")
        print(f"     Risk Level: {loan.risk_level.upper()}")
    
    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
