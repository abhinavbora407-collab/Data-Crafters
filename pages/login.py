import os
import sys
import time
import pandas as pd
import streamlit as st

# Ensure root path is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import query_df
from services.auth_service import authenticate_user, register_new_store_and_manager
from utils.helpers import apply_custom_css

def render_login_page():
    """Render Dual Portal Login Page (Store Manager Sign In vs Store Registration vs Admin Portal)."""
    apply_custom_css()
    
    if "user" not in st.session_state:
        st.session_state["user"] = None
        
    if st.session_state["user"] is not None:
        user = st.session_state["user"]
        st.success(f"Already logged in as {user['username']} ({user['role'].upper()}).")
        if st.button("🚪 Logout Account"):
            st.session_state["user"] = None
            st.rerun()
        return

    st.markdown("""
    <div style="text-align: center; margin-top: 15px; margin-bottom: 25px;">
        <h1 style="font-size: 2.6rem; background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800;">
            📊 Retail Demand Forecasting Platform
        </h1>
        <p style="color: #94a3b8; font-size: 1.05rem;">
            CodeGnan Data Crafters • Inventory Analytics, ML Demand Forecasting & Role-Based Access Control
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    tab_mgr, tab_reg, tab_admin = st.tabs([
        "🏪 Store Manager Sign In",
        "📝 Register New Store & Manager",
        "🛡️ Administrator Security Portal"
    ])
    
    # 1. STORE MANAGER SIGN IN PORTAL
    with tab_mgr:
        col1, col2, col3 = st.columns([1, 1.4, 1])
        with col2:
            st.markdown("""
            <div style="background: rgba(30, 41, 59, 0.7); border-radius: 16px; padding: 24px; border: 1px solid rgba(56, 189, 248, 0.3); box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
                <h3 style="margin-top: 0; color: #38bdf8; text-align: center;">🏪 Store Manager Login</h3>
                <p style="color: #94a3b8; font-size: 0.9rem; text-align: center;">Select store branch & enter credentials to access inventory stock analysis</p>
            </div>
            """, unsafe_allow_html=True)
            
            stores_df = query_df("SELECT id, store_code, store_name FROM stores ORDER BY store_code ASC;")
            
            store_user_mapping = {
                "ALL": ("manager_all", "🌐 All Stores Regional Operations"),
                "STR-001": ("manager_downtown", "Downtown Flagship Store"),
                "STR-002": ("manager_suburban", "Suburban Retail Center"),
                "STR-003": ("manager_northside", "Northside Hypermarket"),
                "STR-004": ("manager_express", "Express Station Hub")
            }
            
            store_options = {"ALL": "🌐 All Stores Regional Operations (Switch Any Store)"}
            for _, row in stores_df.iterrows():
                store_options[row['store_code']] = f"🏢 {row['store_name']} ({row['store_code']})"
                
            selected_store_code = st.selectbox(
                "📍 Select Store Branch to Access",
                options=list(store_options.keys()),
                format_func=lambda x: store_options[x],
                key="store_branch_select"
            )
            
            default_uname, default_sname = store_user_mapping.get(selected_store_code, ("manager_downtown", "Downtown Flagship Store"))
            
            with st.form(f"mgr_login_form_{selected_store_code}"):
                st.markdown(f"**Branch Scope**: `{default_sname}`")
                username = st.text_input("Manager Account Username or Store Code", value=default_uname, key=f"u_{selected_store_code}")
                password = st.text_input("Password", type="password", value="manager123", key=f"p_{selected_store_code}")
                submit_mgr = st.form_submit_button(f"Sign In to {default_sname}")
                
                if submit_mgr:
                    user, msg = authenticate_user(username, password, required_role="manager")
                    if user:
                        st.session_state["user"] = user
                        st.success(f"✅ Credentials Recorded! Welcome Manager {user['username']}. Opening dashboard...")
                        time.sleep(1.2)
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")
                        
            st.info("""
            💡 **Manager Logins for Retail Stores**:
            - 🌐 **All Stores Regional Access**: Username: `manager_all` | Pass: `manager123`
            - 🏢 **Downtown Flagship Store**: Username: `manager_downtown` | Pass: `manager123`
            - 🏬 **Suburban Retail Center**: Username: `manager_suburban` | Pass: `manager123`
            - 🛒 **Northside Hypermarket**: Username: `manager_northside` | Pass: `manager123`
            - 🚉 **Express Station Hub**: Username: `manager_express` | Pass: `manager123`
            """)

    # 2. REGISTER NEW STORE & MANAGER PORTAL
    with tab_reg:
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            st.markdown("""
            <div style="background: rgba(30, 41, 59, 0.7); border-radius: 16px; padding: 24px; border: 1px solid rgba(34, 197, 94, 0.3); box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
                <h3 style="margin-top: 0; color: #4ade80; text-align: center;">📝 Register New Store & Manager</h3>
                <p style="color: #94a3b8; font-size: 0.9rem; text-align: center;">Create a new retail branch account and upload product history CSV</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("reg_store_manager_form"):
                st.markdown("##### 👤 Manager Credentials")
                reg_username = st.text_input("New Manager Username", placeholder="e.g. manager_east", key="reg_u")
                reg_password = st.text_input("Password", type="password", placeholder="e.g. password123", key="reg_p")
                
                st.markdown("##### 🏢 Store Branch Details")
                reg_store_name = st.text_input("New Store Name", placeholder="e.g. Eastside Superstore", key="reg_sn")
                reg_store_code = st.text_input("Store Code (Unique)", placeholder="e.g. STR-005", key="reg_sc")
                reg_location = st.text_input("Location / Address", value="Eastville Plaza", key="reg_loc")
                
                st.markdown("##### 📄 Product Sales History CSV (Optional)")
                reg_csv = st.file_uploader("Upload Product Sales History CSV", type=["csv"], help="CSV columns: store_code, sku, sale_date, quantity_sold, revenue")
                
                submit_reg = st.form_submit_button("✨ Register Store & Manager Account")
                
                if submit_reg:
                    user_sess, msg = register_new_store_and_manager(
                        username=reg_username,
                        password=reg_password,
                        store_code=reg_store_code,
                        store_name=reg_store_name,
                        location=reg_location,
                        csv_file=reg_csv
                    )
                    if user_sess:
                        st.session_state["user"] = user_sess
                        st.success(f"✅ {msg}")
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

    # 3. ADMINISTRATOR SECURITY PORTAL
    with tab_admin:
        col1, col2, col3 = st.columns([1, 1.4, 1])
        with col2:
            st.markdown("""
            <div style="background: rgba(30, 41, 59, 0.7); border-radius: 16px; padding: 24px; border: 1px solid rgba(168, 85, 247, 0.3); box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
                <h3 style="margin-top: 0; color: #c084fc; text-align: center;">🛡️ Admin Security Portal</h3>
                <p style="color: #94a3b8; font-size: 0.9rem; text-align: center;">Access all stores, CSV dataset ingestion, ML model trainer & accuracy analytics</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("admin_login_form"):
                admin_username = st.text_input("Admin Username", value="admin", key="admin_user")
                admin_password = st.text_input("Password", type="password", value="admin123", key="admin_pass")
                submit_admin = st.form_submit_button("Sign In as Administrator")
                
                if submit_admin:
                    user, msg = authenticate_user(admin_username, admin_password, required_role="admin")
                    if user:
                        st.session_state["user"] = user
                        st.success(f"✅ Credentials Recorded! Welcome Administrator {user['username']}. Full Access Granted.")
                        time.sleep(1.2)
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")
                        
            st.warning("""
            🔐 **Admin Portal Demo Account**:
            - Username: `admin` | Password: `admin123`
            """)

if __name__ == "__main__":
    render_login_page()
