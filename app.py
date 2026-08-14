import os
import sys
import streamlit as st

# Ensure root path is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.seed import seed_database
from utils.helpers import apply_custom_css
from pages.login import render_login_page
from pages.manager_dashboard import render_manager_dashboard
from pages.admin_dashboard import render_admin_dashboard
from pages.sales_upload import render_sales_upload_page
from pages.forecast import render_forecast_page
from pages.accuracy import render_accuracy_page

st.set_page_config(
    page_title="Retail Sales Forecasting & Demand Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_css()

# Ensure database schema, tables, and seed data are initialized once per session
if "db_initialized" not in st.session_state:
    try:
        seed_database()
    except Exception as db_err:
        print(f"Notice: Database initialization notice: {db_err}")
    st.session_state["db_initialized"] = True

if "user" not in st.session_state:
    st.session_state["user"] = None

current_user = st.session_state.get("user")

# Sidebar User Info Profile & Logout Header
if current_user is not None:
    with st.sidebar:
        role_cls = "purple" if current_user['role'] == 'admin' else "blue"
        store_info = f"<p style='margin: 6px 0 0 0; color: #94a3b8; font-size: 0.85rem;'><b>Store Scope</b>: <span style='color: #cbd5e1;'>{current_user['store_name']}</span></p>" if current_user.get('store_name') else ""
        
        profile_html = (
            f'<div style="background: rgba(30, 41, 59, 0.7); border-radius: 14px; padding: 16px; border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 15px;">'
            f'<h4 style="margin: 0 0 10px 0; color: #38bdf8; font-size: 1.05rem;">🏬 Retail Forecasting Hub</h4>'
            f'<p style="margin: 4px 0; color: #94a3b8; font-size: 0.85rem;"><b>User</b>: <span style="color: #f8fafc; font-weight: 600;">{current_user["username"]}</span></p>'
            f'<p style="margin: 6px 0; color: #94a3b8; font-size: 0.85rem;"><b>Role</b>: <span class="badge badge-{role_cls}">{current_user["role"].upper()}</span></p>'
            f'{store_info}'
            f'</div>'
        )
        st.markdown(profile_html, unsafe_allow_html=True)
        
        if st.button("🚪 Logout Account"):
            st.session_state["user"] = None
            st.rerun()

# Named functions for st.Page to guarantee unique URL pathnames
def run_login_page():
    render_login_page()

def run_manager_dashboard_page():
    render_manager_dashboard(st.session_state.get("user"))

def run_admin_dashboard_page():
    render_admin_dashboard(st.session_state.get("user"))

def run_sales_upload_page():
    render_sales_upload_page()

def run_forecast_page():
    render_forecast_page()

def run_accuracy_page():
    render_accuracy_page()

# Define Pages with explicit unique url_path parameters
login_page = st.Page(run_login_page, title="Sign In Portal", icon="🔐", url_path="login", default=True)
manager_page = st.Page(run_manager_dashboard_page, title="Store Manager Dashboard", icon="🛒", url_path="manager_dashboard")
admin_page = st.Page(run_admin_dashboard_page, title="Admin Portal", icon="📊", url_path="admin_dashboard")
upload_page = st.Page(run_sales_upload_page, title="Sales CSV Ingestion", icon="📥", url_path="sales_upload")
forecast_page = st.Page(run_forecast_page, title="Demand Forecast Engine", icon="📈", url_path="forecast")
accuracy_page = st.Page(run_accuracy_page, title="Forecast Accuracy (MAPE/RMSE)", icon="🎯", url_path="accuracy")

# Dynamic Navigation Scoping
if current_user is None:
    pg = st.navigation([login_page])
elif current_user['role'] == 'manager':
    pg = st.navigation([manager_page])
else:
    pg = st.navigation([admin_page, accuracy_page, forecast_page, upload_page, manager_page])

pg.run()
