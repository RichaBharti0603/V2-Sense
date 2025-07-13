import streamlit as st
import plotly.graph_objects as go
import time
from world_simulator import WorldSimulator

st.set_page_config(page_title="🚗 V2Sense Enhanced Radar UI", layout="wide")
st.title("🚗 V2Sense: Vehicle-to-Vehicle Collision Prediction Mesh (Enhanced Radar View)")

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Simulation Controls")
    vehicle_count = st.slider("Number of Vehicles", 2, 10, 4)
    speed_min = st.slider("Min Speed", 1, 10, 5)
    speed_max = st.slider("Max Speed", 10, 30, 15)
    field_radius = st.slider("Field Radius", 50, 150, 100)
    autoplay = st.checkbox("Auto Simulate", value=True)
    loop_speed = st.slider("Simulation Speed (seconds)", 0.1, 2.0, 1.0)

# Initialize simulation
if "sim" not in st.session_state:
    st.session_state.sim = WorldSimulator(num_vehicles=vehicle_count, speed_min=speed_min, speed_max=speed_max)

sim = st.session_state.sim
messages, warnings = sim.simulate(do_move=True)

# Setup enhanced radar-style plot
fig = go.Figure()

# Radar rings
for r in range(20, field_radius + 1, 20):
    fig.add_shape(type="circle", x0=-r, y0=-r, x1=r, y1=r,
                  line=dict(color="rgba(0,255,0,0.2)", dash="dot"))

# Cross axes
fig.add_shape(type="line", x0=-field_radius, y0=0, x1=field_radius, y1=0, line=dict(color="green", width=1))
fig.add_shape(type="line", x0=0, y0=-field_radius, x1=0, y1=field_radius, line=dict(color="green", width=1))

# Add vehicle markers
for v in sim.vehicles:
    color = 'red' if any(v.id in w for w in warnings) else 'cyan'
    icon = "🚗" if color == 'cyan' else "⚠️"
    fig.add_trace(go.Scatter(
        x=[v.x], y=[v.y],
        mode='markers+text',
        marker=dict(size=12, color=color),
        text=[f"{icon} {v.id}"],
        textposition="top center",
        name=f"Vehicle {v.id}"
    ))

# Radar layout
fig.update_layout(
    xaxis=dict(range=[-field_radius, field_radius], zeroline=False, showgrid=False, visible=False),
    yaxis=dict(range=[-field_radius, field_radius], zeroline=False, showgrid=False, visible=False),
    height=700,
    plot_bgcolor='black',
    paper_bgcolor='black',
    font=dict(color='white'),
    title="📡 GTA-style Live Radar Simulation",
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# Broadcast logs
with st.expander("📋 Vehicle Broadcasts"):
    for msg in messages:
        st.json(msg)

# Warnings
st.subheader("⚠️ Collision Alerts")
if warnings:
    for w in warnings:
        st.error(w)
else:
    st.success("No imminent collisions detected.")

# Auto-refresh
if autoplay:
    time.sleep(loop_speed)
    st.rerun()
