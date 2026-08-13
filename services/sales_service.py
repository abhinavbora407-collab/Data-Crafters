import pandas as pd
from typing import Tuple, Dict, Any
from database.database import query_df, execute_db, execute_many_db
from utils.validators import validate_sales_csv

def process_sales_csv_upload(df_upload: pd.DataFrame) -> Tuple[int, int, str]:
    """Process uploaded CSV file and insert validated sales records into SQLite DB."""
    is_valid, msg = validate_sales_csv(df_upload)
    if not is_valid:
        return 0, 0, msg
        
    stores_map = {r['store_code']: r['id'] for _, r in query_df("SELECT id, store_code FROM stores;").iterrows()}
    prod_map = {r['sku']: r['id'] for _, r in query_df("SELECT id, sku FROM products;").iterrows()}
    
    records = []
    skipped = 0
    for _, row in df_upload.iterrows():
        s_code = str(row['store_code']).strip()
        p_sku = str(row['sku']).strip()
        
        if s_code in stores_map and p_sku in prod_map:
            records.append((
                int(stores_map[s_code]),
                int(prod_map[p_sku]),
                str(row['sale_date']),
                int(row['quantity_sold']),
                float(row['revenue']),
                int(row.get('is_promotion', 0)),
                int(row.get('is_holiday', 0))
            ))
        else:
            skipped += 1
            
    sql = """
    INSERT OR REPLACE INTO sales_history
    (store_id, product_id, sale_date, quantity_sold, revenue, is_promotion, is_holiday)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """
    inserted = execute_many_db(sql, records)
    return inserted, skipped, "Success"

def log_manual_sale(store_id: int, product_id: int, sale_date: str, quantity_sold: int, 
                    unit_price: float, is_promotion: bool, is_holiday: bool):
    """Log a single daily sales record and deduct stock from inventory."""
    revenue = round(quantity_sold * unit_price, 2)
    execute_db("""
    INSERT OR REPLACE INTO sales_history 
    (store_id, product_id, sale_date, quantity_sold, revenue, is_promotion, is_holiday)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """, (store_id, product_id, sale_date, quantity_sold, revenue, 1 if is_promotion else 0, 1 if is_holiday else 0))
    
    execute_db("""
    UPDATE inventory SET current_stock = MAX(0, current_stock - ?), last_updated = CURRENT_TIMESTAMP
    WHERE store_id = ? AND product_id = ?;
    """, (quantity_sold, store_id, product_id))
