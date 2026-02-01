"""
Migration Script: Migrate data from Clerk user_id to email-based user_id

This script migrates all user data from Clerk user IDs to email-based user IDs.
For komaleswarreddy@gmail.com, it will find the Clerk user_id and migrate all data.
"""

import psycopg2
import os
import sys
from datetime import datetime

# Optional dotenv support
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")


def find_all_user_ids(conn):
    """Find all unique user_ids in the database"""
    cursor = conn.cursor()
    
    # Get all unique user_ids from all tables
    user_ids = set()
    
    # From holdings
    cursor.execute("SELECT DISTINCT user_id FROM holdings")
    for row in cursor.fetchall():
        if row[0]:
            user_ids.add(row[0])
    
    # From portfolio
    cursor.execute("SELECT DISTINCT user_id FROM portfolio")
    for row in cursor.fetchall():
        if row[0]:
            user_ids.add(row[0])
    
    # From watchlists
    cursor.execute("SELECT DISTINCT user_id FROM watchlists")
    for row in cursor.fetchall():
        if row[0]:
            user_ids.add(row[0])
    
    # From portfolio_snapshots
    cursor.execute("SELECT DISTINCT user_id FROM portfolio_snapshots")
    for row in cursor.fetchall():
        if row[0]:
            user_ids.add(row[0])
    
    cursor.close()
    return list(user_ids)


