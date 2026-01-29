import streamlit as st
# Initialize risk history storage
if "risk_history" not in st.session_state:
    st.session_state.risk_history = []

if "last_recorded_minute" not in st.session_state:
    st.session_state.last_recorded_minute = None

st.set_page_config(
    page_title="Treasury Intelligence Dashboard",
    layout="wide"
)

st.title("Treasury Intelligence Dashboard")
st.subheader("Live Macro-Financial Monitoring System")
st.markdown("---")
from datetime import datetime
st.caption(f"Last updated: {datetime.now().strftime('%d %b %Y, %H:%M')}")

st.metric("Today's Treasury Risk Score", "42", delta="Stable")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("FX Risk", "-")

with col2:
    st.metric("Interest Rate Risk", "-")

with col3:
    st.metric("Liquidity Risk", "-")

st.sidebar.header("Monitoring Controls")
st.sidebar.selectbox(
    "Region Focus",
    ["Global", "United States", "Europe", "Asia"]
)
selected_category = st.sidebar.multiselect(
    "Filter by Risk Category",
    ["FX", "Interest Rates", "Geopolitics", "Other"],
    default=["FX", "Interest Rates", "Geopolitics", "Other"]
)

st.write("System status: Initializing")
st.subheader("Latest Relevant Financial News")

import pandas as pd
import feedparser

# Reuters business RSS feed
rss_url = "https://finance.yahoo.com/rss/topstories"

feed = feedparser.parse(rss_url)
st.write("Number of news items fetched:", len(feed.entries))
def classify_headline(headline):
    headline = headline.lower()

    fx_keywords = ["dollar", "euro", "yen", "currency", "fx", "forex"]
    rate_keywords = ["rate", "rates", "interest", "yield", "bond", "fed", "ecb"]
    geo_keywords = ["war", "conflict", "tensions", "sanctions", "geopolitics"]

    if any(word in headline for word in fx_keywords):
        return "FX"
    elif any(word in headline for word in rate_keywords):
        return "Interest Rates"
    elif any(word in headline for word in geo_keywords):
        return "Geopolitics"
    else:
        return "Other"

news_items = []

for entry in feed.entries[:10]:
    news_items.append({
        "Headline": entry.title,
        "Published": entry.published if "published" in entry else "—",
        "Source": "Yahoo Finance",
        "Category": classify_headline(entry.title)
    })


news_df = pd.DataFrame(news_items)
# Count category occurrences
category_counts = news_df["Category"].value_counts()
def risk_level(count):
    if count >= 4:
        return "High"
    elif count >= 2:
        return "Medium"
    else:
        return "Low"

fx_risk = risk_level(category_counts.get("FX", 0))
rate_risk = risk_level(category_counts.get("Interest Rates", 0))

# Placeholder logic for liquidity (will evolve later)
liquidity_risk = "Low"
# Convert risk levels to scores
def risk_score(level, weight):
    if level == "High":
        return weight
    elif level == "Medium":
        return weight * 0.6
    else:
        return weight * 0.2

fx_score = risk_score(fx_risk, 40)
rate_score = risk_score(rate_risk, 40)
liquidity_score = risk_score(liquidity_risk, 20)

treasury_risk_index = int(fx_score + rate_score + liquidity_score)
def risk_band(index):
    if index >= 70:
        return "ALERT", "🔴", "High risk environment detected"
    elif index >= 40:
        return "WATCH", "🟠", "Moderate risk, monitor closely"
    else:
        return "STABLE", "🟢", "Low risk environment"

risk_state, risk_icon, risk_message = risk_band(treasury_risk_index)

from datetime import datetime

current_minute = datetime.now().strftime("%H:%M")

if st.session_state.last_recorded_minute != current_minute:
    st.session_state.risk_history.append({
        "time": current_minute,
        "risk_index": treasury_risk_index
    })
    st.session_state.last_recorded_minute = current_minute

st.subheader("Treasury Risk Index")
st.markdown("---")

st.metric(
    label="Overall Treasury Risk",
    value=f"{treasury_risk_index} / 100",
    delta=risk_state
)
st.caption(
    "This index reflects the intensity of macro-financial risk based on real-time news concentration. "
    "It is intended for monitoring purposes, not forecasting or decision-making."
)

st.write(f"{risk_icon} **{risk_message}**")
if risk_state == "ALERT":
    st.error("Immediate attention recommended for treasury exposure.")
elif risk_state == "WATCH":
    st.warning("Heightened macro-financial activity detected.")
else:
    st.success("Macro-financial environment appears stable.")

st.subheader("Treasury Risk Trend")

history_df = pd.DataFrame(st.session_state.risk_history)

if len(history_df) > 1:
    st.line_chart(history_df.set_index("time")["risk_index"])
else:
    st.write("Waiting for more data points to build trend...")

st.subheader("Key Risk Drivers")

st.markdown("---")
st.subheader("Top Risk Contributors")

contributors_df = category_counts.reset_index()
contributors_df.columns = ["Category", "Number of Headlines"]

st.bar_chart(contributors_df.set_index("Category"))

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("FX Risk", fx_risk)

with col2:
    st.metric("Interest Rate Risk", rate_risk)

with col3:
    st.metric("Liquidity Risk", liquidity_risk)

filtered_news = news_df[news_df["Category"].isin(selected_category)]

display_news = filtered_news[["Headline", "Category", "Source"]]

st.dataframe(
    display_news,
    use_container_width=True,
    hide_index=True
)

