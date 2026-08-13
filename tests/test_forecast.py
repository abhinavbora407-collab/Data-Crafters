import unittest
import numpy as np
from services.accuracy_service import calculate_mape, calculate_rmse, calculate_mae

class TestForecastMetrics(unittest.TestCase):
    def test_accuracy_metrics(self):
        y_true = np.array([100, 200, 300, 400])
        y_pred = np.array([110, 190, 310, 390])
        
        mape = calculate_mape(y_true, y_pred)
        rmse = calculate_rmse(y_true, y_pred)
        mae = calculate_mae(y_true, y_pred)
        
        self.assertAlmostEqual(mape, 5.208333333333334, places=2)
        self.assertAlmostEqual(rmse, 10.0, places=2)
        self.assertAlmostEqual(mae, 10.0, places=2)

if __name__ == "__main__":
    unittest.main()
