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
