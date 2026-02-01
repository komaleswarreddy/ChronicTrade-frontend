#!/usr/bin/env python3
"""Verify predictions were created"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor(cursor_factory=RealDictCursor)

cursor.execute('SELECT model_id, COUNT(*) as count FROM ml_predictions GROUP BY model_id')
results = cursor.fetchall()

print("Predictions per model:")
for r in results:
    print(f"  {r['model_id']}: {r['count']} predictions")

cursor.close()
conn.close()
