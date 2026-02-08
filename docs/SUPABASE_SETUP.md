# Supabase Database Setup

Your Supabase database is now configured!

## Configuration

**Supabase Project:** qbyotspxrjiwfrgcqlya
**URL:** https://qbyotspxrjiwfrgcqlya.supabase.co

## Environment Variables

### Backend (`backend/.env`)
```env
SUPABASE_URL=https://qbyotspxrjiwfrgcqlya.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Frontend (`frontend/.env.local`)
```env
NEXT_PUBLIC_SUPABASE_URL=https://qbyotspxrjiwfrgcqlya.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Database Schema

Run the SQL script in your Supabase SQL Editor:
- File: `docs/supabase-database-setup.sql`
- URL: https://supabase.com/dashboard/project/qbyotspxrjiwfrgcqlya/editor

This creates:
- `users` table - User authentication
- `requests` table - AI council requests
- `responses` table - AI responses
- `subtasks` table - Request subtasks
- `user_api_keys` table - Encrypted API keys
- `provider_costs` table - Cost tracking

## Current Setup

The backend is currently using **SQLite** for local development. The Supabase credentials are configured and ready to use when you're ready to switch.

## Next Steps

1. Run the SQL script in Supabase SQL Editor
2. Start the servers: `.\start-dev.ps1`
3. Test authentication at http://localhost:3000

## Switching to Supabase

The backend uses SQLite by default. Supabase is configured and ready when needed for production deployment.
