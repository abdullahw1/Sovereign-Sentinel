"""
Fallback notification system for Sovereign Sentinel.
Provides email notifications when voice alerts fail.
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class NotificationSystem:
    """Manages fallback notifications via email."""
    
    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None,
        to_emails: Optional[list] = None
    ):
        """
        Initialize the Notification System.
        
        Args:
            smtp_host: SMTP server host
            smtp_port: SMTP server port
            smtp_user: SMTP username
            smtp_password: SMTP password
            from_email: Sender email address
            to_emails: List of recipient email addresses
        """
        self.smtp_host = smtp_host or "smtp.gmail.com"
        self.smtp_port = smtp_port or 587
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = from_email or smtp_user
        self.to_emails = to_emails or []
        self.enabled = bool(smtp_user and smtp_password and to_emails)
        
        if not self.enabled:
            logger.warning("Email notification system not configured - fallback disabled")
        else:
            logger.info(f"Email notification system initialized for {len(self.to_emails)} recipients")
    
    async def send_email_alert(
        self,
        alert: Dict[str, Any],
        reason: str = "Voice alert generation failed"
    ) -> Dict[str, Any]:
        """
        Send email notification for critical alert.
        
        Args:
            alert: Alert dictionary with crisis details
            reason: Reason for fallback notification
            
        Returns:
            Result dictionary with status
        """
        if not self.enabled:
            logger.warning("Email notification disabled - skipping")
            return {
                "status": "skipped",
                "reason": "Email not configured",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        alert_id = alert.get('alertId', 'unknown')
        
        try:
            # Create email message
            subject = f"🚨 CRITICAL ALERT: {alert.get('title', 'Unknown Crisis')}"
            
            body = f"""
SOVEREIGN SENTINEL - CRITICAL ALERT

Alert ID: {alert_id}
Timestamp: {datetime.utcnow().isoformat()}
Severity: {alert.get('severity', 'critical').upper()}

{alert.get('title', 'Unknown Crisis')}

{alert.get('message', '')}

Recommended Action: {alert.get('recommendedHedge', 0)}% Bitcoin Hedge

---
Fallback Reason: {reason}

This is an automated alert from Sovereign Sentinel.
Please log in to the War Room Dashboard for full details and authorization.
"""
            
            # Send to all recipients
            results = []
            for to_email in self.to_emails:
                try:
                    self._send_email(to_email, subject, body)
                    results.append({"email": to_email, "status": "sent"})
                    logger.info(f"Email alert sent to {to_email}")
                except Exception as e:
                    results.append({"email": to_email, "status": "failed", "error": str(e)})
                    logger.error(f"Failed to send email to {to_email}: {e}")
            
            return {
                "status": "sent",
                "alertId": alert_id,
                "recipients": results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to send email alert for {alert_id}: {e}")
            return {
                "status": "failed",
                "alertId": alert_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _send_email(self, to_email: str, subject: str, body: str):
        """
        Send email using SMTP.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body text
        """
        msg = MIMEMultipart()
        msg['From'] = self.from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to SMTP server and send
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
    
    async def log_alert_attempt(
        self,
        alert_id: str,
        attempt_type: str,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log alert attempt for audit trail.
        
        Args:
            alert_id: Alert identifier
            attempt_type: Type of alert attempt ('voice', 'email', 'authorization')
            status: Status of attempt ('success', 'failed', 'skipped')
            details: Additional details about the attempt
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "alertId": alert_id,
            "attemptType": attempt_type,
            "status": status,
            "details": details or {}
        }
        
        # In production, this would write to a database or log file
        logger.info(f"Alert attempt logged: {log_entry}")
        
        return log_entry
