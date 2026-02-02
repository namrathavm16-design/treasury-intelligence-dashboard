import streamlit as st
import pandas as pd
import feedparser
import numpy as np
from datetime import datetime

# ---------------- SESSION STATE ----------------
if "risk_history" not in st.session_state:
    st.session_state.risk_history = []

# ---------------- PAGE CONFIG ------------------
st.set_page_config(page_title="Intelligence Dashboard", layout="wide")

# ---------------- SIDEBAR ----------------
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

# ---------------- HELPER FUNCTIONS ----------------
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
        return 1.0
    elif age <= 120:
        return 0.6
    return 0.2

def saturated_score(x):
    return np.log1p(x)

def risk_level(c):
    return "High" if c >= 4 else "Medium" if c >= 2 else "Low"

def risk_score(level, weight):
    return weight if level == "High" else weight * 0.6 if level == "Medium" else weight * 0.2

def risk_band(i):
    if i >= 70:
        return "ALERT", "🔴"
    if i >= 40:
        return "WATCH", "🟠"
    return "STABLE", "🟢"

def risk_delta(df, minutes):
    if len(df) < 2:
        return None
    cutoff = datetime.now() - pd.Timedelta(minutes=minutes)
    recent = df[df["time"] >= cutoff]
    if len(recent) < 2:
        return None
    return recent["risk_index"].iloc[-1] - recent["risk_index"].iloc[0]

def risk_acceleration(df):
    d30 = risk_delta(df, 30)
    d60 = risk_delta(df, 60)
    if d30 is None or d60 is None:
        return None
    return d30 - d60

def confidence_score(news_df, weighted_scores):
    volume = min(len(news_df) / 10, 1)
    concentration = weighted_scores.max() / weighted_scores.sum() if weighted_scores.sum() > 0 else 0
    recency = news_df.loc[news_df["DecayWeight"] >= 0.6, "DecayWeight"].sum() / news_df["DecayWeight"].sum()
    return round(0.4 * volume + 0.4 * concentration + 0.2 * recency, 2)

def generate_risk_narrative(state, fx_pct, rate_pct, scenario, delta, accel, conf):
    driver = "FX" if fx_pct >= rate_pct else "Interest Rates"
    text = f"Risk is **{state}**, driven mainly by **{driver}** risk. "
    if scenario != "Base Case":
        text += f"Scenario: **{scenario}**. "
    if delta is not None:
        text += "Risk momentum is increasing. " if delta > 0 else "Risk momentum is easing. "
    if accel and accel > 0:
        text += "Acceleration detected. "
    if conf < 0.5:
        text += "Signal confidence is low."
    elif conf >= 0.75:
        text += "Signal confidence is high."
    return text

# ---------------- NEWS INGESTION ----------------
st.title("Intelligence Dashboard")
st.caption(f"Last updated: {datetime.now().strftime('%d %b %Y, %H:%M')}")
st.markdown("---")

feed = feedparser.parse("https://finance.yahoo.com/rss/topstories")

news = []
for e in feed.entries[:10]:
    t = datetime(*e.published_parsed[:6]) if hasattr(e, "published_parsed") else datetime.now()
    news.append({
        "Headline": e.title,
        "Category": classify_headline(e.title),
        "PublishedTime": t
    })

news_df = pd.DataFrame(news)
news_df["DecayWeight"] = news_df["PublishedTime"].apply(decay_weight)
weighted_scores = news_df.groupby("Category")["DecayWeight"].sum()

# ---------------- RISK COMPUTATION ----------------
fx_risk = risk_level(saturated_score(weighted_scores.get("FX", 0)))
rate_risk = risk_level(saturated_score(weighted_scores.get("Interest Rates", 0)))
liq_risk = "Low"

fx_m, rate_m = (1.4, 1.1) if scenario == "Geopolitical Escalation" else (1.0, 1.5) if scenario == "Hawkish Fed" else (1.0, 1.0)

risk_index = int(
    risk_score(fx_risk, 40 * fx_m) +
    risk_score(rate_risk, 40 * rate_m) +
    risk_score(liq_risk, 20)
)

state, icon = risk_band(risk_index)

# ---------------- CONTRIBUTIONS ----------------
fx_c = risk_score(fx_risk, 40 * fx_m)
rate_c = risk_score(rate_risk, 40 * rate_m)
liq_c = risk_score(liq_risk, 20)
total = fx_c + rate_c + liq_c

fx_pct = round(fx_c / total * 100, 1)
rate_pct = round(rate_c / total * 100, 1)

# ---------------- HISTORY ----------------
if st.button("📌 Record Risk Snapshot"):
    st.session_state.risk_history.append({"time": datetime.now(), "risk_index": risk_index})

hist_df = pd.DataFrame(st.session_state.risk_history)
delta_60 = risk_delta(hist_df, 60)
accel = risk_acceleration(hist_df)
conf = confidence_score(news_df, weighted_scores)

# ---------------- DISPLAY ----------------
st.subheader("Treasury Risk Index")
st.info(generate_risk_narrative(state, fx_pct, rate_pct, scenario, delta_60, accel, conf))
st.metric("Overall Risk", f"{risk_index}/100", state)

st.subheader("Top Risk Contributors")
st.bar_chart(pd.DataFrame({"FX": [fx_pct], "Rates": [rate_pct]}).T)

st.subheader("Latest News")
st.dataframe(news_df[["Headline", "Category"]], use_container_width=True)
