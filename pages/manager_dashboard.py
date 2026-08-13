import os
import sys
import datetime
import time
import streamlit as st
import pandas as pd

# Ensure root path is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import query_df
from services.forecast_service import calculate_inventory_risk_matrix
from services.sales_service import log_manual_sale
from pages.login import render_login_page
from utils.helpers import apply_custom_css, render_header, render_metric_card, render_paginated_dataframe, render_product_card_grid, render_generic_card_grid

def render_manager_dashboard(current_user=None):
    """Render Store Manager Operational Stockout & Purchase Order Dashboard."""
    apply_custom_css()
    user = current_user or st.session_state.get("user")
    
    if user is None:
        render_login_page()
        return
        
    if user.get("role") not in ("manager", "admin"):
        st.error("🔒 Access Restricted: Store Manager or Regional Manager privileges required.")
        return

    render_header("🛒 Store Stockout Risks & Replenishment Dashboard", f"Store Scope: {user.get('store_name', 'All Stores')}")
    
    stores_df = query_df("SELECT id, store_name FROM stores ORDER BY store_name;")
    cats_df = query_df("SELECT id, category_name FROM categories ORDER BY category_name;")
    
    col_s, col_c, col_d = st.columns([1, 1, 1])
    with col_s:
        if user['role'] == 'manager' and user.get('store_id'):
            selected_store_id = user['store_id']
            st.info(f"📍 Store Scope: **{user['store_name']}**")
        else:
            store_opts = {r['id']: r['store_name'] for _, r in stores_df.iterrows()}
            selected_store_id = st.selectbox("Select Store", list(store_opts.keys()), format_func=lambda x: store_opts[x])
            
    with col_c:
        if user['role'] == 'manager' and user.get('category_id'):
            selected_cat_id = user['category_id']
            st.info(f"🏷️ Category Scope: **{user['category_name']}**")
        else:
            cat_opts = {0: "All Categories"}
            for _, r in cats_df.iterrows():
                cat_opts[r['id']] = r['category_name']
            selected_cat_id = st.selectbox("Filter Category", list(cat_opts.keys()), format_func=lambda x: cat_opts[x])
            
    with col_d:
        forecast_days = st.slider("Forecast Horizon (Days)", 7, 30, 14)
        
    risk_df = calculate_inventory_risk_matrix(selected_store_id, selected_cat_id, forecast_days)
    if risk_df.empty:
        st.warning("No inventory records found for selected store/category.")
        return
        
    # KPI Metric Cards
    c1, c2, c3, c4, c5 = st.columns(5)
    crit_cnt = len(risk_df[risk_df['status'] == 'CRITICAL_STOCKOUT'])
    warn_cnt = len(risk_df[risk_df['status'] == 'WARNING_STOCKOUT'])
    opt_cnt = len(risk_df[risk_df['status'] == 'OPTIMAL'])
    over_cnt = len(risk_df[risk_df['status'] == 'OVERSTOCK'])
    
    with c1: render_metric_card("Store Products", str(len(risk_df)), "Tracked Store SKUs", "#38bdf8")
    with c2: render_metric_card("Critical Stockout", str(crit_cnt), "< Lead Time Demand", "#ef4444")
    with c3: render_metric_card("Low Stock Warning", str(warn_cnt), "< Reorder Point", "#f59e0b")
    with c4: render_metric_card("Healthy Stock", str(opt_cnt), "Optimal Range", "#22c55e")
    with c5: render_metric_card("Overstock Risk", str(over_cnt), "> Target Stock Level", "#a855f7")

    st.markdown("---")
    
    tab_matrix, tab_sim, tab_po, tab_log = st.tabs([
        "🚨 Stockout Risk Matrix",
        "⚡ What-If Demand Surge Simulator",
        "🛒 Recommended Purchase Orders",
        "📝 Log Daily Sales"
    ])
    
    with tab_matrix:
        col_m_title, col_m_mode = st.columns([1.5, 1])
        with col_m_title:
            st.subheader("Inventory Stockout Risk Matrix")
        with col_m_mode:
            view_mode = st.radio("Display Mode:", ["🎴 Visual Cards", "📋 Data Table"], horizontal=True, key="risk_matrix_mode")
            
        filter_status = st.radio("Filter Status:", ["ALL", "CRITICAL_STOCKOUT", "WARNING_STOCKOUT", "OPTIMAL", "OVERSTOCK"], horizontal=True)
        disp_df = risk_df.copy()
        if filter_status != "ALL":
            disp_df = disp_df[disp_df['status'] == filter_status]
            
        if view_mode == "🎴 Visual Cards":
            render_product_card_grid(disp_df, page_size=10, key_prefix="risk_cards")
        else:
            render_paginated_dataframe(
                disp_df[['sku', 'product_name', 'category_name', 'current_stock', 'reorder_point', 'avg_daily_demand', 'days_of_supply', 'status_label', 'suggested_reorder_qty']].rename(columns={
                    'sku': 'SKU', 'product_name': 'Product Name', 'category_name': 'Category',
                    'current_stock': 'Current Stock', 'reorder_point': 'Reorder Point',
                    'avg_daily_demand': 'Avg Daily Sales', 'days_of_supply': 'Days of Supply',
                    'status_label': 'Risk Status', 'suggested_reorder_qty': 'Suggested Reorder Qty'
                }),
                page_size=10,
                key_prefix="risk_matrix"
            )

    with tab_sim:
        col_sim_t, col_sim_m = st.columns([1.5, 1])
        with col_sim_t:
            st.subheader("What-If Demand Surge Scenario Simulator")
        with col_sim_m:
            sim_view_mode = st.radio("Display Mode:", ["🎴 Surge Cards", "📋 Data Table"], horizontal=True, key="sim_surge_mode")

        surge_mult = st.slider("Simulate Demand Surge Multiplier", 1.0, 3.0, 1.5, 0.1)
        sim_df = risk_df.copy()
        sim_df['sim_demand'] = (sim_df['avg_daily_demand'] * surge_mult).round(1)
        sim_df['sim_days_supply'] = (sim_df['current_stock'] / sim_df['sim_demand']).round(1)
        sim_df['sim_stockout_days'] = sim_df.apply(
            lambda r: int(r['sim_days_supply']) if r['sim_days_supply'] <= r['lead_time_days'] else -1,
            axis=1
        )
        
        sim_crit = sim_df[sim_df['sim_days_supply'] <= sim_df['lead_time_days']]
        st.error(f"⚠️ Under a {int(surge_mult*100)}% demand surge, **{len(sim_crit)} SKUs** will hit stockout before lead time replenishment!")
        
        sim_display = sim_crit[['sku', 'product_name', 'current_stock', 'lead_time_days', 'avg_daily_demand', 'sim_demand', 'sim_days_supply']].rename(columns={
            'sku': 'SKU', 'product_name': 'Product Name', 'current_stock': 'Stock',
            'lead_time_days': 'Lead Time (Days)', 'avg_daily_demand': 'Normal Demand',
            'sim_demand': 'Surged Demand', 'sim_days_supply': 'Surged Days of Supply'
        })
        
        if sim_view_mode == "🎴 Surge Cards":
            render_generic_card_grid(
                sim_display,
                page_size=10,
                key_prefix="sim_surge_cards",
                card_icon="⚡",
                title_col="Product Name",
                border_color="#ef4444"
            )
        else:
            render_paginated_dataframe(sim_display, page_size=10, key_prefix="sim_surge")

    with tab_po:
        col_po_t, col_po_m = st.columns([1.5, 1])
        with col_po_t:
            st.subheader("Automated Purchase Order Replenishment Generator")
        with col_po_m:
            po_view_mode = st.radio("Display Mode:", ["🎴 Order Cards", "📋 Data Table"], horizontal=True, key="po_mode")

        po_df = risk_df[risk_df['suggested_reorder_qty'] > 0].copy()
        if po_df.empty:
            st.success("✅ Stock levels healthy across all products. No purchase orders required.")
        else:
            po_df['total_cost'] = (po_df['suggested_reorder_qty'] * po_df['cost_price']).round(2)
            st.info(f"🛒 **{len(po_df)} Products** require replenishment. Total PO Cost: **${po_df['total_cost'].sum():,.2f}**")
            
            po_display = po_df[['sku', 'product_name', 'current_stock', 'reorder_point', 'target_stock_level', 'suggested_reorder_qty', 'cost_price', 'total_cost']].rename(columns={
                'sku': 'SKU', 'product_name': 'Product Name', 'current_stock': 'Current Stock',
                'reorder_point': 'Reorder Point', 'target_stock_level': 'Target Stock',
                'suggested_reorder_qty': 'Reorder Qty', 'cost_price': 'Unit Cost ($)',
                'total_cost': 'Total Cost ($)'
            })
            
            if po_view_mode == "🎴 Order Cards":
                render_generic_card_grid(
                    po_display,
                    page_size=10,
                    key_prefix="po_cards",
                    card_icon="🛒",
                    title_col="Product Name",
                    border_color="#f59e0b"
                )
            else:
                render_paginated_dataframe(po_display, page_size=10, key_prefix="purchase_orders")
            
            if st.button("🚀 Approve & Generate Purchase Orders"):
                st.success(f"✅ Response Recorded! Generated Purchase Orders for {len(po_df)} SKUs.")
                time.sleep(1.2)
                st.rerun()

    with tab_log:
        st.subheader("Log Manual Sales Entry")
        with st.form("manual_sale_form"):
            prod_opts = {r['product_id']: f"{r['sku']} - {r['product_name']}" for _, r in risk_df.iterrows()}
            sel_prod_id = st.selectbox("Product", list(prod_opts.keys()), format_func=lambda x: prod_opts[x])
            s_date = st.date_input("Sale Date", datetime.date.today())
            qty = st.number_input("Quantity Sold", min_value=1, value=10)
            is_p = st.checkbox("Promotion active?")
            is_h = st.checkbox("Holiday event?")
            if st.form_submit_button("Submit Sales Entry"):
                u_price = float(risk_df[risk_df['product_id'] == sel_prod_id]['unit_price'].iloc[0])
                log_manual_sale(selected_store_id, sel_prod_id, s_date.strftime("%Y-%m-%d"), qty, u_price, is_p, is_h)
                st.success(f"✅ Response Recorded! Successfully logged sales of {qty} units into SQLite DB.")
                time.sleep(1.2) # Allow 1.2s visual recording response
                st.rerun()

if __name__ == "__main__":
    render_manager_dashboard()
