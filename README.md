# Retail Sales Forecasting Application 📈
**Domain**: Data Science / Retail Chains • **Hackathon**: CodeGnan Data Crafters

An end-to-end retail sales demand forecasting and inventory management system built with **SQLite Database Integration**, **Role-Based Access Control (RBAC)**, **ML Time-Series Forecasting (Ridge Regression)**, **Stockout/Overstock Risk Matrix**, and **MAPE/RMSE Accuracy Evaluation**.

---

## 🤖 Machine Learning Demand Prediction Model

### 1. How the Prediction Model Works Based on History
The forecasting engine builds predictive demand models for each of the **112 store-product inventory streams** (4 retail stores $\times$ 28 products) using **Ridge Regression** (`scikit-learn`) trained on **365 days of continuous historical sales data**.

```
+------------------------+      +---------------------------+      +---------------------------+
|  Historical Sales Data | ---> |  Feature Engineering      | ---> |  Ridge Regression Model   |
|  (365 Days per Stream) |      |  (Lags, Rolling, Events)  |      |  (L2 Penalty alpha=1.0)   |
+------------------------+      +---------------------------+      +---------------------------+
                                                                                 |
                                                                                 v
                                                                   +---------------------------+
                                                                   | 14-Day Demand Forecast    |
                                                                   | + 95% Confidence Bounds   |
                                                                   +---------------------------+
```

#### A. Feature Engineering Pipeline ([`forecasting/preprocessing.py`](file:///C:/Users/Admin/.gemini/antigravity/scratch/sales_forecasting/forecasting/preprocessing.py))
To capture seasonality, trends, and promotional surges, historical daily sales records are transformed into rich time-series feature matrices:

1. **Temporal & Calendar Features**:
   - `day_of_week`: Day of week index ($0 = \text{Monday}, 6 = \text{Sunday}$).
   - `is_weekend`: Binary flag ($1$ for Saturday/Sunday, $0$ otherwise).
   - `day_of_month`: Day of month ($1-31$).
   - `month`: Month index ($1-12$).
2. **Seasonal Harmonic Features**:
   - $\sin(2\pi \cdot t / 365)$ & $\cos(2\pi \cdot t / 365)$ (where $t$ represents the day of year) capture smooth annual seasonal demand cycles.
3. **Promotional & Holiday Event Features**:
   - `is_promotion`: Binary flag indicating active promotional marketing events.
   - `is_holiday`: Binary flag indicating major retail holiday periods.
4. **Lagged Sales Features**:
   - `lag_1`: Demand from 1 day prior ($y_{t-1}$).
   - `lag_7`: Demand from 7 days prior ($y_{t-7}$).
   - `lag_14`: Demand from 14 days prior ($y_{t-14}$).
5. **Rolling Window Statistics**:
   - `rolling_mean_7`: 7-day moving average demand ($\mu_{7}$).
   - `rolling_mean_14`: 14-day moving average demand ($\mu_{14}$).
   - `rolling_std_7`: 7-day rolling standard deviation ($\sigma_{7}$).

#### B. Ridge Regression ML Model ([`forecasting/model.py`](file:///C:/Users/Admin/.gemini/antigravity/scratch/sales_forecasting/forecasting/model.py))
- **Objective**: Fits an $L_2$-regularized linear model to minimize prediction error while preventing overfitting caused by multicollinearity among rolling lag features:
  $$\min_{w} \|Y - Xw\|^2_2 + \alpha \|w\|^2_2$$
- **L2 Regularization ($\alpha = 1.0$)**: Ensures stable model weights even when sales exhibit sudden demand spikes or short-term noise.
- **Multi-Step Horizon Forecasting**: Iteratively generates future daily projections over 7-day, 14-day, and 30-day forecast horizons.

#### C. 95% Predictive Confidence Bounds
To account for demand variance, 95% uncertainty confidence intervals are calculated using the model's historical residual standard error ($\hat{\sigma}$):
- **Upper Bound**: $\hat{y}_{t} + 1.96 \times \hat{\sigma}$
- **Lower Bound**: $\max(0, \; \hat{y}_{t} - 1.96 \times \hat{\sigma})$

---

## 🎯 Forecast Accuracy Evaluation Engine

