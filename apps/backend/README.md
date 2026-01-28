# ChronoShift Backend API

FastAPI backend for the wine trading intelligence dashboard.

**Tech Stack:** Python + FastAPI + PostgreSQL

We chose Python + FastAPI + PostgreSQL to support agentic workflows, temporal simulations, and future AI-driven extensions.

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Configure PostgreSQL connection in `.env`:
```
DATABASE_URL=postgresql://user:password@host:port/database
```

3. Initialize database and load mock data:
```bash
python database/init_db.py
```

4. Start the server:
```bash
python start.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --port 4000
```

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/portfolio/summary` - Portfolio summary
- `GET /api/portfolio/holdings` - User holdings
- `GET /api/market/pulse` - Market pulse by region
- `GET /api/arbitrage` - Arbitrage opportunities
- `GET /api/alerts` - System alerts

API documentation available at `/docs` when server is running.

## Database

PostgreSQL database (configure via DATABASE_URL environment variable)

Mock data generated in `mock_data.json` and loaded into database.

## Note on Express Backend

The Express.js backend (`index.js`) is kept in the repository for reference but is not actively used. FastAPI is the current source of truth for all API endpoints.

