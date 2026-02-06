"""
Test script to manually broadcast a mock audio alert to test the UI.
This bypasses OpenAI TTS and sends a test alert directly via WebSocket.
"""
import asyncio
import sys
sys.path.insert(0, '.')

from app.websocket_manager import ws_manager


async def broadcast_test_alert():
    """Broadcast a test audio alert to all connected WebSocket clients."""
    
    print("=" * 60)
    print("BROADCASTING TEST AUDIO ALERT")
    print("=" * 60)
    
    # Create a mock audio alert (simulating successful TTS generation)
    mock_alert = {
        "alertId": "test_ui_alert_001",
        "audioUrl": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",  # Public test audio
        "audioPath": "",
        "status": "generated",
        "script": "Emergency Alert. High-Risk Correlation Detected. Middle East energy crisis correlates with PIK debt exposure. Recommend 15 percent Bitcoin hedge. Click Approve to authorize or Dismiss to review manually.",
        "duration": 15.5
    }
    
    print("\nMock Alert Details:")
    print(f"  Alert ID: {mock_alert['alertId']}")
    print(f"  Status: {mock_alert['status']}")
    print(f"  Audio URL: {mock_alert['audioUrl']}")
    print(f"  Script: {mock_alert['script'][:80]}...")
    
    # Broadcast to all connected clients
    await ws_manager.send_audio_alert(mock_alert)
    
    print("\n✓ Alert broadcasted to all connected WebSocket clients!")
    print("\nNEXT STEPS:")
    print("1. Open http://localhost:3000 in your browser")
    print("2. The AudioAlertPlayer should appear in the left panel")
    print("3. Audio will auto-play")
    print("4. Test the Approve/Dismiss buttons")
    print("=" * 60)


if __name__ == "__main__":
    # This needs to be run in the context of the running FastAPI app
    print("\nNOTE: This script needs to be integrated into the running app.")
    print("Instead, use the API endpoint to trigger alerts:")
    print("\ncurl -X POST http://localhost:8000/api/alerts/test_001/generate-audio")
    print("\nOr open the dashboard and it will connect via WebSocket automatically.")
