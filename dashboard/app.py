import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

st.set_page_config(
    page_title="Zenith Telemetry Dashboard",
    page_icon="⚡",
    layout="wide"
)

API_URL = "http://localhost:8000/api/telemetry"

st.title("⚡ Zenith Telemetry & IoT Dashboard")
st.caption("Live Monitoring System - ESP32 Telemetry & Enterprise Gateway")

# Sidebar
st.sidebar.header("Control Panel")
auto_refresh = st.sidebar.checkbox("Auto Refresh (Every 3s)", value=True)
limit = st.sidebar.slider("Data Limit", min_value=10, max_value=100, value=20)

def fetch_data():
    try:
        response = requests.get(f"{API_URL}?limit={limit}", timeout=3)
        if response.status_code == 200:
            return response.json().get("data", [])
    except Exception as e:
        st.error(f"Gagal terhubung ke API Gateway: {e}")
    return []

data = fetch_data()

if data:
    df = pd.DataFrame(data)
    
    # 1. Metric Cards
    latest = df.iloc[0]
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Device ID", latest["device_id"])
    col2.metric("Pressure (Bar)", f"{latest['pressure_bar']} bar")
    col3.metric("Conveyor RPM", f"{latest['conveyor_rpm']} RPM")
    col4.metric("Status System", latest["status"])

    st.divider()

    # 2. Real-time Charts
    col_chart1, col_chart2 = st.columns(2)
    
    df_sorted = df.sort_values(by="id")
    
    with col_chart1:
        st.subheader("Pneumatic Pressure Trend")
        fig_p = px.line(df_sorted, x="received_at", y="pressure_bar", markers=True, 
                        line_shape="spline", color_discrete_sequence=["#00CC96"])
        st.plotly_chart(fig_p, use_container_width=True)

    with col_chart2:
        st.subheader("Conveyor Speed (RPM)")
        fig_rpm = px.bar(df_sorted, x="received_at", y="conveyor_rpm", 
                         color_discrete_sequence=["#636EFA"])
        st.plotly_chart(fig_rpm, use_container_width=True)

    # 3. Data Logs Table
    st.subheader("📋 Raw Telemetry Logs")
    st.dataframe(df, use_container_width=True)

else:
    st.warning("Belum ada data telemetri yang diterima dari server Gateway.")

if auto_refresh:
    time.sleep(3)
    st.rerun()
