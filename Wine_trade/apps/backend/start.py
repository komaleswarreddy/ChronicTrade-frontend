#!/usr/bin/env python3
"""
Start script for ChronoShift FastAPI backend

We chose Python + FastAPI + PostgreSQL to support agentic workflows, 
temporal simulations, and future AI-driven extensions.
"""
import os
import sys
import subprocess

# Optional dotenv support so the backend can run even if python-dotenv
# is not installed. You can also set env vars via PowerShell or system env.
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except ImportError:  # pragma: no cover
    def load_dotenv(*args, **kwargs):
        return None

def check_database():
    """Check if database connection works and initialize if needed"""
    try:
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
        
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("⚠️  DATABASE_URL not set. Please configure it in .env file")
            return False
        
        # Test connection
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        
        # Check if tables exist
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'assets'
        """)
        if not cursor.fetchone():
            print("⚠️  Database tables not found. Initializing...")
            init_script = os.path.join(os.path.dirname(__file__), 'database', 'init_db.py')
            subprocess.run([sys.executable, init_script])
            print("✅ Database initialized")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"⚠️  Database check failed: {e}")
        print("💡 Make sure PostgreSQL is running and DATABASE_URL is correct")
        return False

def check_dependencies():
    """Check if required dependencies are available"""
    missing = []
    
    # Check sentence-transformers (required for RAG)
    try:
        import sentence_transformers
        print(f"✅ sentence-transformers {sentence_transformers.__version__} available")
    except ImportError:
        missing.append("sentence-transformers")
        print("❌ sentence-transformers not available - RAG queries will fail!")
        print("   Install with: python -m pip install sentence-transformers")
        print("   Or activate venv and install: .\\venv\\Scripts\\Activate.ps1 && python -m pip install sentence-transformers")
    
    # Check if running in venv
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if not in_venv:
        print("⚠️  WARNING: Not running in virtual environment")
        print("   Recommended: Activate venv first: .\\venv\\Scripts\\Activate.ps1")
    
    return len(missing) == 0

if __name__ == '__main__':
    print("Checking dependencies...")
    deps_ok = check_dependencies()
    print()
    
    if check_database():
        # Use plain ASCII in logs to avoid encoding issues on Windows terminals
        print("Starting ChronoShift API server...")
        print("API will be available at http://localhost:4000")
        print("API docs at http://localhost:4000/docs")
        print("Tech Stack: Python + FastAPI + PostgreSQL\n")
        
        if not deps_ok:
            print("⚠️  WARNING: Some dependencies are missing. Server will start but RAG may not work.\n")
        
        import uvicorn
        port = int(os.getenv("PORT", "4000"))
        # Only enable reload in development (not production)
        reload = os.getenv("ENV", "development") == "development"
        uvicorn.run("main:app", host="0.0.0.0", port=port, reload=reload)
    else:
        print("❌ Cannot start server without database connection")
        sys.exit(1)

