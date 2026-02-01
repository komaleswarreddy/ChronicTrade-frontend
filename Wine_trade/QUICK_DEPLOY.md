# Quick Deployment Reference

## 1. Vercel Frontend

```bash
# Set in Vercel Dashboard → Environment Variables:
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...
NEXT_PUBLIC_API_BASE_URL=https://your-backend.railway.app
```

**Root Directory:** `apps/frontend`

---

## 2. Railway Backend

```bash
# Set in Railway Dashboard → Variables:
DATABASE_URL=postgresql://... (auto-set)
CLERK_SECRET_KEY=sk_live_...
CLERK_ISSUER_URL=https://your-app.clerk.accounts.dev
FRONTEND_ORIGIN=https://your-app.vercel.app
ENV=production
AUTONOMY_ENABLED=true
EXECUTION_TIMEOUT_SECONDS=55
```

**Root Directory:** `apps/backend`  
**Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

---

## 3. Run Migrations

```bash
railway run python database/run_migrations.py
```

---

## 4. Verify

```bash
# Health check
curl https://your-backend.railway.app/api/health

# Frontend
open https://your-app.vercel.app
```

---

**Full details:** See `DEPLOYMENT.md`
