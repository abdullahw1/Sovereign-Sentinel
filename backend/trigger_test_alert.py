"""
Script to trigger a test voice alert for demonstration.
"""
import asyncio
import requests
import json

API_BASE = "http://localhost:8000"


async def trigger_test_alert():
    """Trigger a test critical alert with voice generation."""
    
    print("=" * 60)
    print("SOVEREIGN SENTINEL - VOICE ALERT TEST")
    print("=" * 60)
    
    # Create a test alert
    alert_id = "test_critical_alert_001"
    
    print(f"\n1. Generating audio alert for: {alert_id}")
    print("-" * 60)
    
    try:
        response = requests.post(
            f"{API_BASE}/api/alerts/{alert_id}/generate-audio",
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Audio alert generated successfully!")
            print(f"  - Alert ID: {result['alertId']}")
            print(f"  - Status: {result['status']}")
            print(f"  - Audio URL: {result['audioUrl']}")
            print(f"  - Duration: {result['duration']:.2f} seconds")
            print(f"\n  Voice Script:")
            print(f"  \"{result['script']}\"")
            
            if result['status'] == 'failed':
                print(f"\n  ⚠️  Audio generation failed: {result.get('error', 'Unknown error')}")
                if result.get('fallbackResult'):
                    print(f"  ✓ Fallback notification sent: {result['fallbackResult']}")
            
            print("\n" + "=" * 60)
            print("NEXT STEPS:")
            print("=" * 60)
            print("1. Open the dashboard: http://localhost:3000")
            print("2. The audio alert should appear in the left panel")
            print("3. Audio will auto-play (check your volume!)")
            print("4. Click 'APPROVE' or 'DISMISS' to test authorization")
            print("\nThe alert has been broadcasted via WebSocket to all connected clients.")
            print("=" * 60)
            
        else:
            print(f"✗ Failed to generate audio alert: {response.status_code}")
            print(f"  Response: {response.text}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n")


if __name__ == "__main__":
    asyncio.run(trigger_test_alert())
