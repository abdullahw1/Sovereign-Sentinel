"""
Main FastAPI application for Sovereign Sentinel backend.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.you_client import YouAPIClient
from app.osint_scout import OSINTScout
from app.scheduler import ScanScheduler
from app.models import RiskAssessment

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    global you_client, osint_scout, scheduler
    
    logger.info("Starting Sovereign Sentinel backend...")
    
    # Initialize You.com client
    you_client = YouAPIClient(api_key=settings.you_api_key)
    logger.info("You.com API client initialized")
    
    # Initialize OSINT Scout
    osint_scout = OSINTScout(you_client=you_client)
    logger.info("OSINT Scout initialized")
    
    # Initialize and start scheduler
    scheduler = ScanScheduler(osint_scout=osint_scout)
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
