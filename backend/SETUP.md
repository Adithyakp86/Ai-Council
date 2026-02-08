# Backend Setup Guide

Complete guide to set up the AI Council backend application.

---

## Prerequisites

- Python 3.10 or higher
- PostgreSQL database (Supabase recommended)
- Redis server (optional, for caching)
- AI Provider API keys (Groq, Together, OpenRouter, etc.)

---

## 1. Database Setup (Supabase)

### Step 1: Create Supabase Project
1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Create a new project or use existing one
3. Note down your project credentials:
   - Project URL: `https://YOUR_PROJECT_ID.supabase.co`
   - Anon Key: Found in Settings > API
   - Service Role Key: Found in Settings > API
   - Database Password: Set during project creation

### Step 2: Get Database Connection String
1. Go to Settings > Database
2. Find "Connection string" section
3. Select "URI" tab
4. Copy the connection string (format: `postgresql://postgres.[PROJECT_ID]:[PASSWORD]@aws-X-region.pooler.supabase.com:6543/postgres`)
5. **Important**: URL-encode special characters in password:
   - `@` becomes `%40`
   - `#` becomes `%23`
   - `$` becomes `%24`
   - `&` becomes `%26`

### Step 3: Run Database Schema
1. Go to [SQL Editor](https://supabase.com/dashboard/project/YOUR_PROJECT_ID/editor)
2. Open the file `backend/database-schema.sql`
3. Copy the entire contents
4. Paste into Supabase SQL Editor
5. Click "Run" to execute
6. Verify success message appears

---

## 2. Environment Configuration

### Step 1: Copy Environment Template
```bash
cd backend
copy .env.example .env
```

### Step 2: Configure `.env` File

Open `backend/.env` and update the following:

#### Database Configuration
```env
DATABASE_URL=postgresql://postgres.YOUR_PROJECT_ID:YOUR_PASSWORD@aws-X-region.pooler.supabase.com:6543/postgres
```

#### Supabase Configuration
```env
SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
```

#### JWT Configuration
```env
SECRET_KEY=generate_a_secure_random_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_DAYS=7
```

To generate a secure SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### AI Provider API Keys
Get API keys from these providers:

- **Groq**: https://console.groq.com/keys
- **Together AI**: https://api.together.xyz/settings/api-keys
- **OpenRouter**: https://openrouter.ai/keys
- **Hugging Face**: https://huggingface.co/settings/tokens

```env
GROQ_API_KEY=your_groq_api_key
TOGETHER_API_KEY=your_together_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
HUGGINGFACE_API_KEY=your_huggingface_api_key
```

#### Redis Configuration (Optional)
```env
REDIS_URL=redis://localhost:6379/0
```

If you don't have Redis installed, the app will work without caching.

---

## 3. Install Dependencies

### Using pip
```bash
cd backend
pip install -r requirements.txt
```

### Using Poetry (recommended)
```bash
cd backend
poetry install
```

---

## 4. Run the Backend Server

### Development Mode
```bash
cd backend
python -m uvicorn app.main:app --reload
```

The server will start at: http://127.0.0.1:8000

### Production Mode
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 5. Verify Installation

### Check API Documentation
Open your browser and visit:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### Test Health Endpoint
```bash
curl http://127.0.0.1:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected"
}
```

### Test User Registration
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123",
    "name": "Test User"
  }'
```

---

## 6. API Endpoints Overview

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user

### AI Council
- `POST /api/v1/council/query` - Submit AI query
- `GET /api/v1/council/requests` - Get user requests
- `GET /api/v1/council/requests/{id}` - Get request details
- `WS /api/v1/ws/{request_id}` - WebSocket for real-time updates

### User API Keys
- `POST /api/v1/user-api-keys` - Add API key
- `GET /api/v1/user-api-keys` - List user API keys
- `PUT /api/v1/user-api-keys/{id}` - Update API key
- `DELETE /api/v1/user-api-keys/{id}` - Delete API key

### Admin (Admin role required)
- `GET /api/v1/admin/users` - List all users
- `GET /api/v1/admin/stats` - System statistics
- `PUT /api/v1/admin/users/{id}` - Update user

### User Profile
- `GET /api/v1/user/profile` - Get user profile
- `PUT /api/v1/user/profile` - Update profile
- `GET /api/v1/user/requests` - Get user request history

---

## 7. Testing

### Run All Tests
```bash
cd backend
pytest
```

### Run Specific Test File
```bash
pytest tests/test_auth_endpoints.py
```

### Run with Coverage
```bash
pytest --cov=app --cov-report=html
```

---

## 8. Common Issues & Solutions

### Issue: "no such table: users"
**Solution**: Run the database schema in Supabase SQL Editor (Step 1.3)

### Issue: "could not translate host name"
**Solution**: Check DATABASE_URL format and ensure password is URL-encoded

### Issue: "FATAL: Tenant or user not found"
**Solution**: Verify your Supabase connection string includes the correct project ID

### Issue: "Redis connection failed"
**Solution**: Either install Redis or remove REDIS_URL from .env (app works without it)

### Issue: "Invalid API key"
**Solution**: Verify your AI provider API keys are correct and active

---

## 9. Project Structure

```
backend/
├── app/
│   ├── api/              # API endpoints
│   │   ├── auth.py       # Authentication endpoints
│   │   ├── council.py    # AI Council endpoints
│   │   ├── user.py       # User profile endpoints
│   │   ├── admin.py      # Admin endpoints
│   │   └── websocket.py  # WebSocket connections
│   ├── core/             # Core configuration
│   │   ├── config.py     # App configuration
│   │   ├── database.py   # Database connection
│   │   ├── security.py   # Password hashing, JWT
│   │   └── middleware.py # Auth middleware
│   ├── models/           # Database models
│   │   ├── user.py
│   │   ├── request.py
│   │   ├── response.py
│   │   └── subtask.py
│   ├── services/         # Business logic
│   │   ├── council_orchestration_bridge.py
│   │   ├── websocket_manager.py
│   │   └── cloud_ai/     # AI provider integrations
│   └── main.py           # FastAPI application
├── tests/                # Test files
├── database-schema.sql   # Database setup script
├── .env                  # Environment variables
└── pyproject.toml        # Python dependencies
```

---

## 10. Next Steps

1. **Frontend Setup**: Configure the Next.js frontend to connect to this backend
2. **AI Provider Setup**: Add your AI provider API keys in user settings
3. **Deploy**: Follow deployment guide for production setup
4. **Monitor**: Set up logging and monitoring for production

---

## Support

For issues or questions:
- Check the main README.md
- Review API documentation at `/docs`
- Check test files for usage examples
