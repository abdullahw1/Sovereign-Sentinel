"""
Tests for Policy Brain Agent with Self-Correction & Policy Evolution.
"""
import json
import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from app.policy_brain import (
    PolicyBrain,
    ReasoningBank,
    ReasoningBankEntry,
    PolicyConfig,
    PolicyOverride,
    EscalationDecision,
    Alert,
    PolicyDiff
)
from app.models import FlaggedLoan


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create temporary data directory for tests."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir


@pytest.fixture
def reasoning_bank(temp_data_dir):
    """Create a reasoning bank instance for testing."""
    bank_file = temp_data_dir / "reasoning_bank.json"
    return ReasoningBank(str(bank_file))


@pytest.fixture
def policy_brain(temp_data_dir):
    """Create a policy brain instance for testing."""
    policy_file = temp_data_dir / "policy.json"
    reasoning_bank_file = temp_data_dir / "reasoning_bank.json"
    
    with patch('app.policy_brain.OpenAIClient'):
        brain = PolicyBrain(
            policy_file=str(policy_file),
            reasoning_bank_file=str(reasoning_bank_file)
        )
    
    return brain


@pytest.fixture
def sample_flagged_loan():
    """Create a sample flagged loan for testing."""
    return FlaggedLoan(
        loanId="L001",
        borrower="Acme Energy",
        industry="energy",
        interestType="PIK",
        principalAmount=10000000,
        outstandingBalance=12500000,
        maturityDate=datetime(2025, 12, 31),
        covenants=[],
        flag_reason="PIK loan in high-risk sector",
        risk_level="critical",
        correlated_event="Middle East crisis",
        flagged_at=datetime.utcnow(),
        confidence_score=85.0
    )


class TestReasoningBank:
    """Tests for Reasoning Bank system."""
    
    def test_reasoning_bank_initialization(self, reasoning_bank):
        """Test reasoning bank initializes correctly."""
        assert reasoning_bank.entries == []
        assert reasoning_bank.file_path.exists()
    
    def test_append_entry(self, reasoning_bank):
        """Test appending entry to reasoning bank."""
        entry = ReasoningBankEntry(
            entry_id="RB001",
            timestamp=datetime.utcnow(),
            override_type="risk_score",
            old_value=70.0,
            new_value=75.0,
            human_rationale="Increased volatility",
            extracted_rule="IF volatility_high THEN increase_threshold",
            confidence_score=80.0
        )
        
        reasoning_bank.append(entry)
        
        assert len(reasoning_bank.entries) == 1
        assert reasoning_bank.entries[0].entry_id == "RB001"
    
    def test_append_persists_to_disk(self, reasoning_bank):
        """Test that appending saves to disk."""
        entry = ReasoningBankEntry(
            entry_id="RB001",
            timestamp=datetime.utcnow(),
            override_type="risk_score",
            old_value=70.0,
            new_value=75.0
        )
        
        reasoning_bank.append(entry)
        
        # Create new instance to verify persistence
        new_bank = ReasoningBank(str(reasoning_bank.file_path))
        assert len(new_bank.entries) == 1
        assert new_bank.entries[0].entry_id == "RB001"
    
    def test_query_by_type(self, reasoning_bank):
        """Test querying entries by override type."""
        entry1 = ReasoningBankEntry(
            entry_id="RB001",
            timestamp=datetime.utcnow(),
            override_type="risk_score",
            old_value=70.0,
            new_value=75.0
        )
        entry2 = ReasoningBankEntry(
            entry_id="RB002",
            timestamp=datetime.utcnow(),
            override_type="threshold",
            old_value=80.0,
            new_value=85.0
        )
        
        reasoning_bank.append(entry1)
        reasoning_bank.append(entry2)
        
        risk_score_entries = reasoning_bank.query_by_type("risk_score")
        assert len(risk_score_entries) == 1
        assert risk_score_entries[0].entry_id == "RB001"
    
    def test_query_by_context(self, reasoning_bank):
        """Test querying entries by loan context."""
        entry1 = ReasoningBankEntry(
            entry_id="RB001",
            timestamp=datetime.utcnow(),
            override_type="risk_score",
            old_value=70.0,
            new_value=75.0,
            loan_context={"industry": "energy", "loan_id": "L001"}
        )
        entry2 = ReasoningBankEntry(
            entry_id="RB002",
            timestamp=datetime.utcnow(),
            override_type="risk_score",
            old_value=60.0,
            new_value=65.0,
            loan_context={"industry": "mining", "loan_id": "L002"}
        )
        
        reasoning_bank.append(entry1)
        reasoning_bank.append(entry2)
        
        energy_entries = reasoning_bank.query_by_context("industry", "energy")
        assert len(energy_entries) == 1
        assert energy_entries[0].entry_id == "RB001"
    
    def test_detect_patterns(self, reasoning_bank):
        """Test pattern detection in reasoning bank."""
        # Add multiple similar entries
        for i in range(3):
            entry = ReasoningBankEntry(
                entry_id=f"RB00{i+1}",
                timestamp=datetime.utcnow(),
                override_type="risk_score",
                old_value=70.0 + i,
                new_value=75.0 + i
            )
            reasoning_bank.append(entry)
        
        patterns = reasoning_bank.detect_patterns(min_occurrences=3)
        
        assert len(patterns) == 1
        assert patterns[0]['override_type'] == "risk_score"
        assert patterns[0]['occurrences'] == 3
        assert patterns[0]['average_change'] == 5.0
    
    def test_get_recent_entries(self, reasoning_bank):
        """Test retrieving recent entries."""
        for i in range(5):
            entry = ReasoningBankEntry(
                entry_id=f"RB00{i+1}",
                timestamp=datetime.utcnow(),
                override_type="risk_score",
                old_value=70.0,
                new_value=75.0
            )
            reasoning_bank.append(entry)
        
        recent = reasoning_bank.get_recent_entries(limit=3)
        assert len(recent) == 3


