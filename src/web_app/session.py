# src/web_app/session.py
import streamlit as st
from datetime import datetime

def init_session():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "portfolio_rows" not in st.session_state:
        st.session_state.portfolio_rows = []

    if "goal_inputs" not in st.session_state:
        st.session_state.goal_inputs = {
            "target_amount": 10000.0,
            "months": 12,
            "monthly_contribution": 500.0,
            "annual_return_pct": 5.0,
        }

def add_chat_message(role: str, content: str, sources=None, agent=None, payload=None):
    if sources is None:
        sources = []
    st.session_state.chat_history.append(
        {
            "role": role,
            "content": content,
            "sources": sources,
            "agent": agent,
            "payload": payload or {},
            "time": datetime.now(),
        }
    )
