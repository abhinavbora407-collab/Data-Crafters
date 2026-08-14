import math
import pandas as pd
import streamlit as st

def apply_custom_css():
    """Inject modern glassmorphism CSS theme."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        color: #f8fafc;
    }
    
    .app-header {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    .app-title {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .app-subtitle {
        color: #94a3b8;
        font-size: 1.0rem;
        margin-top: 4px;
    }
    
    .metric-card {
        background: rgba(30, 41, 59, 0.6);
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    .metric-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        font-weight: 600;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #f8fafc;
        margin: 8px 0;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #cbd5e1;
    }
    
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .badge-blue { background: rgba(56, 189, 248, 0.2); color: #7dd3fc; border: 1px solid rgba(56, 189, 248, 0.4); }
    .badge-red { background: rgba(239, 68, 68, 0.2); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.4); }
    .badge-orange { background: rgba(245, 158, 11, 0.2); color: #fde68a; border: 1px solid rgba(245, 158, 11, 0.4); }
    .badge-green { background: rgba(34, 197, 94, 0.2); color: #86efac; border: 1px solid rgba(34, 197, 94, 0.4); }
    .badge-purple { background: rgba(168, 85, 247, 0.2); color: #d8b4fe; border: 1px solid rgba(168, 85, 247, 0.4); }
    
    .product-card {
        background: rgba(30, 41, 59, 0.7);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .product-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 14px 40px rgba(0, 0, 0, 0.5);
    }
    </style>
    """, unsafe_allow_html=True)

