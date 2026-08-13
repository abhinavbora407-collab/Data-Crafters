import os
import sys
import pandas as pd
import streamlit as st

# Ensure root path is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.sales_service import process_sales_csv_upload
from pages.login import render_login_page
from utils.helpers import apply_custom_css, render_header

def render_sales_upload_page():
    """Render Sales CSV Upload & Ingestion Page."""
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
        - `sku`: E.g. `SKU-ELEC-001`, `SKU-FASH-002`
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
            
            if st.button("🚀 Process & Ingest Into SQLite DB"):
                inserted, skipped, msg = process_sales_csv_upload(df)
                if inserted > 0:
                    st.success(f"✅ Ingested {inserted} records into SQLite database! (Skipped {skipped} invalid rows)")
                    st.rerun()
                else:
                    st.error(f"❌ Ingestion failed: {msg}")
        except Exception as e:
            st.error(f"❌ Error reading CSV file: {str(e)}")

if __name__ == "__main__":
    render_sales_upload_page()
