"""Redis connection and utilities."""
import asyncio
from typing import Optional

import redis.asyncio as redis
from redis.asyncio import Redis
from redis.exceptions import ConnectionError, TimeoutError

from app.core.config import settings


class RedisClient:
    """Redis client with connection pooling and retry logic."""

    def __init__(self):
        self._client: Optional[Redis] = None
        self._max_retries = 3
        self._retry_delay = 1  # seconds

    async def connect(self) -> None:
        """Establish Redis connection with retry logic."""
        for attempt in range(self._max_retries):
            try:
                self._client = await redis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    max_connections=settings.REDIS_MAX_CONNECTIONS,
                )
                # Test connection
                await self._client.ping()
                print("Redis connection established successfully")
                return
            except (ConnectionError, TimeoutError) as e:
                if attempt < self._max_retries - 1:
                    print(f"Redis connection attempt {attempt + 1} failed: {e}")
                    await asyncio.sleep(self._retry_delay * (attempt + 1))
                else:
                    print(f"Failed to connect to Redis after {self._max_retries} attempts")
                    raise

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            print("Redis connection closed")

    @property
    def client(self) -> Redis:
        """Get Redis client instance."""
        if not self._client:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        return self._client

    # Rate limiting key structures
    def get_rate_limit_key(self, user_id: str, timestamp: int) -> str:
        """Get rate limit key for a user at a specific hour.
        
        Format: rate_limit:{user_id}:hour:{timestamp}
        """
        return f"rate_limit:{user_id}:hour:{timestamp}"

    def get_demo_rate_limit_key(self, ip_address: str, timestamp: int) -> str:
        """Get rate limit key for demo users by IP.
        
        Format: rate_limit:demo:{ip_address}:hour:{timestamp}
        """
        return f"rate_limit:demo:{ip_address}:hour:{timestamp}"

    # WebSocket session tracking keys
    def get_websocket_session_key(self, request_id: str) -> str:
        """Get WebSocket session tracking key.
        
        Format: websocket:active:{request_id}
        """
        return f"websocket:active:{request_id}"

    # Request status cache keys
    def get_request_status_key(self, request_id: str) -> str:
        """Get request status cache key.
        
        Format: request:status:{request_id}
        """
        return f"request:status:{request_id}"

    # Cost estimation cache keys
    def get_cost_estimate_key(self, content_hash: str) -> str:
        """Get cost estimation cache key.
        
        Format: cost:estimate:{content_hash}
        """
        return f"cost:estimate:{content_hash}"

    # Dashboard statistics cache keys
    def get_user_stats_key(self, user_id: str) -> str:
        """Get user statistics cache key.
        
        Format: stats:user:{user_id}
        """
        return f"stats:user:{user_id}"


# Global Redis client instance
redis_client = RedisClient()


async def get_redis() -> Redis:
    """Dependency to get Redis client."""
    return redis_client.client
