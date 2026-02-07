"""Main FastAPI application entry point."""
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import auth, websocket
from app.services.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Starts the WebSocket heartbeat loop on startup.
    """
    # Startup: Start WebSocket heartbeat loop
    logger.info("Starting WebSocket heartbeat loop...")
    heartbeat_task = asyncio.create_task(websocket_manager.heartbeat_loop())
    
    yield
    
    # Shutdown: Cancel heartbeat loop
    logger.info("Stopping WebSocket heartbeat loop...")
    heartbeat_task.cancel()
    try:
        await heartbeat_task
    except asyncio.CancelledError:
        logger.info("WebSocket heartbeat loop stopped")


app = FastAPI(
    title="AI Council API",
    description="Multi-agent AI orchestration platform",
    version="1.0.0",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(websocket.router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Council API",
        "docs": f"{settings.API_V1_PREFIX}/docs",
        "version": "1.0.0",
    }
