import math
import streamlit as st
import plotly.graph_objects as go
import time
from world_simulator import WorldSimulator

# Page config
st.set_page_config(
    page_title="🚗 V2Sense: Collision Prediction Mesh",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Session state init
if "show_dashboard" not in st.session_state:
    st.session_state.show_dashboard = False

if "sim" not in st.session_state:
    st.session_state.sim = WorldSimulator(num_vehicles=4)

if "running" not in st.session_state:
    st.session_state.running = False

# Landing Page
if not st.session_state.show_dashboard:
    st.markdown("""
        <style>
            .main { background-color: #0d1117; color: white; font-family: 'Segoe UI'; }
            h1, h2, h3, p { text-align: center; }
            .btn-center { display: flex; justify-content: center; margin-top: 20px; }
            .wow-list li { margin: 8px 0; font-size: 18px; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1>🚗 V2Sense: Collision Prediction Mesh</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:18px;'>AI-based vehicle-to-vehicle safety mesh to detect and prevent collisions in real-time.</p>", unsafe_allow_html=True)

    st.image("https://i.imgur.com/Df4Qazt.png", caption="Vehicle Sensor Mesh Simulation", use_container_width=True)

    st.markdown("### 🔍 How It Works")
    st.markdown("""
    - 🧠 Each vehicle broadcasts its position, speed, and direction.
    - 📡 Nearby vehicles receive and process these broadcasts.
    - 🤖 The system predicts Time-to-Collision (TTC).
    - 🚨 Visual + audio alerts are triggered when threats are detected.
    """)

    st.markdown("### 🌟 Features", unsafe_allow_html=True)
    st.markdown("""
    <ul class='wow-list'>
    <li>⚡ Real-time radar dashboard</li>
    <li>📶 Vehicle communication mesh</li>
    <li>🚦 Dynamic simulation & collision prediction</li>
    <li>📢 Audible and visual alerts</li>
    <li>🎯 Works for cars, 2-wheelers, and 3-wheelers</li>
    </ul>
    """, unsafe_allow_html=True)

    st.markdown("### 🧩 Learn More")
    st.markdown("""
    - [🔗 GitHub Repo](https://github.com/RichaBharti0603/V2-Sense)
    - [🌐 AI Simulation Demo](https://v2-sense.streamlit.app)
    """)

    if st.button("🚀 Explore Dashboard"):
        st.session_state.show_dashboard = True
        st.experimental_rerun()

    st.stop()

# Sidebar Controls
with st.sidebar:
    st.header("⚙️ Simulation Controls")
    vehicle_count = st.slider("Vehicles", 2, 10, 4)
    speed_min = st.slider("Min Speed", 1, 10, 5)
    speed_max = st.slider("Max Speed", 10, 30, 15)
    field_radius = st.slider("Field Radius", 50, 150, 100)
    loop_speed = st.slider("Simulation Speed", 0.1, 2.0, 1.0)
    start_button = st.button("▶️ Start Simulation")
    stop_button = st.button("⏹️ Stop Simulation")

# Init Simulation
if st.session_state.sim.num_vehicles != vehicle_count:
    st.session_state.sim = WorldSimulator(vehicle_count, speed_min, speed_max)

sim = st.session_state.sim

# Start/Stop
if start_button:
    st.session_state.running = True
if stop_button:
    st.session_state.running = False

# Placeholders
map_placeholder = st.empty()
alerts_placeholder = st.empty()
broadcasts_expander = st.expander("📋 Vehicle Broadcasts")

# Radar Function
def draw_radar(messages, warnings):
    fig = go.Figure()

    # Road Grid
    for r in range(-field_radius, field_radius + 1, 20):
        fig.add_shape(type="line", x0=r, y0=-field_radius, x1=r, y1=field_radius, line=dict(color="gray", width=0.5))
        fig.add_shape(type="line", x0=-field_radius, y0=r, x1=field_radius, y1=r, line=dict(color="gray", width=0.5))

    # Radar Rings
    for r in range(20, field_radius + 1, 20):
        fig.add_shape(type="circle", x0=-r, y0=-r, x1=r, y1=r, line=dict(color="lime", dash="dot", width=1))

    # Crosshairs
    fig.add_shape(type="line", x0=-field_radius, y0=0, x1=field_radius, y1=0, line=dict(color="green"))
    fig.add_shape(type="line", x0=0, y0=-field_radius, x1=0, y1=field_radius, line=dict(color="green"))

    # Vehicles
    for v in sim.vehicles:
        color = 'red' if any(v.id in w for w in warnings) else 'cyan'
        icon = "⚠️" if color == 'red' else "🚗"

        # Trail
        if hasattr(v, "trail") and len(v.trail) > 1:
            xs, ys = zip(*v.trail[-15:])
            fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=color), showlegend=False))

        # Direction Arrow
        dx = 5 * math.cos(math.radians(v.angle))
        dy = 5 * math.sin(math.radians(v.angle))
        fig.add_annotation(ax=v.x - dx, ay=v.y - dy, x=v.x + dx, y=v.y + dy, showarrow=True,
                           arrowhead=3, arrowwidth=2, arrowcolor=color)

        # Icon
        fig.add_trace(go.Scatter(
            x=[v.x], y=[v.y],
            mode="markers+text",
            marker=dict(size=14, color=color),
            text=[f"{icon} {v.id}"],
            textposition="top center"
        ))

    fig.update_layout(
        xaxis=dict(range=[-field_radius, field_radius], visible=False),
        yaxis=dict(range=[-field_radius, field_radius], visible=False),
        height=700,
        plot_bgcolor="#0d1117",
        paper_bgcolor="#0d1117",
        font=dict(color="white"),
        margin=dict(t=20, l=0, r=0, b=0)
    )

    map_placeholder.plotly_chart(fig, use_container_width=True)

    with broadcasts_expander:
        for msg in messages:
            st.json(msg)

    # Alerts
    alerts_placeholder.subheader("⚠️ Collision Alerts")
    if warnings:
        st.markdown("""
            <audio autoplay>
              <source src="https://www.soundjay.com/button/sounds/beep-07.mp3" type="audio/mpeg">
            </audio>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background-color:#ff4444;padding:10px;text-align:center;border-radius:5px;animation:flash 1s infinite;">
            🚨 <strong>Collision Warning!</strong> {len(warnings)} potential threats detected.
        </div>
        <style>
        @keyframes flash {{
            0% {{opacity: 1;}}
            50% {{opacity: 0.3;}}
            100% {{opacity: 1;}}
        }}
        </style>
        """, unsafe_allow_html=True)

        for w in warnings:
            alerts_placeholder.error(w)
    else:
        alerts_placeholder.success("✅ No imminent collisions detected.")

# Draw initial frame
messages, warnings = sim.simulate(do_move=False)
draw_radar(messages, warnings)

# Simulation Loop
if st.session_state.running:
    while True:
        messages, warnings = sim.simulate(do_move=True)
        draw_radar(messages, warnings)
        time.sleep(loop_speed)
