# Quick Setup: Create Your .env Files

## 🚀 Frontend Setup (1 minute)

### Step 1: Create `apps/frontend/.env.local`

Copy this EXACT content:

```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_bWFpbi1ob3VuZC040S5jbGVyay5hY2NvdW50cy5kZXYk
NEXT_PUBLIC_API_BASE=https://chronictrade-backend.onrender.com
```

**That's it! Just 2 lines.**

### Step 2: Restart Frontend
```bash
# Stop current server (Ctrl+C)
npm run dev
# or
yarn dev
```

---

## 🔧 Backend Setup (Render.com)

### Go to: Render Dashboard → ChronicTrade-backend → Environment

Add/Update these variables:

```bash
CLERK_SECRET_KEY=sk_test_C3KSLuNdOdn1nEBNR9JEMq709S6YdL0u5eSZ8ozc7c
CLERK_ISSUER_URL=https://main-hound-0405.clerk.accounts.dev
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.oictdkbhopiqujtsgiui.supabase.co:5432/postgres
FRONTEND_ORIGIN=http://localhost:3000,https://chronictrade-frontend.onrender.com
ENV=production
```

**Note:** Replace `YOUR_PASSWORD` with your actual Supabase password.

---

## ✅ Verify It Works

1. **Frontend:** Open browser → DevTools → Network tab
2. **Look for:** `https://chronictrade-backend.onrender.com/api/...`
3. **Should see:** `200 OK` responses (green)
4. **Should NOT see:** `ERR_BLOCKED_BY_CLIENT` errors

---

## 📝 Need Help?

- Frontend issues? Check `FRONTEND_ENV_SETUP.md`
- Backend issues? Check `BACKEND_ENV_SETUP.md`
- Error explanations? Check `ERROR_FIXES_EXPLAINED.md`
