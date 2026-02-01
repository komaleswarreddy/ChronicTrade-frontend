"""
Script to run alert generation job manually or via scheduler

Usage:
    python scripts/run_alert_generation.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from services.alert_engine import run_alert_generation_job

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL environment variable is required")
    sys.exit(1)

if __name__ == '__main__':
    print("🚀 Starting alert generation job...")
    try:
        result = run_alert_generation_job(DATABASE_URL)
        print(f"✅ Alert generation completed successfully!")
        print(f"   - Total alerts generated: {result['total_alerts']}")
        print(f"   - Users processed: {result['users_processed']}")
    except Exception as e:
        print(f"❌ Alert generation failed: {e}")
        sys.exit(1)

