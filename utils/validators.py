import pandas as pd
from typing import Tuple, List

REQUIRED_CSV_COLUMNS = {'store_code', 'sku', 'sale_date', 'quantity_sold', 'revenue'}

def validate_sales_csv(df: pd.DataFrame) -> Tuple[bool, str]:
    """Validate uploaded CSV schema and basic row constraints."""
    if df.empty:
        return False, "Uploaded CSV is empty."
        
    missing_cols = REQUIRED_CSV_COLUMNS - set(df.columns)
    if missing_cols:
        return False, f"Missing required columns: {', '.join(missing_cols)}"
        
    if (df['quantity_sold'] < 0).any():
        return False, "CSV contains negative values in quantity_sold column."
        
    return True, "Valid CSV schema."

def validate_user_input(username: str, password: str) -> Tuple[bool, str]:
    """Validate username and password format."""
    if not username or len(username.strip()) < 3:
        return False, "Username must be at least 3 characters long."
    if not password or len(password.strip()) < 6:
        return False, "Password must be at least 6 characters long."
    return True, "Valid input."
