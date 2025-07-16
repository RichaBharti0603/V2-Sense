import math
import streamlit as st
import plotly.graph_objects as go
import time
from world_simulator import WorldSimulator

# Config
st.set_page_config(
    page_title="🚗 V2Sense",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Globals
DASHBOARD_HEIGHT = 650
image_path = "assets/landing_visual.png"

# State
if "sim" not in st.session_state:
    st.session_state.sim = WorldSimulator(num_vehicles=4)
if "running" not in st.session_state:
    st.session_state.running = False
if "page" not in st.session_state:
    st.session_state.page = "Landing"

sim = st.session_state.sim

# ---------- Draw Radar Function ----------
def draw_radar(messages, warnings, comm_links=None, height=DASHBOARD_HEIGHT):
    fig = go.Figure()

    for r in range(-100, 101, 20):
        fig.add_shape(type="line", x0=r, y0=-100, x1=r, y1=100,
                      line=dict(color="rgba(50,50,50,0.3)", width=1))
        fig.add_shape(type="line", x0=-100, y0=r, x1=100, y1=r,
                      line=dict(color="rgba(50,50,50,0.3)", width=1))
    for r in range(20, 101, 20):
        fig.add_shape(type="circle", x0=-r, y0=-r, x1=r, y1=r,
                      line=dict(color="rgba(0,255,0,0.2)", dash="dot"))

    for v in sim.vehicles:
        color = 'red' if any(v.id in w for w in warnings) else 'cyan'
        icon = "⚠️" if color == 'red' else "🚗"
        xs, ys = zip(*v.trail[-15:]) if hasattr(v, "trail") else ([v.x], [v.y])
        fig.add_trace(go.Scatter(x=xs, y=ys, mode='lines',
                                 line=dict(color=color, width=2), showlegend=False))
        dx = 5 * math.cos(math.radians(v.angle))
        dy = 5 * math.sin(math.radians(v.angle))
        fig.add_annotation(ax=v.x - dx, ay=v.y - dy, x=v.x + dx, y=v.y + dy,
                           showarrow=True, arrowhead=3, arrowsize=1,
                           arrowwidth=2, arrowcolor=color)
        fig.add_trace(go.Scatter(x=[v.x], y=[v.y], mode='markers+text',
                                 marker=dict(size=14, color=color),
                                 text=[f"{icon} {v.id}"],
                                 textposition="top center"))

    if comm_links:
        for id1, id2 in comm_links:
            v1 = next(v for v in sim.vehicles if v.id == id1)
            v2 = next(v for v in sim.vehicles if v.id == id2)
            fig.add_trace(go.Scatter(
                x=[v1.x, v2.x],
                y=[v1.y, v2.y],
                mode='lines',
                line=dict(color='lime', width=1, dash='dot'),
                showlegend=False
            ))

    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=height,
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white'),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------- Pages ----------
st.sidebar.title("🌐 V2Sense Navigation")
page = st.sidebar.radio("Go to", ["Landing", "Live Radar", "Sensor Cockpit"])
st.session_state.page = page

# ========== LANDING PAGE ==========
if page == "Landing":
    st.markdown("<style>footer {visibility: hidden;}</style>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>🚗 V2Sense: Collision Prediction Mesh</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size:18px; color: gray;'>AI safety mesh to prevent collisions between cars, bikes, and autos.</p>", unsafe_allow_html=True)

    st.markdown(f"<div style='text-align:center'><img src='/{image_path}' width='550'/></div>", unsafe_allow_html=True)

    st.markdown("### 💡 How It Works")
    st.markdown("""
    - Vehicles periodically broadcast location and direction.
    - V2Sense captures telemetry and builds a **communication mesh**.
    - Predicts **Time-to-Collision (TTC)** in real time.
    - Raises alerts and shows simulation on radar.

    #### 💥 Emergency Detection + Visual Alerts  
    - 🔊 Sound alerts  
    - 🚨 Flashing red warning zone  
    - ⭕ Radar mesh with real-time trails  

    ---
    """)

    if st.button("🛰️ Launch Live Dashboard"):
        st.session_state.page = "Live Radar"
        st.rerun()

# ========== RADAR SIMULATION PAGE ==========
elif page == "Live Radar":
    st.title("📡 Real-Time Collision Mesh")
    with st.sidebar:
        st.subheader("⚙️ Controls")
        vehicle_count = st.slider("Vehicles", 2, 10, 4)
        speed_min = st.slider("Min Speed", 1, 10, 5)
        speed_max = st.slider("Max Speed", 10, 30, 15)
        st.session_state.sim = WorldSimulator(vehicle_count, speed_min, speed_max)
        start = st.button("▶️ Start")
        stop = st.button("⏹️ Stop")

    if start: st.session_state.running = True
    if stop: st.session_state.running = False

    placeholder = st.empty()
    alert_placeholder = st.empty()

    def show_radar_frame():
        messages, warnings, comm_links = sim.simulate(do_move=True)
        draw_radar(messages, warnings, comm_links)
        if warnings:
            st.error(f"🚨 {len(warnings)} collision threats detected!")

    # Static or Loop
    if not st.session_state.running:
        messages, warnings, comm_links = sim.simulate(do_move=False)
        draw_radar(messages, warnings, comm_links)
    else:
        while True:
            show_radar_frame()
            time.sleep(1)

# ========== SENSOR COCKPIT PAGE ==========
elif page == "Sensor Cockpit":
    st.title("🚘 Sensor Cockpit Interface")
    st.markdown("""
    ### Vehicle Internal View (Mocked 3D Cockpit)
    - GPS location: `Simulated`
    - Speedometer: `Live from simulation`
    - Nearby Vehicles: `Shown in minimap`
    - Threat Radar: `Color-coded detection zones`
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.image("https://i.imgur.com/wUO2nmK.png", caption="Cockpit HUD", use_column_width=True)

    with col2:
        st.image("https://i.imgur.com/XCFFxZW.png", caption="Sensor Grid", use_column_width=True)

    st.markdown("You can integrate **live GPS + vehicle IMU** in real deployments.")

