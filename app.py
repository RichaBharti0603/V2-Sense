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
    loop_speed = st.slider("Simulation Speed (seconds)", 0.1, 2.0, 1.0)
    start_button = st.button("▶️ Start Simulation")

# Initialize sim
if "sim" not in st.session_state or st.session_state.sim.num_vehicles != vehicle_count:
    st.session_state.sim = WorldSimulator(vehicle_count, speed_min, speed_max)

sim = st.session_state.sim

# Placeholder for dynamic map
map_placeholder = st.empty()
alerts_placeholder = st.empty()
broadcasts_expander = st.expander("📋 Vehicle Broadcasts")

# Run simulation if start button is clicked
if start_button:
    st.session_state.running = True

if "running" not in st.session_state:
    st.session_state.running = False

stop_button = st.button("⏹️ Stop Simulation")
if stop_button:
    st.session_state.running = False

# Function to draw radar
def draw_radar(messages, warnings):
    fig = go.Figure()

    # Radar rings
    for r in range(20, field_radius + 1, 20):
        fig.add_shape(type="circle", x0=-r, y0=-r, x1=r, y1=r,
                      line=dict(color="rgba(0,255,0,0.2)", dash="dot"))

    # Crosshairs
    fig.add_shape(type="line", x0=-field_radius, y0=0, x1=field_radius, y1=0,
                  line=dict(color="green", width=1))
    fig.add_shape(type="line", x0=0, y0=-field_radius, x1=0, y1=field_radius,
                  line=dict(color="green", width=1))

    # Vehicles
    for v in sim.vehicles:
        color = 'red' if any(v.id in w for w in warnings) else 'cyan'
        icon = "🚗" if color == 'cyan' else "⚠️"
        fig.add_trace(go.Scatter(
            x=[v.x], y=[v.y],
            mode='markers+text',
            marker=dict(size=12, color=color),
            text=[f"{icon} {v.id}"],
            textposition="top center"
        ))

    fig.update_layout(
        xaxis=dict(range=[-field_radius, field_radius], visible=False),
        yaxis=dict(range=[-field_radius, field_radius], visible=False),
        height=700,
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white'),
        showlegend=False
    )

    map_placeholder.plotly_chart(fig, use_container_width=True)

    # Broadcasts
    with broadcasts_expander:
        for msg in messages:
            st.json(msg)

    # Alerts
    alerts_placeholder.subheader("⚠️ Collision Alerts")
    if warnings:
        for w in warnings:
            alerts_placeholder.error(w)
    else:
        alerts_placeholder.success("No imminent collisions detected.")

# Real-time loop
while st.session_state.running:
    messages, warnings = sim.simulate(do_move=True)
    draw_radar(messages, warnings)
    time.sleep(loop_speed)
