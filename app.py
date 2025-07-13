import streamlit as st
import plotly.graph_objects as go
import time
from collections import deque
from world_simulator import WorldSimulator

# Set Streamlit page config
st.set_page_config(page_title="V2Sense Enhanced", layout="wide")
st.title("🚗 V2Sense: Vehicle-to-Vehicle Collision Prediction Mesh (Enhanced UI)")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Simulation Settings")
vehicle_count = st.sidebar.slider("Number of Vehicles", 2, 10, 4)
speed_min = st.sidebar.slider("Min Speed", 1, 10, 3)
speed_max = st.sidebar.slider("Max Speed", 5, 30, 15)
field_radius = st.sidebar.slider("Radar Field Radius", 50, 200, 100)

# --- SESSION INIT ---
if "sim" not in st.session_state:
    st.session_state.sim = WorldSimulator(num_vehicles=vehicle_count, speed_min=speed_min, speed_max=speed_max)
    st.session_state.history = deque(maxlen=10)  # last 10 alerts
    st.session_state.ttc_timeline = []

sim = st.session_state.sim

# If config changed, reinitialize simulator
if sim.num_vehicles != vehicle_count or sim.speed_min != speed_min or sim.speed_max != speed_max:
    st.session_state.sim = WorldSimulator(num_vehicles=vehicle_count, speed_min=speed_min, speed_max=speed_max)
    sim = st.session_state.sim

# Run simulation step
messages, warnings = sim.simulate()

# Store alert history
for w in warnings:
    st.session_state.history.append(w)

# TTC tracking
min_ttc = min(
    (
        sim.time_to_collision(v1, v2)
        for i, v1 in enumerate(sim.vehicles)
        for j, v2 in enumerate(sim.vehicles)
        if i != j and sim.time_to_collision(v1, v2)
    ),
    default=None
)
if min_ttc:
    st.session_state.ttc_timeline.append(min_ttc)

# --- PLOTLY RADAR UI ---
fig = go.Figure()

fig.add_shape(type="circle", x0=-field_radius, y0=-field_radius, x1=field_radius, y1=field_radius,
              xref="x", yref="y", line_color="lightgreen")

vehicle_types = ['🚗', '🚌', '🏍️', '🚙', '🚕', '🚓', '🚚', '🚛', '🛵', '🚒']

for i, v in enumerate(sim.vehicles):
    color = 'red' if any(v.id in w for w in warnings) else 'cyan'
    fig.add_trace(go.Scatter(
        x=[v.x], y=[v.y],
        mode='markers+text',
        marker=dict(size=16, color=color),
        text=[f"{vehicle_types[i % len(vehicle_types)]} {v.id}"],
        textposition="top center"
    ))

fig.update_layout(
    xaxis=dict(range=[-field_radius-20, field_radius+20], visible=False),
    yaxis=dict(range=[-field_radius-20, field_radius+20], visible=False),
    height=600,
    plot_bgcolor='black',
    paper_bgcolor='black',
    font=dict(color='white'),
    showlegend=False,
    title="📡 Live Radar View"
)

st.plotly_chart(fig, use_container_width=True)

# --- BROADCAST DATA ---
with st.expander("📋 Vehicle Broadcasts"):
    for msg in messages:
        st.json(msg)

# --- ALERT HISTORY ---
st.subheader("🕒 Collision Alert History")
if st.session_state.history:
    for h in reversed(st.session_state.history):
        st.warning(h)
else:
    st.info("No recent collision alerts.")

# --- TTC GRAPH ---
if st.session_state.ttc_timeline:
    st.subheader("📈 TTC (Time to Collision) Trend")
    st.line_chart(st.session_state.ttc_timeline)

# --- AUDIO ALERT (Browser beep for visual alert presence) ---
if warnings:
    st.markdown("<script>new Audio('https://www.soundjay.com/button/beep-07.wav').play()</script>", unsafe_allow_html=True)

# --- MANUAL REFRESH ---
if st.button("🔁 Refresh Simulation"):
    st.rerun()
