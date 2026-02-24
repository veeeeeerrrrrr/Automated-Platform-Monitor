import streamlit as st
import asyncio
import pandas as pd
import sqlite3

from api_monitor import (
    check_apis_async,
    calculate_sla,
    calculate_health_score,
    configure_chaos,
    calculate_instability
)

from system_monitor import check_system
from log_analyzer import analyze_logs
from db import init_db, fetch_alerts
from streamlit_autorefresh import st_autorefresh

# ---------------- INIT ----------------
st.set_page_config(layout="wide")
init_db()

# Session state FIRST
if "api_list" not in st.session_state:
    st.session_state.api_list = []

# Auto refresh AFTER session exists
if st.session_state.api_list:
    st_autorefresh(interval=5000, key="datarefresh")

# ---------------- MONOSPACE UI ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap');

* { font-family: 'JetBrains Mono', monospace !important; }

body {
    background-color: #0b0b0f;
    color: #f5f5f5;
}

h1 { color: #ffb6c1; font-weight: 600; letter-spacing: -1px; }
h2, h3 { color: #ffc0cb; font-weight: 500; }

.card {
    background: #111117;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid rgba(255, 182, 193, 0.12);
    box-shadow: 0 0 25px rgba(255, 105, 180, 0.06);
    margin-bottom: 20px;
}

button {
    border-radius: 8px !important;
    background: linear-gradient(90deg, #ff6ec7, #ffb6c1) !important;
    color: black !important;
    font-weight: 600 !important;
    transition: 0.2s ease !important;
}

button:hover { transform: scale(1.04); }

.status-up { color: #5effc3; }
.status-down { color: #ff5c75; }

[data-testid="stMetric"] {
    background: #14141b;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid rgba(255,182,193,0.1);
}

hr { border: 1px solid rgba(255,182,193,0.08); }
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.title("N U L L T R A C E")
st.write(
    "Nulltrace is a real-time monitoring dashboard that tracks API availability, "
    "system performance, and service health. Built to stay simple, fast, and reliable."
)

st.divider()

# ---------------- SESSION STATE ----------------
if "api_list" not in st.session_state:
    st.session_state.api_list = []

# ---------------- ADD API ----------------
st.subheader("Add API Endpoint")
new_api = st.text_input("")

if st.button("Add API"):
    if new_api:
        st.session_state.api_list.append(new_api)

st.divider()

# ---------------- CHAOS ENGINEERING ----------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("Chaos Engineering")

enable_chaos = st.toggle("Enable Chaos")

intensity = st.slider(
    "Chaos Intensity",
    min_value=0.0,
    max_value=1.0,
    value=0.1,
    step=0.05
)

api_count = len(st.session_state.api_list)

if api_count > 1:
    blast_radius = st.slider(
        "Blast Radius",
        min_value=1,
        max_value=api_count,
        value=1
    )
else:
    blast_radius = 1
    st.write("Blast Radius: 1 (only one API available)")

duration = st.number_input(
    "Scheduled Duration (seconds, 0 = infinite)",
    min_value=0,
    value=0
)

configure_chaos(
    enabled=enable_chaos,
    intensity=intensity,
    blast_radius=blast_radius,
    duration=duration
)

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- RUN MONITORING ----------------
api_results = []

if st.session_state.api_list:
    api_results = asyncio.run(
        check_apis_async(st.session_state.api_list)
    )

# ---------------- MAIN GRID ----------------
col1, col2 = st.columns(2)

# -------- API MONITORING --------
with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("API Monitoring")

    for url, status, latency in api_results:

        sla = calculate_sla(url)
        health = calculate_health_score(url)
        status_class = "status-up" if status == "UP" else "status-down"

        st.markdown(
            f"<p class='{status_class}'>● {url} — {status} ({latency} ms)</p>",
            unsafe_allow_html=True
        )

        st.write(f"SLA: {sla}%")
        st.write(f"Health Score: {health}/100")
        st.write("")

        # -------- LATENCY GRAPH --------
        conn = sqlite3.connect("metrics.db")
        df = pd.read_sql_query(
            f"SELECT latency FROM api_metrics WHERE url='{url}' ORDER BY timestamp DESC LIMIT 50",
            conn
        )
        conn.close()

        if not df.empty:
            df = df[::-1]  # reverse to chronological order
            st.line_chart(df["latency"], height=150)

    st.markdown("</div>", unsafe_allow_html=True)

# -------- SYSTEM RESOURCES --------
with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("System Resources")

    cpu, ram = check_system()
    st.metric("CPU Usage", f"{cpu}%")
    st.metric("RAM Usage", f"{ram}%")

    instability = calculate_instability()
    st.metric("System Instability Score", f"{instability}%")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- LOG ANALYSIS ----------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("Log Analysis")

log_data = analyze_logs()
st.write(f"Errors: {log_data['errors']}")
st.write(f"Infos: {log_data['infos']}")
st.write(f"Error Rate: {log_data['error_rate']}%")

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- ALERTS ----------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("Alerts")

alerts = fetch_alerts()

if alerts:
    for url, alert_type, message, timestamp in alerts[:10]:
        st.write(f"[{timestamp}] {url} — {alert_type} — {message}")
else:
    st.write("No active alerts")

st.markdown("</div>", unsafe_allow_html=True)