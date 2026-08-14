import os
import datetime
import random
import math
import hashlib
import secrets
from database.database import get_db_connection, execute_db, execute_many_db, query_db_one, init_db

def hash_password(password: str, salt_hex: str = None) -> tuple[str, str]:
    """Generate PBKDF2 password hash."""
    if not salt_hex:
        salt_hex = secrets.token_bytes(32).hex()
    salt_bytes = bytes.fromhex(salt_hex)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt_bytes, 100000).hex()
    return pwd_hash, salt_hex

def seed_database(force_reseed: bool = False):
    """Seed SQLite database with 28 items per store, exactly 5 Low Stock Warning items per store, 4 store managers, and hyper-streamlined 14-day sales data (one-fourth size dataset)."""
    init_db()
    
    conn = get_db_connection()
    try:
        # 1. Stores (4 Stores)
        stores = [
            ("STR-001", "Downtown Flagship Store", "Downtown Mall", "Metro City"),
            ("STR-002", "Suburban Retail Center", "Westside Plaza", "Metro City"),
            ("STR-003", "Northside Hypermarket", "Northway Park", "Northville"),
            ("STR-004", "Express Station Hub", "Central Station", "Metro City"),
        ]
        execute_many_db("INSERT OR IGNORE INTO stores (store_code, store_name, location, city) VALUES (?, ?, ?, ?);", stores)
        
        store_rows = conn.execute("SELECT id, store_code FROM stores;").fetchall()
        store_map = {r['store_code']: r['id'] for r in store_rows}
        
        # 2. Categories (6 Categories)
        categories = [
            ("Electronics", "Smartphones, Laptops, TV & Smart Accessories"),
            ("Apparel & Fashion", "Clothing, Footwear & Accessories"),
            ("Home & Kitchen", "Appliances, Cookware & Home Goods"),
            ("Groceries & Fresh", "Pantry items, Fresh Produce & Beverages"),
            ("Health & Beauty", "Skincare, Personal Care & Grooming"),
            ("Sports & Outdoors", "Fitness Gear, Outdoor & Wellness")
        ]
        execute_many_db("INSERT OR IGNORE INTO categories (category_name, description) VALUES (?, ?);", categories)
        
        cat_rows = conn.execute("SELECT id, category_name FROM categories;").fetchall()
        cat_map = {r['category_name']: r['id'] for r in cat_rows}
        
        # 3. Products (28 Items total across categories)
        products = [
            # Electronics (5 items)
            ("SKU-ELEC-001", "UltraTab Pro 10-inch Tablet", cat_map["Electronics"], 499.99, 320.00, 25, 120, 4),
            ("SKU-ELEC-002", "Wireless Noise-Canceling Headphones", cat_map["Electronics"], 179.99, 95.00, 40, 200, 3),
            ("SKU-ELEC-003", "SmartWatch Series 5", cat_map["Electronics"], 249.99, 140.00, 30, 150, 5),
            ("SKU-ELEC-004", "4K Ultra HD Smart TV 55-inch", cat_map["Electronics"], 699.99, 480.00, 15, 60, 7),
            ("SKU-ELEC-005", "High-Speed Wi-Fi 6 Router", cat_map["Electronics"], 119.99, 65.00, 35, 140, 3),
            
            # Apparel & Fashion (5 items)
            ("SKU-FASH-001", "Organic Cotton Classic T-Shirt", cat_map["Apparel & Fashion"], 29.99, 10.00, 80, 400, 2),
            ("SKU-FASH-002", "Slim-Fit Denim Jeans", cat_map["Apparel & Fashion"], 69.99, 28.00, 50, 250, 3),
            ("SKU-FASH-003", "All-Weather Running Shoes", cat_map["Apparel & Fashion"], 119.99, 55.00, 35, 180, 4),
            ("SKU-FASH-004", "Waterproof Hooded Jacket", cat_map["Apparel & Fashion"], 89.99, 40.00, 40, 200, 4),
            ("SKU-FASH-005", "Leather Casual Belt", cat_map["Apparel & Fashion"], 34.99, 12.00, 60, 300, 2),
            
            # Home & Kitchen (5 items)
            ("SKU-HOME-001", "Digital Air Fryer 5.5L", cat_map["Home & Kitchen"], 129.99, 70.00, 20, 100, 5),
            ("SKU-HOME-002", "Automatic Espresso Coffee Maker", cat_map["Home & Kitchen"], 299.99, 180.00, 15, 80, 7),
            ("SKU-HOME-003", "Stainless Steel Knife Block Set", cat_map["Home & Kitchen"], 89.99, 42.00, 25, 120, 4),
            ("SKU-HOME-004", "Robot Vacuum Cleaner", cat_map["Home & Kitchen"], 249.99, 150.00, 18, 90, 6),
            ("SKU-HOME-005", "Non-Stick Cookware 10-Piece Set", cat_map["Home & Kitchen"], 159.99, 85.00, 20, 100, 5),
            
            # Groceries & Fresh (5 items)
            ("SKU-GROC-001", "Organic Whole Milk (1 Gallon)", cat_map["Groceries & Fresh"], 4.99, 2.50, 150, 600, 1),
            ("SKU-GROC-002", "Artisanal Sourdough Bread", cat_map["Groceries & Fresh"], 5.49, 2.00, 100, 500, 1),
            ("SKU-GROC-003", "Cold Pressed Extra Virgin Olive Oil", cat_map["Groceries & Fresh"], 14.99, 7.50, 60, 300, 3),
            ("SKU-GROC-004", "Premium Roasted Coffee Beans 1kg", cat_map["Groceries & Fresh"], 18.99, 9.00, 80, 400, 2),
            ("SKU-GROC-005", "Organic Raw Honey 500g", cat_map["Groceries & Fresh"], 9.99, 4.50, 70, 350, 3),
            
            # Health & Beauty (4 items)
            ("SKU-BEAU-001", "Hydrating Facial Serum 50ml", cat_map["Health & Beauty"], 39.99, 15.00, 45, 220, 3),
            ("SKU-BEAU-002", "Electric Rechargeable Toothbrush", cat_map["Health & Beauty"], 69.99, 32.00, 30, 150, 4),
            ("SKU-BEAU-003", "Organic Argan Hair Oil 100ml", cat_map["Health & Beauty"], 24.99, 9.50, 50, 250, 2),
            ("SKU-BEAU-004", "Anti-Aging Night Repair Cream 50g", cat_map["Health & Beauty"], 49.99, 20.00, 35, 180, 3),
            
            # Sports & Outdoors (4 items)
            ("SKU-SPRT-001", "Non-Slip Yoga Mat 6mm", cat_map["Sports & Outdoors"], 29.99, 11.00, 60, 300, 2),
            ("SKU-SPRT-002", "Adjustable Dumbbell Set 20kg", cat_map["Sports & Outdoors"], 149.99, 85.00, 20, 100, 5),
            ("SKU-SPRT-003", "Insulated Stainless Water Bottle 1L", cat_map["Sports & Outdoors"], 22.99, 8.00, 75, 380, 2),
            ("SKU-SPRT-004", "Trail Trekking Backpack 35L", cat_map["Sports & Outdoors"], 79.99, 38.00, 40, 200, 4),
        ]
        execute_many_db(
            """INSERT OR IGNORE INTO products 
               (sku, product_name, category_id, unit_price, cost_price, reorder_point, target_stock_level, lead_time_days)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?);""",
            products
        )
        
        prod_rows = conn.execute("SELECT id, sku, category_id, unit_price, reorder_point, target_stock_level, lead_time_days FROM products ORDER BY sku ASC;").fetchall()
        prod_map = {r['sku']: dict(r) for r in prod_rows}
        prod_list = list(prod_rows)
        
        # 4. Store Managers + Regional All-Stores Manager + Admin
        users_to_create = [
            # System Director & Administrators
            ("sarah.jenkins", "SarahAdmin2026!", "sarah.jenkins@retailchain.com", "admin", None, None),
            ("admin", "admin123", "admin@retailchain.com", "admin", None, None),
            
            # Regional Operations Directors (All-Stores Access)
            ("alex.morgan", "AlexOps2026!", "alex.morgan@retailchain.com", "manager", None, None),
            ("manager_all", "manager123", "regional.mgr@retailchain.com", "manager", None, None),
            ("manager_regional", "manager123", "regional.mgr2@retailchain.com", "manager", None, None),
            
            # Downtown Flagship Store (STR-001)
            ("marcus.chen", "MarcusMgr2026!", "marcus.chen@retailchain.com", "manager", store_map["STR-001"], None),
            ("manager_downtown", "manager_downtown123", "downtown.mgr@retailchain.com", "manager", store_map["STR-001"], None),
            ("manager", "manager123", "downtown.alias@retailchain.com", "manager", store_map["STR-001"], None),
            ("str-001", "manager123", "str001@retailchain.com", "manager", store_map["STR-001"], None),
            
            # Suburban Retail Center (STR-002)
            ("rachel.davis", "RachelMgr2026!", "rachel.davis@retailchain.com", "manager", store_map["STR-002"], None),
            ("manager_suburban", "manager_suburban123", "suburban.mgr@retailchain.com", "manager", store_map["STR-002"], None),
            ("manager_west", "manager123", "suburban.alias@retailchain.com", "manager", store_map["STR-002"], None),
            ("str-002", "manager123", "str002@retailchain.com", "manager", store_map["STR-002"], None),
            
            # Northside Hypermarket (STR-003)
            ("karan.patel", "KaranMgr2026!", "karan.patel@retailchain.com", "manager", store_map["STR-003"], None),
            ("manager_northside", "manager_northside123", "northside.mgr@retailchain.com", "manager", store_map["STR-003"], None),
            ("str-003", "manager123", "str003@retailchain.com", "manager", store_map["STR-003"], None),
            
            # Express Station Hub (STR-004)
            ("jessica.taylor", "JessicaMgr2026!", "jessica.taylor@retailchain.com", "manager", store_map["STR-004"], None),
            ("manager_express", "manager_express123", "express.mgr@retailchain.com", "manager", store_map["STR-004"], None),
            ("str-004", "manager123", "str004@retailchain.com", "manager", store_map["STR-004"], None),
        ]
        for u, p, e, r, s_id, c_id in users_to_create:
            pwd_h, s_hex = hash_password(p)
            execute_db(
                "INSERT OR REPLACE INTO users (username, password_hash, salt, email, role, store_id, category_id) VALUES (?, ?, ?, ?, ?, ?, ?);",
                (u, pwd_h, s_hex, e, r, s_id, c_id)
            )
            
        # Check if sales history already exists (One-fourth size 14-day dataset)
        existing_sales = conn.execute("SELECT COUNT(*) as cnt FROM sales_history;").fetchone()
        if not (existing_sales and existing_sales['cnt'] > 300 and not force_reseed):
            end_date = datetime.date.today() - datetime.timedelta(days=1)
            start_date = end_date - datetime.timedelta(days=14) # Reduced to one-fourth size dataset (1,568 records total)
            
            sales_records = []
            curr_date = start_date
            
            while curr_date <= end_date:
                day_of_week = curr_date.weekday()
                is_weekend = 1 if day_of_week in (5, 6) else 0
                month = curr_date.month
                day = curr_date.day
                is_holiday = 1 if (month == 11 and day >= 20 and day <= 30) or (month == 12 and day >= 20) or (month == 7 and day <= 10) else 0
                
                for s_code, s_id in store_map.items():
                    store_mult = 1.4 if s_code == "STR-001" else (1.2 if s_code == "STR-003" else 0.9)
                    for p_sku, p_data in prod_map.items():
                        price = float(p_data['unit_price'])
                        base_qty = 8 if price > 200 else (20 if price > 50 else 50)
                        
                        day_idx = (curr_date - start_date).days
                        seasonal = 1.0 + 0.35 * math.sin(2 * math.pi * day_idx / 14.0)
                        weekend = 1.35 if is_weekend else 1.0
                        holiday = 1.6 if is_holiday else 1.0
                        is_promo = 1 if random.random() < 0.10 else 0
                        promo = 1.4 if is_promo else 1.0
                        noise = random.gauss(1.0, 0.12)
                        
                        calc_qty = max(1, int(base_qty * store_mult * seasonal * weekend * holiday * promo * noise))
                        revenue = round(calc_qty * price, 2)
                        
                        sales_records.append((
                            s_id, p_data['id'], curr_date.strftime("%Y-%m-%d"), calc_qty, revenue, is_promo, is_holiday
                        ))
                curr_date += datetime.timedelta(days=1)
                
            execute_many_db(
                """INSERT OR IGNORE INTO sales_history 
                   (store_id, product_id, sale_date, quantity_sold, revenue, is_promotion, is_holiday) 
                   VALUES (?, ?, ?, ?, ?, ?, ?);""",
                sales_records
            )

        # 5. Inventory: Guaranteed EXACTLY 5 LOW STOCK WARNING ITEMS per store
        inventory_records = []
        
        for s_idx, (s_code, s_id) in enumerate(store_map.items()):
            shift = s_idx * 7
            shuffled_prods = prod_list[shift:] + prod_list[:shift]
            
            critical_prods = shuffled_prods[0:5]   # 5 items -> Critical Stockout Risk
            warning_prods  = shuffled_prods[5:10]  # 5 items -> LOW STOCK WARNING (Guaranteed 5 items!)
            optimal_prods  = shuffled_prods[10:19] # 9 items -> Healthy Stock (Optimal)
            overstock_prods= shuffled_prods[19:28] # 9 items -> Overstock Risk
            
            for p_row in critical_prods:
                reorder_p = int(p_row['reorder_point'])
                stock = max(1, int(reorder_p * 0.15))
                inventory_records.append((s_id, p_row['id'], stock))
                
            for p_row in warning_prods:
                reorder_p = int(p_row['reorder_point'])
                critical_thresh = max(3, int(reorder_p * 0.35))
                stock = critical_thresh + max(2, int(reorder_p * 0.35)) # Strictly inside Low Stock Warning range!
                inventory_records.append((s_id, p_row['id'], stock))
                
            for p_row in optimal_prods:
                reorder_p = int(p_row['reorder_point'])
                target_s  = int(p_row['target_stock_level'])
                stock = max(reorder_p + 5, int((reorder_p + target_s) / 2))
                inventory_records.append((s_id, p_row['id'], stock))
                
            for p_row in overstock_prods:
                target_s  = int(p_row['target_stock_level'])
                stock = int(target_s * 1.4)
                inventory_records.append((s_id, p_row['id'], stock))

        execute_many_db(
            "INSERT OR REPLACE INTO inventory (store_id, product_id, current_stock) VALUES (?, ?, ?);",
            inventory_records
        )
    finally:
        conn.close()
        
    try:
        conn = get_db_connection()
        fc_cnt = conn.execute("SELECT COUNT(*) as cnt FROM forecasts;").fetchone()
        conn.close()
        if not (fc_cnt and fc_cnt['cnt'] > 100 and not force_reseed):
            from services.forecast_service import generate_store_forecasts
            generate_store_forecasts(14)
    except Exception:
        pass

