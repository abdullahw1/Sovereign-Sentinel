# Agentic PIK Toggle Hunter - Implementation Complete

## Overview

The Agentic PIK Toggle Hunter is an AI-powered forensic analysis system that replaces static rule-based flagging with OpenAI-powered multi-step reasoning to detect high-risk PIK (Payment-in-Kind) loan toggles.

## Key Features Implemented

### 1. PIK Toggle Detection
- **Historical Data Analysis**: Loads and analyzes loan payment history to detect when borrowers switch from Cash/Hybrid to PIK payments
- **Toggle Identification**: Automatically identifies loans where interest payment type changed over time
- **Risk Signal**: PIK toggles are a critical indicator of financial distress

### 2. Multi-Step AI Reasoning Chain

The system implements a 4-step reasoning process for each loan:

**Step 1: Identify PIK Loans**
- Analyzes current loan structure
- Explains PIK loan implications
- Identifies payment-in-kind status

**Step 2: Cross-reference with Historical Data**
- Reviews payment history timeline
- Detects payment type changes
- Identifies toggle events (Cash → PIK)

**Step 3: Flag Toggle Events**
- Evaluates industry risk correlation
- Assesses geopolitical event impact
- Makes FLAG/NO_FLAG decision with reasoning

**Step 4: Assess Risk Severity**
- Calculates risk level (low/medium/high/critical)
- Generates confidence score (0-100)
- Provides detailed justification

### 3. Enhanced Data Models

**LoanHistoricalRecord**: Tracks historical payment data
- loan_id, timestamp, interest_type, outstanding_balance

**AgentReasoningTrace**: Stores AI reasoning for transparency
- step, action, observation, reasoning, timestamp

**FlaggedLoan** (Enhanced): Now includes
- confidence_score (0-100)
- agent_reasoning (list of traces)
- pik_toggle_detected (boolean)
- previous_interest_type (string)

### 4. OpenAI Integration

**OpenAIClient**: Wrapper for OpenAI API
- Single-step reasoning with system/user prompts
- Multi-step reasoning chains
- Temperature and token control
- Error handling and logging

### 5. Backward Compatibility

The system maintains backward compatibility:
- `flag_high_risk_loans()`: Original rule-based method (still available)
- `flag_high_risk_loans_with_ai()`: New AI-powered method
- `analyze_portfolio()`: Supports both modes via `use_ai` parameter

## Usage Example

```python
from app.forensic_auditor import ForensicAuditor

# Initialize with OpenAI API key
auditor = ForensicAuditor()

# Analyze portfolio with AI
result = auditor.analyze_portfolio(
    file_path="data/test_ledger.json",
    risky_sectors=["energy", "currency"],
    correlated_event="Middle East energy crisis",
    use_ai=True,
    historical_data_path="data/loan_history.json"
)

# Access results
print(f"PIK toggles detected: {result['pik_toggles_detected']}")
for loan in result['ranked_flagged_loans']:
    print(f"Loan {loan.loan_id}: {loan.flag_reason}")
    print(f"Confidence: {loan.confidence_score}%")
    for trace in loan.agent_reasoning:
        print(f"  Step {trace.step}: {trace.reasoning[:100]}...")
```

## Test Results

Successfully tested with sample data:
- **Total loans analyzed**: 5
- **Flagged loans**: 3
- **PIK toggles detected**: 2
  - L001 (Acme Energy): Cash → PIK toggle
  - L003 (LatAm Telecom): Cash → PIK toggle
- **AI reasoning**: 4 steps per loan with full transparency

## Files Modified/Created

### Modified
- `app/models.py`: Added LoanHistoricalRecord, AgentReasoningTrace, enhanced FlaggedLoan
- `app/forensic_auditor.py`: Added AI-powered analysis methods
- `requirements.txt`: Added openai==1.12.0

### Created
- `app/openai_client.py`: OpenAI API wrapper
- `data/loan_history.json`: Sample historical payment data
- `test_agentic_pik_hunter.py`: Demonstration script
- `data/agentic_analysis_results.json`: Output with full reasoning traces

## Requirements Validated

✅ **Requirement 2.2**: PIK loan flagging with industry correlation
✅ **Requirement 2.3**: Shadow Default detection (PIK toggles)
✅ **Requirement 2.4**: Exposure ranking by outstanding balance

## Next Steps

The agentic PIK toggle hunter is production-ready and can be integrated with:
1. OSINT Scout for real-time geopolitical correlation
2. Policy Brain for escalation decisions
3. War Room Dashboard for visualization
4. Voice Alert System for critical notifications

## Configuration

Ensure `.env` file contains:
```
OPENAI_API_KEY=your_openai_api_key_here
```

The system uses `gpt-4o-mini` model for cost-effective reasoning while maintaining high quality analysis.
