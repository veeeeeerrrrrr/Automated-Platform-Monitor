import streamlit as st
import asyncio
import sqlite3
import pandas as pd
from streamlit_autorefresh import st_autorefresh

from api_monitor import check_apis_async
from system_monitor import check_system
from log_analyzer import analyze_logs
from db import init_db, calculate_uptime
from alerts import evaluate_alerts
from config import API_LIST

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Observability Lab",
    layout="wide",
    page_icon="🧠"
)

# -----------------------------
# AUTO REFRESH (5 sec)
# -----------------------------
st_autorefresh(interval=5000, key="refresh")

# -----------------------------
# CUSTOM CSS
# -----------------------------
st.markdown("""
<style>
body {
    background-color: #0b1220;
}
.main {
    background: linear-gradient(145deg, #0f1a2c, #080f1c);
}

.neon-card {
    background: linear-gradient(145deg, #101c2e, #0c1424);
    padding: 20px;
    border-radius: 20px;
    box-shadow: 0 0 15px rgba(0,255,200,0.15);
    transition: all 0.3s ease-in-out;
}
.neon-card:hover {
    transform: scale(1.02);
    box-shadow: 0 0 25px rgba(0,255,200,0.35);
}

.status-dot {
    height: 12px;
    width: 12px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
}

.pulse-green {
    background-color: #00ffcc;
    animation: pulse 1.5s infinite;
}

.pulse-red {
    background-color: #ff4d4d;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(0,255,200, 0.7); }
    70% { box-shadow: 0 0 0 10px rgba(0,255,200, 0); }
    100% { box-shadow: 0 0 0 0 rgba(0,255,200, 0); }
}

button {
    border-radius: 12px !important;
    transition: all 0.2s ease-in-out;
}
button:hover {
    transform: scale(1.05);
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# INIT DB
# -----------------------------
init_db()

st.title("🧠 Intelligent Platform Observability Lab")
st.caption("Minimal. Modular. Monitored.")

# -----------------------------
# ADD API INPUT
# -----------------------------
new_api = st.text_input("Add API to Monitor")

if st.button("Add API"):
    if new_api:
        API_LIST.append(new_api)
        st.success("API Added Successfully")

# -----------------------------
# RUN MONITORING
# -----------------------------
with st.spinner("Monitoring..."):
    api_results = asyncio.run(check_apis_async())
    cpu, ram = check_system()
    errors, infos = analyze_logs()
    alerts = evaluate_alerts(api_results, cpu, ram)

col1, col2 = st.columns(2)

# -----------------------------
# API CARD
# -----------------------------
with col1:
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("API Monitoring")

    for url, status, latency in api_results:
        dot_class = "pulse-green" if status == "UP" else "pulse-red"
        st.markdown(
            f"<span class='status-dot {dot_class}'></span>"
            f"<b>{url}</b> — {status} ({latency} ms)",
            unsafe_allow_html=True
        )
        st.write(f"Uptime: {calculate_uptime(url)}%")

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# SYSTEM CARD
# -----------------------------
with col2:
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("System Resources")
    st.metric("CPU Usage", f"{cpu}%")
    st.metric("RAM Usage", f"{ram}%")
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# LOG + ALERTS
# -----------------------------
st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
st.subheader("Log Analysis")
st.write(f"Errors: {errors}")
st.write(f"Infos: {infos}")

st.subheader("Alerts")
if alerts:
    for alert in alerts:
        st.error(alert)
else:
    st.success("No active alerts")
st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# LATENCY TREND
# -----------------------------
def fetch_history():
    conn = sqlite3.connect("metrics.db")
    df = pd.read_sql_query("SELECT * FROM api_metrics", conn)
    conn.close()
    return df

history_df = fetch_history()

if not history_df.empty:
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("Latency Trend")
    st.line_chart(history_df["latency"])
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# CHAOS PLACEHOLDER
# -----------------------------
st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
st.subheader("⚠ Chaos Engineering")
st.warning("Chaos module coming soon.")
st.button("Inject Chaos (Placeholder)")
st.markdown("</div>", unsafe_allow_html=True)