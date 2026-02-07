# 🚀 AI Council - Complete Production Deployment Plan

## 📋 Table of Contents
1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Backend Implementation](#backend-implementation)
5. [Frontend Implementation](#frontend-implementation)
6. [API Design](#api-design)
7. [Database Schema](#database-schema)
8. [Authentication & Authorization](#authentication--authorization)
9. [AI Model Integration](#ai-model-integration)
10. [Deployment Strategy](#deployment-strategy)
11. [Cost Analysis](#cost-analysis)
12. [Implementation Timeline](#implementation-timeline)
13. [Testing Strategy](#testing-strategy)
14. [Monitoring & Analytics](#monitoring--analytics)
15. [Security Considerations](#security-considerations)

---

## 🎯 Executive Summary

### Project Goal
Transform AI Council into a fully functional, multi-user web application where users can:
- Submit complex queries through a beautiful web interface
- Watch AI Council orchestrate multiple AI models in real-time
- See detailed breakdowns of how tasks are decomposed and processed
- View cost estimates, confidence scores, and execution metadata
- Access via any device (desktop, tablet, mobile)

### Key Features
- ✅ Multi-user support with authentication
- ✅ Real-time AI orchestration visualization
- ✅ Beautiful, modern UI with dark/light themes
- ✅ Usage tracking and analytics dashboard
- ✅ API access for developers
- ✅ Free tier + paid plans
- ✅ Real AI models (no mocks)
- ✅ Scalable cloud deployment

### Target Users
1. **Developers**: Testing multi-agent AI orchestration
2. **Researchers**: Analyzing AI model coordination
3. **Businesses**: Complex decision-making support
4. **Students**: Learning about AI systems

---

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND LAYER                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Next.js    │  │   React UI   │  │   Tailwind   │         │
│  │   (SSR/SSG)  │  │  Components  │  │     CSS      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│         │                  │                  │                  │
│         └──────────────────┴──────────────────┘                 │
│                            │                                     │
│                    ┌───────▼────────┐                          │
│                    │   API Client   │                          │
│                    │  (Axios/Fetch) │                          │
│                    └───────┬────────┘                          │
└────────────────────────────┼─────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   API Gateway   │
                    │  (Rate Limiting,│
                    │   Auth, CORS)   │
                    └────────┬────────┘
                             │
┌────────────────────────────┼─────────────────────────────────┐
│                    BACKEND LAYER                               │
│                    ┌────────▼────────┐                        │
│                    │   FastAPI App   │                        │
│                    │  (REST + WS)    │                        │
│                    └────────┬────────┘                        │
│                             │                                  │
│         ┌───────────────────┼───────────────────┐            │
│         │                   │                   │            │
│  ┌──────▼──────┐   ┌───────▼────────┐  ┌──────▼──────┐    │
│  │   Auth      │   │  AI Council    │  │   User      │    │
│  │   Service   │   │  Orchestrator  │  │   Service   │    │
│  └─────────────┘   └───────┬────────┘  └─────────────┘    │
│                             │                                  │
│         ┌───────────────────┼───────────────────┐            │
│         │                   │                   │            │
│  ┌──────▼──────┐   ┌───────▼────────┐  ┌──────▼──────┐    │
│  │  Analysis   │   │    Routing     │  │  Execution  │    │
│  │   Layer     │   │     Layer      │  │    Layer    │    │
│  └─────────────┘   └────────────────┘  └──────┬──────┘    │
│                                                 │            │
│                                         ┌───────▼────────┐  │
│                                         │  Arbitration   │  │
│                                         │  & Synthesis   │  │
│                                         └───────┬────────┘  │
└─────────────────────────────────────────────────┼──────────┘
                                                  │
┌─────────────────────────────────────────────────┼──────────┐
│                    AI MODEL LAYER                │          │
│                                                  │          │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────▼───────┐ │
│  │  Groq API    │  │ Together.ai  │  │  OpenRouter     │ │
│  │  (Llama 3)   │  │  (Mixtral)   │  │  (Multiple)     │ │
│  └──────────────┘  └──────────────┘  └─────────────────┘ │
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │  Hugging     │  │   Replicate  │  │   Anthropic     │ │
│  │  Face API    │  │     API      │  │   (Optional)    │ │
│  └──────────────┘  └──────────────┘  └─────────────────┘ │
└────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────┼─────────────────────────────────┐
│                    DATA LAYER                                 │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │  PostgreSQL  │  │    Redis     │  │   S3/Storage    │   │
│  │  (Main DB)   │  │   (Cache)    │  │   (Logs/Files)  │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
└───────────────────────────────────────────────────────────────┘
```

### Data Flow Diagram

```
User Request Flow:
─────────────────

1. User submits query via Web UI
   │
   ▼
2. Frontend validates input & shows loading state
   │
   ▼
3. API call to /api/v1/council/process
   │
   ▼
4. FastAPI receives request
   │
   ├─▶ Authenticate user (JWT)
   ├─▶ Check rate limits (Redis)
   ├─▶ Validate input
   └─▶ Create request record (PostgreSQL)
   │
   ▼
5. AI Council Orchestrator starts processing
   │
   ├─▶ Analysis Layer: Understand intent
   ├─▶ Decomposition: Break into subtasks
   ├─▶ Routing: Select best models
   ├─▶ Execution: Call AI APIs (parallel)
   ├─▶ Arbitration: Resolve conflicts
   └─▶ Synthesis: Create final response
   │
   ▼
6. WebSocket updates sent to frontend (real-time)
   │
   ├─▶ "Analyzing your request..."
   ├─▶ "Created 3 subtasks..."
   ├─▶ "Executing with Llama 3 & Mixtral..."
   ├─▶ "Arbitrating responses..."
   └─▶ "Synthesizing final answer..."
   │
   ▼
7. Final response returned
   │
   ├─▶ Save to database
   ├─▶ Update usage metrics
   ├─▶ Send to frontend
   └─▶ Log for analytics
   │
   ▼
8. Frontend displays beautiful result
   │
   ├─▶ Main response content
   ├─▶ Confidence score visualization
   ├─▶ Cost breakdown
   ├─▶ Models used
   ├─▶ Execution timeline
   └─▶ Subtask details (expandable)
```

---

## 🛠️ Technology Stack

### Frontend Stack
```yaml
Framework: Next.js 14 (App Router)
  - Server-side rendering for SEO
  - API routes for backend proxy
  - Static generation for landing pages
  
UI Library: React 18
  - Hooks for state management
  - Context API for global state
  - React Query for data fetching

Styling: Tailwind CSS + shadcn/ui
  - Utility-first CSS
  - Pre-built components
  - Dark mode support
  - Responsive design

State Management:
  - Zustand (lightweight, simple)
  - React Query (server state)
  
Real-time: Socket.io Client
  - WebSocket connections
  - Real-time updates
  - Reconnection handling

Charts/Viz: Recharts + Framer Motion
  - Beautiful charts
  - Smooth animations
  - Interactive visualizations

Forms: React Hook Form + Zod
  - Type-safe validation
  - Performance optimized
  - Error handling
```

### Backend Stack
```yaml
Framework: FastAPI
  - Async/await support
  - Auto-generated OpenAPI docs
  - Type hints with Pydantic
  - WebSocket support
  
Database: PostgreSQL 15
  - Relational data
  - JSONB for flexible schemas
  - Full-text search
  - Robust transactions

Cache: Redis 7
  - Session storage
  - Rate limiting
  - Response caching
  - Real-time pub/sub

ORM: SQLAlchemy 2.0
  - Async support
  - Type-safe queries
  - Migration management (Alembic)

Authentication: JWT + OAuth2
  - Secure token-based auth
  - Refresh tokens
  - Social login (Google, GitHub)

Task Queue: Celery + Redis
  - Background jobs
  - Scheduled tasks
  - Retry logic

API Clients:
  - httpx (async HTTP)
  - openai (OpenAI SDK)
  - anthropic (Anthropic SDK)
```

### DevOps Stack
```yaml
Hosting:
  - Frontend: Vercel (free tier → $20/mo)
  - Backend: Railway.app ($5-20/mo) or Render.com
  - Database: Railway PostgreSQL or Supabase
  - Redis: Upstash (free tier → $10/mo)

CI/CD:
  - GitHub Actions (free)
  - Automated testing
  - Automated deployment

Monitoring:
  - Sentry (error tracking - free tier)
  - PostHog (analytics - free tier)
  - Better Stack (logging - free tier)

Domain & SSL:
  - Namecheap/Cloudflare ($10-15/year)
  - Free SSL via Cloudflare
```

---


## 🔧 Backend Implementation

### Project Structure
```
ai_council/
├── api/                          # FastAPI application
│   ├── __init__.py
│   ├── main.py                   # FastAPI app entry point
│   ├── dependencies.py           # Dependency injection
│   ├── middleware.py             # CORS, logging, etc.
│   │
│   ├── routes/                   # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py              # /api/v1/auth/*
│   │   ├── council.py           # /api/v1/council/*
│   │   ├── users.py             # /api/v1/users/*
│   │   ├── history.py           # /api/v1/history/*
│   │   └── admin.py             # /api/v1/admin/*
│   │
│   ├── schemas/                  # Pydantic models
│   │   ├── __init__.py
│   │   ├── auth.py              # Login, Register, Token
│   │   ├── council.py           # Request, Response models
│   │   ├── user.py              # User profile models
│   │   └── common.py            # Shared models
│   │
│   ├── services/                 # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py      # Authentication logic
│   │   ├── council_service.py   # AI Council orchestration
│   │   ├── user_service.py      # User management
│   │   └── billing_service.py   # Usage tracking, billing
│   │
│   ├── models/                   # Database models
│   │   ├── __init__.py
│   │   ├── user.py              # User table
│   │   ├── request.py           # Request history
│   │   ├── usage.py             # Usage metrics
│   │   └── subscription.py      # Subscription plans
│   │
│   ├── websocket/                # WebSocket handlers
│   │   ├── __init__.py
│   │   ├── manager.py           # Connection manager
│   │   └── handlers.py          # Event handlers
│   │
│   └── utils/                    # Utilities
│       ├── __init__.py
│       ├── security.py          # Password hashing, JWT
│       ├── rate_limit.py        # Rate limiting
│       └── validators.py        # Input validation
│
├── core/                         # Existing AI Council core
│   ├── models.py
│   ├── interfaces.py
│   └── ...
│
├── execution/                    # AI model integrations
│   ├── groq_model.py            # Groq API integration
│   ├── together_model.py        # Together.ai integration
│   ├── openrouter_model.py      # OpenRouter integration
│   └── huggingface_model.py     # HuggingFace integration
│
├── database/                     # Database setup
│   ├── __init__.py
│   ├── session.py               # DB session management
│   └── migrations/              # Alembic migrations
│
└── config/                       # Configuration
    ├── __init__.py
    ├── settings.py              # Environment variables
    └── ai_models.yaml           # AI model configurations
```

### FastAPI Main Application (api/main.py)
```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import logging

from .routes import auth, council, users, history, admin
from .websocket.manager import ConnectionManager
from .middleware import LoggingMiddleware, RateLimitMiddleware
from .database.session import init_db
from .config.settings import settings

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# WebSocket connection manager
ws_manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    logger.info("🚀 Starting AI Council API...")
    await init_db()
    logger.info("✅ Database initialized")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down AI Council API...")
    await ws_manager.disconnect_all()
    logger.info("✅ Cleanup complete")

# Create FastAPI app
app = FastAPI(
    title="AI Council API",
    description="Multi-Agent AI Orchestration System",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(council.router, prefix="/api/v1/council", tags=["AI Council"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(history.router, prefix="/api/v1/history", tags=["History"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Council API",
        "version": "2.0.0",
        "docs": "/api/docs",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected"
    }

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time updates."""
    await ws_manager.connect(websocket, client_id)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back for heartbeat
            await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        ws_manager.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
```

### Council API Route (api/routes/council.py)
```python
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Optional
import asyncio

from ..schemas.council import (
    CouncilRequest, CouncilResponse, EstimateRequest, EstimateResponse
)
from ..services.council_service import CouncilService
from ..services.auth_service import get_current_user
from ..models.user import User
from ..websocket.manager import ws_manager

router = APIRouter()

@router.post("/process", response_model=CouncilResponse)
async def process_request(
    request: CouncilRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    council_service: CouncilService = Depends()
):
    """
    Process a user request through AI Council.
    
    This endpoint:
    1. Validates the request
    2. Checks user's rate limits and quota
    3. Processes through AI Council orchestration
    4. Returns structured response with metadata
    5. Sends real-time updates via WebSocket
    """
    
    # Check user quota
    if not await council_service.check_user_quota(current_user.id):
        raise HTTPException(
            status_code=429,
            detail="Monthly quota exceeded. Please upgrade your plan."
        )
    
    # Send initial WebSocket update
    await ws_manager.send_personal_message(
        current_user.id,
        {
            "type": "status",
            "message": "Starting AI Council orchestration...",
            "stage": "initializing"
        }
    )
    
    # Process request
    try:
        response = await council_service.process_request(
            user_id=current_user.id,
            content=request.content,
            execution_mode=request.execution_mode,
            websocket_callback=lambda msg: ws_manager.send_personal_message(
                current_user.id, msg
            )
        )
        
        # Track usage in background
        background_tasks.add_task(
            council_service.track_usage,
            current_user.id,
            response
        )
        
        return response
        
    except Exception as e:
        await ws_manager.send_personal_message(
            current_user.id,
            {
                "type": "error",
                "message": f"Error: {str(e)}",
                "stage": "failed"
            }
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/estimate", response_model=EstimateResponse)
async def estimate_cost(
    request: EstimateRequest,
    current_user: User = Depends(get_current_user),
    council_service: CouncilService = Depends()
):
    """
    Estimate cost and time for a request without executing it.
    """
    estimate = await council_service.estimate_request(
        content=request.content,
        execution_mode=request.execution_mode
    )
    return estimate

@router.get("/status/{request_id}")
async def get_request_status(
    request_id: str,
    current_user: User = Depends(get_current_user),
    council_service: CouncilService = Depends()
):
    """
    Get the status of a processing request.
    """
    status = await council_service.get_request_status(
        request_id=request_id,
        user_id=current_user.id
    )
    
    if not status:
        raise HTTPException(status_code=404, detail="Request not found")
    
    return status

@router.get("/models")
async def list_available_models(
    current_user: User = Depends(get_current_user)
):
    """
    List all available AI models and their capabilities.
    """
    return {
        "models": [
            {
                "id": "groq-llama3-70b",
                "name": "Llama 3 70B (Groq)",
                "provider": "Groq",
                "capabilities": ["reasoning", "code", "creative"],
                "speed": "very_fast",
                "cost_per_1k_tokens": 0.0001,
                "available": True
            },
            {
                "id": "together-mixtral-8x7b",
                "name": "Mixtral 8x7B",
                "provider": "Together.ai",
                "capabilities": ["reasoning", "multilingual"],
                "speed": "fast",
                "cost_per_1k_tokens": 0.0002,
                "available": True
            },
            {
                "id": "openrouter-claude-3",
                "name": "Claude 3 Sonnet",
                "provider": "OpenRouter",
                "capabilities": ["reasoning", "research", "analysis"],
                "speed": "medium",
                "cost_per_1k_tokens": 0.003,
                "available": True
            }
        ]
    }
```

### Database Models (api/models/user.py)
```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..database.session import Base

class SubscriptionTier(enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    
    # Subscription
    subscription_tier = Column(
        Enum(SubscriptionTier),
        default=SubscriptionTier.FREE,
        nullable=False
    )
    subscription_expires_at = Column(DateTime, nullable=True)
    
    # Usage tracking
    monthly_requests = Column(Integer, default=0)
    total_requests = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    requests = relationship("Request", back_populates="user")
    usage_records = relationship("UsageRecord", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username}>"
    
    @property
    def quota_limit(self):
        """Get monthly request quota based on subscription tier."""
        quotas = {
            SubscriptionTier.FREE: 50,
            SubscriptionTier.PRO: 1000,
            SubscriptionTier.ENTERPRISE: 10000
        }
        return quotas.get(self.subscription_tier, 50)
    
    @property
    def has_quota_remaining(self):
        """Check if user has remaining quota."""
        return self.monthly_requests < self.quota_limit
```

### AI Model Integration (execution/groq_model.py)
```python
import os
from groq import Groq
from typing import Dict, Any, Optional
import logging

from ..core.interfaces import AIModel, ModelError

logger = logging.getLogger(__name__)

class GroqModel(AIModel):
    """
    Real AI model using Groq API.
    
    Groq provides ultra-fast inference for open-source models.
    Free tier: 14,400 requests/day
    """
    
    def __init__(
        self,
        model_name: str = "llama3-70b-8192",
        api_key: Optional[str] = None
    ):
        self.model_name = model_name
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment")
        
        self.client = Groq(api_key=self.api_key)
        self.request_count = 0
        
        logger.info(f"Initialized Groq model: {model_name}")
    
    def generate_response(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate response using Groq API.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 - 2.0)
            
        Returns:
            Generated response text
            
        Raises:
            ModelError: If API call fails
        """
        try:
            self.request_count += 1
            
            logger.info(f"Groq API call #{self.request_count} to {self.model_name}")
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant that provides accurate, well-reasoned responses."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=kwargs.get("top_p", 1.0),
                stream=False
            )
            
            content = response.choices[0].message.content
            
            logger.info(f"Groq response received: {len(content)} chars")
            
            return content
            
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            raise ModelError(
                model_id=self.get_model_id(),
                error_message=str(e),
                error_type=type(e).__name__
            )
    
    def get_model_id(self) -> str:
        """Get unique model identifier."""
        return f"groq-{self.model_name}"
    
    def get_cost_per_token(self) -> float:
        """Get cost per token for this model."""
        # Groq pricing (as of 2024)
        pricing = {
            "llama3-70b-8192": 0.00000059,  # $0.59 per 1M tokens
            "llama3-8b-8192": 0.00000005,   # $0.05 per 1M tokens
            "mixtral-8x7b-32768": 0.00000024 # $0.24 per 1M tokens
        }
        return pricing.get(self.model_name, 0.0001)
```

---


## 🎨 Frontend Implementation

### Project Structure
```
frontend/
├── app/                          # Next.js 14 App Router
│   ├── layout.tsx               # Root layout
│   ├── page.tsx                 # Landing page
│   ├── globals.css              # Global styles
│   │
│   ├── (auth)/                  # Auth routes
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── register/
│   │   │   └── page.tsx
│   │   └── forgot-password/
│   │       └── page.tsx
│   │
│   ├── (dashboard)/             # Protected routes
│   │   ├── layout.tsx           # Dashboard layout
│   │   ├── dashboard/
│   │   │   └── page.tsx         # Main dashboard
│   │   ├── playground/
│   │   │   └── page.tsx         # AI Council playground
│   │   ├── history/
│   │   │   └── page.tsx         # Request history
│   │   ├── analytics/
│   │   │   └── page.tsx         # Usage analytics
│   │   └── settings/
│   │       └── page.tsx         # User settings
│   │
│   └── api/                     # API routes (proxy)
│       └── [...path]/
│           └── route.ts
│
├── components/                   # React components
│   ├── ui/                      # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   ├── dialog.tsx
│   │   └── ...
│   │
│   ├── layout/                  # Layout components
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   ├── Footer.tsx
│   │   └── DashboardLayout.tsx
│   │
│   ├── council/                 # AI Council specific
│   │   ├── CouncilPlayground.tsx
│   │   ├── RequestForm.tsx
│   │   ├── ResponseDisplay.tsx
│   │   ├── ExecutionTimeline.tsx
│   │   ├── SubtaskCard.tsx
│   │   ├── ModelBadge.tsx
│   │   └── ConfidenceScore.tsx
│   │
│   ├── charts/                  # Data visualization
│   │   ├── UsageChart.tsx
│   │   ├── CostChart.tsx
│   │   └── PerformanceChart.tsx
│   │
│   └── common/                  # Shared components
│       ├── LoadingSpinner.tsx
│       ├── ErrorBoundary.tsx
│       ├── Toast.tsx
│       └── ConfirmDialog.tsx
│
├── lib/                         # Utilities
│   ├── api-client.ts           # API client (axios)
│   ├── websocket.ts            # WebSocket client
│   ├── auth.ts                 # Auth utilities
│   ├── utils.ts                # Helper functions
│   └── constants.ts            # Constants
│
├── hooks/                       # Custom React hooks
│   ├── useAuth.ts              # Authentication hook
│   ├── useCouncil.ts           # AI Council hook
│   ├── useWebSocket.ts         # WebSocket hook
│   └── useLocalStorage.ts      # Local storage hook
│
├── store/                       # State management (Zustand)
│   ├── authStore.ts            # Auth state
│   ├── councilStore.ts         # Council state
│   └── uiStore.ts              # UI state (theme, etc.)
│
├── types/                       # TypeScript types
│   ├── api.ts                  # API types
│   ├── council.ts              # Council types
│   └── user.ts                 # User types
│
└── styles/                      # Additional styles
    └── animations.css          # Custom animations
```

### Main Playground Component (components/council/CouncilPlayground.tsx)
```typescript
'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Sparkles, Loader2, AlertCircle } from 'lucide-react';
import { useCouncil } from '@/hooks/useCouncil';
import { useWebSocket } from '@/hooks/useWebSocket';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select } from '@/components/ui/select';
import { ResponseDisplay } from './ResponseDisplay';
import { ExecutionTimeline } from './ExecutionTimeline';
import { SubtaskCard } from './SubtaskCard';

export function CouncilPlayground() {
  const [input, setInput] = useState('');
  const [executionMode, setExecutionMode] = useState('balanced');
  const [isProcessing, setIsProcessing] = useState(false);
  
  const { processRequest, estimate, response, error } = useCouncil();
  const { messages, isConnected } = useWebSocket();
  
  const [stages, setStages] = useState<string[]>([]);
  const [currentStage, setCurrentStage] = useState('');
  
  // Listen to WebSocket updates
  useEffect(() => {
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      
      if (lastMessage.type === 'status') {
        setCurrentStage(lastMessage.stage);
        setStages(prev => [...prev, lastMessage.message]);
      }
    }
  }, [messages]);
  
  const handleSubmit = async () => {
    if (!input.trim()) return;
    
    setIsProcessing(true);
    setStages([]);
    setCurrentStage('initializing');
    
    try {
      await processRequest({
        content: input,
        execution_mode: executionMode
      });
    } catch (err) {
      console.error('Error processing request:', err);
    } finally {
      setIsProcessing(false);
    }
  };
  
  const handleEstimate = async () => {
    if (!input.trim()) return;
    
    const estimation = await estimate({
      content: input,
      execution_mode: executionMode
    });
    
    // Show estimation in a dialog
    console.log('Estimation:', estimation);
  };
  
  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Header */}
      <div className="mb-8 text-center">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="inline-flex items-center gap-2 mb-4"
        >
          <Sparkles className="w-8 h-8 text-purple-500" />
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            AI Council Playground
          </h1>
        </motion.div>
        <p className="text-gray-600 dark:text-gray-400">
          Experience multi-agent AI orchestration in action
        </p>
      </div>
      
      {/* Input Section */}
      <Card className="p-6 mb-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Your Request
            </label>
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask me anything complex... I'll coordinate multiple AI models to give you the best answer."
              className="min-h-[120px] resize-none"
              disabled={isProcessing}
            />
          </div>
          
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <label className="block text-sm font-medium mb-2">
                Execution Mode
              </label>
              <Select
                value={executionMode}
                onValueChange={setExecutionMode}
                disabled={isProcessing}
              >
                <option value="fast">⚡ Fast (Quick & Cost-Effective)</option>
                <option value="balanced">⚖️ Balanced (Recommended)</option>
                <option value="best_quality">💎 Best Quality (Thorough)</option>
              </Select>
            </div>
            
            <div className="flex gap-2 items-end">
              <Button
                variant="outline"
                onClick={handleEstimate}
                disabled={isProcessing || !input.trim()}
              >
                Estimate Cost
              </Button>
              
              <Button
                onClick={handleSubmit}
                disabled={isProcessing || !input.trim()}
                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4 mr-2" />
                    Process Request
                  </>
                )}
              </Button>
            </div>
          </div>
          
          {/* WebSocket Status */}
          <div className="flex items-center gap-2 text-sm">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="text-gray-600 dark:text-gray-400">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
      </Card>
      
      {/* Processing Stages */}
      <AnimatePresence>
        {isProcessing && stages.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-6"
          >
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Processing Pipeline</h3>
              <ExecutionTimeline stages={stages} currentStage={currentStage} />
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Error Display */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <Card className="p-4 border-red-500 bg-red-50 dark:bg-red-900/20">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-500 mt-0.5" />
              <div>
                <h4 className="font-semibold text-red-700 dark:text-red-400">
                  Error Processing Request
                </h4>
                <p className="text-sm text-red-600 dark:text-red-300 mt-1">
                  {error}
                </p>
              </div>
            </div>
          </Card>
        </motion.div>
      )}
      
      {/* Response Display */}
      {response && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <ResponseDisplay response={response} />
          
          {/* Subtasks */}
          {response.subtasks && response.subtasks.length > 0 && (
            <div>
              <h3 className="text-xl font-semibold mb-4">
                Task Breakdown ({response.subtasks.length} subtasks)
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {response.subtasks.map((subtask, index) => (
                  <SubtaskCard key={index} subtask={subtask} index={index} />
                ))}
              </div>
            </div>
          )}
          
          {/* Metadata */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Execution Details</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Models Used
                </p>
                <p className="text-lg font-semibold">
                  {response.models_used?.length || 0}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Execution Time
                </p>
                <p className="text-lg font-semibold">
                  {response.execution_metadata?.total_execution_time?.toFixed(2)}s
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Total Cost
                </p>
                <p className="text-lg font-semibold">
                  ${response.cost_breakdown?.total_cost?.toFixed(4)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Confidence
                </p>
                <p className="text-lg font-semibold">
                  {(response.overall_confidence * 100).toFixed(0)}%
                </p>
              </div>
            </div>
          </Card>
        </motion.div>
      )}
      
      {/* Example Prompts */}
      {!response && !isProcessing && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Try These Examples</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {[
              "Analyze the pros and cons of renewable energy adoption",
              "Write a Python function to implement binary search with error handling",
              "Compare the economic policies of different countries",
              "Debug this code: [paste your code here]",
              "Research the latest developments in quantum computing",
              "Create a marketing strategy for a new tech startup"
            ].map((example, index) => (
              <Button
                key={index}
                variant="outline"
                className="text-left justify-start h-auto py-3"
                onClick={() => setInput(example)}
              >
                <span className="text-sm">{example}</span>
              </Button>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
```

### Response Display Component (components/council/ResponseDisplay.tsx)
```typescript
'use client';

import { motion } from 'framer-motion';
import { CheckCircle, TrendingUp, Clock, DollarSign } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import ReactMarkdown from 'react-markdown';

interface ResponseDisplayProps {
  response: {
    content: string;
    overall_confidence: number;
    models_used: string[];
    execution_metadata?: {
      total_execution_time: number;
    };
    cost_breakdown?: {
      total_cost: number;
    };
  };
}

export function ResponseDisplay({ response }: ResponseDisplayProps) {
  const confidenceColor = 
    response.overall_confidence >= 0.8 ? 'text-green-600' :
    response.overall_confidence >= 0.6 ? 'text-yellow-600' :
    'text-red-600';
  
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="p-6 border-2 border-purple-200 dark:border-purple-800">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-6 h-6 text-green-500" />
            <h2 className="text-2xl font-bold">AI Council Response</h2>
          </div>
          
          <div className="flex items-center gap-2">
            {response.models_used?.map((model, index) => (
              <Badge key={index} variant="secondary">
                {model}
              </Badge>
            ))}
          </div>
        </div>
        
        {/* Confidence Score */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Confidence Score</span>
            <span className={`text-lg font-bold ${confidenceColor}`}>
              {(response.overall_confidence * 100).toFixed(0)}%
            </span>
          </div>
          <Progress 
            value={response.overall_confidence * 100} 
            className="h-2"
          />
        </div>
        
        {/* Main Content */}
        <div className="prose dark:prose-invert max-w-none mb-6">
          <ReactMarkdown>{response.content}</ReactMarkdown>
        </div>
        
        {/* Metadata Footer */}
        <div className="flex items-center gap-6 pt-4 border-t text-sm text-gray-600 dark:text-gray-400">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4" />
            <span>
              {response.execution_metadata?.total_execution_time?.toFixed(2)}s
            </span>
          </div>
          
          <div className="flex items-center gap-2">
            <DollarSign className="w-4 h-4" />
            <span>
              ${response.cost_breakdown?.total_cost?.toFixed(4)}
            </span>
          </div>
          
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4" />
            <span>
              {response.models_used?.length} models coordinated
            </span>
          </div>
        </div>
      </Card>
    </motion.div>
  );
}
```

---

