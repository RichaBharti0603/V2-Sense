import streamlit as st
import time
from world_simulator import WorldSimulator

st.set_page_config(page_title="V2Sense Radar", layout="wide")
st.title("🚗 V2Sense: Vehicle-to-Vehicle Collision Prediction Mesh")

# Init simulation only once
if "sim" not in st.session_state:
    st.session_state.sim = WorldSimulator(num_vehicles=4)
if "run_count" not in st.session_state:
    st.session_state.run_count = 0

sim = st.session_state.sim
messages, warnings = sim.simulate()

# Display vehicle messages
st.subheader("📡 Vehicle Broadcasts")
for msg in messages:
    st.json(msg)

# Display alerts
st.subheader("⚠️ Alerts")
if warnings:
    for w in warnings:
        st.error(w)
else:
    st.success("No imminent collisions detected.")

# Auto-refresh logic (run every second)
st.session_state.run_count += 1
if st.session_state.run_count <= 100:
    time.sleep(1)
    st.experimental_rerun()
