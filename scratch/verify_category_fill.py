import os
import sys

# Ensure root directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import query_df
from services.forecast_service import calculate_inventory_risk_matrix

stores = query_df("SELECT id, store_code, store_name FROM stores ORDER BY id ASC;")
cats = query_df("SELECT id, category_name FROM categories ORDER BY id ASC;")

print("=" * 75)
print("EMPIRICAL VERIFICATION OF FILLED CATEGORIES ACROSS ALL STORES")
print("=" * 75)

for _, store in stores.iterrows():
    s_id = store['id']
    s_name = store['store_name']
    
    print(f"Store {s_id}: {s_name}")
    full_df = calculate_inventory_risk_matrix(s_id)
    
    for _, cat in cats.iterrows():
        c_id = cat['id']
        c_name = cat['category_name']
        cat_df = full_df[full_df['category_name'] == c_name]
        status_counts = cat_df['status'].value_counts().to_dict()
        
        print(f"  Category: {c_name:<20} | Items: {len(cat_df)} | Status Breakdown: {status_counts}")
    print("-" * 75)