def migrate_user_data(conn, old_user_id: str, new_user_id: str):
    """
    Migrate all data from old_user_id to new_user_id.
    
    Args:
        conn: Database connection
        old_user_id: The old Clerk user ID
        new_user_id: The new email-based user ID
        
    Returns:
        dict: Migration summary
    """
    cursor = conn.cursor()
    
    migration_log = {
        "timestamp": datetime.now().isoformat(),
        "old_user_id": old_user_id,
        "new_user_id": new_user_id,
        "holdings_migrated": 0,
        "portfolio_migrated": False,
        "snapshots_migrated": 0,
        "watchlists_migrated": 0,
        "holdings_events_migrated": 0,
        "errors": []
    }
    
    try:
        # Check if old user has data
        cursor.execute("SELECT COUNT(*) FROM holdings WHERE user_id = %s", (old_user_id,))
        old_holdings_count = cursor.fetchone()[0]
        
        if old_holdings_count == 0:
            print(f"[WARN] No data found for user {old_user_id}. Nothing to migrate.")
            return migration_log
        
        print(f"Found {old_holdings_count} holdings for user {old_user_id}")
        print(f"Migrating to {new_user_id}...")
        
        # Migrate holdings
        cursor.execute("""
            UPDATE holdings
            SET user_id = %s
            WHERE user_id = %s
            RETURNING id
        """, (new_user_id, old_user_id))
        
        migrated_holdings = cursor.fetchall()
        migration_log["holdings_migrated"] = len(migrated_holdings)
        print(f"[OK] Migrated {len(migrated_holdings)} holdings")
        
        # Migrate portfolio summary
        # Check if new_user_id already has a portfolio entry
        cursor.execute("SELECT user_id FROM portfolio WHERE user_id = %s", (new_user_id,))
        new_user_portfolio = cursor.fetchone()
        
        cursor.execute("SELECT user_id FROM portfolio WHERE user_id = %s", (old_user_id,))
        old_user_portfolio = cursor.fetchone()
        
        if old_user_portfolio:
            if new_user_portfolio:
                # Both exist - delete the old one (or merge if needed)
                print(f"[INFO] Portfolio already exists for {new_user_id}, removing old entry")
                cursor.execute("DELETE FROM portfolio WHERE user_id = %s", (old_user_id,))
                migration_log["portfolio_migrated"] = True
                print(f"[OK] Removed duplicate portfolio entry")
            else:
                # Update old to new
                cursor.execute("""
                    UPDATE portfolio
                    SET user_id = %s
                    WHERE user_id = %s
                    RETURNING user_id
                """, (new_user_id, old_user_id))
                if cursor.fetchone():
                    migration_log["portfolio_migrated"] = True
                    print(f"[OK] Migrated portfolio summary")
        
        # Migrate portfolio snapshots
        cursor.execute("""
            UPDATE portfolio_snapshots
            SET user_id = %s
            WHERE user_id = %s
            RETURNING id
        """, (new_user_id, old_user_id))
        
        migrated_snapshots = cursor.fetchall()
        migration_log["snapshots_migrated"] = len(migrated_snapshots)
        print(f"[OK] Migrated {len(migrated_snapshots)} portfolio snapshots")
        
        # Migrate watchlists
        cursor.execute("""
            UPDATE watchlists
            SET user_id = %s
            WHERE user_id = %s
            RETURNING id
        """, (new_user_id, old_user_id))
        
        migrated_watchlists = cursor.fetchall()
        migration_log["watchlists_migrated"] = len(migrated_watchlists)
        print(f"[OK] Migrated {len(migrated_watchlists)} watchlist items")
        
        # Migrate holdings_events
        cursor.execute("""
            UPDATE holdings_events
            SET user_id = %s
            WHERE user_id = %s
            RETURNING id
        """, (new_user_id, old_user_id))
        
        migrated_events = cursor.fetchall()
        migration_log["holdings_events_migrated"] = len(migrated_events)
        print(f"[OK] Migrated {len(migrated_events)} holdings events")
        
        # Migrate other tables that might have user_id
        tables_to_migrate = [
            'simulations',
            'execution_outcomes',
            'agent_proposals',
            'portfolio_capital',
            'portfolio_constraints',
            'strategy_performance',
            'autonomous_executions',
            'execution_steps',
            'compliance_evaluations',
            'execution_gates',
            'logistics_timelines',
            'counterfactual_analyses',
            'outcomes',
            'realized_outcomes',
            'kyc_status',
            'aml_risk_flags',
            'tax_obligations'
        ]
        
        for table in tables_to_migrate:
            try:
                # Check if table exists and has user_id column
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = %s AND column_name = 'user_id'
                """, (table,))
                
                if cursor.fetchone():
                    cursor.execute(f"""
                        UPDATE {table}
                        SET user_id = %s
                        WHERE user_id = %s
                    """, (new_user_id, old_user_id))
                    count = cursor.rowcount
                    if count > 0:
                        print(f"[OK] Migrated {count} records from {table}")
            except Exception as e:
                # Table might not exist, skip it
                pass
        
        conn.commit()
        print(f"\n[OK] Migration completed successfully!")
        print(f"   Old user_id: {old_user_id}")
        print(f"   New user_id: {new_user_id}")
        
    except Exception as e:
        conn.rollback()
        error_msg = f"Migration failed: {str(e)}"
        migration_log["errors"].append(error_msg)
        print(f"[ERROR] {error_msg}")
        raise
    
    finally:
        cursor.close()
    
    return migration_log


def main():
    """Main migration function"""
    if len(sys.argv) < 2:
        print("Finding all user_ids in database...")
        
        conn = psycopg2.connect(DATABASE_URL)
        user_ids = find_all_user_ids(conn)
        conn.close()
        
        if not user_ids:
            print("[ERROR] No user_ids found in database.")
            return
        
        print(f"\nFound {len(user_ids)} unique user_id(s):")
        for uid in user_ids:
            print(f"   - {uid}")
        
        print("\nUsage:")
        print("   python migrate_clerk_to_email.py <old_clerk_user_id>")
        print("\n   Example:")
        print("   python migrate_clerk_to_email.py user_2abc123xyz")
        print("\n   Or to migrate all Clerk user_ids to email:")
        print("   python migrate_clerk_to_email.py --migrate-all")
        return
    
    if sys.argv[1] == '--migrate-all':
        # Migrate all Clerk user_ids to email
        email = "komaleswarreddy@gmail.com"
        conn = psycopg2.connect(DATABASE_URL)
        user_ids = find_all_user_ids(conn)
        conn.close()
        
        # Filter out the email itself and demo-user
        clerk_user_ids = [uid for uid in user_ids if uid != email and uid != 'demo-user' and not '@' in uid]
        
        if not clerk_user_ids:
            print("[ERROR] No Clerk user_ids found to migrate.")
            return
        
        print(f"Migrating {len(clerk_user_ids)} Clerk user_id(s) to {email}...")
        
        for old_user_id in clerk_user_ids:
            print(f"\nMigrating {old_user_id}...")
            conn = psycopg2.connect(DATABASE_URL)
            try:
                result = migrate_user_data(conn, old_user_id, email)
                print(f"[OK] Migration complete for {old_user_id}")
            except Exception as e:
                print(f"[ERROR] Failed to migrate {old_user_id}: {e}")
            finally:
                conn.close()
        
        print("\n[OK] All migrations completed!")
        return
    
    # Migrate specific user_id
    old_user_id = sys.argv[1]
    email = "komaleswarreddy@gmail.com"
    
    print(f"Starting migration from {old_user_id} to {email}...")
    
    conn = psycopg2.connect(DATABASE_URL)
    try:
        result = migrate_user_data(conn, old_user_id, email)
        print("\nMigration Summary:")
        print(f"  - Holdings migrated: {result['holdings_migrated']}")
        print(f"  - Portfolio migrated: {result['portfolio_migrated']}")
        print(f"  - Snapshots migrated: {result['snapshots_migrated']}")
        print(f"  - Watchlists migrated: {result['watchlists_migrated']}")
        print(f"  - Holdings events migrated: {result['holdings_events_migrated']}")
        if result['errors']:
            print(f"  - Errors: {result['errors']}")
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == '__main__':
    main()
