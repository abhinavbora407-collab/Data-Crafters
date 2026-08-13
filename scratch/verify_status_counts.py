import os
import sys

# Ensure root directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import query_df
from services.forecast_service import calculate_inventory_risk_matrix

stores = query_df("SELECT id, store_code, store_name FROM stores ORDER BY id ASC;")

print("=" * 70)
print("EMPIRICAL VERIFICATION OF STATUS CATEGORIES PER STORE")
print("Requirement: Every store must have 4 to 10 items in EVERY category")
print("=" * 70)

for _, store in stores.iterrows():
    s_id = store['id']
    s_name = store['store_name']
    s_code = store['store_code']
    
    df = calculate_inventory_risk_matrix(s_id)
    counts = df['status'].value_counts().to_dict()
    
    crit = counts.get('CRITICAL_STOCKOUT', 0)
    warn = counts.get('WARNING_STOCKOUT', 0)
    opt  = counts.get('OPTIMAL', 0)
    over = counts.get('OVERSTOCK', 0)
    
    print(f"Store {s_id} ({s_code}): {s_name}")
    print(f"   - Critical Stockout Risk  : {crit} items (Req: 4 to 10)")
    print(f"   - Low Stock Warning       : {warn} items (Req: 4 to 10)")
    print(f"   - Healthy Stock (Optimal) : {opt} items (Req: 4 to 10)")
    print(f"   - Overstock Risk          : {over} items (Req: 4 to 10)")
    print(f"   Total Store Catalog       : {len(df)} items")
    print("-" * 70)
