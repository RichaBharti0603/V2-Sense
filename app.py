import streamlit as st
import plotly.graph_objects as go
import time
from world_simulator import WorldSimulator

st.set_page_config(page_title="🚗 V2Sense Radar UI", layout="wide")
st.title("🚗 V2Sense: Vehicle-to-Vehicle Collision Prediction Mesh")

# Sidebar
with st.sidebar:
    st.header("⚙️ Simulation Controls")
    vehicle_count = st.slider("Number of Vehicles", 2, 10, 4)
    speed_min = st.slider("Min Speed", 1, 10, 5)
    speed_max = st.slider("Max Speed", 10, 30, 15)
    field_radius = st.slider("Field Radius", 50, 150, 100)
    loop_speed = st.slider("Simulation Speed (seconds)", 0.1, 2.0, 1.0)
    start_button = st.button("▶️ Start Simulation")
    stop_button = st.button("⏹️ Stop Simulation")

# Init
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

def draw_radar(messages, warnings):
    fig = go.Figure()

    # Background grid (simulated road network)
    for r in range(-field_radius, field_radius + 1, 20):
        fig.add_shape(type="line", x0=r, y0=-field_radius, x1=r, y1=field_radius,
                      line=dict(color="rgba(50,50,50,0.3)", width=1))
        fig.add_shape(type="line", x0=-field_radius, y0=r, x1=field_radius, y1=r,
                      line=dict(color="rgba(50,50,50,0.3)", width=1))

    # Add radar rings
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
        is_warn = any(v.id in w for w in warnings)
        color = 'red' if is_warn else 'cyan'
        icon = "🚗" if not is_warn else "⚠️"

        # Add vehicle trail
        xs, ys = zip(*v.trail)
        fig.add_trace(go.Scatter(
            x=xs, y=ys,
            mode='lines',
            line=dict(color=color, width=2),
            opacity=0.6,
            showlegend=False
        ))

        # Add direction arrow
        arrow_len = 5
        dx = arrow_len * math.cos(math.radians(v.angle))
        dy = arrow_len * math.sin(math.radians(v.angle))
        fig.add_annotation(
            ax=v.x - dx, ay=v.y - dy,
            x=v.x + dx, y=v.y + dy,
            showarrow=True,
            arrowhead=3,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor=color
        )

        # Vehicle icon + label
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

    alerts_placeholder.subheader("⚠️ Collision Alerts")
    if warnings:
        for w in warnings:
            alerts_placeholder.error(w)
    else:
        alerts_placeholder.success("No imminent collisions detected.")

# 🚦 Always draw initial frame
messages, warnings = sim.simulate(do_move=False)
draw_radar(messages, warnings)

# 🟢 If simulation is running, keep updating
if st.session_state.running:
    while True:
        messages, warnings = sim.simulate(do_move=True)
        draw_radar(messages, warnings)
        time.sleep(loop_speed)

