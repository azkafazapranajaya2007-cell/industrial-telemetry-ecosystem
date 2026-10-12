import os
import requests
import streamlit as st
import pandas as pd

# Konfigurasi halaman
st.set_page_config(
    page_title="Zenith Telemetry & IoT Dashboard",
    page_icon="⚡",
    layout="wide"
)

# Ambil URL backend dari environment Docker atau fallback ke localhost
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.title("⚡ Zenith Telemetry & IoT Dashboard")
st.markdown("Live Monitoring System - ESP32 Telemetry & Enterprise Gateway")

# Sidebar
st.sidebar.header("Control Panel")
auto_refresh = st.sidebar.checkbox("Auto Refresh (Every 3s)", value=True)
data_limit = st.sidebar.slider("Data Limit", min_value=5, max_value=100, value=20)

# Fetch Data dari FastAPI Backend
try:
    response = requests.get(f"{BACKEND_URL}/api/telemetry?limit={data_limit}")
    if response.status_code == 200:
        result = response.json()
        logs = result.get("data", [])
        
        if logs:
            df = pd.DataFrame(logs)
            
            # Layout Metrik Utama
            col1, col2, col3 = st.columns(3)
            latest = logs[0]
            col1.metric("Latest Pressure", f"{latest['pressure_bar']} bar")
            col2.metric("Conveyor Speed", f"{latest['conveyor_rpm']} RPM")
            col3.metric("System Status", latest['status'])
            
            st.divider()
            
            # Grafik Telemetri
            st.subheader("📈 Live Pressure & RPM Chart")
            st.line_chart(df[['pressure_bar', 'conveyor_rpm']])
            
            # Tabel Log Mentah
            st.subheader("📋 Raw Telemetry Logs")
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("Belum ada data telemetri yang diterima dari server Gateway.")
    else:
        st.error(f"Gagal mengambil data dari Backend. Status Code: {response.status_code}")
except Exception as e:
    st.error(f"Gagal terhubung ke API Gateway ({BACKEND_URL}): {e}")

# Auto-refresh logic via streamlit-autorefresh atau rerun sederhana
if auto_refresh:
    st.rerun()
