import math
import streamlit as st
import plotly.graph_objects as go
import time
from world_simulator import WorldSimulator

st.set_page_config(page_title="🚗 V2Sense Radar UI", layout="wide")
st.title("🚗 V2Sense: Vehicle-to-Vehicle Collision Prediction Mesh")

# Sidebar Controls
with st.sidebar:
    st.header("⚙️ Simulation Controls")
    vehicle_count = st.slider("Number of Vehicles", 2, 10, 4)
    speed_min = st.slider("Min Speed", 1, 10, 5)
    speed_max = st.slider("Max Speed", 10, 30, 15)
    field_radius = st.slider("Field Radius", 50, 150, 100)
    loop_speed = st.slider("Simulation Speed (seconds)", 0.1, 2.0, 1.0)
    enable_noise = st.checkbox("📡 Simulate GPS Noise", value=True)
    enable_packet_loss = st.checkbox("📭 Simulate Packet Loss", value=True)
    start_button = st.button("▶️ Start Simulation")
    stop_button = st.button("⏹️ Stop Simulation")

# Initialize Simulator
if "sim" not in st.session_state or st.session_state.sim.num_vehicles != vehicle_count:
    st.session_state.sim = WorldSimulator(vehicle_count, speed_min, speed_max)

if "running" not in st.session_state:
    st.session_state.running = False

if start_button:
    st.session_state.running = True
if stop_button:
    st.session_state.running = False

sim = st.session_state.sim
map_placeholder = st.empty()
alerts_placeholder = st.empty()
broadcasts_expander = st.expander("📋 Vehicle Broadcasts")
inbox_expander = st.expander("📡 Vehicle Communication Inboxes")

def draw_radar(messages, warnings, comm_graph):
    fig = go.Figure()

    # Road Grid
    for r in range(-field_radius, field_radius + 1, 20):
        fig.add_shape(type="line", x0=r, y0=-field_radius, x1=r, y1=field_radius,
                      line=dict(color="rgba(50,50,50,0.3)", width=1))
        fig.add_shape(type="line", x0=-field_radius, y0=r, x1=field_radius, y1=r,
                      line=dict(color="rgba(50,50,50,0.3)", width=1))

    # Radar Rings
    for r in range(20, field_radius + 1, 20):
        fig.add_shape(type="circle", x0=-r, y0=-r, x1=r, y1=r,
                      line=dict(color="rgba(0,255,0,0.2)", dash="dot"))

    # Crosshair
    fig.add_shape(type="line", x0=-field_radius, y0=0, x1=field_radius, y1=0,
                  line=dict(color="green", width=1))
    fig.add_shape(type="line", x0=0, y0=-field_radius, x1=0, y1=field_radius,
                  line=dict(color="green", width=1))

    # Mesh connections (success or failure)
    for (sender, receiver, success) in comm_graph:
        line_color = "green" if success else "red"
        dash_style = "dot"
        fig.add_trace(go.Scatter(
            x=[sender.x, receiver.x],
            y=[sender.y, receiver.y],
            mode="lines",
            line=dict(color=line_color, dash=dash_style),
            opacity=0.5,
            showlegend=False
        ))

    # Vehicles
    for v in sim.vehicles:
        is_warn = any(v.id in w for w in warnings)
        color = 'red' if is_warn else 'cyan'
        icon = "🚗" if not is_warn else "⚠️"

        fig.add_trace(go.Scatter(
            x=[v.x], y=[v.y],
            mode='markers+text',
            marker=dict(size=12, color=color),
            text=[f"{icon} {v.id}"],
            textposition="top center",
            name=f"Vehicle {v.id}"
        ))

    # Final layout
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

    with broadcasts_expander:
        for msg in messages:
            st.json(msg)

    with inbox_expander:
        for v in sim.vehicles:
            st.markdown(f"**📡 Inbox of Vehicle {v.id}**")
            for m in v.received_messages:
                st.json(m)

    alerts_placeholder.subheader("⚠️ Collision Alerts")
    if warnings:
        for w in warnings:
            alerts_placeholder.error(w)
    else:
        alerts_placeholder.success("No imminent collisions detected.")

# Initial Static Frame
messages, warnings, comm_graph = sim.simulate(do_move=False, simulate_noise=enable_noise, simulate_loss=enable_packet_loss)
draw_radar(messages, warnings, comm_graph)

# Run Simulation
if st.session_state.running:
    while True:
        messages, warnings, comm_graph = sim.simulate(do_move=True, simulate_noise=enable_noise, simulate_loss=enable_packet_loss)
        draw_radar(messages, warnings, comm_graph)
        time.sleep(loop_speed)
