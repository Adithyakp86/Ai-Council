"""WebSocket endpoint for real-time AI Council orchestration updates."""

import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from fastapi.exceptions import WebSocketException

from app.core.security import verify_token
from app.services.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/{request_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    request_id: str,
    token: str = Query(..., description="JWT authentication token")
):
    """
    WebSocket endpoint for real-time orchestration updates.
    
    Args:
        websocket: WebSocket connection
        request_id: Unique identifier for the request
        token: JWT authentication token from query parameter
        
    Requirements:
        - 19.1: Establish WebSocket Session when request is submitted
        - 19.6: Validate authentication token from query parameter
    """
    # Validate authentication token
    payload = verify_token(token)
    if not payload:
        logger.warning(f"Invalid token for WebSocket connection to request {request_id}")
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Invalid or expired authentication token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        logger.warning(f"No user_id in token for WebSocket connection to request {request_id}")
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Invalid token payload"
        )
    
    # Connect the WebSocket
    try:
        await websocket_manager.connect(request_id, websocket, user_id)
        logger.info(f"WebSocket connected: request_id={request_id}, user_id={user_id}")
        
        # Keep connection alive and handle incoming messages
        try:
            while True:
                # Receive messages from client (e.g., acknowledgments, heartbeat responses)
                data = await websocket.receive_json()
                
                # Handle message acknowledgments
                if data.get("type") == "ack":
                    message_id = data.get("message_id")
                    if message_id:
                        await websocket_manager.acknowledge_message(request_id, message_id)
                        logger.debug(f"Message {message_id} acknowledged for request {request_id}")
                
                # Handle heartbeat responses
                elif data.get("type") == "heartbeat_response":
                    # Update last_heartbeat timestamp
                    if request_id in websocket_manager.connection_metadata:
                        from datetime import datetime
                        websocket_manager.connection_metadata[request_id]["last_heartbeat"] = datetime.utcnow()
                        logger.debug(f"Heartbeat response received for request {request_id}")
                
                # Handle reconnection requests
                elif data.get("type") == "reconnect":
                    logger.info(f"Reconnection requested for request {request_id}")
                    # Replay queued messages
                    await websocket_manager._replay_queued_messages(request_id)
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: request_id={request_id}, user_id={user_id}")
        except Exception as e:
            logger.error(f"Error in WebSocket connection for request {request_id}: {e}")
        finally:
            # Clean up connection
            await websocket_manager.disconnect(request_id)
            logger.info(f"WebSocket cleanup completed for request {request_id}")
            
    except Exception as e:
        logger.error(f"Error establishing WebSocket connection for request {request_id}: {e}")
        raise


@router.get("/ws/status")
async def websocket_status():
    """
    Get WebSocket manager status.
    
    Returns:
        Status information about active WebSocket connections
    """
    return {
        "active_connections": websocket_manager.get_active_connection_count(),
        "status": "operational"
    }
