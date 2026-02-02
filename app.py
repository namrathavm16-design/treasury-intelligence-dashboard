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

scenario = st.sidebar.selectbox(
    "Stress Scenario",
    ["Base Case", "Hawkish Fed", "Geopolitical Escalation"]
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
import numpy as np

def saturated_score(weighted_value):
    return np.log1p(weighted_value)

fx_effective = saturated_score(weighted_scores.get("FX", 0))
rate_effective = saturated_score(weighted_scores.get("Interest Rates", 0))

fx_risk = risk_level(fx_effective)
rate_risk = risk_level(rate_effective)

liquidity_risk = "Low"

# -------- Scenario-based weights --------
if scenario == "Hawkish Fed":
    fx_multiplier = 1.0
    rate_multiplier = 1.5
elif scenario == "Geopolitical Escalation":
    fx_multiplier = 1.4
    rate_multiplier = 1.1
else:  # Base Case
    fx_multiplier = 1.0
    rate_multiplier = 1.0

def risk_score(level, weight):
    return weight if level == "High" else weight * 0.6 if level == "Medium" else weight * 0.2

risk_index = int(
    risk_score(fx_risk, 40 * fx_multiplier)
    + risk_score(rate_risk, 40 * rate_multiplier)
    + risk_score(liquidity_risk, 20)
)

def risk_band(i):
    if i >= 70:
        return "ALERT", "🔴", "High risk environment detected"
    if i >= 40:
        return "WATCH", "🟠", "Moderate risk, monitor closely"
    return "STABLE", "🟢", "Low risk environment"

def compute_risk_index(fx_risk, rate_risk, liquidity_risk, scenario_name):
    if scenario_name == "Hawkish Fed":
        fx_m = 1.0
        rate_m = 1.5
    elif scenario_name == "Geopolitical Escalation":
        fx_m = 1.4
        rate_m = 1.1
    else:  # Base Case
        fx_m = 1.0
        rate_m = 1.0

    return int(
        risk_score(fx_risk, 40 * fx_m)
        + risk_score(rate_risk, 40 * rate_m)
        + risk_score(liquidity_risk, 20)
    )

risk_state, risk_icon, risk_msg = risk_band(risk_index)
base_index = compute_risk_index(fx_risk, rate_risk, liquidity_risk, "Base Case")
hawkish_index = compute_risk_index(fx_risk, rate_risk, liquidity_risk, "Hawkish Fed")
geo_index = compute_risk_index(fx_risk, rate_risk, liquidity_risk, "Geopolitical Escalation")
hawkish_delta = hawkish_index - base_index
geo_delta = geo_index - base_index

hawkish_pct = round((hawkish_delta / base_index) * 100, 1) if base_index > 0 else 0
geo_pct = round((geo_delta / base_index) * 100, 1) if base_index > 0 else 0

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

def confidence_score(news_df, weighted_scores):
    # 1. Volume score (more signals = more confidence)
    total_signals = len(news_df)
    volume_score = min(total_signals / 10, 1.0)  # cap at 10 headlines

    # 2. Concentration score (dominant category strength)
    if weighted_scores.sum() == 0:
        concentration_score = 0
    else:
        concentration_score = weighted_scores.max() / weighted_scores.sum()

    # 3. Recency score (how much weight comes from fresh news)
    recent_weight = news_df.loc[
        news_df["DecayWeight"] >= 0.6, "DecayWeight"
    ].sum()
    total_weight = news_df["DecayWeight"].sum()
    recency_score = recent_weight / total_weight if total_weight > 0 else 0

    # Final confidence score
    return round(
        0.4 * volume_score +
        0.4 * concentration_score +
        0.2 * recency_score,
        2
    )
confidence = confidence_score(news_df, weighted_scores)


st.markdown("### Signal Confidence")

if confidence >= 0.75:
    st.success(f"High confidence in risk signal ({confidence})")
elif confidence >= 0.5:
    st.warning(f"Moderate confidence in risk signal ({confidence})")
else:
    st.error(f"Low confidence — signal may be noisy ({confidence})")

# ---------------- DISPLAY ----------------
st.markdown("---")
st.subheader("Treasury Risk Index")
c1, c2, c3 = st.columns(3)

c1.metric("Base Case", base_index)
c2.metric("Hawkish Fed", hawkish_index)
c3.metric("Geopolitical Escalation", geo_index)

st.markdown("### Stress Impact vs Base Case")

c4, c5 = st.columns(2)

c4.metric(
    "Hawkish Fed Impact",
    f"+{hawkish_delta}",
    f"{hawkish_pct}%"
)

c5.metric(
    "Geopolitical Escalation Impact",
    f"+{geo_delta}",
    f"{geo_pct}%"
)

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
