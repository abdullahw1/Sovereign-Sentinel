"""
Demo script for Policy Brain Agent with Self-Correction & Policy Evolution.

This demonstrates the complete workflow:
1. Reasoning Bank: Persistent storage of human overrides
2. Policy Distillation: AI extracts rules from overrides
3. Policy Diff Approval: Agent proposes changes, user approves
"""
import json
from datetime import datetime
from pathlib import Path

from app.policy_brain import PolicyBrain, PolicyDiff
from app.models import FlaggedLoan


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def main():
    """Run Policy Brain demonstration."""
    
    print_section("POLICY BRAIN DEMO: Self-Correction & Policy Evolution")
    
    # Initialize Policy Brain
    print("Initializing Policy Brain...")
    brain = PolicyBrain(
        policy_file="data/demo_policy.json",
        reasoning_bank_file="data/demo_reasoning_bank.json"
    )
    
    print(f"✓ Initial policy threshold: {brain.policy.risk_threshold}")
    print(f"✓ Reasoning bank entries: {len(brain.reasoning_bank.get_all_entries())}")
    
    # Create sample flagged loan
    sample_loan = FlaggedLoan(
        loanId="L001",
        borrower="Acme Energy Corp",
        industry="energy",
        interestType="PIK",
        principalAmount=10_000_000,
        outstandingBalance=12_500_000,
        maturityDate=datetime(2025, 12, 31),
        covenants=["debt-to-equity < 2.0"],
        flag_reason="PIK toggle detected: switched from Cash to PIK",
        risk_level="critical",
        correlated_event="Middle East energy crisis",
        flagged_at=datetime.utcnow(),
        confidence_score=85.0,
        pik_toggle_detected=True,
        previous_interest_type="Cash"
    )
    
    # Step 1: Evaluate initial risk
    print_section("STEP 1: Initial Risk Evaluation")
    
    decision = brain.evaluate_risk(
        risk_score=75.0,
        flagged_loans=[sample_loan]
    )
    
    print(f"Risk Score: 75.0")
    print(f"Status: {decision.status.upper()}")
    print(f"Recommended Action: {decision.recommended_action}")
    print(f"Hedge Percentage: {decision.hedge_percentage}%")
    print(f"\nReasoning:")
    for reason in decision.reasoning:
        print(f"  • {reason}")
    
    # Step 2: Simulate human override
    print_section("STEP 2: Human Override - User Adjusts Risk Threshold")
    
    print("User manually increases risk threshold from 70 to 75...")
    print("Reason: 'Energy sector showing increased volatility'")
    
    # Distill policy from override
    entry = brain.distill_policy_from_override(
        override_type="risk_threshold",
        old_value=70.0,
        new_value=75.0,
        loan_context={
            "industry": "energy",
            "loan_id": "L001",
            "pik_toggle": True
        },
        human_rationale="Energy sector showing increased volatility"
    )
    
    print(f"\n✓ Reasoning Bank Entry Created:")
    print(f"  Entry ID: {entry.entry_id}")
    print(f"  Override Type: {entry.override_type}")
    print(f"  Change: {entry.old_value} → {entry.new_value}")
    print(f"  Extracted Rule: {entry.extracted_rule}")
    print(f"  Confidence: {entry.confidence_score}%")
    
    # Step 3: Add more overrides to detect pattern
    print_section("STEP 3: Pattern Detection - Multiple Overrides")
    
    print("Simulating 2 more similar overrides...")
    
    for i in range(2):
        brain.distill_policy_from_override(
            override_type="risk_threshold",
            old_value=70.0 + i,
            new_value=75.0 + i,
            loan_context={"industry": "energy"},
            human_rationale=f"Override {i+2}"
        )
    
    patterns = brain.reasoning_bank.detect_patterns(min_occurrences=3)
    
    print(f"\n✓ Patterns Detected: {len(patterns)}")
    for pattern in patterns:
        print(f"  • Type: {pattern['override_type']}")
        print(f"    Occurrences: {pattern['occurrences']}")
        print(f"    Average Change: {pattern['average_change']:.1f}")
    
    # Step 4: Agent proposes policy update
    print_section("STEP 4: Agent Proposes Policy Update")
    
    diff = brain.propose_policy_update(
        field="risk_threshold",
        new_value=75.0,
        reason="Pattern detected: user consistently increases threshold for energy sector"
    )
    
    print(f"Policy Diff ID: {diff.diff_id}")
    print(f"Field: {diff.field}")
    print(f"Change: {diff.old_value} → {diff.new_value}")
    print(f"Status: {diff.status.upper()}")
    print(f"Confidence: {diff.confidence_score}%")
    print(f"\nExplanation:")
    print(f"  {diff.explanation}")
    print(f"\nSupporting Evidence:")
    for evidence in diff.supporting_evidence:
        print(f"  • {evidence}")
    
    # Step 5: User reviews and approves
    print_section("STEP 5: User Reviews and Approves Policy Change")
    
    print("User reviews the proposed change...")
    print("Decision: APPROVED ✓")
    
    result = brain.apply_policy_diff(
        policy_diff=diff,
        approved_by="admin",
        approved=True
    )
    
    print(f"\n✓ Policy Updated: {result}")
    print(f"  New threshold: {brain.policy.risk_threshold}")
    print(f"  Policy history entries: {len(brain.policy_history)}")
    
    # Step 6: Re-evaluate with new policy
    print_section("STEP 6: Re-evaluate Risk with Updated Policy")
    
    decision_new = brain.evaluate_risk(
        risk_score=75.0,
        flagged_loans=[sample_loan]
    )
    
    print(f"Risk Score: 75.0 (same as before)")
    print(f"Status: {decision_new.status.upper()} (was: {decision.status.upper()})")
    print(f"Recommended Action: {decision_new.recommended_action}")
    print(f"\nReasoning:")
    for reason in decision_new.reasoning:
        print(f"  • {reason}")
    
    print("\n✓ Notice: Status changed from CRITICAL to ELEVATED")
    print("  The learned policy now reflects user's risk tolerance!")
    
    # Step 7: Generate alert
    print_section("STEP 7: Generate Alert")
    
    alert = brain.generate_alert(decision_new)
    
    print(f"Alert ID: {alert.alert_id}")
    print(f"Severity: {alert.severity.upper()}")
    print(f"Title: {alert.title}")
    print(f"Message: {alert.message}")
    print(f"Action Required: {alert.action_required}")
    print(f"Recommended Hedge: {alert.recommended_hedge}%")
    
    # Summary
    print_section("SUMMARY: Policy Evolution Complete")
    
    print("✓ Reasoning Bank: Stored 3 human overrides")
    print("✓ Pattern Detection: Identified consistent threshold increases")
    print("✓ Policy Distillation: AI extracted underlying logic rules")
    print("✓ Policy Update: Agent proposed change, user approved")
    print("✓ Continuous Learning: System now reflects learned preferences")
    
    print(f"\nReasoning Bank Entries: {len(brain.reasoning_bank.get_all_entries())}")
    print(f"Policy History: {len(brain.policy_history)} overrides")
    print(f"Current Risk Threshold: {brain.policy.risk_threshold}")
    
    # Show reasoning bank contents
    print("\nReasoning Bank Contents:")
    for entry in brain.reasoning_bank.get_recent_entries(limit=3):
        print(f"  • {entry.entry_id}: {entry.override_type} ({entry.old_value} → {entry.new_value})")
        print(f"    Rule: {entry.extracted_rule[:80]}...")
    
    print("\n" + "="*80)
    print("Demo complete! Policy Brain successfully demonstrated:")
    print("  1. Persistent reasoning bank (append-only audit trail)")
    print("  2. In-context policy distillation with OpenAI")
    print("  3. Logic-gated policy updates with diff approval")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
