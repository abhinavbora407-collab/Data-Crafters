import os
import sys
import streamlit as st

# Ensure root path is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import query_df
from pages.login import render_login_page
from utils.helpers import apply_custom_css, render_header, render_metric_card, render_paginated_dataframe, render_generic_card_grid

def render_admin_dashboard(current_user=None):
    """Render Administrator Control Panel."""
    apply_custom_css()
    user = current_user or st.session_state.get("user")
    
    if user is None:
        render_login_page()
        return
        
    if user.get("role") != "admin":
        st.error("🔒 Access Restricted: Administrator privileges required.")
        return

    render_header("📊 Administrator Operations & Control Center", f"System Overview • Logged in as Administrator: {user['username']}")
    
    # System Stats
    s_cnt = query_df("SELECT COUNT(*) as cnt FROM stores;")['cnt'].iloc[0]
    p_cnt = query_df("SELECT COUNT(*) as cnt FROM products;")['cnt'].iloc[0]
    u_cnt = query_df("SELECT COUNT(*) as cnt FROM users;")['cnt'].iloc[0]
    tx_cnt = query_df("SELECT COUNT(*) as cnt FROM sales_history;")['cnt'].iloc[0]
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_metric_card("Retail Store Branches", str(s_cnt), "Active Stores", "#38bdf8")
    with c2: render_metric_card("Product SKU Catalog", str(p_cnt), "Tracked SKUs", "#818cf8")
    with c3: render_metric_card("User Accounts", str(u_cnt), "RBAC Accounts", "#22c55e")
    with c4: render_metric_card("Historical Sales Records", f"{tx_cnt:,}", "Logged Sales Records", "#c084fc")

    st.markdown("---")
    
    tab_users, tab_audit = st.tabs([
        "👥 User Account Management",
        "📜 System Security Audit Trail"
    ])
    
    with tab_users:
        col_u_t, col_u_m = st.columns([1.5, 1])
        with col_u_t:
            st.subheader("Active User Accounts & RBAC Privileges")
        with col_u_m:
            user_view_mode = st.radio("Display Mode:", ["🎴 User Cards", "📋 Data Table"], horizontal=True, key="user_mode")

        st.info("ℹ️ New Store Managers can self-register their Store Branch & Product History CSV directly on the Login Portal!")
        users_df = query_df("""
        SELECT u.username, u.email, u.role, s.store_name, c.category_name, u.created_at 
        FROM users u
        LEFT JOIN stores s ON u.store_id = s.id
        LEFT JOIN categories c ON u.category_id = c.id
        ORDER BY u.id ASC;
        """)
        
        if user_view_mode == "🎴 User Cards":
            render_generic_card_grid(
                users_df,
                page_size=10,
                key_prefix="admin_users_cards",
                card_icon="👤",
                title_col="username",
                badge_col="role",
                border_color="#818cf8"
            )
        else:
            render_paginated_dataframe(users_df, page_size=10, key_prefix="admin_users_table")

    with tab_audit:
        col_a_t, col_a_m = st.columns([1.5, 1])
        with col_a_t:
            st.subheader("System Security Audit Trail")
        with col_a_m:
            audit_view_mode = st.radio("Display Mode:", ["🎴 Audit Cards", "📋 Data Table"], horizontal=True, key="audit_mode")

        logs_df = query_df("SELECT created_at, username, action, details FROM audit_logs ORDER BY id DESC LIMIT 100;")
        
        if audit_view_mode == "🎴 Audit Cards":
            render_generic_card_grid(
                logs_df,
                page_size=10,
                key_prefix="admin_audit_cards",
                card_icon="📜",
                title_col="action",
                badge_col="username",
                border_color="#c084fc"
            )
        else:
            render_paginated_dataframe(logs_df, page_size=10, key_prefix="admin_audit_table")

if __name__ == "__main__":
    render_admin_dashboard()
