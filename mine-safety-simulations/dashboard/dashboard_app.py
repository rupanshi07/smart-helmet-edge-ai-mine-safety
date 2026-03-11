import streamlit as st
import pandas as pd
import os
import time

# ----------- FILE PATH -----------
DATA_FILE = r"D:\IoT\mine-safety-sim\live_data.csv"

st.set_page_config(page_title="Mine Safety Dashboard", layout="wide")

# ----------- LOAD DATA SAFELY -----------
@st.cache_data(ttl=2)
def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame()

    try:
        df = pd.read_csv(DATA_FILE, on_bad_lines='skip')
    except:
        return pd.DataFrame()

    # Convert numeric columns safely
    numeric_cols = [
        "distance", "rssi", "snr", "sf",
        "packet_success", "vib_rms", "gas_mean", "peak_acc"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

# ----------- HEADER -----------
st.title(" Real-Time Mine Safety Monitoring Dashboard")

df = load_data()

if df.empty:
    st.warning("Waiting for data... live_data.csv is empty.")
    
    # Auto-refresh in 2 seconds
    time.sleep(2)
    st.rerun()

# ----------- LATEST SENSOR SUMMARY -----------
latest = df.iloc[-1]

st.subheader("Latest Sensor Readings")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(" Peak Acceleration", f"{latest['peak_acc']:.2f}")

with col2:
    st.metric(" Gas Mean Level", f"{latest['gas_mean']:.2f}")

with col3:
    st.metric("Vibration RMS", f"{latest['vib_rms']:.2f}")

# ----------- ALERTS -----------
st.subheader(" System Alerts")

alerts = []
if latest["peak_acc"] > 15:
    alerts.append(" **High vibration detected! Possible collapse risk.**")
if latest["gas_mean"] > 50:
    alerts.append(" **Dangerous gas level detected!**")
if latest["packet_success"] < 0.5:
    alerts.append("**Weak communication signal!**")

if alerts:
    for a in alerts:
        st.error(a)
else:
    st.success("All systems normal ")

# ----------- REAL-TIME CHARTS -----------
st.subheader(" Real-Time Sensor Trends")

tab1, tab2, tab3 = st.tabs(["Vibration", "Gas Levels", "Signal Strength"])

with tab1:
    st.line_chart(df[["vib_rms", "peak_acc"]])

with tab2:
    st.line_chart(df["gas_mean"])

with tab3:
    st.line_chart(df[["rssi", "snr"]])

# ----------- TABLE VIEW -----------
st.subheader(" Live Data Table")
st.dataframe(df.tail(50))

# ----------- AUTO REFRESH (EVERY 2 SECONDS) -----------
st.query_params.from_dict({"refresh": "true"})
time.sleep(2)
st.rerun()
