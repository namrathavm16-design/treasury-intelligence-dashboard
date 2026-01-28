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
    st.metric("FX Risk", fx_risk)

with col2:
    st.metric("Interest Rate Risk", rate_risk)

with col3:
    st.metric("Liquidity Risk", liquidity_risk)

st.sidebar.header("Monitoring Controls")
st.sidebar.selectbox(
    "Region Focus",
    ["Global", "United States", "Europe", "Asia"]
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

st.dataframe(news_df, use_container_width=True)
