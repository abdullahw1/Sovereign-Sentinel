"""
Scheduled task management for OSINT Scout scanning.
"""
import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.osint_scout import OSINTScout
from app.config import settings

logger = logging.getLogger(__name__)


class ScanScheduler:
    """Manages scheduled OSINT Scout scans."""
    
    def __init__(self, osint_scout: OSINTScout):
        self.osint_scout = osint_scout
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        
    async def scan_job(self):
        """Job function that performs the scan."""
        try:
            logger.info("Starting scheduled OSINT scan...")
            assessment = await self.osint_scout.scan_geopolitical_events()
            logger.info(
                f"Scheduled scan complete. Risk Score: {assessment.global_risk_score:.2f}"
            )
        except Exception as e:
            logger.error(f"Error during scheduled scan: {e}", exc_info=True)
    
    def start(self):
        """Start the scheduler with configured interval."""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        # Add job with interval trigger
        self.scheduler.add_job(
            self.scan_job,
            trigger=IntervalTrigger(minutes=settings.scan_interval_minutes),
            id='osint_scan',
            name='OSINT Geopolitical Scan',
            replace_existing=True
        )
        
        self.scheduler.start()
        self.is_running = True
        
        logger.info(
            f"Scheduler started. Scans will run every {settings.scan_interval_minutes} minutes"
        )
    
    def stop(self):
        """Stop the scheduler."""
        if not self.is_running:
            return
        
        self.scheduler.shutdown()
        self.is_running = False
        logger.info("Scheduler stopped")
    
    async def run_immediate_scan(self):
        """Run an immediate scan outside the schedule."""
        logger.info("Running immediate scan...")
        return await self.scan_job()
