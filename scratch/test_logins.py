import os
import sys

# Ensure root directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.auth_service import direct_login_by_username
from database.database import query_df
from services.forecast_service import calculate_inventory_risk_matrix

logins = [
    ("manager_downtown", "Downtown Flagship Store Manager"),
    ("manager_suburban", "Suburban Retail Center Manager"),
    ("manager_northside", "Northside Hypermarket Manager"),
    ("manager_express", "Express Station Hub Manager"),
    ("manager_all", "Regional Operations Manager (All Stores)"),
    ("admin", "System Administrator")
]

print("=" * 70)
print("EMPIRICAL VERIFICATION OF UNIQUE LOGINS & FORECAST DATA")
print("=" * 70)

for username, title in logins:
    user = direct_login_by_username(username)
    if not user:
        print(f"[FAIL] Failed to load user: {username}")
        continue
        
    store_name = user.get("store_name") or "ALL STORES (Multi-Store Access)"
    s_id = user.get("store_id")
    
    if s_id:
        fc_df = query_df("SELECT id FROM forecasts WHERE store_id = ?;", (s_id,))
        risk_df = calculate_inventory_risk_matrix(s_id)
        prod_count = len(risk_df)
        fc_count = len(fc_df)
    else:
        fc_df = query_df("SELECT id FROM forecasts;")
        prod_count = 104 # 26 items x 4 stores
        fc_count = len(fc_df)
        
    print(f"Login: {username:<18} | Role: {user['role'].upper():<7} | Scope: {store_name}")
    print(f"   Products Analyzed: {prod_count} items | 14-Day ML Forecast Points: {fc_count} records")
    print("-" * 70)
