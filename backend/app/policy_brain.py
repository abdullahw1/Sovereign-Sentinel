"""
Policy Brain: Orchestrates risk evaluation and policy evolution through continuous learning.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field

from app.models import FlaggedLoan
from app.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


class ReasoningBankEntry(BaseModel):
    """Represents a learned lesson from human override."""
    entry_id: str
    timestamp: datetime
    override_type: Literal['risk_score', 'threshold', 'risk_threshold', 'sector_weight', 'hedge_percentage', 'custom_rule']
    old_value: Any
    new_value: Any
    human_rationale: Optional[str] = None
    extracted_rule: Optional[str] = None
    confidence_score: float = Field(ge=0.0, le=100.0, default=50.0)
    loan_context: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "entry_id": "RB001",
                "timestamp": "2024-01-15T10:30:00Z",
                "override_type": "risk_score",
                "old_value": 75.0,
                "new_value": 85.0,
                "human_rationale": "User increased risk due to recent covenant breach",
                "extracted_rule": "IF covenant_breach THEN increase_risk_by 10%",
                "confidence_score": 80.0,
                "loan_context": {"loan_id": "L001", "industry": "energy"}
            }
        }


class PolicyConfig(BaseModel):
    """Policy configuration with thresholds and rules."""
    risk_threshold: float = Field(ge=0.0, le=100.0, default=70.0)
    pik_exposure_limit: float = Field(default=5_000_000.0)
    auto_execute_enabled: bool = False
    hedge_percentages: Dict[str, float] = Field(default_factory=lambda: {
        "energy": 15.0,
        "currency": 20.0,
        "sovereign": 25.0
    })
    custom_rules: List[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "risk_threshold": 70.0,
                "pik_exposure_limit": 5000000.0,
                "auto_execute_enabled": False,
                "hedge_percentages": {
                    "energy": 15.0,
                    "currency": 20.0,
                    "sovereign": 25.0
                },
                "custom_rules": []
            }
        }


class PolicyOverride(BaseModel):
    """Represents a manual policy override."""
    override_id: str
    timestamp: datetime
    field: str
    old_value: Any
    new_value: Any
    applied_by: str
    reason: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "override_id": "PO001",
                "timestamp": "2024-01-15T10:30:00Z",
                "field": "risk_threshold",
                "old_value": 70.0,
                "new_value": 75.0,
                "applied_by": "admin",
                "reason": "Increased volatility in energy sector"
            }
        }


class EscalationDecision(BaseModel):
    """Represents a risk escalation decision."""
    status: Literal['normal', 'elevated', 'critical']
    recommended_action: str
    hedge_percentage: float = Field(ge=0.0, le=100.0)
    affected_loans: List[FlaggedLoan]
    reasoning: List[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "critical",
                "recommended_action": "Execute 15% BTC hedge immediately",
                "hedge_percentage": 15.0,
                "affected_loans": [],
                "reasoning": [
                    "Global risk score exceeds threshold (75 > 70)",
                    "3 PIK loans flagged in energy sector",
                    "Total exposure: $25M"
                ]
            }
        }


class Alert(BaseModel):
    """Represents a system alert."""
    alert_id: str
    timestamp: datetime
    severity: Literal['info', 'warning', 'critical']
    title: str
    message: str
    action_required: bool
    recommended_hedge: float = Field(ge=0.0, le=100.0, default=0.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "alert_id": "A001",
                "timestamp": "2024-01-15T10:30:00Z",
                "severity": "critical",
                "title": "Shadow Default Risk Detected",
                "message": "High correlation between Middle East crisis and PIK exposure",
                "action_required": True,
                "recommended_hedge": 15.0
            }
        }


class PolicyDiff(BaseModel):
    """Represents a proposed policy change with diff view."""
    diff_id: str
    timestamp: datetime
    field: str
    old_value: Any
    new_value: Any
    explanation: str
    confidence_score: float = Field(ge=0.0, le=100.0)
    supporting_evidence: List[str]
    status: Literal['proposed', 'approved', 'rejected'] = 'proposed'
    
    class Config:
        json_schema_extra = {
            "example": {
                "diff_id": "PD001",
                "timestamp": "2024-01-15T10:30:00Z",
                "field": "risk_threshold",
                "old_value": 70.0,
                "new_value": 75.0,
                "explanation": "Pattern detected: user consistently overrides risk scores upward for energy sector loans",
                "confidence_score": 85.0,
                "supporting_evidence": [
                    "3 overrides in past week",
                    "Average increase: 5 points",
                    "All in energy sector"
                ],
                "status": "proposed"
            }
        }


class ReasoningBank:
    """Persistent storage for learned lessons from human overrides."""
    
    def __init__(self, file_path: str = "data/reasoning_bank.json"):
        """
        Initialize reasoning bank.
        
        Args:
            file_path: Path to reasoning bank JSON file
        """
        self.file_path = Path(file_path)
        self.entries: List[ReasoningBankEntry] = []
        self._ensure_file_exists()
        self._load()
    
    def _ensure_file_exists(self):
        """Create reasoning bank file if it doesn't exist."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._save_to_disk([])
            logger.info(f"Created new reasoning bank at {self.file_path}")
    
    def _load(self):
        """Load reasoning bank from disk."""
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
            
            entries_data = data.get('entries', [])
            self.entries = []
            
            for entry_data in entries_data:
                # Parse timestamp
                if 'timestamp' in entry_data and isinstance(entry_data['timestamp'], str):
                    entry_data['timestamp'] = datetime.fromisoformat(entry_data['timestamp'].replace('Z', '+00:00'))
                
                entry = ReasoningBankEntry(**entry_data)
                self.entries.append(entry)
            
            logger.info(f"Loaded {len(self.entries)} entries from reasoning bank")
            
        except Exception as e:
            logger.error(f"Failed to load reasoning bank: {e}")
            self.entries = []
    
    def _save_to_disk(self, entries: List[ReasoningBankEntry]):
        """Save reasoning bank to disk."""
        try:
            data = {
                "version": "1.0",
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "entries": [
                    {
                        **entry.model_dump(),
                        "timestamp": entry.timestamp.isoformat() + "Z"
                    }
                    for entry in entries
                ]
            }
            
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"Saved {len(entries)} entries to reasoning bank")
            
        except Exception as e:
            logger.error(f"Failed to save reasoning bank: {e}")
            raise
    
    def append(self, entry: ReasoningBankEntry):
        """
        Append a new entry to the reasoning bank (append-only).
        
        Args:
            entry: Reasoning bank entry to append
        """
        self.entries.append(entry)
        self._save_to_disk(self.entries)
        logger.info(f"Appended entry {entry.entry_id} to reasoning bank")
    
    def query_by_type(self, override_type: str) -> List[ReasoningBankEntry]:
        """
        Query entries by override type.
        
        Args:
            override_type: Type of override to filter by
            
        Returns:
            List of matching entries
        """
        return [e for e in self.entries if e.override_type == override_type]
    
    def query_by_context(self, context_key: str, context_value: Any) -> List[ReasoningBankEntry]:
        """
        Query entries by loan context.
        
        Args:
            context_key: Key in loan_context to match
            context_value: Value to match
            
        Returns:
            List of matching entries
        """
        matches = []
        for entry in self.entries:
            if entry.loan_context and context_key in entry.loan_context:
                if entry.loan_context[context_key] == context_value:
                    matches.append(entry)
        return matches
    
    def detect_patterns(self, min_occurrences: int = 3) -> List[Dict[str, Any]]:
        """
        Detect patterns in reasoning bank entries.
        
        Args:
            min_occurrences: Minimum number of similar entries to constitute a pattern
            
        Returns:
            List of detected patterns with metadata
        """
        patterns = []
        
        # Group by override_type
        type_groups = {}
        for entry in self.entries:
            if entry.override_type not in type_groups:
                type_groups[entry.override_type] = []
            type_groups[entry.override_type].append(entry)
        
        # Detect patterns in each group
        for override_type, entries in type_groups.items():
            if len(entries) >= min_occurrences:
                # Calculate average change
                changes = []
                for entry in entries:
                    if isinstance(entry.old_value, (int, float)) and isinstance(entry.new_value, (int, float)):
                        changes.append(entry.new_value - entry.old_value)
                
                if changes:
                    avg_change = sum(changes) / len(changes)
                    patterns.append({
                        'override_type': override_type,
                        'occurrences': len(entries),
                        'average_change': avg_change,
                        'entries': entries
                    })
        
        logger.info(f"Detected {len(patterns)} patterns in reasoning bank")
        return patterns
    
    def get_recent_entries(self, limit: int = 10) -> List[ReasoningBankEntry]:
        """
        Get most recent entries.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of recent entries
        """
        sorted_entries = sorted(self.entries, key=lambda e: e.timestamp, reverse=True)
        return sorted_entries[:limit]
    
    def get_all_entries(self) -> List[ReasoningBankEntry]:
        """Get all entries in the reasoning bank."""
        return self.entries.copy()


