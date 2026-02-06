"""
Main FastAPI application for Sovereign Sentinel backend.
"""
import logging
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path
from typing import Any
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.config import settings
from app.you_client import YouAPIClient
from app.osint_scout import OSINTScout
from app.scheduler import ScanScheduler
from app.models import RiskAssessment
from app.websocket_manager import ws_manager
from app.voice_alert import VoiceAlertSystem
from app.notification import NotificationSystem
from app.treasury_commander import TreasuryCommander
from app.company_analyzer import CompanyAnalyzer

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
you_client: YouAPIClient = None
osint_scout: OSINTScout = None
scheduler: ScanScheduler = None
voice_alert_system = None
notification_system = None
treasury_commander = None
company_analyzer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    global you_client, osint_scout, scheduler, voice_alert_system, notification_system, treasury_commander, company_analyzer
    
    logger.info("Starting Sovereign Sentinel backend...")
    
    # Initialize You.com client
    you_client = YouAPIClient(api_key=settings.you_api_key)
    logger.info("You.com API client initialized")
    
    # Initialize OSINT Scout
    osint_scout = OSINTScout(you_client=you_client)
    logger.info("OSINT Scout initialized")
    
    # Initialize Notification System
    to_emails = []
    if settings.notification_to_emails:
        to_emails = [email.strip() for email in settings.notification_to_emails.split(',')]
    
    notification_system = NotificationSystem(
        smtp_host=settings.smtp_host,
        smtp_port=settings.smtp_port,
        smtp_user=settings.smtp_user,
        smtp_password=settings.smtp_password,
        from_email=settings.notification_from_email,
        to_emails=to_emails
    )
    logger.info("Notification System initialized")
    
    # Initialize Voice Alert System with fallback
    voice_alert_system = VoiceAlertSystem(
        openai_api_key=settings.openai_api_key,
        notification_system=notification_system
    )
    logger.info("Voice Alert System initialized")
    
    # Initialize Treasury Commander
    if settings.composio_api_key:
        treasury_commander = TreasuryCommander(
            composio_api_key=settings.composio_api_key,
            openai_api_key=settings.openai_api_key
        )
        logger.info("Treasury Commander initialized")
    else:
        logger.warning("Treasury Commander not initialized - COMPOSIO_API_KEY not set")
    
    # Initialize Company Analyzer
    company_analyzer = CompanyAnalyzer(
        openai_api_key=settings.openai_api_key,
        you_api_key=settings.you_api_key
    )
    logger.info("Company Analyzer initialized")
    
    # Initialize and start scheduler
    scheduler = ScanScheduler(osint_scout=osint_scout, ws_manager=ws_manager)
    scheduler.start()
    logger.info("Scheduler started")
    
    # Run initial scan
    try:
        await scheduler.run_immediate_scan()
        logger.info("Initial scan completed")
    except Exception as e:
        logger.error(f"Initial scan failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Sovereign Sentinel backend...")
    if scheduler:
        scheduler.stop()
    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Sovereign Sentinel API",
    description="Financial War Room system for detecting Shadow Defaults",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Sovereign Sentinel API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "scheduler_running": scheduler.is_running if scheduler else False,
        "environment": settings.environment
    }


@app.get("/api/risk/latest", response_model=RiskAssessment)
async def get_latest_risk_assessment():
    """
    Get the latest risk assessment.
    
    Returns:
        Latest RiskAssessment object
    """
    if not osint_scout:
        raise HTTPException(status_code=503, detail="OSINT Scout not initialized")
    
    assessment = osint_scout.get_latest_assessment()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="No risk assessment available")
    
    return assessment