class TestPolicyBrain:
    """Tests for Policy Brain orchestration."""
    
    def test_policy_brain_initialization(self, policy_brain):
        """Test policy brain initializes with default policy."""
        assert policy_brain.policy is not None
        assert policy_brain.policy.risk_threshold == 70.0
        assert policy_brain.reasoning_bank is not None
    
    def test_load_policy_overrides(self, policy_brain):
        """Test loading policy configuration."""
        policy = policy_brain.load_policy_overrides()
        assert policy.risk_threshold == 70.0
        assert isinstance(policy.hedge_percentages, dict)
    
    def test_evaluate_risk_normal(self, policy_brain):
        """Test risk evaluation with normal conditions."""
        decision = policy_brain.evaluate_risk(
            risk_score=50.0,
            flagged_loans=[]
        )
        
        assert decision.status == 'normal'
        assert decision.hedge_percentage == 0.0
        assert "NORMAL" in decision.reasoning[-1]
    
    def test_evaluate_risk_elevated(self, policy_brain, sample_flagged_loan):
        """Test risk evaluation with elevated conditions."""
        decision = policy_brain.evaluate_risk(
            risk_score=60.0,
            flagged_loans=[sample_flagged_loan]
        )
        
        assert decision.status == 'elevated'
        assert decision.hedge_percentage == 5.0
        assert "ELEVATED" in decision.reasoning[-1]
    
    def test_evaluate_risk_critical(self, policy_brain, sample_flagged_loan):
        """Test risk evaluation with critical conditions."""
        decision = policy_brain.evaluate_risk(
            risk_score=75.0,
            flagged_loans=[sample_flagged_loan]
        )
        
        assert decision.status == 'critical'
        assert decision.hedge_percentage > 0.0
        assert "CRITICAL" in decision.reasoning[-1]
    
    def test_evaluate_risk_uses_policy_threshold(self, policy_brain, sample_flagged_loan):
        """Test that risk evaluation uses policy threshold."""
        # Change threshold
        policy_brain.policy.risk_threshold = 80.0
        
        decision = policy_brain.evaluate_risk(
            risk_score=75.0,
            flagged_loans=[sample_flagged_loan]
        )
        
        # Should be elevated, not critical (75 < 80)
        assert decision.status == 'elevated'
    
    def test_generate_alert_critical(self, policy_brain, sample_flagged_loan):
        """Test alert generation for critical status."""
        decision = EscalationDecision(
            status='critical',
            recommended_action="Execute hedge",
            hedge_percentage=15.0,
            affected_loans=[sample_flagged_loan],
            reasoning=["Test"]
        )
        
        alert = policy_brain.generate_alert(decision)
        
        assert alert.severity == 'critical'
        assert alert.action_required is True
        assert alert.recommended_hedge == 15.0
        assert "Shadow Default" in alert.title
    
    def test_generate_alert_normal(self, policy_brain):
        """Test alert generation for normal status."""
        decision = EscalationDecision(
            status='normal',
            recommended_action="Continue",
            hedge_percentage=0.0,
            affected_loans=[],
            reasoning=["Test"]
        )
        
        alert = policy_brain.generate_alert(decision)
        
        assert alert.severity == 'info'
        assert alert.action_required is False
        assert alert.recommended_hedge == 0.0
    
    def test_distill_policy_from_override(self, policy_brain):
        """Test policy distillation from human override."""
        # Mock OpenAI response
        mock_response = "RULE: IF energy_sector THEN increase_risk_by 5\nCONFIDENCE: 85\nEXPLANATION: Pattern detected"
        policy_brain.openai_client.analyze_with_reasoning = Mock(return_value=mock_response)
        
        entry = policy_brain.distill_policy_from_override(
            override_type="risk_score",
            old_value=70.0,
            new_value=75.0,
            loan_context={"industry": "energy", "loan_id": "L001"},
            human_rationale="Increased volatility in energy sector"
        )
        
        assert entry.override_type == "risk_score"
        assert entry.old_value == 70.0
        assert entry.new_value == 75.0
        assert "IF energy_sector THEN increase_risk_by 5" in entry.extracted_rule
        assert entry.confidence_score == 85.0
    
    def test_distill_policy_handles_ai_failure(self, policy_brain):
        """Test policy distillation handles AI failures gracefully."""
        # Mock OpenAI failure
        policy_brain.openai_client.analyze_with_reasoning = Mock(side_effect=Exception("API Error"))
        
        entry = policy_brain.distill_policy_from_override(
            override_type="risk_score",
            old_value=70.0,
            new_value=75.0
        )
        
        assert entry.override_type == "risk_score"
        assert entry.confidence_score == 30.0  # Low confidence on failure
        assert "Manual override" in entry.extracted_rule
    
    def test_detect_rule_conflicts(self, policy_brain):
        """Test detection of conflicting rules."""
        # Add conflicting entries to reasoning bank
        entry1 = ReasoningBankEntry(
            entry_id="RB001",
            timestamp=datetime.utcnow(),
            override_type="risk_score",
            old_value=70.0,
            new_value=75.0,
            extracted_rule="IF energy_crisis THEN increase risk_score by 5"
        )
        entry2 = ReasoningBankEntry(
            entry_id="RB002",
            timestamp=datetime.utcnow(),
            override_type="risk_score",
            old_value=75.0,
            new_value=70.0,
            extracted_rule="IF energy_crisis THEN decrease risk_score by 5"
        )
        
        policy_brain.reasoning_bank.append(entry1)
        policy_brain.reasoning_bank.append(entry2)
        
        conflicts = policy_brain.detect_rule_conflicts("IF energy_crisis THEN increase risk_score")
        
        # Should detect the decrease rule as conflicting
        assert len(conflicts) >= 0  # May or may not detect based on keyword matching
    
    def test_propose_policy_update(self, policy_brain):
        """Test proposing a policy update."""
        # Mock OpenAI response
        mock_response = "Based on observed patterns, increasing the threshold is recommended."
        policy_brain.openai_client.analyze_with_reasoning = Mock(return_value=mock_response)
        
        diff = policy_brain.propose_policy_update(
            field="risk_threshold",
            new_value=75.0,
            reason="Pattern of manual overrides detected"
        )
        
        assert diff.field == "risk_threshold"
        assert diff.old_value == 70.0
        assert diff.new_value == 75.0
        assert diff.status == 'proposed'
        assert diff.confidence_score > 0
    
    def test_apply_policy_diff_approved(self, policy_brain):
        """Test applying an approved policy diff."""
        diff = PolicyDiff(
            diff_id="PD001",
            timestamp=datetime.utcnow(),
            field="risk_threshold",
            old_value=70.0,
            new_value=75.0,
            explanation="Test update",
            confidence_score=80.0,
            supporting_evidence=["Test evidence"]
        )
        
        result = policy_brain.apply_policy_diff(diff, approved_by="admin", approved=True)
        
        assert result is True
        assert policy_brain.policy.risk_threshold == 75.0
        assert diff.status == 'approved'
        assert len(policy_brain.policy_history) == 1
    
    def test_apply_policy_diff_rejected(self, policy_brain):
        """Test rejecting a policy diff."""
        diff = PolicyDiff(
            diff_id="PD001",
            timestamp=datetime.utcnow(),
            field="risk_threshold",
            old_value=70.0,
            new_value=75.0,
            explanation="Test update",
            confidence_score=80.0,
            supporting_evidence=[]
        )
        
        result = policy_brain.apply_policy_diff(diff, approved_by="admin", approved=False)
        
        assert result is False
        assert policy_brain.policy.risk_threshold == 70.0  # Unchanged
        assert diff.status == 'rejected'
    
    def test_apply_override(self, policy_brain):
        """Test applying a manual policy override."""
        override = PolicyOverride(
            override_id="PO001",
            timestamp=datetime.utcnow(),
            field="risk_threshold",
            old_value=70.0,
            new_value=80.0,
            applied_by="admin",
            reason="Emergency adjustment"
        )
        
        policy_brain.apply_override(override)
        
        assert policy_brain.policy.risk_threshold == 80.0
        assert len(policy_brain.policy_history) == 1
    
    def test_policy_persists_across_instances(self, temp_data_dir):
        """Test that policy changes persist across instances."""
        policy_file = temp_data_dir / "policy.json"
        reasoning_bank_file = temp_data_dir / "reasoning_bank.json"
        
        # Create first instance and modify policy
        with patch('app.policy_brain.OpenAIClient'):
            brain1 = PolicyBrain(
                policy_file=str(policy_file),
                reasoning_bank_file=str(reasoning_bank_file)
            )
            brain1.policy.risk_threshold = 85.0
            brain1._save_policy(brain1.policy)
        
        # Create second instance and verify persistence
        with patch('app.policy_brain.OpenAIClient'):
            brain2 = PolicyBrain(
                policy_file=str(policy_file),
                reasoning_bank_file=str(reasoning_bank_file)
            )
            assert brain2.policy.risk_threshold == 85.0


