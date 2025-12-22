# Backend Environment Variables Setup

Create a file named `.env` in this directory (`apps/backend/.env`) with the following content:

```env
# Clerk Authentication
# Get your secret key from https://clerk.com dashboard
CLERK_API_KEY=sk_test_your_secret_key_here

# PostgreSQL Database Connection
# Format: postgresql://username:password@host:port/database
DATABASE_URL=postgresql://user:password@host:5432/winedb

# Server Port
PORT=4000

# JWT Secret (for custom JWT if needed)
JWT_SECRET=your-random-secret-key-here
```

## How to get your Clerk Secret Key:

1. Go to [https://clerk.com](https://clerk.com) and sign up/login
2. Create a new application (or select existing one)
3. Go to "API Keys" section
4. Copy the **Secret Key** (starts with `sk_test_` or `sk_live_`)
5. Paste it in your `.env` file

## Database Setup:

### Option 1: Local PostgreSQL
```bash
createdb winedb
# Then use: postgresql://postgres:yourpassword@localhost:5432/winedb
```

### Option 2: Cloud Database (Free)
- **Neon**: https://neon.tech (recommended)
- **Supabase**: https://supabase.com
- **Railway**: https://railway.app

Copy the connection string they provide and paste it as `DATABASE_URL`

## Quick Setup:

```bash
# Copy the example file
cp env.example .env

# Then edit .env and replace the placeholder values
```

## Generate JWT Secret:

```bash
# On Linux/Mac:
openssl rand -base64 32

# On Windows PowerShell:
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))
```

