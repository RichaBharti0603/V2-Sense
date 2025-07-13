import streamlit as st
import plotly.graph_objects as go
import time
from world_simulator import WorldSimulator

st.set_page_config(page_title="V2Sense Radar", layout="wide")

# 🚀 Branding
st.markdown("<h1 style='text-align:center; color:#00ffcc;'>🚗 V2Sense</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center; color:white;'>Vehicle-to-Vehicle Collision Prediction Mesh</h4>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar controls
st.sidebar.title("🔧 Simulation Controls")
vehicle_count = st.sidebar.slider("Number of Vehicles", 2, 10, 4)
speed_min = st.sidebar.slider("Min Speed", 5, 15, 6)
speed_max = st.sidebar.slider("Max Speed", 15, 30, 20)
autoplay = st.sidebar.checkbox("Auto Move Vehicles", value=True)
loop_speed = st.sidebar.slider("Refresh Every (s)", 1, 5, 1)

# Init simulator
if "sim" not in st.session_state or st.session_state.get("reset", False):
    st.session_state.sim = WorldSimulator(vehicle_count, speed_min, speed_max)
    st.session_state.last_config = (vehicle_count, speed_min, speed_max)
    st.session_state.reset = False
else:
    config = (vehicle_count, speed_min, speed_max)
    if config != st.session_state.last_config:
        st.session_state.sim = WorldSimulator(vehicle_count, speed_min, speed_max)
        st.session_state.last_config = config

sim = st.session_state.sim

# 🚦 Simulation Step
messages, warnings = sim.simulate(do_move=autoplay)

# UI Layout
fig = go.Figure()

# Draw grid (road look)
for i in range(-80, 100, 40):
    fig.add_shape(type="line", x0=i, y0=-100, x1=i, y1=100,
                  line=dict(color="gray", width=1, dash="dot"))
    fig.add_shape(type="line", x0=-100, y0=i, x1=100, y1=i,
                  line=dict(color="gray", width=1, dash="dot"))

# Map frame
fig.add_shape(
    type="rect", x0=-100, y0=-100, x1=100, y1=100,
    line=dict(color="lightgray", width=2)
)

# Plot vehicles with TTC
for v in sim.vehicles:
    ttc_label = ""
    for w in warnings:
        if v.id in w:
            ttc_label = w.replace("⚠️", "").strip()

    color = "red" if ttc_label else "deepskyblue"
    fig.add_trace(go.Scatter(
        x=[v.x], y=[v.y],
        mode="markers+text",
        marker=dict(size=18, color=color),
        text=[f"🚗 {v.id}<br>{ttc_label}" if ttc_label else f"🚗 {v.id}"],
        textposition="top center"
    ))

fig.update_layout(
    height=640,
    xaxis=dict(range=[-120, 120], visible=False),
    yaxis=dict(range=[-120, 120], visible=False),
    plot_bgcolor="black",
    paper_bgcolor="black",
    font=dict(color="white"),
    margin=dict(l=0, r=0, t=40, b=0),
    showlegend=False,
    title="🛣️ Live Radar with Real-Time Vehicle Movement"
)

st.plotly_chart(fig, use_container_width=True)

# 🧠 Broadcast Data
with st.expander("📋 Vehicle Broadcasts"):
    for msg in messages:
        st.json(msg)

# 🛑 Alerts
st.subheader("⚠️ Collision Warnings")
if warnings:
    for w in warnings:
        st.error(w)
else:
    st.success("No imminent collisions detected.")

# Refresh manually if not autoplaying
if not autoplay:
    if st.button("🔁 Manual Step"):
        st.rerun()

# Auto-refresh (only if autoplay is checked)
# Auto-refresh (only if autoplay is checked)
if autoplay:
    placeholder = st.empty()
    with placeholder:
        time.sleep(loop_speed)
        st.rerun()

