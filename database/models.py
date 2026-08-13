# SQL DDL Models & Schema Definitions for SQLite Database

CREATE_STORES_TABLE = """
CREATE TABLE IF NOT EXISTS stores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    store_code VARCHAR(20) UNIQUE NOT NULL,
    store_name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_CATEGORIES_TABLE = """
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);
"""

CREATE_PRODUCTS_TABLE = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku VARCHAR(30) UNIQUE NOT NULL,
    product_name VARCHAR(120) NOT NULL,
    category_id INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    cost_price DECIMAL(10, 2) NOT NULL,
    reorder_point INTEGER NOT NULL DEFAULT 50,
    target_stock_level INTEGER NOT NULL DEFAULT 200,
    lead_time_days INTEGER NOT NULL DEFAULT 3,
    FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE
);
"""

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    salt VARCHAR(64) NOT NULL,
    email VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'manager')),
    store_id INTEGER NULL,
    category_id INTEGER NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (store_id) REFERENCES stores (id) ON DELETE SET NULL,
    FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE SET NULL
);
"""

CREATE_INVENTORY_TABLE = """
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    store_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    current_stock INTEGER NOT NULL DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (store_id) REFERENCES stores (id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE,
    UNIQUE(store_id, product_id)
);
"""

CREATE_SALES_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS sales_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    store_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    sale_date DATE NOT NULL,
    quantity_sold INTEGER NOT NULL CHECK (quantity_sold >= 0),
    revenue DECIMAL(12, 2) NOT NULL,
    is_promotion INTEGER DEFAULT 0 CHECK (is_promotion IN (0, 1)),
    is_holiday INTEGER DEFAULT 0 CHECK (is_holiday IN (0, 1)),
    FOREIGN KEY (store_id) REFERENCES stores (id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE,
    UNIQUE(store_id, product_id, sale_date)
);
"""

CREATE_FORECASTS_TABLE = """
CREATE TABLE IF NOT EXISTS forecasts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    store_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    forecast_date DATE NOT NULL,
    predicted_demand DECIMAL(10, 2) NOT NULL,
    lower_bound DECIMAL(10, 2) NOT NULL,
    upper_bound DECIMAL(10, 2) NOT NULL,
    model_type VARCHAR(50) DEFAULT 'Ridge-Time-Series',
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (store_id) REFERENCES stores (id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE,
    UNIQUE(store_id, product_id, forecast_date)
);
"""

CREATE_ACCURACY_LOGS_TABLE = """
CREATE TABLE IF NOT EXISTS forecast_accuracy_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    store_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    evaluation_date DATE NOT NULL,
    mape DECIMAL(8, 4) NOT NULL,
    rmse DECIMAL(8, 4) NOT NULL,
    mae DECIMAL(8, 4) NOT NULL,
    sample_size INTEGER NOT NULL,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (store_id) REFERENCES stores (id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
);
"""

CREATE_AUDIT_LOGS_TABLE = """
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username VARCHAR(50),
    action VARCHAR(100) NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

ALL_TABLE_STATEMENTS = [
    CREATE_STORES_TABLE,
    CREATE_CATEGORIES_TABLE,
    CREATE_PRODUCTS_TABLE,
    CREATE_USERS_TABLE,
    CREATE_INVENTORY_TABLE,
    CREATE_SALES_HISTORY_TABLE,
    CREATE_FORECASTS_TABLE,
    CREATE_ACCURACY_LOGS_TABLE,
    CREATE_AUDIT_LOGS_TABLE
]
