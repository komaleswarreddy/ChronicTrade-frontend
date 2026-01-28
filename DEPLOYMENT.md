# ChronoShift Production Deployment Guide

**Stack:**
- Frontend: Next.js → Vercel
- Backend: FastAPI → Railway
- Database: PostgreSQL → Railway Postgres
- Authentication: Clerk

---

## PHASE 1: CODEBASE VALIDATION ✅

### Structure Identified:
- `apps/frontend/` - Next.js frontend
- `apps/backend/` - FastAPI backend
- `apps/agents/` - Agent execution modules
- `apps/backend/database/` - Migration scripts

### Issues Found (FIXED):
1. ✅ CORS hardcoded to `localhost:3000` → Fixed to use `FRONTEND_ORIGIN` env var
2. ✅ Port hardcoded in `start.py` → Fixed to use `PORT` env var
3. ✅ Frontend has fallback localhost URLs → Acceptable (uses env var as primary)

### Verified:
- ✅ No hardcoded demo users in API endpoints
- ✅ All endpoints require `get_authenticated_user` dependency
- ✅ Execution engine uses async/background-safe patterns
- ✅ Database uses `DATABASE_URL` env variable
- ✅ Clerk integration present in frontend and backend

---

## PHASE 2: FRONTEND DEPLOYMENT (VERCEL)

### Files Created:
- `vercel.json` - Vercel deployment configuration

### Environment Variables Required:
```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...
NEXT_PUBLIC_API_BASE_URL=https://your-backend.railway.app
```

### Deployment Steps:

1. **Connect Repository to Vercel:**
   ```bash
   # Via Vercel Dashboard:
   # 1. Go to https://vercel.com/new
   # 2. Import your GitHub repository
   # 3. Set Root Directory to: apps/frontend
   ```

2. **Configure Environment Variables in Vercel:**
   - Go to Project Settings → Environment Variables
   - Add:
     - `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` (from Clerk Dashboard)
     - `NEXT_PUBLIC_API_BASE_URL` (your Railway backend URL)

3. **Deploy:**
   ```bash
   # Vercel will auto-deploy on git push
   # Or manually trigger from dashboard
   ```

4. **Verify:**
   - Frontend loads at `https://your-app.vercel.app`
   - Clerk sign-in works
   - API calls go to Railway backend

---

## PHASE 3: BACKEND DEPLOYMENT (RAILWAY)

### Files Created:
- `apps/backend/railway.json` - Railway configuration
- `apps/backend/Procfile` - Process file for Railway

### Code Changes Made:
- ✅ `apps/backend/main.py` - CORS now uses `FRONTEND_ORIGIN` env var
- ✅ `apps/backend/start.py` - Port now uses `PORT` env var

### Environment Variables Required:
```bash
DATABASE_URL=postgresql://user:pass@host:port/db
CLERK_SECRET_KEY=sk_live_...
CLERK_ISSUER_URL=https://your-clerk-instance.clerk.accounts.dev
FRONTEND_ORIGIN=https://your-app.vercel.app
PORT=4000
ENV=production
AUTONOMY_ENABLED=true
EXECUTION_TIMEOUT_SECONDS=55
```

### Deployment Steps:

1. **Create Railway Project:**
   ```bash
   # Via Railway Dashboard:
   # 1. Go to https://railway.app/new
   # 2. Create new project
   # 3. Add PostgreSQL service
   # 4. Add Python service from GitHub
   ```

2. **Configure PostgreSQL:**
   - Railway auto-creates `DATABASE_URL` env var
   - Note the connection string

3. **Configure Backend Service:**
   - Set Root Directory: `apps/backend`
   - Set Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Or Railway will auto-detect from `railway.json`

4. **Set Environment Variables:**
   - `DATABASE_URL` (auto-set by Railway Postgres)
   - `CLERK_SECRET_KEY` (from Clerk Dashboard)
   - `CLERK_ISSUER_URL` (from Clerk Dashboard, e.g., `https://your-app.clerk.accounts.dev`)
   - `FRONTEND_ORIGIN` (your Vercel frontend URL)
   - `PORT` (Railway sets this automatically)
   - `ENV=production`
   - `AUTONOMY_ENABLED=true`
   - `EXECUTION_TIMEOUT_SECONDS=55`

5. **Deploy:**
   ```bash
   # Railway auto-deploys on git push
   # Or trigger manually from dashboard
   ```

6. **Get Backend URL:**
   - Railway provides: `https://your-backend.railway.app`
   - Update Vercel `NEXT_PUBLIC_API_BASE_URL` with this URL

---

## PHASE 4: DATABASE MIGRATIONS

### Migration Script Created:
- `apps/backend/database/run_migrations.py` - Production migration runner

### Migration Order:
1. Core schema (`schema.sql`)
2. Phase 8-23 migrations (in order)
3. Phase C1-C5 migrations (execution engine)

### Run Migrations:

**Option 1: Via Railway CLI (Recommended):**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to project
railway link