### 2. How Forecast Accuracy is Evaluated
The accuracy evaluation service ([`services/accuracy_service.py`](file:///C:/Users/Admin/.gemini/antigravity/scratch/sales_forecasting/services/accuracy_service.py)) continuously measures model reliability by comparing predicted demand ($\hat{y}$) against actual sales outcomes ($y$).

#### A. Empirical Evaluation Metrics
For every store-product pair, three quantitative statistical error metrics are computed and logged to the SQLite database:

1. **MAPE (Mean Absolute Percentage Error)**:
   $$\text{MAPE} = \frac{100\%}{n} \sum_{i=1}^{n} \left| \frac{y_i - \hat{y}_i}{y_i} \right|$$
   - *Interpretation*: Measures the average percentage forecast deviation. A MAPE $< 15\%$ indicates high model accuracy.

2. **RMSE (Root Mean Squared Error)**:
   $$\text{RMSE} = \sqrt{\frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2}$$
   - *Interpretation*: Penalizes larger forecast errors more heavily, highlighting risk during high-demand spikes.

3. **MAE (Mean Absolute Error)**:
   $$\text{MAE} = \frac{1}{n} \sum_{i=1}^{n} |y_i - \hat{y}_i|$$
   - *Interpretation*: Represents the average absolute error magnitude in actual product units.

#### B. Accuracy Logging & Dashboard Analytics ([`pages/accuracy.py`](file:///C:/Users/Admin/.gemini/antigravity/scratch/sales_forecasting/pages/accuracy.py))
- Accuracy metrics are written to the SQLite table `forecast_accuracy_logs`.
- Interactive Plotly box plots and histograms visualize MAPE error distributions by product category across all store branches.

---

## 🏬 Multi-Store Access & Role-Based Access Control (RBAC)

### Demo Logins

| Role | Username | Password | Scope / Permissions |
| :--- | :--- | :--- | :--- |
| **Regional Manager** | `manager_all` | `manager123` | Access & switch between **All 4 Stores** |
| **Downtown Manager** | `manager_downtown` | `manager123` | Downtown Flagship Store (`STR-001`) |
| **Suburban Manager** | `manager_suburban` | `manager123` | Suburban Retail Center (`STR-002`) |
| **Northside Manager** | `manager_northside` | `manager123` | Northside Hypermarket (`STR-003`) |
| **Express Manager** | `manager_express` | `manager123` | Express Station Hub (`STR-004`) |
| **Administrator** | `admin` | `admin123` | Full System Access, User Management & CSV Upload |

*(Store Managers can also log in directly using store codes: `str-001`, `str-002`, `str-003`, `str-004`)*

---

## 📂 Project Directory Structure

```text
sales_forecasting/
│
├── app.py                      # Main Streamlit application entry point & router
│
├── database/
│   ├── database.py             # SQLite connection pool & query runner
│   ├── models.py               # Database table DDL schema definitions
│   └── seed.py                 # Seeder script for 365 days of sales & inventory
│
├── services/
│   ├── auth_service.py         # PBKDF2 password hashing & RBAC authentication
│   ├── forecast_service.py     # Inventory risk matrix & PO generator
│   ├── accuracy_service.py     # MAPE, RMSE, MAE metrics calculation & logging
│   └── sales_service.py        # CSV batch ingestion & sales logger
│
├── forecasting/
│   ├── preprocessing.py        # Time-series feature engineering (Lags & Rolling statistics)
│   ├── moving_average.py       # Baseline moving average algorithms
│   └── model.py                # Ridge regression ML demand model
│
├── pages/
│   ├── login.py                # Dual-portal login interface
│   ├── manager_dashboard.py    # Store inventory risk matrix & restock POs
│   ├── admin_dashboard.py      # Admin system overview & RBAC user manager
│   ├── sales_upload.py         # CSV dataset ingestion tool
│   ├── forecast.py             # 14-day ML demand forecast curves & confidence bounds
│   └── accuracy.py             # Forecast accuracy analytics (MAPE / RMSE)
│
├── utils/
│   ├── helpers.py              # Custom CSS theme & UI metric card components
│   └── validators.py           # Data schema & input validation helpers
│
├── tests/
│   ├── test_auth.py            # Authentication unit tests
│   ├── test_forecast.py        # Forecast & accuracy unit tests
│   └── test_database.py        # Database initialization unit tests
│
├── requirements.txt            # Python dependencies
└── README.md                   # System documentation
```

---

## 🚀 Quickstart & Execution

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Automated Unit Tests
```bash
python -m unittest discover tests
```

### 3. Launch Application
```bash
python -m streamlit run app.py
```
Open **`http://localhost:8501`** in your browser.
