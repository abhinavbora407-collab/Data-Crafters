import os
import sys
import streamlit as st

# Ensure root path is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ai_chat_service import process_ai_query
from pages.login import render_login_page
from utils.helpers import apply_custom_css, render_header

def render_ai_chat_page():
    """Render Interactive AI Inventory & Forecasting Assistant Page."""
    apply_custom_css()
    user = st.session_state.get("user")
    
    if user is None:
        render_login_page()
        return
        
    render_header("🤖 AI Inventory & Forecasting Assistant", f"Live AI Data Copilot • Active User: {user['username']}")
    
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = [
            {
                "role": "assistant",
                "content": (
                    f"Hello **{user['username']}**! 👋 I am your AI Inventory & Demand Forecasting Assistant.\n\n"
                    f"Ask me anything about your store stock levels, critical stockout risks, recommended purchase orders, or ML demand predictions!"
                )
            }
        ]
        
    # Quick action prompt pills
    st.markdown("##### 💡 Suggested AI Prompts:")
    p_col1, p_col2, p_col3, p_col4 = st.columns(4)
    
    prompt_to_submit = None
    with p_col1:
        if st.button("🚨 Critical Stockout Risks", use_container_width=True, key="p1"):
            prompt_to_submit = "Which items are at critical stockout risk?"
    with p_col2:
        if st.button("🛒 Reorder Recommendations", use_container_width=True, key="p2"):
            prompt_to_submit = "Show me reorder recommendations and purchase orders."
    with p_col3:
        if st.button("📈 5-Day Demand Forecast", use_container_width=True, key="p3"):
            prompt_to_submit = "Show me the 5-day demand forecast breakdown."
    with p_col4:
        if st.button("🎯 Forecast Accuracy (MAPE)", use_container_width=True, key="p4"):
            prompt_to_submit = "What is our ML forecast accuracy MAPE and RMSE?"
            
    st.markdown("---")
    
    # Display Chat History
    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Process user chat input or quick prompt click
    user_input = st.chat_input("Ask AI Assistant about stock levels, demand predictions, or purchase orders...")
    
    active_prompt = prompt_to_submit or user_input
    if active_prompt:
        # Append User Message
        st.session_state["chat_messages"].append({"role": "user", "content": active_prompt})
        with st.chat_message("user"):
            st.markdown(active_prompt)
            
        # Generate & Append AI Assistant Response
        with st.chat_message("assistant"):
            with st.spinner("🤖 Analyzing real-time SQLite database & forecasting models..."):
                response_text = process_ai_query(active_prompt, current_user=user)
                st.markdown(response_text)
                
        st.session_state["chat_messages"].append({"role": "assistant", "content": response_text})
        st.rerun()
        
    # Option to clear chat conversation
    if st.button("🧹 Clear Chat History", help="Reset conversation window"):
        st.session_state["chat_messages"] = [
            {
                "role": "assistant",
                "content": f"Chat history cleared. How can I assist you today, **{user['username']}**?"
            }
        ]
        st.rerun()

if __name__ == "__main__":
    render_ai_chat_page()