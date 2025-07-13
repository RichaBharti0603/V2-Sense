import streamlit as st
import time
from world_simulator import WorldSimulator

st.set_page_config(page_title="V2Sense Radar", layout="wide")
st.title("🚗 V2Sense: Vehicle-to-Vehicle Collision Prediction Mesh")

if "sim" not in st.session_state:
    st.session_state.sim = WorldSimulator(num_vehicles=4)

sim = st.session_state.sim
messages, warnings = sim.simulate()

st.subheader("📡 Vehicle Broadcasts")
for msg in messages:
    st.write(msg)

st.subheader("⚠️ Alerts")
if warnings:
    for w in warnings:
        st.error(w)
else:
    st.success("No imminent collisions detected.")

time.sleep(1)
st.experimental_rerun()
