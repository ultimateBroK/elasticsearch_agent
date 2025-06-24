"""WebSocket handlers with proper dependency injection."""

import json
import logging
import asyncio
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect, Depends
from app.core.dependencies import get_elasticsearch_agent, get_redis_service
from app.agents.elasticsearch_agent import ElasticsearchAgent
from app.services.redis import RedisService
import uuid

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket connection manager for real-time chat."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.sessions: Dict[str, str] = {}  # session_id -> connection_id
    
    async def connect(self, websocket: WebSocket, session_id: str = None) -> str:
        """Connect a new WebSocket client."""
        await websocket.accept()
        
        connection_id = str(uuid.uuid4())
        self.active_connections[connection_id] = websocket
        
        # Associate with session
        if not session_id:
            session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = connection_id
        
        logger.info(f"WebSocket connected: {connection_id} (session: {session_id})")
        return connection_id
    
    def disconnect(self, connection_id: str):
        """Disconnect a WebSocket client."""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
            
            # Remove from sessions
            session_to_remove = None
            for session_id, conn_id in self.sessions.items():
                if conn_id == connection_id:
                    session_to_remove = session_id
                    break
            
            if session_to_remove:
                del self.sessions[session_to_remove]
            
            logger.info(f"WebSocket disconnected: {connection_id}")
    
    async def send_message(self, connection_id: str, message: dict):
        """Send message to specific connection."""
        websocket = self.active_connections.get(connection_id)
        if websocket:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to {connection_id}: {e}")
                self.disconnect(connection_id)
    
    async def send_error(self, connection_id: str, error_message: str):
        """Send error message to specific connection."""
        await self.send_message(connection_id, {
            "type": "error",
            "error": error_message
        })
    
    async def send_typing_indicator(self, connection_id: str, is_typing: bool):
        """Send typing indicator to specific connection."""
        await self.send_message(connection_id, {
            "type": "typing",
            "typing": is_typing
        })
    
    def get_session_id(self, connection_id: str) -> str:
        """Get session ID for connection."""
        for session_id, conn_id in self.sessions.items():
            if conn_id == connection_id:
                return session_id
        return None


# Global connection manager
manager = ConnectionManager()


class WebSocketHandler:
    """WebSocket handler with dependency injection."""
    
    def __init__(
        self,
        agent: ElasticsearchAgent,
        redis_service: RedisService
    ):
        self.agent = agent
        self.redis_service = redis_service
    
    async def handle_chat_message(self, connection_id: str, message_data: dict):
        """Handle chat message through the agent with enhanced error handling."""
        try:
            # Input validation
            user_message = message_data.get("message", "").strip()
            if not user_message:
                await manager.send_error(connection_id, "Empty message received")
                return
            
            if len(user_message) > 1000:  # Limit message length
                await manager.send_error(connection_id, "Message too long (max 1000 characters)")
                return
            
            session_id = manager.get_session_id(connection_id)
            if not session_id:
                await manager.send_error(connection_id, "Session not found")
                return
            
            # Send typing indicator
            await manager.send_typing_indicator(connection_id, True)
            
            # Echo user message
            await manager.send_message(connection_id, {
                "type": "message",
                "sender": "user",
                "content": user_message,
                "timestamp": message_data.get("timestamp")
            })
            
            try:
                # Process through agent with timeout protection
                agent_result = await asyncio.wait_for(
                    self.agent.process_message(
                        user_message=user_message,
                        session_id=session_id
                    ),
                    timeout=60.0  # 60 second timeout
                )
                
                # Stop typing indicator
                await manager.send_typing_indicator(connection_id, False)
                
                # Send agent response
                await manager.send_message(connection_id, {
                    "type": "message",
                    "sender": "agent",
                    "content": agent_result["response"],
                    "chart_config": agent_result.get("chart_config"),
                    "data": agent_result.get("data", []),
                    "intent": agent_result.get("intent", "general"),
                    "timestamp": None  # Let frontend set timestamp
                })
                
                # Update session in Redis (non-blocking)
                try:
                    session_data = {
                        "last_message": user_message,
                        "last_response": agent_result["response"],
                        "intent": agent_result.get("intent", "general"),
                        "connection_id": connection_id,
                        "timestamp": message_data.get("timestamp")
                    }
                    await self.redis_service.set_session(session_id, session_data)
                except Exception as redis_error:
                    logger.warning(f"Failed to update session in Redis: {redis_error}")
                    # Don't fail the whole request for Redis issues
                
            except asyncio.TimeoutError:
                await manager.send_typing_indicator(connection_id, False)
                await manager.send_error(connection_id, "Request timed out. Please try a simpler query.")
            except Exception as agent_error:
                await manager.send_typing_indicator(connection_id, False)
                logger.error(f"Agent processing failed: {agent_error}")
                await manager.send_message(connection_id, {
                    "type": "message",
                    "sender": "agent",
                    "content": "I apologize, but I encountered an issue processing your request. Please try rephrasing your question.",
                    "timestamp": None
                })
            
        except Exception as e:
            logger.error(f"Error in chat message handler: {e}")
            await manager.send_typing_indicator(connection_id, False)
            await manager.send_error(connection_id, "An unexpected error occurred")


async def handle_websocket_chat(
    websocket: WebSocket, 
    session_id: str = None,
    agent: ElasticsearchAgent = Depends(get_elasticsearch_agent),
    redis_service: RedisService = Depends(get_redis_service)
):
    """WebSocket endpoint handler with dependency injection."""
    connection_id = await manager.connect(websocket, session_id)
    handler = WebSocketHandler(agent, redis_service)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message_data = json.loads(data)
                message_type = message_data.get("type", "message")
                
                if message_type == "message":
                    await handler.handle_chat_message(connection_id, message_data)
                elif message_type == "ping":
                    await manager.send_message(connection_id, {"type": "pong"})
                else:
                    await manager.send_error(connection_id, f"Unknown message type: {message_type}")
                    
            except json.JSONDecodeError:
                await manager.send_error(connection_id, "Invalid JSON format")
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                await manager.send_error(connection_id, "Internal server error")
    
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(connection_id)