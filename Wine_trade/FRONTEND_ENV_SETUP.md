# Frontend Environment Setup - Exact Values

## 📝 Create `apps/frontend/.env.local` File

**IMPORTANT:** This file is gitignored (not committed to git) - your secrets stay safe!

### Step 1: Create the file

Create a new file: `apps/frontend/.env.local`

### Step 2: Copy this EXACT content (with your actual values):

```bash
# Clerk PUBLISHABLE Key (Public - Safe to expose)
# Get from: https://clerk.com/dashboard → Your App → API Keys
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_bWFpbi1ob3VuZC040S5jbGVyay5hY2NvdW50cy5kZXYk

# Backend API URL - Point to Render backend
NEXT_PUBLIC_API_BASE=https://chronictrade-backend.onrender.com
```

### Step 3: Verify your values

✅ **NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY:**
- Should start with `pk_test_` (development) or `pk_live_` (production)
- From your image, you have: `pk_test_bWFpbi1ob3VuZC040S5jbGVyay5hY2NvdW50cy5kZXYk`
- ✅ **USE THIS EXACT VALUE**

✅ **NEXT_PUBLIC_API_BASE:**
- Should be: `https://chronictrade-backend.onrender.com`
- ✅ **USE THIS EXACT VALUE**

### Step 4: Restart Frontend

After creating `.env.local`:
1. Stop the dev server (Ctrl+C)
2. Restart: `npm run dev` or `yarn dev`
3. Hard refresh browser (Ctrl+Shift+R)

---

## ❌ What NOT to Include

**DO NOT** put these in frontend `.env.local`:
- ❌ `CLERK_SECRET_KEY` (secret keys belong in backend only!)
- ❌ `DATABASE_URL` (backend only)
- ❌ Any other secret keys

---

## ✅ Final `.env.local` File Should Look Like:

```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_bWFpbi1ob3VuZC040S5jbGVyay5hY2NvdW50cy5kZXYk
NEXT_PUBLIC_API_BASE=https://chronictrade-backend.onrender.com
```

**That's it! Just 2 lines.**

---

## 🔍 Verify It's Working

1. Open browser DevTools → Network tab
2. Refresh the page
3. Look for API calls:
   - ✅ Should see: `https://chronictrade-backend.onrender.com/api/...`
   - ❌ Should NOT see: `localhost:4000/api/...`
4. Check for errors:
   - ✅ No `ERR_BLOCKED_BY_CLIENT` errors
   - ✅ API calls return `200 OK`
