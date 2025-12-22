# Quick Setup Guide

## 🚀 Quick Start (5 minutes)

### Step 1: Install Dependencies

```bash
# Frontend
cd apps/frontend
npm install

# Backend  
cd ../backend
npm install
```

### Step 2: Database Setup

**Option A: Local PostgreSQL**
```bash
createdb winedb
psql winedb < ../../db/schema.sql
```

**Option B: Cloud Database (Free)**
1. Sign up at [Neon.tech](https://neon.tech) or [Supabase](https://supabase.com)
2. Create a new database
3. Copy the connection string (looks like: `postgresql://user:pass@host:5432/dbname`)
4. Run the schema: Copy contents of `db/schema.sql` and run in your database SQL editor

### Step 3: Clerk Setup

1. Go to [clerk.com](https://clerk.com) → Sign up (free)
2. Create new application
3. Copy **Publishable Key** (starts with `pk_`)
4. Copy **Secret Key** (starts with `sk_`)

### Step 4: Environment Variables

**Create `apps/frontend/.env.local`:**
```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_key_here
NEXT_PUBLIC_API_BASE=http://localhost:4000
```

**Create `apps/backend/.env`:**
```env
CLERK_API_KEY=sk_test_your_key_here
DATABASE_URL=postgresql://user:password@host:5432/winedb
PORT=4000
JWT_SECRET=any-random-string-here
```

### Step 5: Run the Application

**Terminal 1 (Backend):**
```bash
cd apps/backend
npm run dev
```
✅ Should see: "Server listening on 4000"

**Terminal 2 (Frontend):**
```bash
cd apps/frontend
npm run dev
```
✅ Should see: "Ready on http://localhost:3000"

### Step 6: Test

1. Open browser: `http://localhost:3000`
2. Click "Register" → Create account with Clerk
3. Navigate to `/dashboard`
4. You should see portfolio cards and chart!

## ✅ Checklist

- [ ] Dependencies installed (frontend & backend)
- [ ] PostgreSQL database created
- [ ] Schema.sql executed
- [ ] Clerk account created
- [ ] Environment variables configured
- [ ] Backend running on port 4000
- [ ] Frontend running on port 3000
- [ ] Can register/login via Clerk
- [ ] Dashboard loads successfully

## 🐛 Common Issues

**"Cannot find module 'dotenv'"**
→ Run `npm install` in `apps/backend`

**"Database connection error"**
→ Check DATABASE_URL format and ensure database exists

**"Clerk authentication not working"**
→ Verify publishable key in `.env.local` matches Clerk dashboard

**"Port 3000/4000 already in use"**
→ Change ports in package.json scripts or kill existing processes

## 📚 Next Steps

- Replace mock data with real database queries
- Add server-side Clerk session verification
- Seed database with wine data (Kaggle CSV)
- Implement additional features (watchlist, alerts)

---

For detailed documentation, see [README.md](./README.md)