def seed_sales_history_for_store(store_id: int, num_days: int = 14) -> int:
    """Generate synthetic historical sales for all catalog products for a given store_id."""
    conn = get_db_connection()
    try:
        prod_rows = conn.execute("SELECT id, sku, unit_price FROM products;").fetchall()
        if not prod_rows:
            return 0
            
        end_date = datetime.date.today() - datetime.timedelta(days=1)
        start_date = end_date - datetime.timedelta(days=num_days - 1)
        
        sales_records = []
        curr_date = start_date
        store_mult = 1.0 + ((store_id % 3) * 0.15)
        
        while curr_date <= end_date:
            day_of_week = curr_date.weekday()
            is_weekend = 1 if day_of_week in (5, 6) else 0
            month = curr_date.month
            day = curr_date.day
            is_holiday = 1 if (month == 11 and day >= 20 and day <= 30) or (month == 12 and day >= 20) or (month == 7 and day <= 10) else 0
            
            for p_row in prod_rows:
                price = float(p_row['unit_price'])
                base_qty = 8 if price > 200 else (20 if price > 50 else 50)
                
                day_idx = (curr_date - start_date).days
                seasonal = 1.0 + 0.35 * math.sin(2 * math.pi * day_idx / 14.0)
                weekend = 1.35 if is_weekend else 1.0
                holiday = 1.6 if is_holiday else 1.0
                is_promo = 1 if random.random() < 0.10 else 0
                promo = 1.4 if is_promo else 1.0
                noise = random.gauss(1.0, 0.12)
                
                calc_qty = max(1, int(base_qty * store_mult * seasonal * weekend * holiday * promo * noise))
                revenue = round(calc_qty * price, 2)
                
                sales_records.append((
                    store_id, p_row['id'], curr_date.strftime("%Y-%m-%d"), calc_qty, revenue, is_promo, is_holiday
                ))
            curr_date += datetime.timedelta(days=1)
            
        inserted = execute_many_db(
            """INSERT OR IGNORE INTO sales_history 
               (store_id, product_id, sale_date, quantity_sold, revenue, is_promotion, is_holiday) 
               VALUES (?, ?, ?, ?, ?, ?, ?);""",
            sales_records
        )
        return inserted
    finally:
        conn.close()

def ensure_sales_history_for_all_stores(num_days: int = 14) -> int:
    """Check all registered store branches and generate historical sales for any store lacking history."""
    conn = get_db_connection()
    try:
        store_rows = conn.execute("SELECT id FROM stores;").fetchall()
        if not store_rows:
            return 0
        total_added = 0
        for r in store_rows:
            s_id = r['id']
            cnt = conn.execute("SELECT COUNT(*) as c FROM sales_history WHERE store_id = ?;", (s_id,)).fetchone()
            if not cnt or cnt['c'] < 10:
                total_added += seed_sales_history_for_store(s_id, num_days)
        return total_added
    finally:
        conn.close()
