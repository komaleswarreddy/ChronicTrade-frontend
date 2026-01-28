"""
Snapshot Service - Generate and manage portfolio snapshots

This module handles creating daily portfolio snapshots for historical tracking.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from typing import List, Dict
from services.portfolio_service import calculate_portfolio_summary


def create_portfolio_snapshot(conn, user_id: str, date: str = None, force_update: bool = True) -> bool:
    """
    Create or update a portfolio snapshot for a user on a specific date.
    
    Args:
        conn: PostgreSQL database connection
        user_id: User ID to create snapshot for
        date: Date string in YYYY-MM-DD format (defaults to today)
        force_update: If True, always update even if snapshot exists (default True)
        
    Returns:
        bool: True if snapshot was created/updated, False if it already exists and force_update=False
    """
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Calculate current portfolio value
    summary = calculate_portfolio_summary(conn, user_id)
    total_value = summary["total_value"]
    
    # Always update snapshot to ensure it's current
    cursor.execute("""
        INSERT INTO portfolio_snapshots (user_id, date, total_value)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id, date) DO UPDATE SET
            total_value = EXCLUDED.total_value,
            created_at = CURRENT_TIMESTAMP
    """, (user_id, date, total_value))
    
    conn.commit()
    cursor.close()
    return True


def get_portfolio_trend(conn, user_id: str, days: int = 30, ensure_today: bool = True) -> List[Dict]:
    """
    Get portfolio trend data for the last N days.
    
    Args:
        conn: PostgreSQL database connection
        user_id: User ID to get trend for
        days: Number of days of history to return (default 30)
        ensure_today: If True, ensure today's snapshot exists before fetching (default True)
        
    Returns:
        List of dicts with date and value for trend chart
    """
    # CRITICAL FIX: Always force update today's snapshot to ensure fresh data
    # This ensures the trend chart always shows the most current portfolio value
    create_portfolio_snapshot(conn, user_id, force_update=True)
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    today = datetime.now()
    start_date = (today - timedelta(days=days)).strftime('%Y-%m-%d')
    today_str = today.strftime('%Y-%m-%d')
    
    # Get snapshots for the last N days, always including today
    cursor.execute("""
        SELECT date, total_value
        FROM portfolio_snapshots
        WHERE user_id = %s
        AND date >= %s
        ORDER BY date ASC
    """, (user_id, start_date))
    
    rows = cursor.fetchall()
    cursor.close()
    
    # If no snapshots exist, create one for today
    if not rows:
        create_portfolio_snapshot(conn, user_id, force_update=True)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT date, total_value
            FROM portfolio_snapshots
            WHERE user_id = %s
            AND date >= %s
            ORDER BY date ASC
        """, (user_id, start_date))
        rows = cursor.fetchall()
        cursor.close()
    
    # Format for frontend chart
    trend_data = []
    today_str = datetime.now().strftime('%Y-%m-%d')
    today_formatted = datetime.now().strftime('%b %d')
    today_in_data = False
    
    for row in rows:
        date_str = row["date"]
        # Handle both string and date object formats
        if isinstance(date_str, str):
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            row_date_str = date_str
        else:
            date_obj = date_str
            row_date_str = date_obj.strftime('%Y-%m-%d')
        
        # Check if this is today's snapshot
        if row_date_str == today_str:
            today_in_data = True
        
        trend_data.append({
            "date": date_obj.strftime('%b %d'),
            "value": round(float(row["total_value"]), 2)
        })
    
    # CRITICAL FIX: Always ensure today is included with current value (most up-to-date)
    # Force update today's snapshot to ensure it's current
    create_portfolio_snapshot(conn, user_id, force_update=True)
    
    # Get current portfolio value (most accurate) - recalculate to ensure freshness
    summary = calculate_portfolio_summary(conn, user_id)
    current_value = round(summary["total_value"], 2)
    
    # Update today's entry if it exists, otherwise add it
    if today_in_data:
        # Update the last entry if it's today
        for i in range(len(trend_data) - 1, -1, -1):
            if trend_data[i]["date"] == today_formatted:
                trend_data[i]["value"] = current_value
                break
    else:
        # Add today's entry
        trend_data.append({
            "date": today_formatted,
            "value": current_value
        })
    
    # CRITICAL FIX: Ensure data is sorted by date after adding today
    # Convert date strings back to datetime for proper sorting
    def get_sort_key(item):
        date_str = item["date"]
        try:
            # Parse date like "Jan 28" and add current year
            parsed = datetime.strptime(date_str, '%b %d')
            # Use current year
            return parsed.replace(year=datetime.now().year)
        except:
            # Fallback: use today if parsing fails
            return datetime.now()
    
    trend_data.sort(key=get_sort_key)
    
    return trend_data


def generate_snapshots_for_all_users(conn):
    """
    Generate snapshots for all users who have holdings.
    This should be called daily (e.g., via cron job).
    
    Args:
        conn: PostgreSQL database connection
    """
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get all unique user IDs from holdings
    cursor.execute("""
        SELECT DISTINCT user_id FROM holdings
    """)
    
    users = cursor.fetchall()
    cursor.close()
    
    today = datetime.now().strftime('%Y-%m-%d')
    created_count = 0
    
    for user_row in users:
        user_id = user_row["user_id"]
        if create_portfolio_snapshot(conn, user_id, today):
            created_count += 1
    
    return created_count

