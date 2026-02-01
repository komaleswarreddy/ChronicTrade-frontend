#!/usr/bin/env python3
"""
Auto-run migrations on startup for Render.com deployment

This script can be used as a standalone migration runner or called from main.py
"""

import os
import sys
from pathlib import Path

# Add project directory to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def run_migrations():
    """Run database migrations"""
    try:
        # Add database directory to path
        database_dir = project_dir / "database"
        if str(database_dir) not in sys.path:
            sys.path.insert(0, str(database_dir))
        
        from run_migrations import main as migrate_main
        print("🔄 Running database migrations...")
        migrate_main()
        print("✅ Migrations completed successfully!")
        return True
    except Exception as e:
        print(f"⚠️ Migration error (non-critical): {e}")
        # Don't fail startup if migrations fail (might already be run)
        return False

if __name__ == "__main__":
    run_migrations()
