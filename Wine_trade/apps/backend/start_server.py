#!/usr/bin/env python3
"""
Startup script for Render.com deployment - FORCEFUL VERSION
Ensures immediate port binding at any cost
"""
import os
import sys

# Force immediate output flushing
sys.stdout.flush()
sys.stderr.flush()

# Ensure we're in the right directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Get port from environment (Render sets this automatically)
port = int(os.environ.get('PORT', 10000))
host = os.environ.get('HOST', '0.0.0.0')

# CRITICAL: Flush output immediately
print("🚀 Starting ChronoShift API server...", flush=True)
print(f"📍 Binding to {host}:{port}", flush=True)
print(f"📁 Working directory: {os.getcwd()}", flush=True)
sys.stdout.flush()

# Check for required environment variables
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("⚠️  WARNING: DATABASE_URL not set. Database operations may fail.", flush=True)
    sys.stdout.flush()

try:
    import uvicorn
    print(f"✅ Uvicorn version: {uvicorn.__version__}", flush=True)
    sys.stdout.flush()
except ImportError:
    print("❌ ERROR: uvicorn not installed!", flush=True)
    sys.exit(1)

# CRITICAL: Don't import app here - let uvicorn do it
# This avoids any blocking operations during import
print("✅ Skipping app import check - uvicorn will import it", flush=True)
print(f"🌐 Starting server on http://{host}:{port}", flush=True)
print(f"📚 API docs will be available at http://{host}:{port}/docs", flush=True)
print("-" * 50, flush=True)
sys.stdout.flush()

# CRITICAL: Start server IMMEDIATELY - use programmatic API for better control
# This ensures port binding happens as fast as possible
try:
    # Import app with timeout protection
    print("📦 Importing FastAPI app...", flush=True)
    try:
        from main import app
        print("✅ FastAPI app imported successfully", flush=True)
    except Exception as import_error:
        print(f"❌ ERROR: Failed to import app: {import_error}", flush=True)
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        sys.exit(1)
    
    # Use uvicorn's programmatic API with explicit config
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level="info",
        access_log=True,
        reload=False,  # Disable reload in production
        loop="asyncio",  # Use asyncio event loop
        timeout_keep_alive=5,
        timeout_graceful_shutdown=5,
    )
    
    server = uvicorn.Server(config)
    print(f"🌐 Starting uvicorn server on {host}:{port}...", flush=True)
    sys.stdout.flush()
    
    # Run server - this will bind to port immediately
    server.run()
    
except KeyboardInterrupt:
    print("\n🛑 Server stopped by user", flush=True)
    sys.exit(0)
except Exception as e:
    print(f"❌ ERROR: Server failed to start: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.stdout.flush()
    sys.exit(1)