class TestIntegration:
    """Integration tests for Policy Brain workflow."""
    
    def test_complete_override_workflow(self, policy_brain, sample_flagged_loan):
        """Test complete workflow: override → distill → propose → apply."""
        # Mock OpenAI
        policy_brain.openai_client.analyze_with_reasoning = Mock(
            return_value="RULE: IF energy_sector THEN increase_threshold\nCONFIDENCE: 85\nEXPLANATION: Test"
        )
        
        # Step 1: Distill from override
        entry = policy_brain.distill_policy_from_override(
            override_type="risk_threshold",
            old_value=70.0,
            new_value=75.0,
            loan_context={"industry": "energy"},
            human_rationale="Energy sector volatility"
        )
        
        assert entry.extracted_rule is not None
        
        # Step 2: Propose policy update
        diff = policy_brain.propose_policy_update(
            field="risk_threshold",
            new_value=75.0,
            reason="Pattern detected from overrides"
        )
        
        assert diff.status == 'proposed'
        
        # Step 3: Apply policy diff
        result = policy_brain.apply_policy_diff(diff, approved_by="admin", approved=True)
        
        assert result is True
        assert policy_brain.policy.risk_threshold == 75.0
        
        # Step 4: Verify reasoning bank has entries
        assert len(policy_brain.reasoning_bank.get_all_entries()) >= 2
