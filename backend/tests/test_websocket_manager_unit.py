"""
Unit Tests for WebSocket Manager

Tests connection establishment, message sending, broadcasting, 
reconnection, and message replay functionality.

**Validates: Requirements 19.1, 19.2, 19.3**
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import WebSocket

from app.services.websocket_manager import WebSocketManager


@pytest.mark.asyncio
async def test_connect_establishes_connection():
    """
    Test that connect() properly establishes and tracks a WebSocket connection.
    
    Validates: Requirement 19.1 - Establish WebSocket Session
    """
    manager = WebSocketManager()
    
    # Create mock WebSocket
    mock_websocket = AsyncMock(spec=WebSocket)
    mock_websocket.accept = AsyncMock()
    mock_websocket.send_json = AsyncMock()
    
    request_id = "test-request-123"
    user_id = "test-user-456"
    
    # Connect
    await manager.connect(request_id, mock_websocket, user_id)
    
    # Verify connection was accepted
    mock_websocket.accept.assert_called_once()
    
    # Verify connection is tracked
    assert manager.is_connected(request_id)
    assert request_id in manager.active_connections
    assert manager.active_connections[request_id] == mock_websocket
    
    # Verify metadata is stored
    metadata = manager.get_connection_metadata(request_id)
    assert metadata is not None
    assert metadata["user_id"] == user_id
    assert "connected_at" in metadata
    assert "last_heartbeat" in metadata
    
    # Verify connection confirmation was sent
    assert mock_websocket.send_json.call_count >= 1
    first_call = mock_websocket.send_json.call_args_list[0]
    message = first_call[0][0]
    assert message["type"] == "connection_established"


@pytest.mark.asyncio
async def test_disconnect_removes_connection():
    """
    Test that disconnect() properly removes a WebSocket connection.
    
    Validates: Requirement 19.1 - Connection cleanup
    """
    manager = WebSocketManager()
    
    # Create and connect mock WebSocket
    mock_websocket = AsyncMock(spec=WebSocket)
    mock_websocket.accept = AsyncMock()
    mock_websocket.send_json = AsyncMock()
    mock_websocket.close = AsyncMock()
    
    request_id = "test-request-disconnect"
    user_id = "test-user-disconnect"
    
    await manager.connect(request_id, mock_websocket, user_id)
    assert manager.is_connected(request_id)
    
    # Disconnect
    await manager.disconnect(request_id)
    
    # Verify connection was closed
    mock_websocket.close.assert_called_once()
    
    # Verify connection is no longer tracked
    assert not manager.is_connected(request_id)
    assert request_id not in manager.active_connections


@pytest.mark.asyncio
async def test_send_message_sends_to_active_connection():
    """
    Test that send_message() successfully sends messages to active connections.
    
    Validates: Requirement 19.1 - Message sending
    """
    manager = WebSocketManager()
    
    # Create and connect mock WebSocket
    mock_websocket = AsyncMock(spec=WebSocket)
    mock_websocket.accept = AsyncMock()
    mock_websocket.send_json = AsyncMock()
    
    request_id = "test-request-send"
    user_id = "test-user-send"
    
    await manager.connect(request_id, mock_websocket, user_id)
    
    # Send a message
    test_message = {
        "type": "test_event",
        "data": {"key": "value"}
    }
    
    result = await manager.send_message(request_id, test_message)
    
    # Verify message was sent
    assert result is True
    
    # Verify send_json was called with the message (plus message_id)
    calls = [call[0][0] for call in mock_websocket.send_json.call_args_list]
    # Find the test message (skip connection_established)
    test_messages = [msg for msg in calls if msg.get("type") == "test_event"]
    assert len(test_messages) == 1
    assert test_messages[0]["data"] == {"key": "value"}
    assert "message_id" in test_messages[0]


@pytest.mark.asyncio
async def test_send_message_queues_when_connection_inactive():
    """
    Test that send_message() queues messages when connection is not active.
    
    Validates: Requirement 19.2 - Queue messages when connection drops
    """
    manager = WebSocketManager()
    
    request_id = "test-request-queue"
    
    # Send message without active connection
    test_message = {
        "type": "queued_event",
        "data": {"queued": True}
    }
    
    result = await manager.send_message(request_id, test_message)
    
    # Verify message was not sent (no active connection)
    assert result is False
    
    # Verify message was queued
    assert request_id in manager.message_queue
    assert len(manager.message_queue[request_id]) > 0
    
    # Find the queued message
    queued_messages = [msg for msg in manager.message_queue[request_id] if msg.get("type") == "queued_event"]
    assert len(queued_messages) == 1
    assert queued_messages[0]["data"] == {"queued": True}


@pytest.mark.asyncio
async def test_broadcast_progress_sends_formatted_message():
    """
    Test that broadcast_progress() sends properly formatted orchestration messages.
    
    Validates: Requirement 19.1 - Broadcast orchestration progress
    """
    manager = WebSocketManager()
    
    # Create and connect mock WebSocket
    mock_websocket = AsyncMock(spec=WebSocket)
    mock_websocket.accept = AsyncMock()
    mock_websocket.send_json = AsyncMock()
    
    request_id = "test-request-broadcast"
    user_id = "test-user-broadcast"
    
    await manager.connect(request_id, mock_websocket, user_id)
    
    # Broadcast progress
    event_type = "analysis_complete"
    event_data = {
        "intent": "research",
        "complexity": "complex"
    }
    
    result = await manager.broadcast_progress(request_id, event_type, event_data)
    
    # Verify message was sent
    assert result is True
    
    # Verify message format
    calls = [call[0][0] for call in mock_websocket.send_json.call_args_list]
    progress_messages = [msg for msg in calls if msg.get("type") == event_type]
    assert len(progress_messages) == 1
    
    message = progress_messages[0]
    assert message["type"] == event_type
    assert "timestamp" in message
    assert message["data"] == event_data
    assert "message_id" in message


@pytest.mark.asyncio
async def test_reconnection_replays_queued_messages():
    """
    Test that reconnection replays queued messages from last acknowledged point.
    
    Validates: Requirements 19.2, 19.3 - Message replay on reconnection
    """
    manager = WebSocketManager()
    
    request_id = "test-request-replay"
    user_id = "test-user-replay"
    
    # Queue some messages (simulating disconnection)
    for i in range(3):
        await manager.send_message(request_id, {
            "type": "queued_message",
            "data": {"index": i}
        })
    
    # Verify messages were queued
    assert request_id in manager.message_queue
    assert len(manager.message_queue[request_id]) == 3
    
    # Create and connect mock WebSocket (simulating reconnection)
    mock_websocket = AsyncMock(spec=WebSocket)
    mock_websocket.accept = AsyncMock()
    mock_websocket.send_json = AsyncMock()
    
    await manager.connect(request_id, mock_websocket, user_id)
    
    # Verify queued messages were replayed
    calls = [call[0][0] for call in mock_websocket.send_json.call_args_list]
    queued_messages = [msg for msg in calls if msg.get("type") == "queued_message"]
    
    # Should have replayed all 3 queued messages
    assert len(queued_messages) == 3
    
    # Verify messages are in order
    for i, msg in enumerate(queued_messages):
        assert msg["data"]["index"] == i
    
    # Verify queue was cleared after replay
    assert len(manager.message_queue.get(request_id, [])) == 0


@pytest.mark.asyncio
async def test_acknowledge_message_updates_last_ack():
    """
    Test that acknowledge_message() properly tracks acknowledged messages.
    
    Validates: Requirement 19.3 - Resume from last acknowledged message
    """
    manager = WebSocketManager()
    
    request_id = "test-request-ack"
    
    # Acknowledge some messages
    await manager.acknowledge_message(request_id, 1)
    assert manager.last_ack[request_id] == 1
    
    await manager.acknowledge_message(request_id, 3)
    assert manager.last_ack[request_id] == 3
    
    # Acknowledging older message should not decrease last_ack
    await manager.acknowledge_message(request_id, 2)
    assert manager.last_ack[request_id] == 3


@pytest.mark.asyncio
async def test_reconnection_skips_acknowledged_messages():
    """
    Test that reconnection only replays messages after last acknowledged.
    
    Validates: Requirement 19.3 - Resume from last acknowledged message
    """
    manager = WebSocketManager()
    
    request_id = "test-request-skip-ack"
    user_id = "test-user-skip-ack"
    
    # Initialize message counter
    manager.message_counters[request_id] = 0
    
    # Queue messages with specific IDs
    for i in range(1, 6):
        message = {
            "type": "test_message",
            "data": {"index": i},
            "message_id": i
        }
        manager._queue_message(request_id, message)
    
    # Acknowledge messages 1-3
    await manager.acknowledge_message(request_id, 3)
    
    # Create and connect mock WebSocket (simulating reconnection)
    mock_websocket = AsyncMock(spec=WebSocket)
    mock_websocket.accept = AsyncMock()
    mock_websocket.send_json = AsyncMock()
    
    await manager.connect(request_id, mock_websocket, user_id)
    
    # Verify only messages 4-5 were replayed (after last ack)
    calls = [call[0][0] for call in mock_websocket.send_json.call_args_list]
    test_messages = [msg for msg in calls if msg.get("type") == "test_message"]
    
    # Should only replay messages with ID > 3
    assert len(test_messages) == 2
    assert test_messages[0]["message_id"] == 4
    assert test_messages[1]["message_id"] == 5


@pytest.mark.asyncio
async def test_get_active_connection_count():
    """
    Test that get_active_connection_count() returns correct count.
    """
    manager = WebSocketManager()
    
    # Initially no connections
    assert manager.get_active_connection_count() == 0
    
    # Add connections
    mock_websocket1 = AsyncMock(spec=WebSocket)
    mock_websocket1.accept = AsyncMock()
    mock_websocket1.send_json = AsyncMock()
    
    mock_websocket2 = AsyncMock(spec=WebSocket)
    mock_websocket2.accept = AsyncMock()
    mock_websocket2.send_json = AsyncMock()
    
    await manager.connect("request-1", mock_websocket1, "user-1")
    assert manager.get_active_connection_count() == 1
    
    await manager.connect("request-2", mock_websocket2, "user-2")
    assert manager.get_active_connection_count() == 2
    
    # Remove one connection
    await manager.disconnect("request-1")
    assert manager.get_active_connection_count() == 1


@pytest.mark.asyncio
async def test_cleanup_old_data():
    """
    Test that cleanup_old_data() removes old metadata and queues.
    """
    manager = WebSocketManager()
    
    request_id = "test-request-cleanup"
    
    # Add old metadata (25 hours ago)
    manager.connection_metadata[request_id] = {
        "user_id": "test-user",
        "connected_at": datetime.utcnow() - timedelta(hours=25),
        "last_heartbeat": datetime.utcnow() - timedelta(hours=25)
    }
    
    # Add message queue
    manager.message_queue[request_id] = [{"type": "old_message"}]
    manager.last_ack[request_id] = 5
    manager.message_counters[request_id] = 10
    
    # Run cleanup
    await manager.cleanup_old_data(max_age_hours=24)
    
    # Verify old data was removed
    assert request_id not in manager.connection_metadata
    assert request_id not in manager.message_queue
    assert request_id not in manager.last_ack
    assert request_id not in manager.message_counters


@pytest.mark.asyncio
async def test_send_message_handles_websocket_disconnect():
    """
    Test that send_message() handles WebSocketDisconnect gracefully.
    
    Validates: Requirement 19.2 - Queue messages when connection drops
    """
    from fastapi import WebSocketDisconnect
    
    manager = WebSocketManager()
    
    # Create mock WebSocket that raises WebSocketDisconnect
    mock_websocket = AsyncMock(spec=WebSocket)
    mock_websocket.accept = AsyncMock()
    mock_websocket.send_json = AsyncMock(side_effect=WebSocketDisconnect())
    mock_websocket.close = AsyncMock()
    
    request_id = "test-request-disconnect-error"
    user_id = "test-user-disconnect-error"
    
    await manager.connect(request_id, mock_websocket, user_id)
    
    # Try to send message (should handle disconnect)
    test_message = {"type": "test", "data": {}}
    result = await manager.send_message(request_id, test_message)
    
    # Verify message was not sent successfully
    assert result is False
    
    # Verify connection was removed
    assert not manager.is_connected(request_id)
    
    # Verify message was queued for replay
    assert request_id in manager.message_queue
    queued = [msg for msg in manager.message_queue[request_id] if msg.get("type") == "test"]
    assert len(queued) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
