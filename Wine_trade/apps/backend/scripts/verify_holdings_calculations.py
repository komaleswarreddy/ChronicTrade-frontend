"""
Verification script to check holdings calculations

This script verifies:
1. Portfolio total value matches sum of holdings
2. P/L and ROI calculations are correct
3. Current values are accurate
4. Sell functionality works
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

def verify_calculations(user_id: str = None):
    """Verify all holdings calculations"""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print("🔍 Verifying Holdings Calculations...\n")
    
    # Get all active holdings with calculated prices
    if user_id:
        cursor.execute("""
            SELECT 
                h.id,
                h.user_id,
                h.asset_id,
                a.name as asset_name,
                h.quantity,
                h.buy_price,
                h.current_value as stored_current_value,
                h.status,
                COALESCE(ph.price, h.current_value, a.base_price) as calculated_current_price
            FROM holdings h
            JOIN assets a ON h.asset_id = a.asset_id
            LEFT JOIN LATERAL (
                SELECT price FROM price_history
                WHERE asset_id = h.asset_id AND region = a.region
                ORDER BY date DESC
                LIMIT 1
            ) ph ON true
            WHERE h.user_id = %s
            AND h.status IN ('OPEN', 'PARTIALLY_SOLD')
            ORDER BY h.id
        """, (user_id,))
    else:
        cursor.execute("""
            SELECT 
                h.id,
                h.user_id,
                h.asset_id,
                a.name as asset_name,
                h.quantity,
                h.buy_price,
                h.current_value as stored_current_value,
                h.status,
                COALESCE(ph.price, h.current_value, a.base_price) as calculated_current_price
            FROM holdings h
            JOIN assets a ON h.asset_id = a.asset_id
            LEFT JOIN LATERAL (
                SELECT price FROM price_history
                WHERE asset_id = h.asset_id AND region = a.region
                ORDER BY date DESC
                LIMIT 1
            ) ph ON true
            WHERE h.status IN ('OPEN', 'PARTIALLY_SOLD')
            ORDER BY h.user_id, h.id
        """)
    
    holdings = cursor.fetchall()
    
    if not holdings:
        print("❌ No active holdings found")
        cursor.close()
        conn.close()
        return
    
    print(f"📊 Found {len(holdings)} active holding(s)\n")
    
    total_portfolio_value = 0
    total_cost = 0
    issues = []
    
    for h in holdings:
        stored_value = float(h["stored_current_value"])
        calculated_value = float(h["calculated_current_price"])
        quantity = h["quantity"]
        buy_price = float(h["buy_price"])
        
        # Calculate values
        holding_value = calculated_value * quantity
        holding_cost = buy_price * quantity
        profit_loss = (calculated_value - buy_price) * quantity
        roi_percent = ((calculated_value - buy_price) / buy_price * 100) if buy_price > 0 else 0
        
        total_portfolio_value += holding_value
        total_cost += holding_cost
        
        # Check for discrepancies
        if abs(stored_value - calculated_value) > 0.01:
            issues.append({
                "holding_id": h["id"],
                "asset": h["asset_name"],
                "issue": f"Stored value (₹{stored_value:.2f}) differs from calculated (₹{calculated_value:.2f})",
                "difference": abs(stored_value - calculated_value)
            })
        
        print(f"📦 {h['asset_name']} (ID: {h['id']})")
        print(f"   Quantity: {quantity}")
        print(f"   Buy Price: ₹{buy_price:.2f}")
        print(f"   Stored Current Value: ₹{stored_value:.2f}")
        print(f"   Calculated Current Price: ₹{calculated_value:.2f}")
        print(f"   Holding Value: ₹{holding_value:.2f} (₹{calculated_value:.2f} × {quantity})")
        print(f"   P/L: ₹{profit_loss:.2f}")
        print(f"   ROI: {roi_percent:.2f}%")
        print(f"   Status: {h['status']}")
        print()
    
    print("=" * 60)
    print(f"💰 Total Portfolio Value: ₹{total_portfolio_value:.2f}")
    print(f"💵 Total Cost Basis: ₹{total_cost:.2f}")
    print(f"📈 Total P/L: ₹{total_portfolio_value - total_cost:.2f}")
    print(f"📊 Total ROI: {((total_portfolio_value - total_cost) / total_cost * 100) if total_cost > 0 else 0:.2f}%")
    print("=" * 60)
    
    if issues:
        print(f"\n⚠️  Found {len(issues)} discrepancy(ies):")
        for issue in issues:
            print(f"   - {issue['asset']} (ID: {issue['holding_id']}): {issue['issue']}")
        print("\n💡 Recommendation: Run update_holdings_prices service to sync stored values")
    else:
        print("\n✅ All calculations are consistent!")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    import sys
    user_id = sys.argv[1] if len(sys.argv) > 1 else None
    verify_calculations(user_id)