@app.post("/api/scan/immediate", response_model=RiskAssessment)
async def trigger_immediate_scan():
    """
    Trigger an immediate OSINT scan.
    
    Returns:
        RiskAssessment from the scan
    """
    if not scheduler:
        raise HTTPException(status_code=503, detail="Scheduler not initialized")
    
    try:
        await scheduler.run_immediate_scan()
        assessment = osint_scout.get_latest_assessment()
        
        if not assessment:
            raise HTTPException(status_code=500, detail="Scan completed but no assessment available")
        
        return assessment
        
    except Exception as e:
        logger.error(f"Error during immediate scan: {e}")
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@app.get("/api/scan/status")
async def get_scan_status():
    """
    Get the status of the scanning scheduler.
    
    Returns:
        Scheduler status information
    """
    if not scheduler:
        raise HTTPException(status_code=503, detail="Scheduler not initialized")
    
    return {
        "is_running": scheduler.is_running,
        "interval_minutes": settings.scan_interval_minutes,
        "latest_assessment_available": osint_scout.get_latest_assessment() is not None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


# Pydantic models for API requests
class PIKStatusUpdate(BaseModel):
    status: str


class PolicyOverrideRequest(BaseModel):
    overrideId: str
    timestamp: str
    field: str
    oldValue: Any
    newValue: Any
    appliedBy: str
    reason: str


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates.
    Clients connect here to receive live updates about risk scores, alerts, agent logs, etc.
    """
    await ws_manager.connect(websocket)
    try:
        # Keep connection alive and handle incoming messages
        while True:
            # Receive messages from client (if any)
            data = await websocket.receive_text()
            # Echo back or handle client messages if needed
            logger.debug(f"Received WebSocket message: {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)


# Dashboard API endpoints
@app.get("/api/dashboard/state")
async def get_dashboard_state():
    """
    Get complete dashboard state including risk score, flagged loans, alerts, etc.
    """
    # Get latest risk assessment
    assessment = osint_scout.get_latest_assessment() if osint_scout else None
    
    # Mock data for now - will be replaced with real data from other agents
    dashboard_state = {
        "currentRiskScore": assessment.global_risk_score if assessment else 0,
        "flaggedLoans": [],  # Will be populated by Forensic Auditor
        "activeAlerts": [],  # Will be populated by Policy Brain
        "systemStatus": [
            {
                "service": "OSINT Scout",
                "status": "operational" if osint_scout else "down",
                "lastCheck": datetime.utcnow().isoformat()
            },
            {
                "service": "Scheduler",
                "status": "operational" if (scheduler and scheduler.is_running) else "down",
                "lastCheck": datetime.utcnow().isoformat()
            }
        ],
        "recentAgentActivity": []  # Will be populated by agent logs
    }
    
    return dashboard_state


@app.get("/api/risk/current")
async def get_current_risk_score():
    """Get current risk score."""
    if not osint_scout:
        raise HTTPException(status_code=503, detail="OSINT Scout not initialized")
    
    assessment = osint_scout.get_latest_assessment()
    if not assessment:
        raise HTTPException(status_code=404, detail="No risk assessment available")
    
    return {
        "globalRiskScore": assessment.global_risk_score,
        "sentiment": assessment.sentiment,
        "timestamp": assessment.timestamp.isoformat()
    }


@app.get("/api/loans/flagged")
async def get_flagged_loans():
    """Get list of flagged loans."""
    # Mock data - will be replaced with real data from Forensic Auditor
    return []


@app.post("/api/loans/{loan_id}/pik-status")
async def toggle_pik_status(loan_id: str, update: PIKStatusUpdate):
    """
    Toggle PIK status for a loan.
    
    Args:
        loan_id: Loan identifier
        update: New status information
    """
    # Mock implementation - will be replaced with real logic
    logger.info(f"Toggling PIK status for loan {loan_id} to {update.status}")
    
    # Broadcast update to WebSocket clients
    await ws_manager.send_loan_update({
        "loanId": loan_id,
        "newStatus": update.status,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    return {"success": True, "loanId": loan_id, "newStatus": update.status}


@app.get("/api/alerts/active")
async def get_active_alerts():
    """Get list of active alerts."""
    # Mock data - will be replaced with real data from Policy Brain
    return []


@app.get("/api/policy/config")
async def get_policy_config():
    """Get current policy configuration."""
    # Mock data - will be replaced with real data from Policy Brain
    return {
        "riskThreshold": 70,
        "pikExposureLimit": 5000000,
        "autoExecuteEnabled": False,
        "hedgePercentages": {
            "energy": 15,
            "currency": 20,
            "sovereign": 25
        },
        "customRules": []
    }


@app.post("/api/policy/override")
async def apply_policy_override(override: PolicyOverrideRequest):
    """
    Apply a policy override.
    
    Args:
        override: Policy override details
    """
    logger.info(f"Applying policy override: {override.field} = {override.newValue}")
    
    # Mock implementation - will be replaced with real logic from Policy Brain
    # Broadcast update to WebSocket clients
    await ws_manager.send_policy_update({
        "field": override.field,
        "newValue": override.newValue,
        "timestamp": override.timestamp
    })
    
    return {"success": True, "overrideId": override.overrideId}


@app.get("/api/logs/agents")
async def get_agent_logs(limit: Optional[int] = 50):
    """
    Get recent agent activity logs.
    
    Args:
        limit: Maximum number of logs to return
    """
    # Mock data - will be replaced with real agent logs
    return []


@app.get("/api/system/status")
async def get_system_status():
    """Get system status for all services."""
    
    return [
        {
            "service": "OSINT Scout",
            "status": "operational" if osint_scout else "down",
            "lastCheck": datetime.utcnow().isoformat()
        },
        {
            "service": "Scheduler",
            "status": "operational" if (scheduler and scheduler.is_running) else "down",
            "lastCheck": datetime.utcnow().isoformat()
        },
        {
            "service": "Forensic Auditor",
            "status": "operational",
            "lastCheck": datetime.utcnow().isoformat()
        },
        {
            "service": "Policy Brain",
            "status": "operational",
            "lastCheck": datetime.utcnow().isoformat()
        }
    ]


# Voice Alert System endpoints
@app.post("/api/alerts/{alert_id}/generate-audio")
async def generate_audio_alert(alert_id: str):
    """
    Generate audio alert for a critical alert.
    
    Args:
        alert_id: Alert identifier
    """
    if not voice_alert_system:
        raise HTTPException(status_code=503, detail="Voice Alert System not initialized")
    
    # Mock alert data - in production, this would fetch from Policy Brain
    alert_data = {
        "alertId": alert_id,
        "title": "High-Risk Correlation Detected",
        "message": "Middle East energy crisis correlates with PIK debt exposure",
        "recommendedHedge": 15.0
    }
    
    try:
        result = await voice_alert_system.generate_audio_alert(alert_data)
        
        # Broadcast audio alert to WebSocket clients
        await ws_manager.broadcast("audio_alert", result)
        
        return result
    except Exception as e:
        logger.error(f"Failed to generate audio alert: {e}")
        raise HTTPException(status_code=500, detail=f"Audio generation failed: {str(e)}")


@app.post("/api/alerts/{alert_id}/authorize")
async def authorize_alert(alert_id: str, action: str):
    """
    Handle user authorization response to an alert.
    
    Args:
        alert_id: Alert identifier
        action: User action ('approve' or 'dismiss')
    """
    if not voice_alert_system:
        raise HTTPException(status_code=503, detail="Voice Alert System not initialized")
    
    if action not in ['approve', 'dismiss']:
        raise HTTPException(status_code=400, detail="Action must be 'approve' or 'dismiss'")
    
    try:
        result = await voice_alert_system.handle_user_response(alert_id, action)
        
        # Broadcast authorization result to WebSocket clients
        await ws_manager.broadcast("authorization", result)
        
        # Log the authorization
        logger.info(f"Alert {alert_id} {action}ed by user")
        
        return result
    except Exception as e:
        logger.error(f"Failed to process authorization: {e}")
        raise HTTPException(status_code=500, detail=f"Authorization failed: {str(e)}")


# Serve audio files
@app.get("/audio/{filename}")
async def serve_audio(filename: str):
    """
    Serve audio alert files.
    
    Args:
        filename: Audio file name
    """
    audio_path = Path("data/audio_alerts") / filename
    
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(
        path=str(audio_path),
        media_type="audio/mpeg",
        filename=filename
    )


# Test endpoint for UI development
@app.post("/api/test/broadcast-mock-alert")
async def broadcast_mock_alert():
    """
    Broadcast a mock audio alert for UI testing (bypasses OpenAI TTS).
    Uses a public test audio file.
    """
    mock_alert = {
        "alertId": f"test_ui_alert_{int(datetime.utcnow().timestamp())}",
        "audioUrl": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
        "audioPath": "",
        "status": "generated",
        "script": "Emergency Alert. High-Risk Correlation Detected. Middle East energy crisis correlates with PIK debt exposure. Recommend 15 percent Bitcoin hedge. Click Approve to authorize or Dismiss to review manually.",
        "duration": 15.5
    }
    
    # Broadcast to all connected clients
    await ws_manager.send_audio_alert(mock_alert)
    
    logger.info(f"Mock alert broadcasted: {mock_alert['alertId']}")
    
    return {
        "success": True,
        "message": "Mock alert broadcasted to all connected clients",
        "alert": mock_alert
    }



# Treasury Commander endpoints
@app.post("/api/hedge/execute")
async def execute_hedge(
    alert_id: str,
    hedge_percentage: float,
    portfolio_value: float = 10000000.0
):
    """
    Execute Bitcoin hedge after authorization.
    
    Args:
        alert_id: Alert identifier that was authorized
        hedge_percentage: Percentage to hedge (0-100)
        portfolio_value: Total portfolio value in USD
    """
    if not treasury_commander:
        raise HTTPException(
            status_code=503,
            detail="Treasury Commander not initialized - COMPOSIO_API_KEY required"
        )
    
    try:
        # Create mock authorization (in production, this would come from voice alert)
        authorization = {
            "authorized": True,
            "alertId": alert_id,
            "timestamp": datetime.utcnow().isoformat(),
            "action": "approve"
        }
        
        # Execute hedge with agent reasoning
        result = await treasury_commander.execute_hedge_with_verification(
            authorization, hedge_percentage, portfolio_value
        )
        
        # Broadcast result to WebSocket clients
        await ws_manager.broadcast("hedge_executed", result)
        
        logger.info(f"Hedge executed for alert {alert_id}: {result.get('status')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to execute hedge: {e}")
        raise HTTPException(status_code=500, detail=f"Hedge execution failed: {str(e)}")


@app.get("/api/hedge/agent-memory")
async def get_agent_memory():
    """
    Get Treasury Commander agent memory (decision traces).
    
    Returns:
        List of agent reasoning steps
    """
    if not treasury_commander:
        raise HTTPException(
            status_code=503,
            detail="Treasury Commander not initialized"
        )
    
    return {
        "agent_memory": treasury_commander.get_agent_memory(),
        "memory_size": len(treasury_commander.get_agent_memory())
    }


@app.post("/api/hedge/clear-memory")
async def clear_agent_memory():
    """Clear Treasury Commander agent memory."""
    if not treasury_commander:
        raise HTTPException(
            status_code=503,
            detail="Treasury Commander not initialized"
        )
    
    treasury_commander.clear_agent_memory()
    
    return {"success": True, "message": "Agent memory cleared"}


@app.post("/api/test/execute-mock-hedge")
async def execute_mock_hedge():
    """
    Execute a mock hedge for testing (bypasses authorization).
    """
    if not treasury_commander:
        raise HTTPException(
            status_code=503,
            detail="Treasury Commander not initialized - COMPOSIO_API_KEY required"
        )
    
    try:
        # Mock authorization
        authorization = {
            "authorized": True,
            "alertId": f"test_hedge_{int(datetime.utcnow().timestamp())}",
            "timestamp": datetime.utcnow().isoformat(),
            "action": "approve"
        }
        
        # Execute hedge with 15% hedge percentage
        result = await treasury_commander.execute_hedge_with_verification(
            authorization, hedge_percentage=15.0, portfolio_value=10000000.0
        )
        
        # Simplify result for JSON serialization
        simplified_result = {
            "status": result.get("status"),
            "tradeId": result.get("tradeId"),
            "timestamp": result.get("timestamp"),
            "asset": result.get("asset"),
            "amount": result.get("amount"),
            "price": result.get("price"),
            "totalCost": result.get("totalCost"),
            "human_readable_report": result.get("human_readable_report"),
            "agent_reasoning_steps": len(result.get("agent_reasoning", []))
        }
        
        # Broadcast simplified result
        await ws_manager.broadcast("hedge_executed", simplified_result)
        
        return {
            "success": True,
            "message": "Mock hedge executed",
            "result": simplified_result
        }
        
    except Exception as e:
        logger.error(f"Mock hedge execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Mock hedge failed: {str(e)}")



# Agent execution endpoints for dashboard
@app.post("/api/forensic/analyze")
async def run_forensic_analysis():
    """
    Run forensic analysis on loan portfolio.
    Returns flagged loans with PIK toggle detection.
    """
    try:
        from app.forensic_auditor import ForensicAuditor
        
        # Initialize forensic auditor with API key
        auditor = ForensicAuditor(openai_api_key=settings.openai_api_key)
        
        # Load test ledger
        ledger_path = "data/test_ledger.json"
        loan_history_path = "data/loan_history.json"
        
        # Analyze portfolio (this method handles everything)
        result = auditor.analyze_portfolio(
            file_path=ledger_path,
            risky_sectors=["energy", "sovereign"],
            correlated_event="Geopolitical crisis",
            format="json",
            use_ai=True,
            historical_data_path=loan_history_path
        )
        
        flagged_loans = result.get('ranked_flagged_loans', [])
        total_loans = result.get('total_loans', 0)
        
        # Calculate detailed metrics
        total_exposure = sum(loan.outstanding_balance for loan in flagged_loans)
        pik_toggles = [loan for loan in flagged_loans if loan.pik_toggle_detected]
        critical_loans = [loan for loan in flagged_loans if loan.risk_level == 'critical']
        
        # Build detailed reasoning
        details = []
        for loan in flagged_loans:
            if loan.pik_toggle_detected:
                details.append(f"🚨 {loan.borrower} (${loan.outstanding_balance:,.0f}): Switched from {loan.previous_interest_type} to PIK - DISTRESS SIGNAL")
            else:
                details.append(f"⚠️ {loan.borrower} (${loan.outstanding_balance:,.0f}): PIK loan in {loan.industry} sector")
        
        # Broadcast detailed log to WebSocket
        await ws_manager.send_agent_log({
            "timestamp": datetime.utcnow().isoformat(),
            "agent": "Forensic_Auditor",
            "action": "Portfolio analysis completed",
            "reasoning": f"Analyzed {total_loans} loans totaling ${sum(auditor.parse_ledger(ledger_path, 'json')[i].outstanding_balance for i in range(total_loans)):,.0f}. Found {len(pik_toggles)} PIK TOGGLES (borrowers stopped paying cash interest). Total exposure: ${total_exposure:,.0f}",
            "outcome": f"🚨 {len(critical_loans)} CRITICAL | {len(flagged_loans)} total flagged | {len(pik_toggles)} PIK toggles detected"
        })
        
        return {
            "success": True,
            "totalLoans": total_loans,
            "totalExposure": total_exposure,
            "flaggedLoans": [
                {
                    "loanId": loan.loan_id,
                    "borrower": loan.borrower,
                    "industry": loan.industry,
                    "riskLevel": loan.risk_level,
                    "confidenceScore": loan.confidence_score,
                    "pikToggleDetected": loan.pik_toggle_detected,
                    "outstandingBalance": loan.outstanding_balance,
                    "principalAmount": loan.principal_amount,
                    "previousType": loan.previous_interest_type if loan.pik_toggle_detected else None,
                    "flagReason": loan.flag_reason
                }
                for loan in flagged_loans
            ],
            "pikToggles": result.get('pik_toggles_detected', 0),
            "criticalCount": len(critical_loans),
            "details": details
        }
        
    except Exception as e:
        logger.error(f"Forensic analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/policy/evaluate")
async def run_policy_evaluation():
    """
    Run policy brain evaluation.
    Evaluates risk correlation and determines escalation status.
    """
    try:
        from app.policy_brain import PolicyBrain
        from app.models import FlaggedLoan
        
        # Get latest risk assessment
        assessment = osint_scout.get_latest_assessment() if osint_scout else None
        
        if not assessment:
            raise HTTPException(status_code=404, detail="No risk assessment available")
        
        # Initialize policy brain with file paths
        policy_brain = PolicyBrain(
            policy_file="data/demo_policy.json",
            reasoning_bank_file="data/demo_reasoning_bank.json"
        )
        
        # Mock flagged loans (in production, would come from forensic auditor)
        flagged_loans = [
            FlaggedLoan(
                loanId="L001",
                borrower="Acme Energy",
                industry="energy",
                interestType="PIK",
                principalAmount=10000000,
                outstandingBalance=12500000,
                maturityDate=datetime.utcnow(),
                covenants=[],
                flag_reason="PIK toggle detected",
                risk_level="critical",
                correlated_event="Middle East energy crisis",
                flagged_at=datetime.utcnow(),
                confidence_score=85.0,
                pik_toggle_detected=True
            )
        ]
        
        # Evaluate risk
        decision = policy_brain.evaluate_risk(
            assessment.global_risk_score,
            flagged_loans
        )
        
        # Convert to dict
        decision_dict = {
            "status": decision.status,
            "recommendedAction": decision.recommended_action,
            "recommendedHedge": decision.hedge_percentage,
            "affectedLoans": len(decision.affected_loans),
            "reasoning": " | ".join(decision.reasoning)
        }
        
        # Broadcast to WebSocket
        await ws_manager.send_agent_log({
            "timestamp": datetime.utcnow().isoformat(),
            "agent": "Policy_Brain",
            "action": "Risk evaluation completed",
            "reasoning": decision_dict["reasoning"],
            "outcome": f"Status: {decision.status}, Hedge: {decision.hedge_percentage}%"
        })
        
        # If CRITICAL, generate alert
        if decision.status == 'critical':
            alert = {
                "alertId": f"alert_{int(datetime.utcnow().timestamp())}",
                "timestamp": datetime.utcnow().isoformat(),
                "severity": "critical",
                "title": "High-Risk Correlation Detected",
                "message": f"Risk score {assessment.global_risk_score} correlates with {len(flagged_loans)} PIK loans",
                "actionRequired": True,
                "recommendedHedge": decision.hedge_percentage
            }
            
            await ws_manager.send_alert(alert)
        
        return decision_dict
        
    except Exception as e:
        logger.error(f"Policy evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")



# Custom Company Analysis endpoint
class CompanyAnalysisRequest(BaseModel):
    company_name: str
    industry: str
    financial_data: Dict[str, Any]
    analysis_focus: List[str] = ["liquidity", "profitability", "solvency", "industry_risk"]


@app.post("/api/company/analyze")
async def analyze_custom_company(request: CompanyAnalysisRequest):
    """
    Analyze a custom company with financial statements.
    
    Args:
        request: Company analysis request with financial data
    
    Returns:
        Comprehensive risk assessment
    """
    if not company_analyzer:
        raise HTTPException(status_code=503, detail="Company Analyzer not initialized")
    
    try:
        logger.info(f"Analyzing company: {request.company_name} in {request.industry}")
        
        # Broadcast start
        await ws_manager.send_agent_log({
            "timestamp": datetime.utcnow().isoformat(),
            "agent": "Company_Analyzer",
            "action": f"Analyzing {request.company_name}...",
            "reasoning": f"Researching {request.industry} industry and analyzing financial statements",
            "outcome": "pending"
        })
        
        # Run analysis
        result = await company_analyzer.analyze_company(
            company_name=request.company_name,
            industry=request.industry,
            financial_data=request.financial_data,
            analysis_focus=request.analysis_focus
        )
        
        # Broadcast completion
        risk_score = result.get("overall_risk_score", 50)
        risk_level = "LOW" if risk_score < 30 else "MEDIUM" if risk_score < 60 else "HIGH" if risk_score < 80 else "CRITICAL"
        
        await ws_manager.send_agent_log({
            "timestamp": datetime.utcnow().isoformat(),
            "agent": "Company_Analyzer",
            "action": "Analysis completed",
            "reasoning": f"Risk Score: {risk_score}/100 | Industry: {request.industry} | Ratios calculated: {len(result.get('financial_ratios', {}))}",
            "outcome": f"🎯 {risk_level} RISK | {len(result.get('recommendations', []))} recommendations"
        })
        
        return result
        
    except Exception as e:
        logger.error(f"Company analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
