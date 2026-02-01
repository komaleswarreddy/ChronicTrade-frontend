# Environment Variables Setup Guide

## 🔐 Clerk Configuration

### Frontend (`apps/frontend/.env.local`)

Create this file manually (it's gitignored for security):

```bash
# Clerk PUBLISHABLE Key (public, safe to expose)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_publishable_key_here

# Backend API URL
# For production (Render backend):
NEXT_PUBLIC_API_BASE=https://chronictrade-backend.onrender.com
# For local development:
# NEXT_PUBLIC_API_BASE=http://localhost:4000
```

**Important:**
- ✅ Use `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` (starts with `pk_test_`)
- ❌ **NEVER** put `CLERK_SECRET_KEY` in frontend files!

### Backend (`apps/backend/.env` or Render Environment Variables)

```bash
# Clerk SECRET Key (private, keep secure!)
CLERK_SECRET_KEY=sk_test_your_secret_key_here

# Clerk Issuer URL (optional)
CLERK_ISSUER_URL=https://your-app.clerk.accounts.dev

# Database
DATABASE_URL=postgresql://user:password@host:5432/database

# Frontend Origin (for CORS)
FRONTEND_ORIGIN=http://localhost:3000

# Environment
ENV=production
```

**Important:**
- ✅ Use `CLERK_SECRET_KEY` (starts with `sk_test_`)
- ❌ **NEVER** use `CLERK_API_KEY` (old/deprecated name)

## 📍 Where to Find Clerk Keys

1. Go to https://clerk.com/dashboard
2. Select your application
3. Go to **"API Keys"** section
4. Copy:
   - **Publishable key** → Frontend `.env.local`
   - **Secret key** → Backend `.env` or Render environment variables

## 🚀 Quick Setup Steps

### 1. Frontend Setup

```bash
cd apps/frontend
cp env.local.example .env.local
# Edit .env.local with your actual keys
```

### 2. Backend Setup (Local)

```bash
cd apps/backend
cp env.example .env
# Edit .env with your actual keys
```

### 3. Backend Setup (Render)

1. Go to Render dashboard → Your backend service
2. Go to **Environment** tab
3. Add/Update these variables:
   - `CLERK_SECRET_KEY=sk_test_...`
   - `DATABASE_URL=postgresql://...`
   - `FRONTEND_ORIGIN=http://localhost:3000`
   - `ENV=production`

## ⚠️ Common Mistakes

1. **Putting secret key in frontend** ❌
   - Secret keys should ONLY be in backend
   - Frontend only needs publishable key

2. **Using wrong variable name** ❌
   - Backend: `CLERK_SECRET_KEY` (not `CLERK_API_KEY`)
   - Frontend: `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`

3. **Wrong API base URL** ❌
   - Local dev: `http://localhost:4000`
   - Production: `https://chronictrade-backend.onrender.com`

4. **Missing CORS origin** ❌
   - Backend needs `FRONTEND_ORIGIN` for CORS
   - Set to your frontend URL (e.g., `http://localhost:3000`)

## ✅ Verification

After setup, verify:

1. **Frontend**: Check browser console - no Clerk errors
2. **Backend**: Check Render logs - Clerk SDK initialized successfully
3. **API Calls**: Network tab shows successful requests (no `ERR_BLOCKED_BY_CLIENT`)
