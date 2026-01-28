# Backend Environment Setup - Render.com

## 📝 Render.com Backend Environment Variables

Go to: **Render Dashboard → ChronicTrade-backend → Environment**

### Required Variables:

```bash
# Clerk SECRET Key (Private - Keep secure!)
CLERK_SECRET_KEY=sk_test_C3KSLuNdOdn1nEBNR9JEMq709S6YdL0u5eSZ8ozc7c

# Clerk Issuer URL (from Clerk dashboard)
CLERK_ISSUER_URL=https://your-app.clerk.accounts.dev

# Database Connection (Supabase)
DATABASE_URL=postgresql://postgres:password@db.oictdkbhopiqujtsgiui.supabase.co:5432/postgres

# Frontend Origin (for CORS) - Support both local and production
FRONTEND_ORIGIN=http://localhost:3000,https://chronictrade-frontend.onrender.com

# Environment
ENV=production

# Optional: Execution settings
AUTONOMY_ENABLED=false
EXECUTION_TIMEOUT_SECONDS=300

# Optional: JWT Secret (if using custom JWT)
JWT_SECRET=your-random-secret-key-here
```

---

## ✅ Exact Values to Use (Based on Your Setup)

### 1. CLERK_SECRET_KEY
```
sk_test_C3KSLuNdOdn1nEBNR9JEMq709S6YdL0u5eSZ8ozc7c
```
- ✅ Use this exact value (from your image)

### 2. CLERK_ISSUER_URL
```
https://your-app.clerk.accounts.dev
```
- ⚠️ Replace `your-app` with your actual Clerk app name
- Find it in Clerk Dashboard → Your App → Settings → API Keys

### 3. DATABASE_URL
```
postgresql://postgres:password@db.oictdkbhopiqujtsgiui.supabase.co:5432/postgres
```
- ⚠️ Replace `password` with your actual Supabase password
- Or use the Transaction Pooler URL (port 6543) if available

### 4. FRONTEND_ORIGIN
```
http://localhost:3000,https://chronictrade-frontend.onrender.com
```
- ✅ Use this exact value (supports both local and production)

### 5. ENV
```
production
```
- ✅ Use this exact value (enables auto-migrations)

---

## 🔍 Verify Setup

After updating environment variables in Render:

1. **Backend will auto-restart** (takes ~30 seconds)
2. **Check Render logs** for:
   - ✅ "Clerk SDK initialized successfully"
   - ✅ "Migrations completed successfully"
   - ✅ "Your service is live 🎉"

3. **Test API endpoint:**
   - Visit: `https://chronictrade-backend.onrender.com/api/health`
   - Should return: `{"status":"ok"}`

---

## ⚠️ Important Notes

1. **Never commit secrets to git** - These values are only in Render environment variables
2. **CLERK_SECRET_KEY** is different from `CLERK_API_KEY` (old name)
3. **FRONTEND_ORIGIN** must include both URLs (comma-separated) for local + production
4. **ENV=production** enables automatic database migrations on startup
