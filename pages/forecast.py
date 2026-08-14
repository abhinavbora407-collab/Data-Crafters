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
    if stores_df.empty:
        st.error("No store branches found in database.")
        return
        
    col_s, col_p, col_btn = st.columns([1.2, 1.5, 1])
    
    with col_s:
        if user.get('role') == 'manager' and user.get('store_id'):
            s_id = user['store_id']
            st.info(f"📍 Store Scope: **{user.get('store_name', 'Store Branch')}**")
        else:
            s_opts = {r['id']: r['store_name'] for _, r in stores_df.iterrows()}
            s_id = st.selectbox("Select Store Branch", list(s_opts.keys()), format_func=lambda x: s_opts[x], key="fc_store")
            
    prods_df = query_df("SELECT id, sku, product_name, reorder_point FROM products WHERE id IN (SELECT product_id FROM inventory WHERE store_id = ?) ORDER BY sku ASC;", (s_id,))
    if prods_df.empty:
        prods_df = query_df("SELECT id, sku, product_name, reorder_point FROM products ORDER BY sku ASC;")
        
    if prods_df.empty:
        st.warning("⚠️ No products catalog available.")
        return
        
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

    # Load Product Data safely
    selected_prod = prods_df[prods_df['id'] == p_id]
    if selected_prod.empty:
        st.warning("Please select a valid product SKU.")
        return
    p_data = dict(selected_prod.iloc[0])

    # Load Forecast & Historical Sales Data (Auto-generate if missing)
    fc_df = query_df(
        "SELECT forecast_date, predicted_demand, lower_bound, upper_bound, model_type FROM forecasts WHERE store_id = ? AND product_id = ? ORDER BY forecast_date ASC;",
        (s_id, p_id)
    )
    hist_df = query_df(
        "SELECT sale_date, quantity_sold FROM sales_history WHERE store_id = ? AND product_id = ? ORDER BY sale_date ASC;",
        (s_id, p_id)
    )
    
    if fc_df.empty or hist_df.empty:
        with st.spinner("Generating 14-day sales history & ML demand forecasts..."):
            generate_store_forecasts(14)
            fc_df = query_df(
                "SELECT forecast_date, predicted_demand, lower_bound, upper_bound, model_type FROM forecasts WHERE store_id = ? AND product_id = ? ORDER BY forecast_date ASC;",
                (s_id, p_id)
            )
            hist_df = query_df(
                "SELECT sale_date, quantity_sold FROM sales_history WHERE store_id = ? AND product_id = ? ORDER BY sale_date ASC;",
                (s_id, p_id)
            )

    # Calculate Overview Metrics
    last_hist_qty = hist_df['quantity_sold'].iloc[-1] if not hist_df.empty else 0
    pred_total_14d = round(float(fc_df['predicted_demand'].sum()), 1) if not fc_df.empty else 0.0
    pred_avg_daily = round(float(fc_df['predicted_demand'].mean()), 1) if not fc_df.empty else 0.0
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Latest Historical Daily Sales", f"{last_hist_qty} units")
    with m2:
        st.metric("Predicted 14-Day Demand Sum", f"{pred_total_14d} units")
    with m3:
        st.metric("Avg Daily Forecast Demand", f"{pred_avg_daily} units/day")
    with m4:
        st.metric("Reorder Threshold", f"{p_data['reorder_point']} units")

    st.markdown("---")

    # Plotly Forecast Chart
    fig = go.Figure()
    
    # 1. Historical Sales Curve (Cyan Solid Line)
    if not hist_df.empty:
        fig.add_trace(go.Scatter(
            x=hist_df['sale_date'],
            y=hist_df['quantity_sold'],
            mode='lines+markers',
            name='Historical Sales',
            line=dict(color='#38bdf8', width=3),
            marker=dict(size=6, color='#38bdf8'),
            hovertemplate='<b>Historical Date</b>: %{x}<br><b>Quantity Sold</b>: %{y} units<extra></extra>'
        ))

    # 2. Forecast Curve & Confidence Interval (Violet Dashed Line)
    if not fc_df.empty:
        # Confidence Band Fill
        fig.add_trace(go.Scatter(
            x=fc_df['forecast_date'].tolist() + fc_df['forecast_date'].tolist()[::-1],
            y=fc_df['upper_bound'].tolist() + fc_df['lower_bound'].tolist()[::-1],
            fill='toself',
            fillcolor='rgba(129, 140, 248, 0.20)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            showlegend=True,
            name='95% Confidence Band'
        ))
        
        # Connect last historical data point to first forecast data point if historical data exists
        fc_x = fc_df['forecast_date'].tolist()
        fc_y = fc_df['predicted_demand'].tolist()
        if not hist_df.empty:
            fc_x = [hist_df['sale_date'].iloc[-1]] + fc_x
            fc_y = [hist_df['quantity_sold'].iloc[-1]] + fc_y

        fig.add_trace(go.Scatter(
            x=fc_x,
            y=fc_y,
            mode='lines+markers',
            name='ML Predicted Demand (Ridge)',
            line=dict(color='#818cf8', width=3, dash='dash'),
            marker=dict(size=6, color='#c084fc'),
            hovertemplate='<b>Forecast Date</b>: %{x}<br><b>Predicted Demand</b>: %{y} units<extra></extra>'
        ))

    # Reorder Point Reference Line (Amber Horizontal Line)
    fig.add_hline(
        y=p_data['reorder_point'],
        line_dash="dot",
        line_color="#f59e0b",
        line_width=2,
        annotation_text=f"Reorder Threshold ({p_data['reorder_point']} units)",
        annotation_position="top left",
        annotation_font=dict(color="#f59e0b", size=12)
    )

    fig.update_layout(
        title=dict(
            text=f"📊 Demand Forecast Curve: {p_data['product_name']} ({p_data['sku']})",
            font=dict(size=18, color="#f8fafc")
        ),
        xaxis=dict(
            title="Date",
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.1)",
            tickfont=dict(color="#cbd5e1")
        ),
        yaxis=dict(
            title="Daily Demand (Units)",
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.1)",
            tickfont=dict(color="#cbd5e1")
        ),
        template="plotly_dark",
        paper_bgcolor='#0f172a',
        plot_bgcolor='rgba(30, 41, 59, 0.6)',
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#f8fafc")
        ),
        margin=dict(l=40, r=40, t=80, b=40)
    )
    
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    render_forecast_page()
