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


# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(layout="wide")

init_db()
st_autorefresh(interval=5000, key="refresh")


# -------------------------------------------------
# CUSTOM PREMIUM CSS
# -------------------------------------------------
st.markdown("""
<style>

body {
    background-color: #0b0b0f;
    color: #f5f5f5;
}

.main {
    background: linear-gradient(145deg, #0b0b0f, #111117);
}

h1, h2, h3 {
    color: #ffb6c1;
    font-weight: 600;
}

/* Card styling */
.card {
    background: linear-gradient(145deg, #121218, #0e0e14);
    padding: 25px;
    border-radius: 18px;
    border: 1px solid rgba(255, 182, 193, 0.15);
    box-shadow: 0 0 25px rgba(255, 105, 180, 0.08);
    transition: 0.3s ease;
}

.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 0 35px rgba(255, 105, 180, 0.25);
}

/* Status dot */
.status-dot {
    height: 10px;
    width: 10px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
}

.green {
    background-color: #4cffb0;
}

.red {
    background-color: #ff4c6a;
}

/* Buttons */
button {
    border-radius: 12px !important;
    background: linear-gradient(90deg, #ff6ec7, #ffb6c1) !important;
    color: black !important;
    font-weight: 600 !important;
    transition: 0.2s ease-in-out !important;
}

button:hover {
    transform: scale(1.05);
}

[data-testid="stMetric"] {
    background: #14141b;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid rgba(255,182,193,0.1);
}

hr {
    border: 1px solid rgba(255,182,193,0.1);
}

</style>
""", unsafe_allow_html=True)


# -------------------------------------------------
# TITLE
# -------------------------------------------------
st.markdown("<h1>Intelligent Platform Observability Lab</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)


# -------------------------------------------------
# SESSION STATE FOR APIS
# -------------------------------------------------
if "api_list" not in st.session_state:
    st.session_state.api_list = [
        "https://api.github.com",
        "https://jsonplaceholder.typicode.com/posts"
    ]


# -------------------------------------------------
# ADD API INPUT
# -------------------------------------------------
new_api = st.text_input("Add API Endpoint")

if st.button("Add API"):
    if new_api:
        st.session_state.api_list.append(new_api)
        st.success("API added successfully.")


# -------------------------------------------------
# RUN MONITORING
# -------------------------------------------------
api_results = asyncio.run(check_apis_async(st.session_state.api_list))
cpu, ram = check_system()
errors, infos = analyze_logs()
alerts = evaluate_alerts(api_results, cpu, ram)


col1, col2 = st.columns(2)


# -------------------------------------------------
# API MONITORING CARD
# -------------------------------------------------
with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("API Monitoring")

    for url, status, latency in api_results:
        color_class = "green" if status == "UP" else "red"
        st.markdown(
            f"<span class='status-dot {color_class}'></span>"
            f"<strong>{url}</strong> — {status} ({latency} ms)",
            unsafe_allow_html=True
        )
        st.write(f"Uptime: {calculate_uptime(url)}%")

    st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------------------------
# SYSTEM CARD
# -------------------------------------------------
with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("System Resources")
    st.metric("CPU Usage", f"{cpu}%")
    st.metric("RAM Usage", f"{ram}%")
    st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------------------------
# LOGS & ALERTS
# -------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='card'>", unsafe_allow_html=True)

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


# -------------------------------------------------
# LATENCY TREND
# -------------------------------------------------
def fetch_history():
    conn = sqlite3.connect("metrics.db")
    df = pd.read_sql_query("SELECT * FROM api_metrics", conn)
    conn.close()
    return df

history_df = fetch_history()

if not history_df.empty:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Latency Trend")
    st.line_chart(history_df["latency"])
    st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------------------------
# CHAOS SECTION
# -------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("Chaos Engineering")
st.write("Chaos module coming soon.")
st.button("Inject Chaos (Placeholder)")
st.markdown("</div>", unsafe_allow_html=True)
