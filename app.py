import streamlit as st
import plotly.graph_objects as go
import time
from world_simulator import WorldSimulator

# Streamlit page setup
st.set_page_config(page_title="🚗 V2Sense Radar", layout="wide")
st.title("🚗 V2Sense: Vehicle-to-Vehicle Collision Prediction Mesh")

# Sidebar controls
st.sidebar.title("🔧 Simulation Settings")
vehicle_count = st.sidebar.slider("Number of Vehicles", 2, 10, 4)
speed_min = st.sidebar.slider("Min Speed", 5, 15, 8)
speed_max = st.sidebar.slider("Max Speed", 15, 30, 20)

# Detect configuration changes
if "last_config" not in st.session_state or st.session_state.get("force_reset", False):
    st.session_state.last_config = (vehicle_count, speed_min, speed_max)
    st.session_state.sim = WorldSimulator(vehicle_count, speed_min, speed_max)
    st.session_state.force_reset = False
else:
    current_config = (vehicle_count, speed_min, speed_max)
    if current_config != st.session_state.last_config:
        st.session_state.sim = WorldSimulator(vehicle_count, speed_min, speed_max)
        st.session_state.last_config = current_config

# Run simulation step
sim = st.session_state.sim
messages, warnings = sim.simulate()

# === Enhanced Plotly Radar ===
field_radius = 100
fig = go.Figure()

# Draw city grid (roads)
for i in range(-80, 100, 40):
    fig.add_shape(type="line", x0=i, y0=-100, x1=i, y1=100,
                  line=dict(color="gray", width=1, dash="dot"))  # Vertical lines
    fig.add_shape(type="line", x0=-100, y0=i, x1=100, y1=i,
                  line=dict(color="gray", width=1, dash="dot"))  # Horizontal lines

# Draw radar/road boundary
fig.add_shape(
    type="rect",
    x0=-field_radius, y0=-field_radius,
    x1=field_radius, y1=field_radius,
    line=dict(color="lightgray", width=2)
)

# Plot vehicle markers
for v in sim.vehicles:
    color = 'red' if any(v.id in w for w in warnings) else 'deepskyblue'
    fig.add_trace(go.Scatter(
        x=[v.x], y=[v.y],
        mode='markers+text',
        marker=dict(size=18, color=color, line=dict(color='white', width=1)),
        text=[f"🚗 {v.id}"],
        textposition="top center",
        name=f"Vehicle {v.id}"
    ))

fig.update_layout(
    xaxis=dict(range=[-120, 120], visible=False),
    yaxis=dict(range=[-120, 120], visible=False),
    height=620,
    plot_bgcolor='#0a0a0a',
    paper_bgcolor='#0a0a0a',
    font=dict(color='white'),
    title="🛣️ City Grid Simulation (Top-Down View)",
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# Broadcasts
with st.expander("📋 Vehicle Broadcasts"):
    for msg in messages:
        st.json(msg)

# Alerts
st.subheader("⚠️ Collision Alerts")
if warnings:
    for w in warnings:
        st.error(w)
else:
    st.success("✅ No imminent collisions detected.")

# Button to refresh manually
col1, col2 = st.columns([1, 5])
with col1:
    if st.button("🔁 Refresh Simulation"):
        st.rerun()
