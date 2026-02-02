import streamlit as st
import pandas as pd
import feedparser
from datetime import datetime

# ---------------- SESSION STATE ----------------
if "risk_history" not in st.session_state:
    st.session_state.risk_history = []

# ---------------- PAGE CONFIG ------------------
st.set_page_config(page_title="Intelligence Dashboard", layout="wide")

st.title("Intelligence Dashboard")
st.subheader("Live Macro-Financial Monitoring System")
st.caption(f"Last updated: {datetime.now().strftime('%d %b %Y, %H:%M')}")
st.markdown("---")

# ---------------- PLACEHOLDER TOP METRICS ----------------
st.metric("Today's Risk Score", "42", delta="Stable")

c1, c2, c3 = st.columns(3)
c1.metric("FX Risk", "—")
c2.metric("Interest Rate Risk", "—")
c3.metric("Liquidity Risk", "—")

# ---------------- SIDEBAR ----------------
st.sidebar.header("Monitoring Controls")
st.sidebar.selectbox("Region Focus", ["Global", "United States", "Europe", "Asia"])

selected_category = st.sidebar.multiselect(
    "Filter by Risk Category",
    ["FX", "Interest Rates", "Geopolitics", "Other"],
    default=["FX", "Interest Rates", "Geopolitics", "Other"]
)

# ---------------- NEWS INGESTION ----------------
st.subheader("Latest Relevant Financial News")

rss_url = "https://finance.yahoo.com/rss/topstories"
feed = feedparser.parse(rss_url)

def classify_headline(h):
    h = h.lower()
    if any(k in h for k in ["dollar", "euro", "yen", "currency", "fx", "forex"]):
        return "FX"
    if any(k in h for k in ["rate", "rates", "interest", "yield", "bond", "fed", "ecb"]):
        return "Interest Rates"
    if any(k in h for k in ["war", "conflict", "tensions", "sanctions", "geopolitics"]):
        return "Geopolitics"
    return "Other"

news_items = []

for e in feed.entries[:10]:
    if hasattr(e, "published_parsed") and e.published_parsed:
        published_time = datetime(*e.published_parsed[:6])
    else:
        published_time = datetime.now()

    news_items.append({
        "Headline": e.title,
        "Source": "Yahoo Finance",
        "Category": classify_headline(e.title),
        "PublishedTime": published_time
    })
def decay_weight(published_time):
    age_minutes = (datetime.now() - published_time).total_seconds() / 60

    if age_minutes <= 30:
        return 1.0
    elif age_minutes <= 120:
        return 0.6
    else:
        return 0.2

news_df = pd.DataFrame(news_items)

# ---------------- RISK LOGIC ----------------
news_df["DecayWeight"] = news_df["PublishedTime"].apply(decay_weight)

weighted_scores = (
    news_df
    .groupby("Category")["DecayWeight"]
    .sum()
)


def risk_level(c):
    return "High" if c >= 4 else "Medium" if c >= 2 else "Low"

fx_risk = risk_level(weighted_scores.get("FX", 0))
rate_risk = risk_level(weighted_scores.get("Interest Rates", 0))

liquidity_risk = "Low"

def risk_score(level, weight):
    return weight if level == "High" else weight * 0.6 if level == "Medium" else weight * 0.2

risk_index = int(
    risk_score(fx_risk, 40) +
    risk_score(rate_risk, 40) +
    risk_score(liquidity_risk, 20)
)

def risk_band(i):
    if i >= 70: return "ALERT", "🔴", "High risk environment detected"
    if i >= 40: return "WATCH", "🟠", "Moderate risk, monitor closely"
    return "STABLE", "🟢", "Low risk environment"

risk_state, risk_icon, risk_msg = risk_band(risk_index)

# ---------------- SNAPSHOT BUTTON ----------------
if st.button("📌 Record Risk Snapshot"):
    st.session_state.risk_history.append({
        "time": datetime.now().strftime("%d %b %Y %H:%M"),
        "risk_index": risk_index,
        "state": risk_state
    })

# ---------------- RISK INDEX ----------------
st.markdown("---")
st.subheader("Treasury Risk Index")

st.metric("Overall Risk", f"{risk_index} / 100", delta=risk_state)
st.write(f"{risk_icon} **{risk_msg}**")

if risk_state == "ALERT":
    st.error("Immediate attention recommended.")
elif risk_state == "WATCH":
    st.warning("Heightened macro-financial activity detected.")
else:
    st.success("Macro-financial environment appears stable.")

# ---------------- TREND ----------------
st.subheader("Risk Trend")

hist_df = pd.DataFrame(st.session_state.risk_history)
if len(hist_df) > 1:
    st.line_chart(hist_df.set_index("time")["risk_index"])
else:
    st.write("Record snapshots to build a trend.")

# ---------------- HISTORY (HIDDEN) ----------------
st.markdown("---")
st.subheader("Risk History")

if st.checkbox("Show detailed snapshot history", key="show_history"):
    if hist_df.empty:
        st.info("No snapshots recorded yet.")
    else:
        st.dataframe(hist_df, use_container_width=True, hide_index=True)
        st.download_button(
            "⬇️ Download Risk History (CSV)",
            hist_df.to_csv(index=False).encode(),
            "treasury_risk_history.csv",
            "text/csv"
        )

# ---------------- DRIVERS ----------------
st.subheader("Top Risk Contributors")
drivers = counts.reset_index()
drivers.columns = ["Category", "Headlines"]
st.bar_chart(drivers.set_index("Category"))

# ---------------- NEWS TABLE ----------------
filtered = news_df[news_df["Category"].isin(selected_category)]
st.dataframe(filtered, use_container_width=True, hide_index=True)