class PolicyBrain:
    """Orchestrates risk evaluation and policy evolution."""
    
    def __init__(
        self,
        policy_file: str = "data/policy.json",
        reasoning_bank_file: str = "data/reasoning_bank.json",
        openai_api_key: Optional[str] = None
    ):
        """
        Initialize Policy Brain.
        
        Args:
            policy_file: Path to policy configuration file
            reasoning_bank_file: Path to reasoning bank file
            openai_api_key: OpenAI API key for distillation
        """
        self.policy_file = Path(policy_file)
        self.reasoning_bank = ReasoningBank(reasoning_bank_file)
        self.openai_client = OpenAIClient(api_key=openai_api_key)
        self.policy_history: List[PolicyOverride] = []
        self.policy: PolicyConfig = self._load_policy()
    
    def _load_policy(self) -> PolicyConfig:
        """Load policy configuration from disk."""
        self.policy_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.policy_file.exists():
            # Create default policy
            default_policy = PolicyConfig()
            self._save_policy(default_policy)
            logger.info("Created default policy configuration")
            return default_policy
        
        try:
            with open(self.policy_file, 'r') as f:
                data = json.load(f)
            
            config_data = data.get('config', {})
            policy = PolicyConfig(**config_data)
            
            # Load history
            history_data = data.get('history', [])
            for h in history_data:
                if 'timestamp' in h and isinstance(h['timestamp'], str):
                    h['timestamp'] = datetime.fromisoformat(h['timestamp'].replace('Z', '+00:00'))
                self.policy_history.append(PolicyOverride(**h))
            
            logger.info(f"Loaded policy configuration with {len(self.policy_history)} historical overrides")
            return policy
            
        except Exception as e:
            logger.error(f"Failed to load policy: {e}")
            return PolicyConfig()
    
    def _save_policy(self, policy: PolicyConfig):
        """Save policy configuration to disk."""
        try:
            data = {
                "version": "1.0",
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "config": policy.model_dump(),
                "history": [
                    {
                        **h.model_dump(),
                        "timestamp": h.timestamp.isoformat() + "Z"
                    }
                    for h in self.policy_history
                ]
            }
            
            with open(self.policy_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info("Saved policy configuration")
            
        except Exception as e:
            logger.error(f"Failed to save policy: {e}")
            raise
    
    def load_policy_overrides(self) -> PolicyConfig:
        """
        Reload policy configuration from disk.
        
        Returns:
            Current policy configuration
        """
        self.policy = self._load_policy()
        return self.policy
    
    def evaluate_risk(
        self,
        risk_score: float,
        flagged_loans: List[FlaggedLoan]
    ) -> EscalationDecision:
        """
        Evaluate risk and make escalation decision.
        
        Args:
            risk_score: Global risk score (0-100)
            flagged_loans: List of flagged loans
            
        Returns:
            Escalation decision with recommended actions
        """
        reasoning = []
        
        # Check risk threshold
        threshold_exceeded = risk_score > self.policy.risk_threshold
        reasoning.append(
            f"Global risk score: {risk_score:.1f} {'>' if threshold_exceeded else '<='} threshold {self.policy.risk_threshold:.1f}"
        )
        
        # Check flagged loans
        has_flagged_loans = len(flagged_loans) > 0
        reasoning.append(f"Flagged loans: {len(flagged_loans)}")
        
        # Calculate total exposure
        total_exposure = sum(loan.outstanding_balance for loan in flagged_loans)
        reasoning.append(f"Total exposure: ${total_exposure:,.2f}")
        
        # Determine status
        if threshold_exceeded and has_flagged_loans:
            status = 'critical'
            
            # Determine hedge percentage based on affected sectors
            sectors = set(loan.industry for loan in flagged_loans)
            hedge_percentages = [
                self.policy.hedge_percentages.get(sector, 10.0)
                for sector in sectors
            ]
            hedge_percentage = max(hedge_percentages) if hedge_percentages else 15.0
            
            recommended_action = f"Execute {hedge_percentage:.0f}% BTC hedge immediately"
            reasoning.append(f"CRITICAL: Risk threshold exceeded AND loans flagged")
            
        elif threshold_exceeded or has_flagged_loans:
            status = 'elevated'
            hedge_percentage = 5.0
            recommended_action = "Monitor closely, prepare for potential hedge"
            reasoning.append("ELEVATED: One condition met, monitoring required")
            
        else:
            status = 'normal'
            hedge_percentage = 0.0
            recommended_action = "Continue normal operations"
            reasoning.append("NORMAL: No immediate action required")
        
        return EscalationDecision(
            status=status,
            recommended_action=recommended_action,
            hedge_percentage=hedge_percentage,
            affected_loans=flagged_loans,
            reasoning=reasoning
        )
    
    def generate_alert(self, decision: EscalationDecision) -> Alert:
        """
        Generate alert from escalation decision.
        
        Args:
            decision: Escalation decision
            
        Returns:
            Alert object
        """
        alert_id = f"A{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        if decision.status == 'critical':
            severity = 'critical'
            title = "Shadow Default Risk Detected"
            message = f"High correlation detected. {len(decision.affected_loans)} loans flagged. {decision.recommended_action}"
            action_required = True
        elif decision.status == 'elevated':
            severity = 'warning'
            title = "Elevated Risk Level"
            message = f"Risk conditions detected. {decision.recommended_action}"
            action_required = False
        else:
            severity = 'info'
            title = "Normal Operations"
            message = "No immediate risks detected"
            action_required = False
        
        return Alert(
            alert_id=alert_id,
            timestamp=datetime.utcnow(),
            severity=severity,
            title=title,
            message=message,
            action_required=action_required,
            recommended_hedge=decision.hedge_percentage
        )

    def distill_policy_from_override(
        self,
        override_type: str,
        old_value: Any,
        new_value: Any,
        loan_context: Optional[Dict[str, Any]] = None,
        human_rationale: Optional[str] = None
    ) -> ReasoningBankEntry:
        """
        Use OpenAI to distill WHY a human made an override and extract the underlying logic rule.
        
        This is the AGENTIC UPGRADE for in-context policy distillation.
        
        Args:
            override_type: Type of override (risk_score, threshold, etc.)
            old_value: Original value
            new_value: New value after override
            loan_context: Context about the loan (if applicable)
            human_rationale: Optional human-provided reason
            
        Returns:
            Reasoning bank entry with extracted rule
        """
        # Build context for AI
        context_str = ""
        if loan_context:
            context_str = "\n".join([f"- {k}: {v}" for k, v in loan_context.items()])
        
        rationale_str = human_rationale or "No explicit rationale provided"
        
        # Create distillation prompt
        system_prompt = """You are a financial policy analyst. Your job is to analyze human overrides and extract the underlying logic rule that explains WHY the human made this decision.

Focus on:
1. What pattern or condition triggered the override?
2. What general rule can be extracted?
3. How confident are you in this rule (0-100)?

Respond in this format:
RULE: <extracted rule in IF-THEN format>
CONFIDENCE: <0-100>
EXPLANATION: <brief explanation>"""
        
        user_prompt = f"""A user manually changed a {override_type} value:
- Old Value: {old_value}
- New Value: {new_value}
- Change: {new_value - old_value if isinstance(old_value, (int, float)) and isinstance(new_value, (int, float)) else 'N/A'}

Context:
{context_str}

Human Rationale: {rationale_str}

Task: Extract the underlying logic rule that explains this override."""
        
        try:
            response = self.openai_client.analyze_with_reasoning(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3,
                max_tokens=500
            )
            
            # Parse response
            extracted_rule = "No rule extracted"
            confidence_score = 50.0
            
            if 'RULE:' in response:
                rule_part = response.split('RULE:')[1].split('CONFIDENCE:')[0].strip()
                extracted_rule = rule_part
            
            if 'CONFIDENCE:' in response:
                try:
                    conf_part = response.split('CONFIDENCE:')[1].split('EXPLANATION:')[0].strip()
                    confidence_score = float(conf_part)
                    confidence_score = max(0.0, min(100.0, confidence_score))
                except:
                    pass
            
            logger.info(f"Distilled rule: {extracted_rule} (confidence: {confidence_score})")
            
        except Exception as e:
            logger.error(f"Policy distillation failed: {e}")
            extracted_rule = f"Manual override: {override_type} changed from {old_value} to {new_value}"
            confidence_score = 30.0
        
        # Create reasoning bank entry
        entry_id = f"RB{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        entry = ReasoningBankEntry(
            entry_id=entry_id,
            timestamp=datetime.utcnow(),
            override_type=override_type,
            old_value=old_value,
            new_value=new_value,
            human_rationale=human_rationale,
            extracted_rule=extracted_rule,
            confidence_score=confidence_score,
            loan_context=loan_context
        )
        
        # Append to reasoning bank
        self.reasoning_bank.append(entry)
        
        return entry
    
    def detect_rule_conflicts(self, new_rule: str) -> List[ReasoningBankEntry]:
        """
        Detect if a new rule contradicts existing rules in the reasoning bank.
        
        Args:
            new_rule: New rule to check for conflicts
            
        Returns:
            List of conflicting entries
        """
        conflicts = []
        
        # Simple keyword-based conflict detection
        # In production, this could use semantic similarity with embeddings
        new_rule_lower = new_rule.lower()
        
        for entry in self.reasoning_bank.get_all_entries():
            if not entry.extracted_rule:
                continue
            
            existing_rule_lower = entry.extracted_rule.lower()
            
            # Check for opposite conditions
            # Example: "IF X THEN increase" vs "IF X THEN decrease"
            if 'increase' in new_rule_lower and 'decrease' in existing_rule_lower:
                # Check if they reference the same condition
                new_words = set(new_rule_lower.split())
                existing_words = set(existing_rule_lower.split())
                common_words = new_words & existing_words
                
                # If they share significant words, might be a conflict
                if len(common_words) > 3:
                    conflicts.append(entry)
            
            elif 'decrease' in new_rule_lower and 'increase' in existing_rule_lower:
                new_words = set(new_rule_lower.split())
                existing_words = set(existing_rule_lower.split())
                common_words = new_words & existing_words
                
                if len(common_words) > 3:
                    conflicts.append(entry)
        
        if conflicts:
            logger.warning(f"Detected {len(conflicts)} potential rule conflicts")
        
        return conflicts
    
    def propose_policy_update(
        self,
        field: str,
        new_value: Any,
        reason: str
    ) -> PolicyDiff:
        """
        Propose a policy update based on learned patterns (doesn't auto-apply).
        
        This is the AGENTIC UPGRADE for logic-gated policy updates.
        
        Args:
            field: Policy field to update
            new_value: Proposed new value
            reason: Reason for the proposal
            
        Returns:
            Policy diff for user review
        """
        # Get current value
        old_value = getattr(self.policy, field, None)
        
        # Query reasoning bank for supporting evidence
        patterns = self.reasoning_bank.detect_patterns(min_occurrences=2)
        supporting_evidence = []
        
        for pattern in patterns:
            if pattern['override_type'] == field:
                supporting_evidence.append(
                    f"{pattern['occurrences']} overrides detected (avg change: {pattern['average_change']:.2f})"
                )
        
        # Get recent related entries
        recent_entries = self.reasoning_bank.query_by_type(field)
        if recent_entries:
            supporting_evidence.append(f"Most recent override: {recent_entries[-1].timestamp.strftime('%Y-%m-%d %H:%M')}")
        
        # Use AI to generate explanation
        system_prompt = """You are a financial policy advisor. Explain why a policy change is being proposed based on observed patterns.

Be concise and focus on:
1. What pattern was detected
2. Why this change makes sense
3. Potential risks or considerations"""
        
        user_prompt = f"""Policy Change Proposal:
Field: {field}
Current Value: {old_value}
Proposed Value: {new_value}
Reason: {reason}

Supporting Evidence:
{chr(10).join(f'- {e}' for e in supporting_evidence) if supporting_evidence else '- No historical evidence'}

Task: Generate a clear explanation for why this policy change is being proposed."""
        
        try:
            explanation = self.openai_client.analyze_with_reasoning(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.4,
                max_tokens=400
            )
            
            # Calculate confidence based on supporting evidence
            confidence_score = min(50.0 + (len(supporting_evidence) * 15.0), 95.0)
            
        except Exception as e:
            logger.error(f"Failed to generate explanation: {e}")
            explanation = f"Proposing to change {field} from {old_value} to {new_value}. {reason}"
            confidence_score = 40.0
        
        # Create policy diff
        diff_id = f"PD{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        policy_diff = PolicyDiff(
            diff_id=diff_id,
            timestamp=datetime.utcnow(),
            field=field,
            old_value=old_value,
            new_value=new_value,
            explanation=explanation,
            confidence_score=confidence_score,
            supporting_evidence=supporting_evidence,
            status='proposed'
        )
        
        logger.info(f"Proposed policy update: {field} = {new_value} (confidence: {confidence_score})")
        return policy_diff
    
    def apply_policy_diff(
        self,
        policy_diff: PolicyDiff,
        approved_by: str,
        approved: bool
    ) -> bool:
        """
        Apply or reject a policy diff after user review.
        
        Args:
            policy_diff: Policy diff to apply
            approved_by: User who approved/rejected
            approved: Whether the diff was approved
            
        Returns:
            True if policy was updated, False otherwise
        """
        # Update diff status
        policy_diff.status = 'approved' if approved else 'rejected'
        
        # Log to reasoning bank
        entry_id = f"RB{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        reasoning_entry = ReasoningBankEntry(
            entry_id=entry_id,
            timestamp=datetime.utcnow(),
            override_type=policy_diff.field,
            old_value=policy_diff.old_value,
            new_value=policy_diff.new_value,
            human_rationale=f"Policy diff {policy_diff.status} by {approved_by}",
            extracted_rule=policy_diff.explanation,
            confidence_score=policy_diff.confidence_score
        )
        self.reasoning_bank.append(reasoning_entry)
        
        if not approved:
            logger.info(f"Policy diff {policy_diff.diff_id} rejected by {approved_by}")
            return False
        
        # Apply the change
        try:
            setattr(self.policy, policy_diff.field, policy_diff.new_value)
            
            # Create policy override record
            override = PolicyOverride(
                override_id=policy_diff.diff_id,
                timestamp=datetime.utcnow(),
                field=policy_diff.field,
                old_value=policy_diff.old_value,
                new_value=policy_diff.new_value,
                applied_by=approved_by,
                reason=policy_diff.explanation
            )
            self.policy_history.append(override)
            
            # Save policy
            self._save_policy(self.policy)
            
            logger.info(f"Applied policy diff {policy_diff.diff_id}: {policy_diff.field} = {policy_diff.new_value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply policy diff: {e}")
            return False
    
    def apply_override(
        self,
        override: PolicyOverride
    ) -> None:
        """
        Apply a manual policy override immediately.
        
        Args:
            override: Policy override to apply
        """
        try:
            # Apply the change
            setattr(self.policy, override.field, override.new_value)
            
            # Add to history
            self.policy_history.append(override)
            
            # Save policy
            self._save_policy(self.policy)
            
            logger.info(f"Applied override {override.override_id}: {override.field} = {override.new_value}")
            
        except Exception as e:
            logger.error(f"Failed to apply override: {e}")
            raise