# Run migrations
railway run python apps/backend/database/run_migrations.py
```

**Option 2: Via Railway Dashboard:**
1. Go to your backend service
2. Open "Deployments" → "Latest"
3. Open "Shell"
4. Run:
   ```bash
   python database/run_migrations.py
   ```

**Option 3: Local (for testing):**
```bash
cd apps/backend
export DATABASE_URL="your-railway-postgres-url"
python database/run_migrations.py
```

### ⚠️ CRITICAL: DO NOT RUN `init_db.py` IN PRODUCTION
- `init_db.py` drops tables and creates demo data
- Use `run_migrations.py` instead (additive migrations only)

---

## PHASE 5: BACKGROUND EXECUTION SAFETY ✅

### Verified:
- ✅ Agent execution uses `asyncio.wait_for` with 55s timeout
- ✅ Runs in thread pool executor (doesn't block event loop)
- ✅ Execution engine has per-step timeouts
- ✅ Kill switch via `autonomy_service.check_kill_switch()`
- ✅ Execution failures are persisted (not crashing service)
- ✅ Agents have `MAX_ITERATIONS` limit (prevents infinite loops)

### No Changes Required:
- Execution engine is production-ready

---

## PHASE 6: ENVIRONMENT VARIABLES

### Frontend (Vercel):
```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...
NEXT_PUBLIC_API_BASE_URL=https://your-backend.railway.app
```

### Backend (Railway):
```bash
DATABASE_URL=postgresql://... (auto-set by Railway)
CLERK_SECRET_KEY=sk_live_...
CLERK_ISSUER_URL=https://your-app.clerk.accounts.dev
FRONTEND_ORIGIN=https://your-app.vercel.app
PORT=4000 (auto-set by Railway)
ENV=production
AUTONOMY_ENABLED=true
EXECUTION_TIMEOUT_SECONDS=55
```

### Clerk Configuration:
1. Get keys from https://clerk.com/dashboard
2. Use **Production** keys (not test keys)
3. Set allowed origins in Clerk Dashboard:
   - Frontend URL: `https://your-app.vercel.app`
   - Backend URL: `https://your-backend.railway.app`

---

## PHASE 7: VERIFICATION CHECKLIST

### Pre-Deployment:
- [ ] All environment variables set in Vercel
- [ ] All environment variables set in Railway
- [ ] Database migrations run successfully
- [ ] Clerk production keys configured
- [ ] CORS allows frontend origin

### Post-Deployment:

#### Authentication:
- [ ] User can sign in via Clerk
- [ ] JWT tokens are validated correctly
- [ ] No 401/403 errors on API calls

#### Frontend:
- [ ] Dashboard loads portfolio data
- [ ] No console errors
- [ ] API calls go to Railway backend (not localhost)

#### Backend:
- [ ] Health check: `GET /api/health` returns 200
- [ ] API docs: `GET /docs` loads
- [ ] Database connection works

#### Features:
- [ ] AI recommendations run (`POST /api/agent/run`)
- [ ] Simulation creation works (`POST /api/simulations`)
- [ ] Simulation execution works (`POST /api/simulations/{id}/execute`)
- [ ] Execution canvas animates correctly
- [ ] Compliance & logistics display
- [ ] Holdings appear after execution
- [ ] Portfolio trend chart updates

#### Execution Engine:
- [ ] Agents complete within timeout (55s)
- [ ] No hanging requests
- [ ] Execution steps complete deterministically
- [ ] Background tasks don't crash service

---

## TROUBLESHOOTING

### Frontend shows "Cannot connect to backend":
- Check `NEXT_PUBLIC_API_BASE_URL` in Vercel
- Verify Railway backend is running
- Check CORS configuration (`FRONTEND_ORIGIN`)

### 401 Unauthorized errors:
- Verify Clerk keys are production keys
- Check `CLERK_ISSUER_URL` matches your Clerk instance
- Verify Clerk Dashboard has correct allowed origins

### Database connection errors:
- Verify `DATABASE_URL` is set correctly
- Check Railway Postgres is running
- Run migrations: `python database/run_migrations.py`

### Execution hangs or times out:
- Check `EXECUTION_TIMEOUT_SECONDS` is set
- Verify agent timeouts are configured (55s)
- Check Railway logs for errors

### Migrations fail:
- Ensure `DATABASE_URL` is correct
- Check PostgreSQL version compatibility
- Run migrations one at a time to identify issue

---

## DEPLOYMENT COMMANDS SUMMARY

```bash
# 1. Deploy Frontend (Vercel)
# Via Vercel Dashboard or:
vercel --prod

# 2. Deploy Backend (Railway)
# Via Railway Dashboard or:
railway up

# 3. Run Migrations
railway run python apps/backend/database/run_migrations.py

# 4. Verify Deployment
curl https://your-backend.railway.app/api/health
```

---

## FILES MODIFIED/CREATED

### Created:
- `vercel.json` - Vercel deployment config
- `apps/backend/railway.json` - Railway deployment config
- `apps/backend/Procfile` - Process file
- `apps/backend/database/run_migrations.py` - Migration runner
- `DEPLOYMENT.md` - This file

### Modified:
- `apps/backend/main.py` - CORS uses `FRONTEND_ORIGIN` env var
- `apps/backend/start.py` - Port uses `PORT` env var

### No Changes Required:
- Frontend code (already uses env vars)
- Backend execution engine (already production-ready)
- Agent code (already has timeouts)

---

**Deployment Complete!** 🚀
