import os
import sys
import streamlit as st
import plotly.express as px

# Ensure root path is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import query_df
from services.accuracy_service import get_accuracy_logs_summary, evaluate_forecast_accuracy
from pages.login import render_login_page
from utils.helpers import apply_custom_css, render_header, render_metric_card, render_paginated_dataframe, render_generic_card_grid

def render_accuracy_page():
    """Render Forecast Accuracy & Model Evaluation Metrics (MAPE / RMSE)."""
    apply_custom_css()
    user = st.session_state.get("user")
    
    if user is None:
        render_login_page()
        return
        
    render_header("🎯 Forecast Accuracy & Model Evaluation", "Empirical validation of ML Ridge regression predictive error metrics (MAPE, RMSE, MAE)")
    
    col_btn, _ = st.columns([1, 2])
    with col_btn:
        if st.button("🔄 Re-Calculate Forecast Accuracy Logs", key="btn_eval_acc"):
            with st.spinner("Evaluating MAPE & RMSE across all store-product pairs..."):
                cnt = evaluate_forecast_accuracy()
                st.success(f"Evaluated {cnt} accuracy log records!")
                st.rerun()

    acc_df = query_df("""
    SELECT l.evaluation_date, l.mape, l.rmse, l.mae, l.sample_size, s.store_name, c.category_name, p.sku, p.product_name
    FROM forecast_accuracy_logs l
    JOIN stores s ON l.store_id = s.id
    JOIN products p ON l.product_id = p.id
    JOIN categories c ON p.category_id = c.id
    ORDER BY l.evaluation_date DESC, l.mape ASC;
    """)
    
    if acc_df.empty:
        st.info("ℹ️ No accuracy logs evaluated yet. Run forecast generator to calculate MAPE/RMSE metrics!")
        return

    # Metrics Overview
    avg_mape = round(float(acc_df['mape'].mean()), 2)
    avg_rmse = round(float(acc_df['rmse'].mean()), 2)
    avg_mae = round(float(acc_df['mae'].mean()), 2)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_metric_card("Network Avg MAPE", f"{avg_mape}%", "Mean Absolute % Error", "#38bdf8")
    with c2: render_metric_card("Network Avg RMSE", f"{avg_rmse}", "Root Mean Sq Error", "#818cf8")
    with c3: render_metric_card("Network Avg MAE", f"{avg_mae}", "Mean Absolute Error", "#22c55e")
    with c4: render_metric_card("Evaluated Streams", str(len(acc_df)), "Store-Product Pairs", "#c084fc")

    st.markdown("---")
    
    col_chart, col_dist = st.columns([1.3, 1])
    with col_chart:
        st.subheader("MAPE Error Rate by Product Category")
        fig_cat = px.box(acc_df, x="category_name", y="mape", color="category_name", template="plotly_dark", labels={"mape": "MAPE (%)", "category_name": "Category"})
        fig_cat.update_layout(paper_bgcolor='rgba(15, 23, 42, 0)', plot_bgcolor='rgba(30, 41, 59, 0.5)', height=380, showlegend=False)
        st.plotly_chart(fig_cat, use_container_width=True)
        
    with col_dist:
        st.subheader("MAPE Error Distribution")
        fig_hist = px.histogram(acc_df, x="mape", nbins=15, template="plotly_dark", color_discrete_sequence=['#38bdf8'])
        fig_hist.update_layout(paper_bgcolor='rgba(15, 23, 42, 0)', plot_bgcolor='rgba(30, 41, 59, 0.5)', height=380)
        st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("---")
    
    col_acc_t, col_acc_m = st.columns([1.5, 1])
    with col_acc_t:
        st.subheader("Accuracy Log Analytics & Performance Stream Metrics")
    with col_acc_m:
        acc_view_mode = st.radio("Display Mode:", ["🎴 Accuracy Cards", "📋 Data Table"], horizontal=True, key="acc_mode")

    # Filter controls to streamline streams table size
    col_store_f, col_limit_f = st.columns([1, 1])
    with col_store_f:
        store_opts = ["All Stores"] + list(acc_df['store_name'].unique())
        selected_store_filter = st.selectbox("Filter Store Branch", store_opts, key="acc_store_filter")
        
    with col_limit_f:
        limit_opts = ["All Streams", "Top 15 Most Accurate Streams (Lowest MAPE)", "Top 15 Highest Error Streams (Highest MAPE)"]
        selected_limit_filter = st.selectbox("Filter Mode", limit_opts, key="acc_limit_filter")
        
    filtered_df = acc_df.copy()
    if selected_store_filter != "All Stores":
        filtered_df = filtered_df[filtered_df['store_name'] == selected_store_filter]
        
    if "Lowest MAPE" in selected_limit_filter:
        filtered_df = filtered_df.sort_values("mape", ascending=True).head(15)
    elif "Highest MAPE" in selected_limit_filter:
        filtered_df = filtered_df.sort_values("mape", ascending=False).head(15)
        
    display_acc_df = filtered_df[['evaluation_date', 'store_name', 'category_name', 'sku', 'product_name', 'mape', 'rmse', 'sample_size']].rename(columns={
        'evaluation_date': 'Eval Date', 'store_name': 'Store', 'category_name': 'Category',
        'sku': 'SKU', 'product_name': 'Product Name', 'mape': 'MAPE (%)', 'rmse': 'RMSE', 'sample_size': 'Days Evaluated'
    })
    
    if acc_view_mode == "🎴 Accuracy Cards":
        render_generic_card_grid(
            display_acc_df,
            page_size=10,
            key_prefix="acc_cards",
            card_icon="🎯",
            title_col="Product Name",
            badge_col="Category",
            border_color="#38bdf8"
        )
    else:
        render_paginated_dataframe(
            display_acc_df,
            page_size=10,
            key_prefix="acc_logs_table"
        )

if __name__ == "__main__":
    render_accuracy_page()
