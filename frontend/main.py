import streamlit as st
from sidebar import sidebar
from chat import chat_area

st.set_page_config(page_title="Config AI", layout="wide")

# Load global CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Top bar
st.markdown('<div class="topbar">🛠 Config AI</div>', unsafe_allow_html=True)

# Sidebar
sidebar()

# Chat
chat_area()
