import os
import sys
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Ensure root path is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.sales_service import process_sales_csv_upload
from forecasting.model import forecast_demand_ridge
from pages.login import render_login_page
from utils.helpers import apply_custom_css, render_header

def render_sales_upload_page():
    """Render Sales CSV Upload & Ingestion Page with interactive demand chart visualization."""
    apply_custom_css()
    user = st.session_state.get("user")
    
    if user is None:
        render_login_page()
        return
        
    if user.get("role") != "admin":
        st.error("🔒 Access Restricted: CSV Data Ingestion is reserved for Administrators.")
        return
        
    render_header("📥 Historical Sales CSV Data Ingestion", "Upload bulk transaction logs to retrain demand forecasting models")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### CSV Format Specifications:")
        st.markdown("""
        Uploaded CSV files must contain the following required columns:
        - `store_code`: E.g. `STR-001`, `STR-002`
        - `sku`: E.g. `SKU-ELEC-001`, `SKU-FASH-001`
        - `sale_date`: Format `YYYY-MM-DD`
        - `quantity_sold`: Integer $> 0$
        - `revenue`: Price float
        - `is_promotion`: `0` or `1`
        - `is_holiday`: `0` or `1`
        """)
        
    with col2:
        sample_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sample_sales.csv")
        if os.path.exists(sample_path):
            with open(sample_path, "rb") as f:
                st.download_button(
                    "📥 Download Sample Template CSV",
                    data=f,
                    file_name="sample_sales.csv",
                    mime="text/csv"
                )
            
    uploaded = st.file_uploader("Upload Sales CSV File", type=["csv"])
    if uploaded is not None:
        try:
            df = pd.read_csv(uploaded)
            st.write("### Dataset Preview:", df.head())
            
            btn_col1, btn_col2 = st.columns([1, 1])
            with btn_col1:
                ingest_btn = st.button("🚀 Process & Ingest Into SQLite DB", use_container_width=True)
            with btn_col2:
                graph_btn = st.button("📈 Show Demand Graph Below", use_container_width=True)
                
            if ingest_btn:
                inserted, skipped, msg = process_sales_csv_upload(df)
                if inserted > 0:
                    st.success(f"✅ Ingested {inserted} records into SQLite database! (Skipped {skipped} invalid rows)")
                    st.rerun()
                else:
                    st.error(f"❌ Ingestion failed: {msg}")
                    
            if graph_btn or st.session_state.get("show_upload_graph", False):
                st.session_state["show_upload_graph"] = True
                st.markdown("---")
                st.markdown("### 📈 Uploaded CSV Demand Forecast Curve")
                
                # Check required columns for plotting
                if 'sale_date' in df.columns and 'quantity_sold' in df.columns:
                    # Group sales by date
                    df_daily = df.groupby('sale_date', as_index=False)['quantity_sold'].sum().sort_values('sale_date')
                    if 'is_promotion' not in df_daily.columns:
                        df_daily['is_promotion'] = 0
                    if 'is_holiday' not in df_daily.columns:
                        df_daily['is_holiday'] = 0
                        
                    # Generate 5-day ML forecast predictions
                    fc_df = forecast_demand_ridge(df_daily, horizon=5)
                    
                    # Compute Summary Metrics
                    total_units = int(df_daily['quantity_sold'].sum())
                    avg_daily = round(float(df_daily['quantity_sold'].mean()), 1)
                    pred_sum = round(float(fc_df['predicted_demand'].sum()), 1)
                    
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.metric("Total CSV Ingest Volume", f"{total_units:,} units")
                    with m2:
                        st.metric("Average Daily Historical Sales", f"{avg_daily} units/day")
                    with m3:
                        st.metric("5-Day Forecast Demand Sum", f"{pred_sum} units")
                        
                    # Plotly Figure
                    fig = go.Figure()
                    
                    # 1. Historical Sales Trace
                    fig.add_trace(go.Scatter(
                        x=df_daily['sale_date'],
                        y=df_daily['quantity_sold'],
                        mode='lines+markers',
                        name='Uploaded CSV Sales',
                        line=dict(color='#38bdf8', width=3),
                        marker=dict(size=7, color='#38bdf8'),
                        hovertemplate='<b>Date</b>: %{x}<br><b>Units Sold</b>: %{y} units<extra></extra>'
                    ))
                    
                    # 2. Confidence Band
                    if not fc_df.empty:
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
                        
                        # Bridge point connection
                        fc_x = fc_df['forecast_date'].tolist()
                        fc_y = fc_df['predicted_demand'].tolist()
                        if not df_daily.empty:
                            fc_x = [df_daily['sale_date'].iloc[-1]] + fc_x
                            fc_y = [df_daily['quantity_sold'].iloc[-1]] + fc_y
                            
                        # 3. Forecast Trace
                        fig.add_trace(go.Scatter(
                            x=fc_x,
                            y=fc_y,
                            mode='lines+markers',
                            name='ML Predicted Demand (Ridge)',
                            line=dict(color='#818cf8', width=3, dash='dash'),
                            marker=dict(size=7, color='#c084fc'),
                            hovertemplate='<b>Forecast Date</b>: %{x}<br><b>Predicted Demand</b>: %{y} units<extra></extra>'
                        ))
                        
                    fig.update_layout(
                        title=dict(
                            text="📊 Historical Sales & 5-Day ML Demand Prediction Curve",
                            font=dict(size=18, color="#f8fafc")
                        ),
                        xaxis=dict(
                            title="Date",
                            showgrid=True,
                            gridcolor="rgba(255, 255, 255, 0.1)",
                            tickfont=dict(color="#cbd5e1")
                        ),
                        yaxis=dict(
                            title="Daily Units Sold / Predicted",
                            showgrid=True,
                            gridcolor="rgba(255, 255, 255, 0.1)",
                            tickfont=dict(color="#cbd5e1")
                        ),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1,
                            font=dict(color="#e2e8f0")
                        ),
                        margin=dict(l=40, r=40, t=60, b=40),
                        paper_bgcolor="rgba(15, 23, 42, 0.6)",
                        plot_bgcolor="rgba(15, 23, 42, 0.6)",
                        height=450
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("⚠️ Uploaded CSV file must contain `sale_date` and `quantity_sold` columns to plot demand graph.")
        except Exception as e:
            st.error(f"❌ Error reading CSV file: {str(e)}")

if __name__ == "__main__":
    render_sales_upload_page()
