import numpy as np
import pandas as pd
from typing import List

def simple_moving_average(series: pd.Series, window: int = 7, horizon: int = 14) -> List[float]:
    """Calculate Simple Moving Average forecast for horizon days."""
    if len(series) == 0:
        return [10.0] * horizon
    recent_mean = float(series.tail(window).mean())
    return [max(0.0, recent_mean)] * horizon

def weighted_moving_average(series: pd.Series, weights: List[float] = [0.5, 0.3, 0.2], horizon: int = 14) -> List[float]:
    """Calculate Weighted Moving Average forecast for horizon days."""
    if len(series) < len(weights):
        return simple_moving_average(series, horizon=horizon)
    recent = series.tail(len(weights)).values[::-1]
    weights_arr = np.array(weights) / np.sum(weights)
    weighted_val = float(np.sum(recent * weights_arr))
    return [max(0.0, weighted_val)] * horizon
