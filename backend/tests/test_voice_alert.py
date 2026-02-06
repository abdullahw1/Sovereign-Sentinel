"""
Test script for Voice Alert System.
"""
import asyncio
from app.voice_alert import VoiceAlertSystem
from app.notification import NotificationSystem
from app.config import settings


async def test_voice_alert_generation():
    """Test voice alert generation."""
    print("Testing Voice Alert System...")
    
    # Initialize notification system (without email config for testing)
    notification_system = NotificationSystem()
    
    # Initialize voice alert system
    voice_alert = VoiceAlertSystem(
        openai_api_key=settings.openai_api_key,
        notification_system=notification_system
    )
    
    # Test alert data
    test_alert = {
        "alertId": "test_alert_001",
        "title": "High-Risk Correlation Detected",
        "message": "Middle East energy crisis correlates with PIK debt exposure in energy sector",
        "recommendedHedge": 15.0,
        "severity": "critical"
    }
    
    print("\n1. Testing voice script generation...")
    script = voice_alert.generate_voice_script(test_alert)
    print(f"Generated script: {script}")
    
    print("\n2. Testing audio alert generation...")
    result = await voice_alert.generate_audio_alert(test_alert)
    print(f"Audio generation result: {result['status']}")
    if result['status'] == 'generated':
        print(f"Audio URL: {result['audioUrl']}")
        print(f"Duration: {result['duration']:.2f} seconds")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
        if result.get('fallbackResult'):
            print(f"Fallback result: {result['fallbackResult']}")
    
    print("\n3. Testing user authorization...")
    auth_result = await voice_alert.handle_user_response("test_alert_001", "approve")
    print(f"Authorization result: {auth_result}")
    
    print("\nVoice Alert System test completed!")


if __name__ == "__main__":
    asyncio.run(test_voice_alert_generation())
