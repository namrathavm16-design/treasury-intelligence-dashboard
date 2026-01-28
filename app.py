import streamlit as st

st.set_page_config(
    page_title="Treasury Intelligence Dashboard",
    layout="wide"
)

st.title("Treasury Intelligence Dashboard")
st.subheader("Live Macro-Financial Monitoring System")

st.metric("Today's Treasury Risk Score", "42", delta="Stable")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("FX Risk", "Low")

with col2:
    st.metric("Interest Rate Risk", "Medium")

with col3:
    st.metric("Liquidity Risk", "Low")

st.sidebar.header("Monitoring Controls")
st.sidebar.selectbox(
    "Region Focus",
    ["Global", "United States", "Europe", "Asia"]
)

st.write("System status: Initializing")
st.subheader("Latest Relevant Financial News")

import pandas as pd

news_data = pd.DataFrame({
    "Time": ["09:00", "11:30", "14:15"],
    "Headline": [
        "US inflation comes in higher than expected",
        "ECB officials signal pause in rate hikes",
        "Oil prices jump amid Middle East tensions"
    ],
    "Category": ["Inflation", "Interest Rates", "Geopolitics"],
    "Preliminary Impact": ["High", "Medium", "High"]
})

st.dataframe(news_data, use_container_width=True)

