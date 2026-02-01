#!/usr/bin/env python3
"""
Startup script for Render.com deployment
Ensures proper port binding and error handling
"""
import os
import sys

# Ensure we're in the right directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Get port from environment (Render sets this automatically)
port = int(os.environ.get('PORT', 10000))
host = os.environ.get('HOST', '0.0.0.0')

print(f"🚀 Starting ChronoShift API server...")
print(f"📍 Binding to {host}:{port}")
print(f"📁 Working directory: {os.getcwd()}")

# Check for required environment variables
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("⚠️  WARNING: DATABASE_URL not set. Database operations may fail.")

try:
    import uvicorn
    print(f"✅ Uvicorn version: {uvicorn.__version__}")
except ImportError:
    print("❌ ERROR: uvicorn not installed!")
    sys.exit(1)

try:
    # Import the app to check for import errors early
    from main import app
    print("✅ FastAPI app imported successfully")
except Exception as e:
    print(f"❌ ERROR: Failed to import app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(f"🌐 Starting server on http://{host}:{port}")
print(f"📚 API docs will be available at http://{host}:{port}/docs")
print("-" * 50)

# CRITICAL: Start server immediately to bind to port
# This ensures Render detects the open port before timeout
try:
    # Use reload=False for production (Render)
    # This ensures faster startup and immediate port binding
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        log_level="info",
        access_log=True,
        reload=False,  # Disable reload in production
        loop="asyncio"  # Use asyncio event loop
    )
except Exception as e:
    print(f"❌ ERROR: Server failed to start: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
