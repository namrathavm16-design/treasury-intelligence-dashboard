import streamlit as st
import pandas as pd
import feedparser
import numpy as np
from datetime import datetime

# ================= SESSION STATE =================
if "risk_history" not in st.session_state:
    st.session_state.risk_history = []

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Treasury Intelligence Dashboard", layout="wide")

st.markdown("""
<style>
.block-container { padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
st.sidebar.header("Monitoring Controls")

scenario = st.sidebar.selectbox(
    "Stress Scenario",
    ["Base Case", "Hawkish Fed", "Geopolitical Escalation"]
)

selected_category = st.sidebar.multiselect(
    "Filter by Risk Category",
    ["FX", "Interest Rates", "Geopolitics", "Other"],
    default=["FX", "Interest Rates", "Geopolitics", "Other"]
)

# ================= HELPER FUNCTIONS =================
def classify_headline(h):
    h = h.lower()
    if any(k in h for k in ["dollar", "euro", "yen", "currency", "fx", "forex"]):
        return "FX"
    if any(k in h for k in ["rate", "rates", "interest", "yield", "bond", "fed", "ecb"]):
        return "Interest Rates"
    if any(k in h for k in ["war", "conflict", "tensions", "sanctions", "geopolitics"]):
        return "Geopolitics"
    return "Other"

def decay_weight(published_time):
    age = (datetime.now() - published_time).total_seconds() / 60
    if age <= 30:
