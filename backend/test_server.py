"""Quick test server for development - uses SQLite instead of PostgreSQL."""
import os
import sys

# Set environment variables for testing
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"  # Optional for auth testing
os.environ["SECRET_KEY"] = "test-secret-key-for-development-only"
os.environ["DEBUG"] = "true"

# Import after setting env vars
import uvicorn
from app.main import app
from app.core.database import sync_engine
from app.models.base import Base

# Create tables
print("Creating database tables...")
Base.metadata.create_all(bind=sync_engine)
print("Database tables created!")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 AI Council Backend Test Server")
    print("="*60)
    print("\n📍 Server running at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/api/v1/docs")
    print("📖 Alternative Docs: http://localhost:8000/api/v1/redoc")
    print("\n🔐 Available Endpoints:")
    print("  POST /api/v1/auth/register - Register new user")
    print("  POST /api/v1/auth/login - Login")
    print("  GET  /api/v1/auth/me - Get current user")
    print("  POST /api/v1/auth/logout - Logout")
    print("  POST /api/v1/auth/refresh - Refresh token")
    print("\n💡 Tip: First registered user becomes admin!")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
