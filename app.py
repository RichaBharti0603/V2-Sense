import math
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

def draw_radar(messages, warnings, comm_links):
    fig = go.Figure()

    # Background grid (simulated roads)
    for r in range(-field_radius, field_radius + 1, 20):
        fig.add_shape(type="line", x0=r, y0=-field_radius, x1=r, y1=field_radius,
                      line=dict(color="rgba(50,50,50,0.3)", width=1))
        fig.add_shape(type="line", x0=-field_radius, y0=r, x1=field_radius, y1=r,
                      line=dict(color="rgba(50,50,50,0.3)", width=1))

    # Pulsing radar rings
    for r in range(20, field_radius + 1, 20):
        fig.add_shape(type="circle", x0=-r, y0=-r, x1=r, y1=r,
                      line=dict(color="rgba(0,255,0,0.2)", dash="dot"))

    # Radar crosshairs
    fig.add_shape(type="line", x0=-field_radius, y0=0, x1=field_radius, y1=0,
                  line=dict(color="green", width=1))
    fig.add_shape(type="line", x0=0, y0=-field_radius, x1=0, y1=field_radius,
                  line=dict(color="green", width=1))

    # Vehicles & Trails
    for v in sim.vehicles:
        is_warn = any(v.id in w for w in warnings)
        color = 'red' if is_warn else 'cyan'
        icon = "🚗" if not is_warn else "⚠️"

        xs, ys = zip(*v.trail)
        fig.add_trace(go.Scatter(x=xs, y=ys, mode='lines', line=dict(color=color, width=2), opacity=0.6))

        # Arrow (direction)
        dx = 5 * math.cos(math.radians(v.angle))
        dy = 5 * math.sin(math.radians(v.angle))
        fig.add_annotation(ax=v.x - dx, ay=v.y - dy,
                           x=v.x + dx, y=v.y + dy,
                           arrowhead=3, arrowsize=1, arrowwidth=2,
                           arrowcolor=color, showarrow=True)

        fig.add_trace(go.Scatter(x=[v.x], y=[v.y], mode='markers+text',
                                 marker=dict(size=12, color=color),
                                 text=[f"{icon} {v.id}"],
                                 textposition="top center"))

    # Communication lines
    for id1, id2 in comm_links:
        v1 = next(v for v in sim.vehicles if v.id == id1)
        v2 = next(v for v in sim.vehicles if v.id == id2)
        fig.add_trace(go.Scatter(x=[v1.x, v2.x], y=[v1.y, v2.y],
                                 mode='lines',
                                 line=dict(color="orange", dash="dot", width=1),
                                 showlegend=False))

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

    # 🚨 Collision Alerts Section
    alerts_placeholder.subheader("⚠️ Collision Alerts")
    if warnings:
        st.markdown("""
            <audio autoplay>
              <source src="https://www.soundjay.com/button/sounds/beep-07.mp3" type="audio/mpeg">
            </audio>
        """, unsafe_allow_html=True)

        st.markdown(
            f"""
            <div style="background-color:#ff4444;padding:10px;text-align:center;border-radius:5px;animation:flash 1s infinite;">
                🚨 <strong>Collision Warning!</strong> {len(warnings)} potential threats detected.
            </div>
            <style>
            @keyframes flash {{
                0% {{opacity: 1;}}
                50% {{opacity: 0.4;}}
                100% {{opacity: 1;}}
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
        for w in warnings:
            alerts_placeholder.error(w)
    else:
        alerts_placeholder.success("✅ No imminent collisions detected.")

# 🧠 Initial static radar
messages, warnings, comm_links = sim.simulate(do_move=False)
draw_radar(messages, warnings, comm_links)

# 🌀 Live simulation
if st.session_state.running:
    while True:
        messages, warnings, comm_links = sim.simulate(do_move=True)
        draw_radar(messages, warnings, comm_links)
        time.sleep(loop_speed)
