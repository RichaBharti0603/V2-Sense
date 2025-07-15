import math
import streamlit as st
import plotly.graph_objects as go
import time
from world_simulator import WorldSimulator

st.set_page_config(page_title="V2Sense", layout="wide")

# ======================== HERO SECTION ========================
st.markdown("""
    <div style='text-align:center; padding: 30px 0;'>
        <h1 style='font-size: 3em; color: #00FFCC;'>🚗 V2Sense</h1>
        <h3 style='color: white;'>Vehicle-to-Vehicle Collision Prediction Mesh</h3>
        <p style='font-size: 18px; max-width:700px; margin:auto; color:#ccc;'>An AI-powered system for real-time vehicle communication, predictive collision alerts, and dynamic radar-based simulation for road safety.</p>
        <a href="#dashboard"><button style='margin-top:20px; font-size: 18px; padding: 10px 30px; background-color: #00cc99; color: white; border: none; border-radius: 5px;'>Explore Dashboard</button></a>
    </div>
""", unsafe_allow_html=True)

# ======================== INFO CARDS ========================
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🌐 Real-Time Mesh Communication")
    st.markdown("Vehicles broadcast their location, speed, and angle to nearby peers in real time.")

with col2:
    st.markdown("### 🚨 Predictive Collision Alerts")
    st.markdown("AI computes time-to-collision to detect and alert drivers before an accident occurs.")

with col3:
    st.markdown("### ⚙️ Customizable Simulation")
    st.markdown("Experiment with vehicle count, speed range, and radar radius interactively.")

# ======================== HOW IT WORKS ========================
st.markdown("---")
st.markdown("## 🛠️ How It Works")
st.markdown("""
1. 🚙 Vehicles collect data like **speed**, **angle**, and **position**.
2. 📡 Data is **broadcast** wirelessly to nearby vehicles.
3. 🧠 A central system predicts potential **collisions** using AI.
4. 🚨 Alerts are visualized in a **radar-style dashboard**.
""")

# ======================== MEET THE DEVICE ========================
st.markdown("---")
st.markdown("## 🔍 Meet the Device")
st.image("https://images.unsplash.com/photo-1604754742629-4f1c4df521cd?auto=format&fit=crop&w=500&q=80", caption="A palm-sized AI-driven sensor module for all types of vehicles", width=500)

# ======================== DASHBOARD SIMULATION ========================
st.markdown("---")
st.markdown("<h2 id='dashboard'>📊 Live Simulation Dashboard</h2>", unsafe_allow_html=True)

# ==== Sidebar Controls ====
with st.sidebar:
    st.header("⚙️ Simulation Controls")
    vehicle_count = st.slider("Number of Vehicles", 2, 10, 4)
    speed_min = st.slider("Min Speed", 1, 10, 5)
    speed_max = st.slider("Max Speed", 10, 30, 15)
    field_radius = st.slider("Field Radius", 50, 150, 100)
    loop_speed = st.slider("Simulation Speed (seconds)", 0.1, 2.0, 1.0)
    start_button = st.button("▶️ Start Simulation")
    stop_button = st.button("⏹️ Stop Simulation")

# ==== Session ====
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

    # Grid + Radar rings
    for r in range(-field_radius, field_radius + 1, 20):
        fig.add_shape(type="line", x0=r, y0=-field_radius, x1=r, y1=field_radius,
                      line=dict(color="rgba(50,50,50,0.3)", width=1))
        fig.add_shape(type="line", x0=-field_radius, y0=r, x1=field_radius, y1=r,
                      line=dict(color="rgba(50,50,50,0.3)", width=1))
    for r in range(20, field_radius + 1, 20):
        fig.add_shape(type="circle", x0=-r, y0=-r, x1=r, y1=r,
                      line=dict(color="rgba(0,255,0,0.2)", dash="dot"))
    fig.add_shape(type="line", x0=-field_radius, y0=0, x1=field_radius, y1=0, line=dict(color="green", width=1))
    fig.add_shape(type="line", x0=0, y0=-field_radius, x1=0, y1=field_radius, line=dict(color="green", width=1))

    for v in sim.vehicles:
        is_warn = any(v.id in w for w in warnings)
        color = 'red' if is_warn else 'cyan'
        icon = "🚗" if not is_warn else "⚠️"

        xs, ys = zip(*v.trail)
        fig.add_trace(go.Scatter(x=xs, y=ys, mode='lines', line=dict(color=color, width=2), opacity=0.6, showlegend=False))

        dx = 5 * math.cos(math.radians(v.angle))
        dy = 5 * math.sin(math.radians(v.angle))
        fig.add_annotation(ax=v.x - dx, ay=v.y - dy, x=v.x + dx, y=v.y + dy,
                           showarrow=True, arrowhead=3, arrowsize=1, arrowwidth=2, arrowcolor=color)
        fig.add_trace(go.Scatter(x=[v.x], y=[v.y], mode='markers+text',
                                 marker=dict(size=12, color=color),
                                 text=[f"{icon} {v.id}"], textposition="top center"))

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

    # 🚨 Alerts
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
                50% {{opacity: 0.4;}}
                100% {{opacity: 1;}}
            }}
            </style>
        """, unsafe_allow_html=True)

        for w in warnings:
            alerts_placeholder.error(w)
    else:
        alerts_placeholder.success("✅ No imminent collisions detected.")

# 🌟 Show default state
messages, warnings, _ = sim.simulate(do_move=False)
draw_radar(messages, warnings)

# 🔁 Loop
if st.session_state.running:
    while True:
        messages, warnings, _ = sim.simulate(do_move=True)
        draw_radar(messages, warnings)
        time.sleep(loop_speed)
