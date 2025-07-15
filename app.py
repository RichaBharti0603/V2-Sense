import math
import streamlit as st
import plotly.graph_objects as go
import time
from world_simulator import WorldSimulator

# Set page configuration
st.set_page_config(
    page_title="🚗 V2Sense",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"  # Sidebar collapsed initially
)

# Hide Streamlit footer
st.markdown("<style>footer {visibility: hidden;}</style>", unsafe_allow_html=True)

# Initialize session state
if "show_dashboard" not in st.session_state:
    st.session_state.show_dashboard = False
if "rerun_trigger" not in st.session_state:
    st.session_state.rerun_trigger = False
if "sim" not in st.session_state:
    st.session_state.sim = WorldSimulator(num_vehicles=4)
if "running" not in st.session_state:
    st.session_state.running = False

# Landing Page
if not st.session_state.show_dashboard:
    st.markdown("""
        <h1 style='text-align: center; font-size: 48px;'>🚗 V2Sense: Collision Prediction Mesh</h1>
        <p style='text-align: center; font-size: 20px; color: gray;'>AI-based vehicle-to-vehicle safety mesh that predicts and prevents road accidents in real time.</p>
    """, unsafe_allow_html=True)

    st.image("https://i.imgur.com/Df4Qazt.png", use_container_width=True)  # Updated param

    if st.button("🚀 Explore Dashboard"):
        st.session_state.show_dashboard = True
        st.session_state.rerun_trigger = True
        st.stop()

    if st.session_state.rerun_trigger:
        st.session_state.rerun_trigger = False
        st.experimental_rerun()

    st.stop()  # Prevent running further code on landing page

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

# Update simulation if vehicle count changes
if st.session_state.sim.num_vehicles != vehicle_count:
    st.session_state.sim = WorldSimulator(vehicle_count, speed_min, speed_max)

sim = st.session_state.sim

# Start/Stop toggle
if start_button:
    st.session_state.running = True
if stop_button:
    st.session_state.running = False

# UI Placeholders
map_placeholder = st.empty()
alerts_placeholder = st.empty()
broadcasts_expander = st.expander("📋 Vehicle Broadcasts")

# Draw UI
def draw_radar(messages, warnings):
    fig = go.Figure()

    # Radar grid and rings
    for r in range(-field_radius, field_radius + 1, 20):
        fig.add_shape(type="line", x0=r, y0=-field_radius, x1=r, y1=field_radius,
                      line=dict(color="rgba(50,50,50,0.3)", width=1))
        fig.add_shape(type="line", x0=-field_radius, y0=r, x1=field_radius, y1=r,
                      line=dict(color="rgba(50,50,50,0.3)", width=1))
    for r in range(20, field_radius + 1, 20):
        fig.add_shape(type="circle", x0=-r, y0=-r, x1=r, y1=r,
                      line=dict(color="rgba(0,255,0,0.2)", dash="dot"))

    # Axis lines
    fig.add_shape(type="line", x0=-field_radius, y0=0, x1=field_radius, y1=0, line=dict(color="green", width=1))
    fig.add_shape(type="line", x0=0, y0=-field_radius, x1=0, y1=field_radius, line=dict(color="green", width=1))

    # Plot each vehicle
    for v in sim.vehicles:
        color = 'red' if any(v.id in w for w in warnings) else 'cyan'
        icon = "⚠️" if color == 'red' else "🚗"

        # Trail
        if hasattr(v, "trail") and v.trail:
            xs, ys = zip(*v.trail[-15:])
            fig.add_trace(go.Scatter(x=xs, y=ys, mode='lines',
                                     line=dict(color=color, width=2), showlegend=False))

        # Direction
        dx = 5 * math.cos(math.radians(v.angle))
        dy = 5 * math.sin(math.radians(v.angle))
        fig.add_annotation(
            ax=v.x - dx, ay=v.y - dy,
            x=v.x + dx, y=v.y + dy,
            showarrow=True, arrowhead=3, arrowsize=1,
            arrowwidth=2, arrowcolor=color
        )

        # Marker
        fig.add_trace(go.Scatter(
            x=[v.x], y=[v.y],
            mode='markers+text',
            marker=dict(size=14, color=color),
            text=[f"{icon} {v.id}"],
            textposition="top center"
        ))

    # Layout
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

# Initial frame (no move)
messages, warnings = sim.simulate(do_move=False)
draw_radar(messages, warnings)

# Loop on run
if st.session_state.running:
    while True:
        messages, warnings = sim.simulate(do_move=True)
        draw_radar(messages, warnings)
        time.sleep(loop_speed)
