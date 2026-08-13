import datetime
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from forecasting.preprocessing import create_time_features

def forecast_demand_ridge(df: pd.DataFrame, horizon: int = 14) -> pd.DataFrame:
    """Train Ridge regression time-series model and return multi-step predictions."""
    if df.empty or len(df) < 14:
        last_date = datetime.date.today()
        dates = [last_date + datetime.timedelta(days=i) for i in range(1, horizon + 1)]
        return pd.DataFrame({
            "forecast_date": [d.strftime("%Y-%m-%d") for d in dates],
            "predicted_demand": [10.0] * horizon,
            "lower_bound": [7.0] * horizon,
            "upper_bound": [13.0] * horizon,
            "model_type": "Baseline"
        })
        
    df_feat = create_time_features(df)
    feature_cols = ['day_of_week', 'day_of_month', 'month', 'lag_1', 'lag_7', 'rolling_7_mean', 'rolling_14_mean', 'is_promotion', 'is_holiday']
    
    X = df_feat[feature_cols]
    y = df_feat['quantity_sold']
    
    model = Ridge(alpha=1.0)
    model.fit(X, y)
    
    residuals = y - model.predict(X)
    res_std = float(np.std(residuals)) if len(residuals) > 0 else 2.0
    
    last_date = pd.to_datetime(df_feat['sale_date'].iloc[-1])
    results = []
    current_hist = list(df_feat['quantity_sold'].values)
    
    for i in range(1, horizon + 1):
        next_date = last_date + pd.Timedelta(days=i)
        dow = next_date.dayofweek
        dom = next_date.day
        month = next_date.month
        is_hol = 1 if (month == 11 and dom >= 20 and dom <= 30) or (month == 12 and dom >= 20) else 0
        
        lag_1 = current_hist[-1]
        lag_7 = current_hist[-7] if len(current_hist) >= 7 else current_hist[0]
        r7 = float(np.mean(current_hist[-7:])) if len(current_hist) >= 7 else float(np.mean(current_hist))
        r14 = float(np.mean(current_hist[-14:])) if len(current_hist) >= 14 else float(np.mean(current_hist))
        
        X_next = pd.DataFrame([{
            'day_of_week': dow,
            'day_of_month': dom,
            'month': month,
            'lag_1': lag_1,
            'lag_7': lag_7,
            'rolling_7_mean': r7,
            'rolling_14_mean': r14,
            'is_promotion': 0,
            'is_holiday': is_hol
        }])
        
        pred = max(0.0, float(model.predict(X_next)[0]))
        lower_b = max(0.0, float(pred - 1.96 * res_std))
        upper_b = float(pred + 1.96 * res_std)
        
        results.append({
            "forecast_date": next_date.strftime("%Y-%m-%d"),
            "predicted_demand": round(pred, 2),
            "lower_bound": round(lower_b, 2),
            "upper_bound": round(upper_b, 2),
            "model_type": "Ridge-Time-Series"
        })
        current_hist.append(pred)
        
    return pd.DataFrame(results)
