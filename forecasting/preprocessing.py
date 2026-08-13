import pandas as pd

def create_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create temporal features: dayofweek, dayofmonth, month, lags, rolling averages."""
    df = df.sort_values("sale_date").copy()
    df['sale_date'] = pd.to_datetime(df['sale_date'])
    
    df['day_of_week'] = df['sale_date'].dt.dayofweek
    df['day_of_month'] = df['sale_date'].dt.day
    df['month'] = df['sale_date'].dt.month
    
    df['lag_1'] = df['quantity_sold'].shift(1)
    df['lag_7'] = df['quantity_sold'].shift(7)
    df['rolling_7_mean'] = df['quantity_sold'].shift(1).rolling(window=7, min_periods=1).mean()
    df['rolling_14_mean'] = df['quantity_sold'].shift(1).rolling(window=14, min_periods=1).mean()
    
    df = df.bfill().ffill().fillna(0)
    return df
