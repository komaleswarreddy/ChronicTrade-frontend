# ChronoShift - Wine Trading Intelligence Dashboard

A full-stack wine trading intelligence platform built with Next.js, Python FastAPI, PostgreSQL, and Clerk authentication.

## 🚀 Tech Stack

- **Frontend**: Next.js (pages router), React, Tailwind CSS, Recharts
- **Backend**: Python + FastAPI (supports agentic workflows, temporal simulations, and AI-driven extensions)
- **Authentication**: Clerk (social logins including Google)
- **Database**: PostgreSQL

**Why Python + FastAPI + PostgreSQL?** We chose this stack to support agentic workflows, temporal simulations, and future AI-driven extensions.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- Node.js (v16 or higher) and npm (for frontend)
- Python 3.9+ (for backend)
- PostgreSQL database (local or cloud)
- A Clerk account (free tier available)

## 🛠️ Setup Instructions

### 1. Clone and Install Dependencies

```bash
# Install frontend dependencies
cd apps/frontend
npm install

# Install backend dependencies
cd ../backend
pip install -r requirements.txt
```

### 2. Set Up PostgreSQL Database

Choose one of these options:

**Option A: Local PostgreSQL**
```bash
# Create database
createdb winedb

# Run schema
psql winedb < ../../db/schema.sql
```

**Option B: Cloud Database (Recommended for free tier)**
- Sign up for a free PostgreSQL database at:
  - [Neon](https://neon.tech) (recommended)
  - [Supabase](https://supabase.com)
  - [Railway](https://railway.app)
- Copy the connection string (DATABASE_URL)

### 3. Set Up Clerk Authentication

1. Go to [https://clerk.com](https://clerk.com) and create a free account
2. Create a new application
3. In the Clerk dashboard:
   - Copy the **Publishable Key** (starts with `pk_`)
   - Copy the **Secret Key** (starts with `sk_`)
   - (Optional) Add Google OAuth provider in the dashboard

### 4. Configure Environment Variables

**Frontend** (`apps/frontend/.env.local`):
```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
NEXT_PUBLIC_API_BASE=http://localhost:4000
```

**Backend** (`apps/backend/.env`):
```env
CLERK_API_KEY=sk_test_...
DATABASE_URL=postgresql://user:password@host:5432/winedb
PORT=4000
```

> 💡 **Tip**: Copy `.env.example` files and fill in your actual values:
> - `cp apps/frontend/env.local.example apps/frontend/.env.local`
> - `cp apps/backend/env.example apps/backend/.env`

### 5. Initialize Database

```bash
cd apps/backend
python database/init_db.py
```

This will create the PostgreSQL schema and load mock data.

### 6. Run the Application

**Terminal 1 - Backend:**
```bash
cd apps/backend
python start.py
```
Backend will run on `http://localhost:4000`

**Terminal 2 - Frontend:**
```bash
cd apps/frontend
npm run dev
```
Frontend will run on `http://localhost:3000`

### 7. Test the Application

1. Visit `http://localhost:3000`
2. Click "Register" to create an account via Clerk
3. Sign in and navigate to `/dashboard`
4. You should see the dashboard with portfolio cards and chart

## 📁 Project Structure

```
Wine_trade/
├── apps/
│   ├── frontend/          # Next.js frontend application
│   │   ├── pages/         # Next.js pages
│   │   ├── components/    # React components
│   │   ├── styles/        # Global CSS and Tailwind
│   │   └── package.json
│   └── backend/           # Python FastAPI backend
│       ├── main.py        # FastAPI application
│       ├── start.py       # Server startup script
│       ├── requirements.txt # Python dependencies
│       └── database/      # Database initialization
│           ├── init_db.py # Database setup and mock data
│           └── schema.sql # PostgreSQL schema
├── db/
│   ├── schema.sql         # Original PostgreSQL schema (reference)
│   └── prisma.schema.example  # Prisma schema (optional)
└── README.md
```

## 🔐 Security Notes

- **Protect server routes**: Verify Clerk session server-side using Clerk server SDK before returning user-specific data
- **Never expose DB credentials**: Use environment variables and keep them server-side only
- **Production**: Use HTTPS, proper cookie flags, and restrict CORS to your domain

## 📊 Database Schema

The database includes the following tables:
- `users` - User accounts (linked to Clerk)
- `wines` - Wine catalog
- `holdings` - User wine holdings
- `orders` - Buy/sell orders

See `db/schema.sql` for full schema details.

## 🎨 UI Components

- **NavBar** - Navigation with sign in/out
- **PortfolioCard** - Summary cards (Total Value, Open Orders, P/L)
- **PortfolioChart** - Line chart showing portfolio trend
- **Dashboard** - Main dashboard page with all components

## 🔄 API Endpoints

- `GET /api/health` - Health check
- `GET /api/portfolio/summary` - Portfolio summary (total value, ROI, change)
- `GET /api/portfolio/holdings` - User holdings list
- `GET /api/market/pulse` - Market pulse by region
- `GET /api/arbitrage` - Arbitrage opportunities
- `GET /api/alerts` - System alerts

API documentation available at `http://localhost:4000/docs` when server is running.

## 📝 Next Steps

1. ✅ Set up Clerk authentication
2. ✅ Create PostgreSQL database
3. ✅ Run database schema
4. ✅ Install dependencies
5. ✅ Configure environment variables
6. ✅ Start backend and frontend
7. 🔄 Replace mocked dashboard values with real queries
8. 🔄 Integrate data seeding script for wines (from Kaggle CSV)
9. 🔄 Add server-side Clerk session verification
10. 🔄 Implement additional features (watchlist, alerts, etc.)

## 🆓 Free Data Sources

For development, consider these free wine data sources:
- **Kaggle Wine Datasets** - Download CSV and import to PostgreSQL
- **Public Government/Retail Open Data** - Country-specific open data portals
- **Mock Data** - Use mock data for development

Note: For production, consider commercial providers like Liv-ex or Wine-Searcher (paid plans).

## 🐛 Troubleshooting

**Backend won't start:**
- Check that PostgreSQL is running
- Verify DATABASE_URL is correct
- Ensure port 4000 is not in use

**Frontend Clerk errors:**
- Verify NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY is set correctly
- Check Clerk dashboard for correct application settings

**Database connection errors:**
- Verify DATABASE_URL format: `postgresql://user:password@host:port/database`
- Check database exists and is accessible
- Ensure schema has been run

## 📄 License

This project is for educational purposes.

## 👤 Author

Komal

---

**Happy coding! 🍷**

