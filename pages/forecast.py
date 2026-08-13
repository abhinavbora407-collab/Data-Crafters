import os
import sys
import datetime
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Ensure root path is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import query_df
from services.forecast_service import generate_store_forecasts
from pages.login import render_login_page
from utils.helpers import apply_custom_css, render_header

def render_forecast_page():
    """Render Demand Forecast Engine Page with multi-step ML predictions."""
    apply_custom_css()
    user = st.session_state.get("user")
    
    if user is None:
        render_login_page()
        return
        
    render_header("📈 ML Demand Forecast Engine", "14-day Ridge regression predictive curves with 95% confidence bounds")
    
    stores_df = query_df("SELECT id, store_name FROM stores ORDER BY store_name;")
    col_s, col_p, col_btn = st.columns([1.2, 1.5, 1])
    
    with col_s:
        if user['role'] == 'manager' and user.get('store_id'):
            s_id = user['store_id']
            st.info(f"📍 Store Scope: **{user['store_name']}**")
        else:
            s_opts = {r['id']: r['store_name'] for _, r in stores_df.iterrows()}
            s_id = st.selectbox("Select Store Branch", list(s_opts.keys()), format_func=lambda x: s_opts[x], key="fc_store")
            
    prods_df = query_df("SELECT id, sku, product_name, reorder_point FROM products WHERE id IN (SELECT product_id FROM inventory WHERE store_id = ?);", (s_id,))
    
    with col_p:
        p_opts = {r['id']: f"{r['sku']} - {r['product_name']}" for _, r in prods_df.iterrows()}
        p_id = st.selectbox("Select Product SKU", list(p_opts.keys()), format_func=lambda x: p_opts[x], key="fc_prod")
        
    with col_btn:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🚀 Re-Run ML Forecast Engine", key="btn_run_fc"):
            with st.spinner("Training Ridge Regression Time-Series Model..."):
                cnt = generate_store_forecasts(14)
                st.success(f"Generated {cnt} predictions across network!")
                st.rerun()

    # Load Forecast Data
    fc_df = query_df(
        "SELECT forecast_date, predicted_demand, lower_bound, upper_bound, model_type FROM forecasts WHERE store_id = ? AND product_id = ? ORDER BY forecast_date ASC;",
        (s_id, p_id)
    )
    hist_df = query_df(
        "SELECT sale_date, quantity_sold FROM sales_history WHERE store_id = ? AND product_id = ? ORDER BY sale_date DESC LIMIT 30;",
        (s_id, p_id)
    )
    
    p_data = dict(prods_df[prods_df['id'] == p_id].iloc[0])
    
    # Plotly Forecast Chart
    fig = go.Figure()
    if not hist_df.empty:
        hist_df = hist_df.sort_values("sale_date")
        fig.add_trace(go.Scatter(
            x=hist_df['sale_date'], y=hist_df['quantity_sold'], mode='lines+markers',
            name='Historical Sales', line=dict(color='#38bdf8', width=2)
        ))
        
    if not fc_df.empty:
        # Confidence Band
        fig.add_trace(go.Scatter(
            x=fc_df['forecast_date'].tolist() + fc_df['forecast_date'].tolist()[::-1],
            y=fc_df['upper_bound'].tolist() + fc_df['lower_bound'].tolist()[::-1],
            fill='toself', fillcolor='rgba(129, 140, 248, 0.15)',
            line=dict(color='rgba(255,255,255,0)'), hoverinfo="skip", showlegend=True, name='95% Confidence Band'
        ))
        fig.add_trace(go.Scatter(
            x=fc_df['forecast_date'], y=fc_df['predicted_demand'], mode='lines+markers',
            name='ML Predicted Demand', line=dict(color='#818cf8', width=3, dash='dash')
        ))
        
    fig.add_hline(
        y=p_data['reorder_point'], line_dash="dot", line_color="#f59e0b",
        annotation_text=f"Reorder Threshold ({p_data['reorder_point']} units)"
    )
    
    fig.update_layout(
        title=f"Demand Curve: {p_data['product_name']} ({p_data['sku']})",
        xaxis_title="Date", yaxis_title="Daily Units", template="plotly_dark",
        paper_bgcolor='rgba(15, 23, 42, 0)', plot_bgcolor='rgba(30, 41, 59, 0.5)', height=450
    )
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    render_forecast_page()
