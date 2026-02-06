"""
Voice Alert System for Sovereign Sentinel.
Generates audio alerts using OpenAI TTS API for critical situations.
"""
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from openai import OpenAI
from app.config import settings
from app.models import Alert
from app.notification import NotificationSystem

logger = logging.getLogger(__name__)


class VoiceAlertSystem:
    """Manages voice alert generation using OpenAI TTS."""
    
    def __init__(self, openai_api_key: str, notification_system: Optional[NotificationSystem] = None):
        """
        Initialize the Voice Alert System.
        
        Args:
            openai_api_key: OpenAI API key for TTS
            notification_system: Optional fallback notification system
        """
        self.client = OpenAI(api_key=openai_api_key)
        self.audio_dir = Path("data/audio_alerts")
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.notification_system = notification_system
        logger.info("Voice Alert System initialized")
    
    def generate_voice_script(self, alert: Dict[str, Any]) -> str:
        """
        Generate voice script from alert data.
        
        Args:
            alert: Alert dictionary with crisis details
            
        Returns:
            Voice script text
        """
        title = alert.get('title', 'Unknown Crisis')
        message = alert.get('message', '')
        recommended_hedge = alert.get('recommendedHedge', 0)
        
        # Extract crisis type and portfolio details from message
        script = (
            f"Emergency Alert. {title}. "
            f"{message} "
        )
        
        if recommended_hedge > 0:
            script += f"Recommend {recommended_hedge} percent Bitcoin hedge. "
        
        script += "Click Approve to authorize or Dismiss to review manually."
        
        return script
    
    async def generate_audio_alert(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate audio alert using OpenAI TTS API.
        
        Args:
            alert: Alert dictionary containing crisis details
            
        Returns:
            AudioAlertResult dictionary with audio URL and metadata
        """
        alert_id = alert.get('alertId', f"alert_{int(datetime.utcnow().timestamp())}")
        
        try:
            # Generate voice script
            script = self.generate_voice_script(alert)
            logger.info(f"Generated voice script for alert {alert_id}: {script[:100]}...")
            
            # Generate audio using OpenAI TTS
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=script,
                speed=1.0
            )
            
            # Save audio file
            audio_filename = f"{alert_id}_{int(datetime.utcnow().timestamp())}.mp3"
            audio_path = self.audio_dir / audio_filename
            
            response.stream_to_file(str(audio_path))
            
            # Calculate duration (approximate based on text length)
            # Average speaking rate: ~150 words per minute
            word_count = len(script.split())
            duration = (word_count / 150) * 60  # in seconds
            
            logger.info(f"Audio alert generated successfully: {audio_filename}")
            
            # Log successful attempt
            if self.notification_system:
                await self.notification_system.log_alert_attempt(
                    alert_id, "voice", "success", {"audioFile": audio_filename}
                )
            
            return {
                "alertId": alert_id,
                "audioUrl": f"/audio/{audio_filename}",
                "audioPath": str(audio_path),
                "status": "generated",
                "script": script,
                "duration": duration
            }
            
        except Exception as e:
            logger.error(f"Failed to generate audio alert for {alert_id}: {e}")
            
            # Log failed attempt
            if self.notification_system:
                await self.notification_system.log_alert_attempt(
                    alert_id, "voice", "failed", {"error": str(e)}
                )
            
            # Attempt fallback notification
            fallback_result = None
            if self.notification_system:
                try:
                    fallback_result = await self.notification_system.send_email_alert(
                        alert, reason=f"Voice alert generation failed: {str(e)}"
                    )
                    logger.info(f"Fallback email notification sent for alert {alert_id}")
                except Exception as email_error:
                    logger.error(f"Fallback email notification also failed: {email_error}")
            
            return {
                "alertId": alert_id,
                "audioUrl": "",
                "audioPath": "",
                "status": "failed",
                "script": self.generate_voice_script(alert),
                "duration": 0,
                "error": str(e),
                "fallbackResult": fallback_result
            }
    
    async def handle_user_response(
        self, 
        alert_id: str, 
        action: str
    ) -> Dict[str, Any]:
        """
        Handle user response to audio alert.
        
        Args:
            alert_id: Alert identifier
            action: User action ('approve' or 'dismiss')
            
        Returns:
            AuthorizationResult dictionary
        """
        authorized = action.lower() == 'approve'
        
        result = {
            "authorized": authorized,
            "timestamp": datetime.utcnow().isoformat(),
            "alertId": alert_id,
            "action": action
        }
        
        logger.info(f"User response for alert {alert_id}: {action} (authorized={authorized})")
        
        # Log authorization attempt
        if self.notification_system:
            await self.notification_system.log_alert_attempt(
                alert_id, "authorization", "success", {"action": action, "authorized": authorized}
            )
        
        return result
    
    def cleanup_old_audio_files(self, max_age_hours: int = 24):
        """
        Clean up old audio files to save disk space.
        
        Args:
            max_age_hours: Maximum age of files to keep in hours
        """
        try:
            current_time = datetime.utcnow().timestamp()
            max_age_seconds = max_age_hours * 3600
            
            for audio_file in self.audio_dir.glob("*.mp3"):
                file_age = current_time - audio_file.stat().st_mtime
                if file_age > max_age_seconds:
                    audio_file.unlink()
                    logger.info(f"Deleted old audio file: {audio_file.name}")
                    
        except Exception as e:
            logger.error(f"Error cleaning up audio files: {e}")
