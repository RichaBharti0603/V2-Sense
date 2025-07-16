import math
import streamlit as st
import plotly.graph_objects as go
import time
from world_simulator import WorldSimulator

# Page Config
st.set_page_config(
    page_title="🚗 V2Sense",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for WOW UI
st.markdown("""
<style>
    html, body, [class*="css"] {
        background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
        color: white;
    }
    footer {visibility: hidden;}
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
    }
    .title-text {
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        color: #00FFFF;
        margin-bottom: 0.5rem;
    }
    .subtitle-text {
        font-size: 1.25rem;
        text-align: center;
        color: #ccc;
    }
</style>
""", unsafe_allow_html=True)

# Globals
image_path = "assets/landing_visual.png"
DASHBOARD_HEIGHT = 600

# Session State
if "show_dashboard" not in st.session_state:
    st.session_state.show_dashboard = False
if "sim" not in st.session_state:
    st.session_state.sim = WorldSimulator(num_vehicles=4)
if "running" not in st.session_state:
    st.session_state.running = False

# Landing Page
if not st.session_state.show_dashboard:
    st.markdown("<div class='title-text'>🚗 V2Sense: Collision Prediction Mesh</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle-text'>AI-based vehicle-to-vehicle safety mesh that predicts and prevents road accidents in real time.</div>", unsafe_allow_html=True)
    st.markdown("### 🌐 What is V2Sense?")
    st.markdown("V2Sense is an AI-powered simulation that models real-time vehicle communication to detect and prevent collisions using radar data, speed, direction, and proximity.")
    
    # Centered Image
    try:
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.image(image_path, use_container_width=True)
    except:
        st.warning("🚫 Landing image missing! Please save to `assets/landing_visual.png`")

    st.markdown("### 🚀 Features")
    st.markdown("""
    - Real-time radar simulation
    - Vehicle-to-vehicle communication mesh
    - Time-to-collision based alert system
    - Sound and visual alerts
    - Support for 2W/3W/4W vehicles
    """)

    if st.button("🚀 Explore Dashboard"):
        st.session_state.show_dashboard = True
        st.experimental_rerun()

    st.markdown("---")
    st.markdown("📂 [View on GitHub](https://github.com/RichaBharti0603/V2-Sense) | 📧 Contact: richa@example.com")
    st.stop()

# Sidebar Controls
with st.sidebar:
    st.header("⚙️ Simulation Controls")
    vehicle_count = st.slider("Number of Vehicles", 2, 10, 4)
    speed_min = st.slider("Min Speed", 1, 10, 5)
    speed_max = st.slider("Max Speed", 10, 30, 15)
    field_radius = st.slider("Field Radius", 50, 150, 100)
    loop_speed = st.slider("Simulation Speed (seconds)", 0.1, 2.0, 1.0)
    start_button = st.button("▶️ Start Simulation")
    stop_button = st.button("⏹️ Stop Simulation")

# Reset Simulator if vehicle count changes
if st.session_state.sim.num_vehicles != vehicle_count:
    st.session_state.sim = WorldSimulator(vehicle_count, speed_min, speed_max)

sim = st.session_state.sim
if start_button: st.session_state.running = True
if stop_button: st.session_state.running = False

map_placeholder = st.empty()
alerts_placeholder = st.empty()
broadcasts_expander = st.expander("📋 Vehicle Broadcasts")

# Draw Radar
def draw_radar(messages, warnings, comm_links=None, height=DASHBOARD_HEIGHT):
    fig = go.Figure()

    for r in range(-field_radius, field_radius + 1, 20):
        fig.add_shape(type="line", x0=r, y0=-field_radius, x1=r, y1=field_radius,
                      line=dict(color="rgba(80,80,80,0.2)", width=1))
        fig.add_shape(type="line", x0=-field_radius, y0=r, x1=field_radius, y1=r,
                      line=dict(color="rgba(80,80,80,0.2)", width=1))
    for r in range(20, field_radius + 1, 20):
        fig.add_shape(type="circle", x0=-r, y0=-r, x1=r, y1=r,
                      line=dict(color="rgba(0,255,0,0.1)", dash="dot"))

    fig.add_shape(type="line", x0=-field_radius, y0=0, x1=field_radius, y1=0,
                  line=dict(color="lime", width=1))
    fig.add_shape(type="line", x0=0, y0=-field_radius, x1=0, y1=field_radius,
                  line=dict(color="lime", width=1))

    # Vehicles
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
                                 text=[f"{icon} {v.id}"], textposition="top center"))

    # Communication Lines
    if comm_links:
        for id1, id2 in comm_links:
            v1 = next(v for v in sim.vehicles if v.id == id1)
            v2 = next(v for v in sim.vehicles if v.id == id2)
            fig.add_trace(go.Scatter(
                x=[v1.x, v2.x], y=[v1.y, v2.y],
                mode='lines',
                line=dict(color='deepskyblue', width=1, dash='dot'),
                showlegend=False
            ))

    fig.update_layout(
        xaxis=dict(range=[-field_radius, field_radius], visible=False),
        yaxis=dict(range=[-field_radius, field_radius], visible=False),
        height=height,
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white'),
        margin=dict(t=10, b=10, l=0, r=0),
        showlegend=False
    )
    map_placeholder.plotly_chart(fig, use_container_width=True)

    with broadcasts_expander:
        for msg in messages:
            st.json(msg)

    # Alerts Section
    alerts_placeholder.subheader("⚠️ Collision Alerts")
    if warnings:
        st.markdown("""
        <audio autoplay>
          <source src="https://www.soundjay.com/button/sounds/beep-07.mp3" type="audio/mpeg">
        </audio>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background-color:#ff4444;padding:10px;text-align:center;border-radius:5px;animation:flash 1s infinite;">
            🚨 <strong>Collision Warning!</strong> {len(warnings)} threats detected!
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

# Run Static Frame
messages, warnings, comm_links = sim.simulate(do_move=False)
draw_radar(messages, warnings, comm_links)

# Run Loop if Active
if st.session_state.running:
    while True:
        messages, warnings, comm_links = sim.simulate(do_move=True)
        draw_radar(messages, warnings, comm_links)
        time.sleep(loop_speed)
