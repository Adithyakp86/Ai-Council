# 🚀 Supabase Quick Reference

## ⚡ 30-Second Setup

### 1. Get Database Password
```
Dashboard → Settings → Database → Connection String (URI)
Copy password from: postgres:[PASSWORD]@aws...
```

### 2. Update backend/.env
```bash
DATABASE_URL=postgresql://postgres.qbyotspxrjiwfrgcqlya:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

### 3. Run SQL Script
```
Dashboard → SQL Editor → New Query
Paste: supabase-database-setup.sql
Click: Run
```

### 4. Test & Start
```bash
python test-supabase-connection.py
cd backend && python -m uvicorn app.main:app --reload
cd frontend && npm run dev
```

## 🔗 Quick Links

| Resource | URL |
|----------|-----|
| **Dashboard** | https://supabase.com/dashboard/project/qbyotspxrjiwfrgcqlya |
| **SQL Editor** | https://supabase.com/dashboard/project/qbyotspxrjiwfrgcqlya/editor |
| **Database Settings** | https://supabase.com/dashboard/project/qbyotspxrjiwfrgcqlya/settings/database |
| **API Settings** | https://supabase.com/dashboard/project/qbyotspxrjiwfrgcqlya/settings/api |
| **Table Editor** | https://supabase.com/dashboard/project/qbyotspxrjiwfrgcqlya/editor |

## 🔑 Credentials (Configured)

```bash
# Backend (.env)
SUPABASE_URL=https://qbyotspxrjiwfrgcqlya.supabase.co
SUPABASE_ANON_KEY=eyJhbGci...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...

# Frontend (.env.local)
NEXT_PUBLIC_SUPABASE_URL=https://qbyotspxrjiwfrgcqlya.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGci...
```

## 👤 Test Login

```
Email: admin@example.com
Password: admin123
```

**⚠️ Change this password immediately!**

## 📊 Database Tables

- ✅ `users` - User accounts
- ✅ `requests` - AI queries
- ✅ `responses` - AI responses
- ✅ `subtasks` - Task breakdown
- ✅ `user_api_keys` - Encrypted API keys
- ✅ `provider_costs` - Cost tracking

## 🧪 Quick Tests

### Test Connection
```bash
python test-supabase-connection.py
```

### Test Registration API
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123","full_name":"Test"}'
```

### Test Login API
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'
```

## ⚠️ Security Checklist

- [ ] Get database password from Supabase
- [ ] Update DATABASE_URL in backend/.env
- [ ] Run SQL setup script
- [ ] Test connection
- [ ] Change admin password
- [ ] Rotate API keys (they're public now!)
- [ ] Never commit .env files

## 🐛 Common Issues

### "Connection refused"
→ Check DATABASE_URL password

### "Table doesn't exist"
→ Run supabase-database-setup.sql

### "Authentication failed"
→ Verify Supabase keys in .env files

### "RLS policy violation"
→ Check if RLS policies were created

## 📚 Full Documentation

- `SUPABASE_SETUP_COMPLETE.md` - Complete setup summary
- `SUPABASE_DATABASE_SETUP.md` - Detailed guide
- `supabase-database-setup.sql` - SQL schema
- `test-supabase-connection.py` - Connection test

## 🎯 What's Next?

1. Complete the 30-second setup above
2. Test login at http://localhost:3000/login
3. Create a new user account
4. Submit an AI query
5. Check Supabase dashboard to see data

---

**Project Reference:** qbyotspxrjiwfrgcqlya