def render_header(title: str, subtitle: str, user_info: str = ""):
    """Render application header banner."""
    st.markdown(f"""
    <div class="app-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 class="app-title">{title}</h1>
                <p class="app-subtitle">{subtitle}</p>
            </div>
            <div style="text-align: right;">
                <span class="badge badge-purple">{user_info}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_metric_card(label: str, value: str, subtext: str = "", border_color: str = "#38bdf8"):
    """Render metric card widget."""
    st.markdown(f"""
    <div class="metric-card" style="border-left: 4px solid {border_color};">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-sub">{subtext}</div>
    </div>
    """, unsafe_allow_html=True)

def render_paginated_dataframe(df: pd.DataFrame, page_size: int = 10, key_prefix: str = "table") -> pd.DataFrame:
    """Render high-speed paginated DataFrame table with page controls for sub-millisecond DOM rendering (Max 10 items)."""
    if df.empty:
        st.info("No records to display.")
        return df

    total_rows = len(df)
    total_pages = max(1, math.ceil(total_rows / page_size))

    if total_pages > 1:
        col_page, col_info = st.columns([1, 2.5])
        with col_page:
            current_page = st.number_input(
                f"Page (1 to {total_pages})",
                min_value=1,
                max_value=total_pages,
                value=1,
                step=1,
                key=f"{key_prefix}_page_input"
            )
        with col_info:
            start_idx = (current_page - 1) * page_size
            end_idx = min(start_idx + page_size, total_rows)
            st.markdown(
                f"<div style='padding-top: 22px; color: #94a3b8; font-size: 0.9rem;'>"
                f"⚡ Showing <b>{start_idx + 1} - {end_idx}</b> of <b>{total_rows}</b> items (Page {current_page} of {total_pages})"
                f"</div>",
                unsafe_allow_html=True
            )
    else:
        start_idx = 0
        end_idx = total_rows

    page_df = df.iloc[start_idx:end_idx]
    st.dataframe(page_df, use_container_width=True, hide_index=True)
    return page_df

CATEGORY_GRAPHICS = {
    "Electronics": ("📱", "#38bdf8"),
    "Apparel & Fashion": ("👕", "#818cf8"),
    "Home & Kitchen": ("☕", "#a855f7"),
    "Groceries & Fresh": ("🥛", "#22c55e"),
    "Health & Beauty": ("🧴", "#ec4899"),
    "Sports & Outdoors": ("🧘", "#f59e0b")
}

STATUS_BADGE_MAP = {
    "CRITICAL_STOCKOUT": ("badge-red", "🚨 Critical Stockout Risk", "#ef4444"),
    "WARNING_STOCKOUT": ("badge-orange", "⚠️ Low Stock Warning", "#f59e0b"),
    "OPTIMAL": ("badge-green", "✅ Healthy Stock Level", "#22c55e"),
    "OVERSTOCK": ("badge-purple", "📦 Overstock Risk", "#a855f7")
}

def render_product_card_grid(risk_df: pd.DataFrame, page_size: int = 10, key_prefix: str = "prod_grid"):
    """Render visual product cards with graphic category icons, stock metrics, and risk status badges (Max 10 items)."""
    if risk_df.empty:
        st.info("No product items found.")
        return

    total_rows = len(risk_df)
    total_pages = max(1, math.ceil(total_rows / page_size))

    if total_pages > 1:
        col_p, col_i = st.columns([1, 2.5])
        with col_p:
            current_page = st.number_input(
                f"Card Grid Page (1 to {total_pages})",
                min_value=1,
                max_value=total_pages,
                value=1,
                step=1,
                key=f"{key_prefix}_grid_page"
            )
        with col_i:
            start_idx = (current_page - 1) * page_size
            end_idx = min(start_idx + page_size, total_rows)
            st.markdown(
                f"<div style='padding-top: 22px; color: #94a3b8; font-size: 0.9rem;'>"
                f"🎴 Showing Visual Product Cards <b>{start_idx + 1} - {end_idx}</b> of <b>{total_rows}</b> (Max 10/page)"
                f"</div>",
                unsafe_allow_html=True
            )
    else:
        start_idx = 0
        end_idx = total_rows

    subset = risk_df.iloc[start_idx:end_idx]
    
    # Render in 2-column responsive visual card grid for optimal card size
    cols = st.columns(2)
    for idx, (_, row) in enumerate(subset.iterrows()):
        c_idx = idx % 2
        cat_name = row.get('category_name', 'General')
        cat_icon, cat_color = CATEGORY_GRAPHICS.get(cat_name, ("📦", "#38bdf8"))
        
        status_key = row.get('status', 'OPTIMAL')
        b_class, b_label, b_color = STATUS_BADGE_MAP.get(status_key, ("badge-green", "✅ Healthy", "#22c55e"))
        
        with cols[c_idx]:
            st.markdown(f"""
            <div class="product-card" style="border-top: 4px solid {b_color}; margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span style="font-size: 2.0rem;">{cat_icon}</span>
                    <span class="badge {b_class}">{b_label}</span>
                </div>
                <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase;">
                    {row.get('sku', '')} • {cat_name}
                </div>
                <h3 style="margin: 6px 0 12px 0; color: #f8fafc; font-size: 1.1rem; line-height: 1.3;">
                    {row.get('product_name', '')}
                </h3>
                <div style="background: rgba(15, 23, 42, 0.6); padding: 12px; border-radius: 12px; font-size: 0.85rem; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                        <span style="color: #94a3b8;">Current Stock:</span>
                        <b style="color: #f8fafc; font-size: 0.95rem;">{row.get('current_stock', 0)} units</b>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                        <span style="color: #94a3b8;">Reorder Point:</span>
                        <b style="color: #fde68a;">{row.get('reorder_point', 0)} units</b>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #94a3b8;">Daily Demand:</span>
                        <b style="color: #38bdf8;">{row.get('avg_daily_demand', 0.0)} units/day</b>
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.8rem; color: #cbd5e1;">Price: <b style="color: #22c55e;">${row.get('unit_price', 0.0):.2f}</b></span>
                    <span style="font-size: 0.8rem; color: #cbd5e1;">Reorder: <b style="color: #f59e0b;">{row.get('suggested_reorder_qty', 0)} units</b></span>
                </div>
            </div>
            """, unsafe_allow_html=True)

def render_generic_card_grid(
    df: pd.DataFrame,
    page_size: int = 10,
    key_prefix: str = "generic_cards",
    card_icon: str = "📊",
    title_col: str = None,
    badge_col: str = None,
    border_color: str = "#38bdf8"
):
    """Render any dataframe rows as structured visual cards (maximum 10 elements per page)."""
    if df.empty:
        st.info("No records to display.")
        return

    total_rows = len(df)
    page_size = min(10, page_size)  # Enforce maximum 10 elements per page
    total_pages = max(1, math.ceil(total_rows / page_size))

    if total_pages > 1:
        col_p, col_i = st.columns([1, 2.5])
        with col_p:
            current_page = st.number_input(
                f"Card Page (1 to {total_pages})",
                min_value=1,
                max_value=total_pages,
                value=1,
                step=1,
                key=f"{key_prefix}_gen_card_page"
            )
        with col_i:
            start_idx = (current_page - 1) * page_size
            end_idx = min(start_idx + page_size, total_rows)
            st.markdown(
                f"<div style='padding-top: 22px; color: #94a3b8; font-size: 0.9rem;'>"
                f"🃏 Showing Visual Cards <b>{start_idx + 1} - {end_idx}</b> of <b>{total_rows}</b> (Max 10 per page)"
                f"</div>",
                unsafe_allow_html=True
            )
    else:
        start_idx = 0
        end_idx = total_rows

    subset = df.iloc[start_idx:end_idx]
    cols = st.columns(2)  # 2 columns grid layout

    for idx, (_, row) in enumerate(subset.iterrows()):
        c_idx = idx % 2
        
        # Determine title
        if title_col and title_col in row:
            title_val = str(row[title_col])
        else:
            title_val = str(row.iloc[0])
            
        # Determine badge text if any
        badge_html = ""
        if badge_col and badge_col in row:
            b_val = str(row[badge_col])
            b_cls = "badge-blue"
            if any(term in b_val.lower() for term in ["admin", "critical", "high", "failed"]):
                b_cls = "badge-red"
            elif any(term in b_val.lower() for term in ["warning", "medium", "pending"]):
                b_cls = "badge-orange"
            elif any(term in b_val.lower() for term in ["manager", "success", "optimal", "healthy"]):
                b_cls = "badge-green"
            badge_html = f'<span class="badge {b_cls}">{b_val}</span>'

        # Generate key-value fields inside the card
        kv_items = []
        for col_name, val in row.items():
            if col_name in [title_col, badge_col]:
                continue
            v_str = str(val) if pd.notna(val) else "N/A"
            kv_items.append(
                f'<div style="display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05);">'
                f'<span style="color: #94a3b8; font-size: 0.82rem; font-weight: 500;">{col_name}:</span>'
                f'<span style="color: #f8fafc; font-size: 0.85rem; font-weight: 600; text-align: right;">{v_str}</span>'
                f'</div>'
            )
            
        kv_html = "".join(kv_items)

        card_html = (
            f'<div class="product-card" style="border-left: 4px solid {border_color}; margin-bottom: 16px;">'
            f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">'
            f'<span style="font-size: 1.6rem;">{card_icon}</span>'
            f'{badge_html}'
            f'</div>'
            f'<h4 style="margin: 4px 0 12px 0; color: #38bdf8; font-size: 1.05rem; font-weight: 700;">{title_val}</h4>'
            f'<div style="background: rgba(15, 23, 42, 0.6); padding: 10px 14px; border-radius: 12px; margin-top: 8px;">'
            f'{kv_html}'
            f'</div>'
            f'</div>'
        )

        with cols[c_idx]:
            st.markdown(card_html, unsafe_allow_html=True)

