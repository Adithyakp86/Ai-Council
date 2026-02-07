"""WebSocket Manager for real-time communication during AI Council orchestration."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
from fastapi import WebSocket, WebSocketDisconnect
import json

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections for real-time updates during request processing."""
    
    def __init__(self):
        # Active WebSocket connections: request_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Connection metadata: request_id -> metadata dict
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Message queue for reconnection: request_id -> list of messages
        self.message_queue: Dict[str, List[Dict[str, Any]]] = {}
        
        # Last acknowledged message ID: request_id -> message_id
        self.last_ack: Dict[str, int] = {}
        
        # Message counter for tracking: request_id -> counter
        self.message_counters: Dict[str, int] = {}
        
        logger.info("WebSocketManager initialized")
    
    async def connect(self, request_id: str, websocket: WebSocket, user_id: str) -> None:
        """
        Accept and register a new WebSocket connection.
        
        Args:
            request_id: Unique identifier for the request
            websocket: WebSocket connection object
            user_id: ID of the user making the connection
        """
        try:
            await websocket.accept()
            
            self.active_connections[request_id] = websocket
            self.connection_metadata[request_id] = {
                "user_id": user_id,
                "connected_at": datetime.utcnow(),
                "last_heartbeat": datetime.utcnow(),
                "reconnection_count": 0
            }
            
            # Initialize message tracking
            if request_id not in self.message_counters:
                self.message_counters[request_id] = 0
            if request_id not in self.last_ack:
                self.last_ack[request_id] = 0
            
            logger.info(f"WebSocket connected for request {request_id}, user {user_id}")
            
            # Send connection confirmation
            await self.send_message(request_id, {
                "type": "connection_established",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "request_id": request_id,
                    "message": "WebSocket connection established"
                }
            })
            
            # Replay queued messages if this is a reconnection
            await self._replay_queued_messages(request_id)
            
        except Exception as e:
            logger.error(f"Error connecting WebSocket for request {request_id}: {e}")
            raise
    
    async def disconnect(self, request_id: str) -> None:
        """
        Remove a WebSocket connection and clean up metadata.
        
        Args:
            request_id: Unique identifier for the request
        """
        if request_id in self.active_connections:
            try:
                websocket = self.active_connections[request_id]
                await websocket.close()
            except Exception as e:
                logger.warning(f"Error closing WebSocket for request {request_id}: {e}")
            
            del self.active_connections[request_id]
            logger.info(f"WebSocket disconnected for request {request_id}")
        
        # Keep metadata and message queue for potential reconnection
        # They will be cleaned up after a timeout period
    
    async def send_message(self, request_id: str, message: Dict[str, Any]) -> bool:
        """
        Send a message to a specific WebSocket connection.
        
        Args:
            request_id: Unique identifier for the request
            message: Message dictionary to send
            
        Returns:
            True if message was sent successfully, False otherwise
        """
        # Add message ID for tracking
        self.message_counters[request_id] = self.message_counters.get(request_id, 0) + 1
        message["message_id"] = self.message_counters[request_id]
        
        if request_id in self.active_connections:
            websocket = self.active_connections[request_id]
            try:
                await websocket.send_json(message)
                logger.debug(f"Message sent to request {request_id}: {message.get('type')}")
                return True
            except WebSocketDisconnect:
                logger.warning(f"WebSocket disconnected while sending message to request {request_id}")
                await self.disconnect(request_id)
                # Queue message for replay on reconnection
                self._queue_message(request_id, message)
                return False
            except Exception as e:
                logger.error(f"Error sending message to request {request_id}: {e}")
                await self.disconnect(request_id)
                # Queue message for replay on reconnection
                self._queue_message(request_id, message)
                return False
        else:
            # Connection not active, queue message for potential reconnection
            logger.debug(f"Connection not active for request {request_id}, queuing message")
            self._queue_message(request_id, message)
            return False
    
    async def broadcast_progress(
        self, 
        request_id: str, 
        event_type: str, 
        data: Dict[str, Any]
    ) -> bool:
        """
        Broadcast orchestration progress to connected client.
        
        Args:
            request_id: Unique identifier for the request
            event_type: Type of orchestration event (e.g., "analysis_complete")
            data: Event data dictionary
            
        Returns:
            True if message was sent successfully, False otherwise
        """
        message = {
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        return await self.send_message(request_id, message)
    
    def _queue_message(self, request_id: str, message: Dict[str, Any]) -> None:
        """
        Queue a message for replay when connection is re-established.
        
        Args:
            request_id: Unique identifier for the request
            message: Message to queue
        """
        if request_id not in self.message_queue:
            self.message_queue[request_id] = []
        
        self.message_queue[request_id].append(message)
        logger.debug(f"Message queued for request {request_id}, queue size: {len(self.message_queue[request_id])}")
    
    async def _replay_queued_messages(self, request_id: str) -> None:
        """
        Replay queued messages after reconnection.
        
        Args:
            request_id: Unique identifier for the request
        """
        if request_id not in self.message_queue:
            return
        
        queued_messages = self.message_queue[request_id]
        last_ack_id = self.last_ack.get(request_id, 0)
        
        # Filter messages that haven't been acknowledged
        messages_to_replay = [
            msg for msg in queued_messages 
            if msg.get("message_id", 0) > last_ack_id
        ]
        
        if messages_to_replay:
            logger.info(f"Replaying {len(messages_to_replay)} queued messages for request {request_id}")
            
            for message in messages_to_replay:
                if request_id in self.active_connections:
                    try:
                        await self.active_connections[request_id].send_json(message)
                    except Exception as e:
                        logger.error(f"Error replaying message for request {request_id}: {e}")
                        break
            
            # Clear replayed messages
            self.message_queue[request_id] = []
    
    async def acknowledge_message(self, request_id: str, message_id: int) -> None:
        """
        Mark a message as acknowledged by the client.
        
        Args:
            request_id: Unique identifier for the request
            message_id: ID of the acknowledged message
        """
        self.last_ack[request_id] = max(self.last_ack.get(request_id, 0), message_id)
        logger.debug(f"Message {message_id} acknowledged for request {request_id}")
    
    async def heartbeat_loop(self) -> None:
        """
        Send periodic heartbeat messages to keep connections alive.
        Disconnects inactive connections after 5 minutes.
        """
        logger.info("Starting WebSocket heartbeat loop")
        
        while True:
            try:
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                
                current_time = datetime.utcnow()
                inactive_timeout = timedelta(minutes=5)
                
                # Create a list of request_ids to avoid modifying dict during iteration
                request_ids = list(self.active_connections.keys())
                
                for request_id in request_ids:
                    if request_id not in self.connection_metadata:
                        continue
                    
                    metadata = self.connection_metadata[request_id]
                    last_heartbeat = metadata.get("last_heartbeat")
                    
                    # Check if connection is inactive
                    if last_heartbeat and (current_time - last_heartbeat) > inactive_timeout:
                        logger.warning(f"Disconnecting inactive connection for request {request_id}")
                        await self.disconnect(request_id)
                        continue
                    
                    # Send heartbeat
                    if request_id in self.active_connections:
                        try:
                            await self.active_connections[request_id].send_json({
                                "type": "heartbeat",
                                "timestamp": current_time.isoformat()
                            })
                            metadata["last_heartbeat"] = current_time
                            logger.debug(f"Heartbeat sent to request {request_id}")
                        except WebSocketDisconnect:
                            logger.warning(f"WebSocket disconnected during heartbeat for request {request_id}")
                            await self.disconnect(request_id)
                        except Exception as e:
                            logger.error(f"Error sending heartbeat to request {request_id}: {e}")
                            await self.disconnect(request_id)
                
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
                # Continue the loop even if there's an error
                await asyncio.sleep(5)
    
    def get_active_connection_count(self) -> int:
        """
        Get the number of active WebSocket connections.
        
        Returns:
            Number of active connections
        """
        return len(self.active_connections)
    
    def is_connected(self, request_id: str) -> bool:
        """
        Check if a WebSocket connection is active for a request.
        
        Args:
            request_id: Unique identifier for the request
            
        Returns:
            True if connection is active, False otherwise
        """
        return request_id in self.active_connections
    
    def get_connection_metadata(self, request_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a WebSocket connection.
        
        Args:
            request_id: Unique identifier for the request
            
        Returns:
            Connection metadata dictionary or None if not found
        """
        return self.connection_metadata.get(request_id)
    
    async def cleanup_old_data(self, max_age_hours: int = 24) -> None:
        """
        Clean up old connection metadata and message queues.
        
        Args:
            max_age_hours: Maximum age in hours for data to keep
        """
        current_time = datetime.utcnow()
        max_age = timedelta(hours=max_age_hours)
        
        # Clean up old metadata
        request_ids_to_remove = []
        for request_id, metadata in self.connection_metadata.items():
            if request_id not in self.active_connections:
                connected_at = metadata.get("connected_at")
                if connected_at and (current_time - connected_at) > max_age:
                    request_ids_to_remove.append(request_id)
        
        for request_id in request_ids_to_remove:
            del self.connection_metadata[request_id]
            if request_id in self.message_queue:
                del self.message_queue[request_id]
            if request_id in self.last_ack:
                del self.last_ack[request_id]
            if request_id in self.message_counters:
                del self.message_counters[request_id]
            logger.info(f"Cleaned up old data for request {request_id}")


# Global WebSocket manager instance
websocket_manager = WebSocketManager()
