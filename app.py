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

# ---------------- TOP METRICS ----------------
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
    published_time = datetime(*e.published_parsed[:6]) if hasattr(e, "published_parsed") else datetime.now()
    news_items.append({
        "Headline": e.title,
        "Source": "Yahoo Finance",
        "Category": classify_headline(e.title),
        "PublishedTime": published_time
    })

news_df = pd.DataFrame(news_items)

# ---------------- TIME DECAY ----------------
def decay_weight(published_time):
    age_minutes = (datetime.now() - published_time).total_seconds() / 60
    if age_minutes <= 30:
        return 1.0
    elif age_minutes <= 120:
        return 0.6
    return 0.2

news_df["DecayWeight"] = news_df["PublishedTime"].apply(decay_weight)

weighted_scores = news_df.groupby("Category")["DecayWeight"].sum()

# ---------------- RISK LOGIC ----------------
def risk_level(c):
    return "High" if c >= 4 else "Medium" if c >= 2 else "Low"

fx_risk = risk_level(weighted_scores.get("FX", 0))
rate_risk = risk_level(weighted_scores.get("Interest Rates", 0))
liquidity_risk = "Low"

def risk_score(level, weight):
    return weight if level == "High" else weight * 0.6 if level == "Medium" else weight * 0.2

risk_index = int(
    risk_score(fx_risk, 40)
    + risk_score(rate_risk, 40)
    + risk_score(liquidity_risk, 20)
)

def risk_band(i):
    if i >= 70:
        return "ALERT", "🔴", "High risk environment detected"
    if i >= 40:
        return "WATCH", "🟠", "Moderate risk, monitor closely"
    return "STABLE", "🟢", "Low risk environment"

risk_state, risk_icon, risk_msg = risk_band(risk_index)

# ---------------- SNAPSHOT ----------------
if st.button("📌 Record Risk Snapshot"):
    st.session_state.risk_history.append({
        "time": datetime.now(),
        "risk_index": risk_index,
        "state": risk_state
    })

# ---------------- MOMENTUM ----------------
def risk_delta(history_df, minutes):
    if len(history_df) < 2:
        return None
    cutoff = datetime.now() - pd.Timedelta(minutes=minutes)
    recent = history_df[history_df["time"] >= cutoff]
    if len(recent) < 2:
        return None
    return recent["risk_index"].iloc[-1] - recent["risk_index"].iloc[0]
def risk_acceleration(history_df, short_window=30, long_window=60):
    delta_short = risk_delta(history_df, short_window)
    delta_long = risk_delta(history_df, long_window)

    if delta_short is None or delta_long is None:
        return None

    return delta_short - delta_long


hist_df = pd.DataFrame(st.session_state.risk_history)
delta_60 = risk_delta(hist_df, 60)

acceleration = risk_acceleration(hist_df, 30, 60)


st.markdown("### Risk Acceleration")

if acceleration is None:
    st.write("Not enough data to calculate acceleration.")
else:
    if acceleration > 0:
        st.warning(f"⚠ Risk acceleration detected (+{acceleration:.1f})")
    elif acceleration < 0:
        st.success(f"Risk pressure easing ({acceleration:.1f})")
    else:
        st.write("Risk momentum stable.")


# ---------------- DISPLAY ----------------
st.markdown("---")
st.subheader("Treasury Risk Index")
st.metric("Overall Risk", f"{risk_index} / 100", delta=risk_state)
st.write(f"{risk_icon} **{risk_msg}**")

st.markdown("### Risk Momentum")
if delta_60 is None:
    st.write("Not enough snapshot data.")
else:
    arrow = "↑" if delta_60 > 0 else "↓" if delta_60 < 0 else "→"
    st.metric("Δ Risk (60 min)", f"{delta_60:+}", arrow)

# ---------------- TREND ----------------
st.subheader("Risk Trend")
if len(hist_df) > 1:
    st.line_chart(hist_df.set_index("time")["risk_index"])
else:
    st.write("Record snapshots to build a trend.")

# ---------------- DRIVERS ----------------
st.subheader("Top Risk Contributors")
drivers = weighted_scores.reset_index()
drivers.columns = ["Category", "Weighted Impact"]
st.bar_chart(drivers.set_index("Category"))

# ---------------- NEWS ----------------
filtered = news_df[news_df["Category"].isin(selected_category)]
st.dataframe(filtered[["Headline", "Category", "Source"]], use_container_width=True, hide_index=True)
