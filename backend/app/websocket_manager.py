"""
WebSocket manager for real-time communication with frontend clients.
"""
import json
import logging
from typing import Dict, Set, Any
from datetime import datetime
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and broadcasts events to clients."""
    
    def __init__(self):
        # Store active connections
        self.active_connections: Set[WebSocket] = set()
        
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket client connected. Total connections: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket client disconnected. Total connections: {len(self.active_connections)}")
        
    async def broadcast(self, event_type: str, data: Any):
        """
        Broadcast a message to all connected clients.
        
        Args:
            event_type: Type of event (risk_update, agent_log, alert, etc.)
            data: Event data to send
        """
        if not self.active_connections:
            return
            
        message = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send to all connected clients
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to client: {e}")
                disconnected.add(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_risk_update(self, risk_assessment: Dict[str, Any]):
        """Broadcast a risk assessment update."""
        await self.broadcast("risk_update", risk_assessment)
        
    async def send_agent_log(self, agent_log: Dict[str, Any]):
        """Broadcast an agent activity log."""
        await self.broadcast("agent_log", agent_log)
        
    async def send_alert(self, alert: Dict[str, Any]):
        """Broadcast an alert."""
        await self.broadcast("alert", alert)
        
    async def send_loan_update(self, loan_data: Dict[str, Any]):
        """Broadcast a loan update."""
        await self.broadcast("loan_update", loan_data)
        
    async def send_policy_update(self, policy_data: Dict[str, Any]):
        """Broadcast a policy configuration update."""
        await self.broadcast("policy_update", policy_data)
        
    async def send_system_status(self, status_data: Dict[str, Any]):
        """Broadcast system status update."""
        await self.broadcast("system_status", status_data)
    
    async def send_audio_alert(self, audio_data: Dict[str, Any]):
        """Broadcast audio alert."""
        await self.broadcast("audio_alert", audio_data)
    
    async def send_authorization(self, auth_data: Dict[str, Any]):
        """Broadcast authorization result."""
        await self.broadcast("authorization", auth_data)
    
    async def send_hedge_executed(self, hedge_data: Dict[str, Any]):
        """Broadcast hedge execution result."""
        await self.broadcast("hedge_executed", hedge_data)


# Global WebSocket manager instance
ws_manager = WebSocketManager()
