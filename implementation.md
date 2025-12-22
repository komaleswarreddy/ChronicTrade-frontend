{
  "project": {
    "name": "wine-invest-platform",
    "description": "Next.js frontend + Node.js backend + PostgreSQL starter for Wine Investment Platform (Clerk auth, Tailwind UI, sample dashboard)",
    "author": "Komal",
    "tech_stack": {
      "frontend": "Next.js (pages router), React, Tailwind CSS, react-chartjs-2",
      "backend": "Node.js (Express), pg (node-postgres) or Prisma optional",
      "auth": "Clerk (social logins incl Google)",
      "database": "PostgreSQL"
    }
  },
  "goals": [
    "Scaffold Next.js frontend with Clerk authentication (login/register via Clerk)",
    "Create protected dashboard/homepage with portfolio summary cards and chart",
    "Scaffold Node.js backend with Express and Postgres connection",
    "Provide SQL schema (schema.sql) and Prisma schema example",
    "Provide .env.example and step-by-step setup instructions"
  ],
  "env_example": {
    "FRONTEND (client/.env.local)": {
      "NEXT_PUBLIC_CLERK_FRONTEND_API": "REPLACE_WITH_CLERK_FRONTEND_API",
      "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY": "REPLACE_WITH_CLERK_PUBLISHABLE_KEY",
      "NEXT_PUBLIC_API_BASE": "http://localhost:4000"
    },
    "BACKEND (server/.env)": {
      "CLERK_API_KEY": "REPLACE_WITH_CLERK_API_KEY",
      "DATABASE_URL": "postgresql://user:password@host:5432/winedb",
      "PORT": "4000",
      "JWT_SECRET": "random-secret-if-you-use-jwt"
    }
  },
  "files": [
    {
      "path": "apps/frontend/package.json",
      "content": "{\n  \"name\": \"wine-frontend\",\n  \"version\": \"0.1.0\",\n  \"private\": true,\n  \"scripts\": {\n    \"dev\": \"next dev -p 3000\",\n    \"build\": \"next build\",\n    \"start\": \"next start\"\n  },\n  \"dependencies\": {\n    \"next\": \"latest\",\n    \"react\": \"latest\",\n    \"react-dom\": \"latest\",\n    \"@clerk/nextjs\": \"latest\",\n    \"tailwindcss\": \"latest\",\n    \"autoprefixer\": \"latest\",\n    \"postcss\": \"latest\",\n    \"axios\": \"latest\",\n    \"react-chartjs-2\": \"latest\",\n    \"chart.js\": \"latest\"\n  }\n}\n"
    },
    {
      "path": "apps/frontend/tailwind.config.js",
      "content": "module.exports = {\n  content: [\"./pages/**/*.{js,ts,jsx,tsx}\", \"./components/**/*.{js,ts,jsx,tsx}\"],\n  theme: {\n    extend: {\n      colors: {\n        wine: {\n          50: '#f8f2f3',\n          100: '#eedfe1',\n          500: '#7b1730',\n          700: '#4d0f1a'\n        },\n        gold: '#d4af37'\n      }\n    }\n  },\n  plugins: []\n}\n"
    },
    {
      "path": "apps/frontend/postcss.config.js",
      "content": "module.exports = {\n  plugins: {\n    tailwindcss: {},\n    autoprefixer: {}\n  }\n}\n"
    },
    {
      "path": "apps/frontend/pages/_app.js",
      "content": "import '../styles/globals.css'\nimport { ClerkProvider } from '@clerk/nextjs'\n\nfunction MyApp({ Component, pageProps }) {\n  return (\n    <ClerkProvider frontendApi={process.env.NEXT_PUBLIC_CLERK_FRONTEND_API}>\n      <Component {...pageProps} />\n    </ClerkProvider>\n  )\n}\n\nexport default MyApp\n"
    },
    {
      "path": "apps/frontend/pages/index.js",
      "content": "import Link from 'next/link'\nimport Head from 'next/head'\n\nexport default function Home() {\n  return (\n    <div className=\"min-h-screen bg-gradient-to-b from-wine-50 to-white\">\n      <Head>\n        <title>Wine Invest — Welcome</title>\n      </Head>\n      <main className=\"max-w-4xl mx-auto p-6\">\n        <header className=\"flex items-center justify-between py-6\">\n          <h1 className=\"text-3xl font-bold text-wine-700\">Wine Invest</h1>\n          <nav className=\"space-x-4\">\n            <Link href=\"/sign-in\"><a className=\"px-4 py-2 bg-wine-500 text-white rounded\">Sign In</a></Link>\n            <Link href=\"/register\"><a className=\"px-4 py-2 border border-wine-700 text-wine-700 rounded\">Register</a></Link>\n          </nav>\n        </header>\n\n        <section className=\"mt-12 bg-white p-8 rounded shadow\">\n          <h2 className=\"text-xl font-semibold\">Start your wine portfolio</h2>\n          <p className=\"mt-2 text-gray-600\">Sign in to view your holdings, predictions, and arbitrage alerts.</p>\n        </section>\n      </main>\n    </div>\n  )\n}\n"
    },
    {
      "path": "apps/frontend/pages/sign-in.js",
      "content": "import { SignIn } from '@clerk/nextjs'\n\nexport default function SignInPage() {\n  return (\n    <div className=\"min-h-screen flex items-center justify-center bg-wine-50\">\n      <div className=\"w-full max-w-md p-6 bg-white rounded shadow\">\n        <h2 className=\"text-2xl font-semibold mb-4\">Sign in</h2>\n        <SignIn path=\"/sign-in\" routing=\"path\" signUpUrl=\"/register\" />\n      </div>\n    </div>\n  )\n}\n"
    },
    {
      "path": "apps/frontend/pages/register.js",
      "content": "import { SignUp } from '@clerk/nextjs'\n\nexport default function RegisterPage() {\n  return (\n    <div className=\"min-h-screen flex items-center justify-center bg-wine-50\">\n      <div className=\"w-full max-w-md p-6 bg-white rounded shadow\">\n        <h2 className=\"text-2xl font-semibold mb-4\">Create account</h2>\n        <SignUp path=\"/register\" routing=\"path\" signInUrl=\"/sign-in\" />\n      </div>\n    </div>\n  )\n}\n"
    },
    {
      "path": "apps/frontend/pages/dashboard.js",
      "content": "import { useEffect, useState } from 'react'\nimport { SignedIn, SignedOut, useUser } from '@clerk/nextjs'\nimport axios from 'axios'\nimport NavBar from '../components/NavBar'\nimport PortfolioCard from '../components/PortfolioCard'\nimport PortfolioChart from '../components/PortfolioChart'\n\nexport default function Dashboard() {\n  const [data, setData] = useState(null)\n  const { isLoaded, user } = useUser()\n\n  useEffect(() => {\n    async function fetchDashboard() {\n      try {\n        const res = await axios.get(`${process.env.NEXT_PUBLIC_API_BASE}/api/dashboard`, { withCredentials: true })\n        setData(res.data)\n      } catch (err) {\n        console.error(err)\n      }\n    }\n    fetchDashboard()\n  }, [])\n\n  return (\n    <div className=\"min-h-screen bg-gray-50\">\n      <NavBar />\n      <main className=\"max-w-6xl mx-auto p-6\">\n        <SignedOut>\n          <div className=\"text-center p-8 bg-white rounded shadow\">Please sign in to see your dashboard.</div>\n        </SignedOut>\n\n        <SignedIn>\n          <h2 className=\"text-2xl font-semibold mb-4\">Welcome{user ? `, ${user.firstName || ''}` : ''}</h2>\n\n          <div className=\"grid grid-cols-1 md:grid-cols-3 gap-4 mb-6\">\n            <PortfolioCard title=\"Total Value\" value={data ? `$${data.totalValue}` : '–'} />\n            <PortfolioCard title=\"Open Orders\" value={data ? data.openOrders : '–'} />\n            <PortfolioCard title=\"Profit / Loss\" value={data ? `$${data.profitLoss}` : '–'} />\n          </div>\n\n          <div className=\"bg-white p-4 rounded shadow\">\n            <h3 className=\"font-medium mb-2\">Portfolio Trend</h3>\n            <PortfolioChart points={data ? data.trend : [100,110,120,115,130]} />\n          </div>\n        </SignedIn>\n      </main>\n    </div>\n  )\n}\n"
    },
    {
      "path": "apps/frontend/components/NavBar.js",
      "content": "import Link from 'next/link'\nimport { SignedIn, SignedOut, SignInButton, SignOutButton, useUser } from '@clerk/nextjs'\n\nexport default function NavBar(){\n  const { user } = useUser()\n  return (\n    <header className=\"bg-white shadow\">\n      <div className=\"max-w-6xl mx-auto p-4 flex items-center justify-between\">\n        <div className=\"flex items-center space-x-4\">\n          <div className=\"text-wine-700 font-bold text-xl\">Wine Invest</div>\n          <nav className=\"hidden md:flex space-x-3\">\n            <Link href=\"/dashboard\"><a className=\"text-gray-600\">Dashboard</a></Link>\n            <Link href=\"#\"><a className=\"text-gray-600\">Market</a></Link>\n            <Link href=\"#\"><a className=\"text-gray-600\">Portfolio</a></Link>\n          </nav>\n        </div>\n\n        <div>\n          <SignedOut>\n            <SignInButton>\n              <button className=\"px-3 py-1 bg-wine-500 text-white rounded\">Sign in</button>\n            </SignInButton>\n          </SignedOut>\n\n          <SignedIn>\n            <div className=\"flex items-center gap-3\">\n              <div className=\"text-sm\">{user ? user.emailAddresses?.[0]?.emailAddress : ''}</div>\n              <SignOutButton>\n                <button className=\"px-3 py-1 border rounded\">Sign out</button>\n              </SignOutButton>\n            </div>\n          </SignedIn>\n        </div>\n      </div>\n    </header>\n  )\n}\n"
    },
    {
      "path": "apps/frontend/components/PortfolioCard.js",
      "content": "export default function PortfolioCard({title, value}){\n  return (\n    <div className=\"bg-white p-4 rounded shadow\">\n      <div className=\"text-sm text-gray-500\">{title}</div>\n      <div className=\"text-2xl font-semibold\">{value}</div>\n    </div>\n  )\n}\n"
    },
    {
      "path": "apps/frontend/components/PortfolioChart.js",
      "content": "import { Line } from 'react-chartjs-2'\nimport { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend } from 'chart.js'\nChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend)\n\nexport default function PortfolioChart({ points = [100,110,120,115,130] }){\n  const labels = points.map((_,i) => `T-${points.length - i}`)\n  const data = {\n    labels,\n    datasets: [\n      {\n        label: 'Portfolio Value',\n        data: points,\n        fill: false,\n        tension: 0.2\n      }\n    ]\n  }\n  return <Line data={data} />\n}\n"
    },
    {
      "path": "apps/frontend/styles/globals.css",
      "content": "@tailwind base;\\n@tailwind components;\\n@tailwind utilities;\\nbody { background-color: #fff; }\n"
    },
    {
      "path": "apps/backend/package.json",
      "content": "{\n  \"name\": \"wine-backend\",\n  \"version\": \"0.1.0\",\n  \"private\": true,\n  \"main\": \"index.js\",\n  \"scripts\": {\n    \"dev\": \"node index.js\"\n  },\n  \"dependencies\": {\n    \"express\": \"latest\",\n    \"pg\": \"latest\",\n    \"cors\": \"latest\",\n    \"body-parser\": \"latest\",\n    \"axios\": \"latest\"\n  }\n}\n"
    },
    {
      "path": "apps/backend/index.js",
      "content": "require('dotenv').config()\nconst express = require('express')\nconst bodyParser = require('body-parser')\nconst cors = require('cors')\nconst { Pool } = require('pg')\n\nconst app = express()\napp.use(cors({ origin: 'http://localhost:3000', credentials: true }))\napp.use(bodyParser.json())\n\nconst pool = new Pool({ connectionString: process.env.DATABASE_URL })\n\n// Simple health\napp.get('/api/health', (req, res) => res.json({ ok: true }))\n\n// Sample protected route (in production validate user via Clerk)\napp.get('/api/dashboard', async (req, res) => {\n  try {\n    // TODO: verify session with Clerk (server-side) before returning user data\n    // For now, return sample aggregated values\n    const totalValueResult = await pool.query('SELECT COALESCE(SUM(current_value),0) AS total FROM holdings WHERE owner_id = $1', ['demo-user'])\n    const totalValue = totalValueResult.rows[0].total || 0\n\n    // Dummy trend data - replace with real historic values query\n    const trend = [100, 110, 120, 115, 130]\n\n    res.json({ totalValue, trend, openOrders: 2, profitLoss: 350 })\n  } catch (err) {\n    console.error(err)\n    res.status(500).json({ error: 'server error' })\n  }\n})\n\n// GET wines\napp.get('/api/wines', async (req, res) => {\n  try {\n    const r = await pool.query('SELECT * FROM wines LIMIT 100')\n    res.json(r.rows)\n  } catch (err) { res.status(500).json({ error: String(err) }) }\n})\n\n// POST create holding\napp.post('/api/holdings', async (req, res) => {\n  const { owner_id, wine_id, qty, purchase_price } = req.body\n  try {\n    const r = await pool.query('INSERT INTO holdings(owner_id, wine_id, qty, purchase_price, current_value) VALUES($1,$2,$3,$4,$4) RETURNING *', [owner_id, wine_id, qty, purchase_price])\n    res.json(r.rows[0])\n  } catch (err) { res.status(500).json({ error: String(err) }) }\n})\n\nconst port = process.env.PORT || 4000\napp.listen(port, () => console.log('Server listening on', port))\n"
    },
    {
      "path": "db/schema.sql",
      "content": "-- PostgreSQL schema for Wine Investment Platform\n\nCREATE TABLE users (\n  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),\n  clerk_id TEXT UNIQUE,\n  email TEXT UNIQUE,\n  full_name TEXT,\n  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()\n);\n\nCREATE TABLE wines (\n  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),\n  lwin TEXT, -- optional wine identifier\n  producer TEXT,\n  name TEXT,\n  vintage INT,\n  region TEXT,\n  critic_score INT,\n  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()\n);\n\nCREATE TABLE holdings (\n  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),\n  owner_id UUID REFERENCES users(id) ON DELETE CASCADE,\n  wine_id UUID REFERENCES wines(id) ON DELETE SET NULL,\n  qty INT DEFAULT 1,\n  purchase_price NUMERIC(12,2),\n  current_value NUMERIC(12,2),\n  added_at TIMESTAMP WITH TIME ZONE DEFAULT now()\n);\n\nCREATE TABLE orders (\n  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),\n  owner_id UUID REFERENCES users(id),\n  wine_id UUID REFERENCES wines(id),\n  type TEXT, -- buy/sell\n  amount NUMERIC(12,2),\n  status TEXT,\n  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()\n);\n"
    },
    {
      "path": "db/prisma.schema.example",
      "content": "generator client {\n  provider = \"prisma-client-js\"\n}\n\ndatasource db {\n  provider = \"postgresql\"\n  url      = env(\"DATABASE_URL\")\n}\n\nmodel User {\n  id        String   @id @default(uuid())\n  clerkId   String?  @unique\n  email     String   @unique\n  fullName  String?\n  holdings  Holding[]\n  createdAt DateTime @default(now())\n}\n\nmodel Wine {\n  id         String   @id @default(uuid())\n  lwin       String?\n  producer   String?\n  name       String?\n  vintage    Int?\n  region     String?\n  criticScore Int?\n  holdings   Holding[]\n  createdAt  DateTime @default(now())\n}\n\nmodel Holding {\n  id           String  @id @default(uuid())\n  owner        User    @relation(fields: [ownerId], references: [id])\n  ownerId      String\n  wine         Wine?   @relation(fields: [wineId], references: [id])\n  wineId       String?\n  qty          Int     @default(1)\n  purchasePrice Float\n  currentValue  Float\n  addedAt      DateTime @default(now())\n}\n"
    },
    {
      "path": ".cursor-instructions.json",
      "content": "{\n  \"instructions\": [\n    \"Run: cd apps/frontend && npm install\",\n    \"Run: cd apps/backend && npm install\",\n    \"Create a Postgres database and run db/schema.sql (or use Prisma migrate with prisma.schema)\",\n    \"Register at https://clerk.com (free) and create an application. Copy the frontend API (or publishable key) and server API key into the .env files.\",\n    \"Set NEXT_PUBLIC_API_BASE=http://localhost:4000 in frontend .env.local\",\n    \"Start backend: cd apps/backend && npm run dev\",\n    \"Start frontend: cd apps/frontend && npm run dev\",\n    \"Visit http://localhost:3000, register/sign-in via Clerk and check /dashboard\"\n  ]\n}\n"
    }
  ],
  "free-data-sources-and-apis": {
    "note": "There is no guaranteed free global wine prices API. For early development you can either use: public/open datasets (Kaggle: wine reviews/prices), mock data, or partner API trials. When ready to go live, consider paid feeds (Wine-Searcher, Liv-ex) or licensed auction feeds. Below are options to explore and how to fetch them.",
    "suggested_sources": [
      {
        "name": "Kaggle Wine Datasets (e.g., wine-reviews, wine-prices)",
        "type": "open dataset (CSV)",
        "how_to_fetch": "Download CSV from Kaggle, upload to your server or S3, import into Postgres. Use simple CSV import or write a script to seed the wines table."
      },
      {
        "name": "Public Government / Retail Open Data (country-specific)",
        "type": "open data",
        "how_to_fetch": "Search for retailer open data portals (e.g., LCBO in Canada has open data). Download product catalogs and import relevant fields."
      },
      {
        "name": "Mock + Scraper approach (dev only)",
        "type": "web-scraping (adhere to TOS!)",
        "how_to_fetch": "Use Puppeteer or Python BeautifulSoup to scrape public price pages for testing. In production prefer license/API access."
      }
    ],
    "note2": "When you want live market prices consider commercial providers (Liv-ex, Wine-Searcher, auction houses). They usually require registration and paid plans — so for student free tier development use Kaggle + mocks."
  },
  "ui-spec-homepage": {
    "principles": [
      "Clear top navigation (logo, Dashboard, Market, Portfolio, Profile).",
      "Top summary row (cards): Total Portfolio Value, Open Orders, P/L, Liquidity score.",
      "Main area: Portfolio value chart (last 12 months), Watchlist, Recent Activity feed.",
      "Right sidebar: Alerts (arbitrage/opportunity), Quick Actions (Add Holding, Create Order).",
      "Use wine themed colors (burgundy, gold) sparingly for accents; keep layout clean like a finance dashboard."
    ],
    "components": [
      "NavBar (logo, links, sign in/out)",
      "TopSummaryCards (3-4 cards)",
      "PortfolioChart (line)",
      "HoldingsTable (list of wines with qty, avg price, current price, ROI)",
      "Watchlist (simple cards)",
      "AlertsPanel (notifications)",
      "ProfileCard (user info, KYC status placeholder)"
    ],
    "homepage-data-to-fetch-on-load": [
      "GET /api/dashboard -> returns aggregated totals & trend array",
      "GET /api/holdings -> list of holdings for user",
      "GET /api/watchlist -> user's watchlist",
      "GET /api/alerts -> latest alerts"
    ]
  },
  "security-notes": [
    "Protect server routes: verify Clerk session server-side using Clerk server SDK or verify JWTs before returning user-specific data.",
    "Never expose DB credentials in frontend. Use environment variables and server-side only.",
    "In production use HTTPS, proper cookie flags, CORS restricted to your domain."
  ],
  "next_steps_and_checklist": [
    "1) Create a free account on Clerk and set up an app. Add Google OAuth provider inside Clerk's dashboard (register your OAuth Client there).",
    "2) Create a Postgres DB (Neon, Supabase, or Railway have free tiers). Copy DATABASE_URL to server/.env.",
    "3) Run SQL: psql < db/schema.sql or use Prisma migrations with db/prisma.schema.example.",
    "4) Install all npm packages in frontend and backend and modify .env values with real keys.",
    "5) Start the backend and frontend, then register a test user via Clerk. Use dashboard page to validate API hits to backend.",
    "6) Replace mocked dashboard values with real queries from holdings/wines tables and integrate data seeding script for wines from a Kaggle CSV."
  ]
}
