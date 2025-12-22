# Frontend Environment Variables Setup

Create a file named `.env.local` in this directory (`apps/frontend/.env.local`) with the following content:

```env
# Clerk Authentication
# Get your keys from https://clerk.com dashboard
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_publishable_key_here

# Backend API URL
NEXT_PUBLIC_API_BASE=http://localhost:4000
```

## How to get your Clerk keys:

1. Go to [https://clerk.com](https://clerk.com) and sign up/login
2. Create a new application (or select existing one)
3. Go to "API Keys" section
4. Copy the **Publishable Key** (starts with `pk_test_` or `pk_live_`)
5. Paste it in your `.env.local` file

## Quick Setup:

```bash
# Copy the example file
cp env.local.example .env.local

# Then edit .env.local and replace the placeholder values
```

