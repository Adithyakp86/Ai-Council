# Quick Start Guide

Get the AI Council application running in 5 minutes.

---

## Step 1: Database Setup (2 minutes)

1. Go to [Supabase SQL Editor](https://supabase.com/dashboard/project/qbyotspxrjiwfrgcqlya/editor)
2. Open `backend/database-schema.sql` in your code editor
3. Copy the entire file contents
4. Paste into Supabase SQL Editor
5. Click **Run**
6. Wait for "Database setup completed successfully!" message

---

## Step 2: Backend Configuration (1 minute)

1. Open `backend/.env`
2. Verify these are set correctly:
   ```env
   DATABASE_URL=postgresql://postgres.qbyotspxrjiwfrgcqlya:Shri%40742174@aws-1-ap-south-1.pooler.supabase.com:6543/postgres
   SUPABASE_URL=https://qbyotspxrjiwfrgcqlya.supabase.co
   SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

---

## Step 3: Start Backend (30 seconds)

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Backend runs at: http://127.0.0.1:8000

---

## Step 4: Start Frontend (30 seconds)

```bash
cd frontend
npm run dev
```

Frontend runs at: http://localhost:3000

---

## Step 5: Test It! (1 minute)

1. Open http://localhost:3000
2. Click "Register" or "Get Started"
3. Create account with:
   - Email: your-email@example.com
   - Password: (your choice)
   - Name: Your Name
4. Login and start using AI Council!

---

## Troubleshooting

### Backend won't start?
- Check `backend/.env` has correct DATABASE_URL
- Verify you ran the database schema in Supabase

### Frontend can't connect?
- Check `frontend/.env.local` has:
  ```env
  NEXT_PUBLIC_API_URL=http://localhost:8000
  ```

### Database errors?
- Re-run `backend/database-schema.sql` in Supabase SQL Editor
- Check password is URL-encoded in DATABASE_URL (@ becomes %40)

---

## What's Next?

- **Add AI Provider Keys**: Go to Settings > API Keys in the app
- **Read Full Setup**: See `backend/SETUP.md` for detailed configuration
- **API Documentation**: Visit http://127.0.0.1:8000/docs

---

## Important Files

- `backend/database-schema.sql` - Database setup (run in Supabase)
- `backend/.env` - Backend configuration
- `frontend/.env.local` - Frontend configuration
- `backend/SETUP.md` - Detailed backend setup guide
