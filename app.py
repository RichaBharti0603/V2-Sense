import math
import time
import streamlit as st
import plotly.graph_objects as go
from world_simulator import WorldSimulator

# Page config
st.set_page_config(page_title="V2Sense – Collision Prevention Mesh", layout="wide")

# ---------------------------------------------
# 🎯 Hero Section
# ---------------------------------------------
with st.container():
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="font-size: 3em;">🚗 V2Sense</h1>
            <p style="font-size: 1.5em;">Vehicle-to-Vehicle Collision Prediction Mesh</p>
            <p style="font-size: 1.1em; color: #ddd;">Smarter Roads. Safer Lives. For Everyone.</p>
        </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------
# 🧾 About Section
# ---------------------------------------------
with st.container():
    st.subheader("📘 What is V2Sense?")
    st.markdown("""
    **V2Sense** is a smart safety mesh system that enables vehicles to broadcast their live position, speed, and direction — allowing real-time prediction of potential collisions using a radar-inspired dashboard.

    - Helps reduce road accidents for 2W, 3W & 4W vehicles
    - Completely software-based prototype
    - Built using Python, Streamlit, and Plotly
    - Custom-designed for submission to the **James Dyson Award**
    """)

# ---------------------------------------------
# 🛠️ Key Features
# ---------------------------------------------
with st.container():
    st.subheader("🌟 Key Features")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("✅ **Real-Time Radar Mesh**")
        st.markdown("📡 **Vehicle Broadcast Simulation**")
    with col2:
        st.markdown("🧠 **Collision Prediction Engine**")
        st.markdown("🎯 **2W, 3W, 4W Compatible**")
    with col3:
        st.markdown("🚨 **Sound + Flash Alerts**")
        st.markdown("📈 **Expandable Smart Grid**")

# ---------------------------------------------
# ⚙️ Sidebar Config
# ---------------------------------------------
with st.sidebar:
    st.header("⚙️ Simulation Controls")
    vehicle_count = st.slider("Number of Vehicles", 2, 10, 4)
    speed_min = st.slider("Min Speed", 1, 10, 5)
    speed_max = st.slider("Max Speed", 10, 30, 15)
    field_radius = st.slider("Field Radius", 50, 150, 100)
    loop_speed = st.slider("Simulation Speed (seconds)", 0.1, 2.0, 1.0)
    start_button = st.button("▶️ Start Simulation")
    stop_button = st.button("⏹️ Stop Simulation")

# ---------------------------------------------
# 🧠 Simulation Setup
# ---------------------------------------------
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

# ---------------------------------------------
# 📡 Drawing Function
# ---------------------------------------------
def draw_radar(messages, warnings):
    fig = go.Figure()

    for r in range(-field_radius, field_radius + 1, 20):
        fig.add_shape(type="line", x0=r, y0=-field_radius, x1=r, y1=field_radius,
                      line=dict(color="rgba(50,50,50,0.3)", width=1))
        fig.add_shape(type="line", x0=-field_radius, y0=r, x1=field_radius, y1=r,
                      line=dict(color="rgba(50,50,50,0.3)", width=1))

    for r in range(20, field_radius + 1, 20):
        fig.add_shape(type="circle", x0=-r, y0=-r, x1=r, y1=r,
                      line=dict(color="rgba(0,255,0,0.2)", dash="dot"))

    fig.add_shape(type="line", x0=-field_radius, y0=0, x1=field_radius, y1=0,
                  line=dict(color="green", width=1))
    fig.add_shape(type="line", x0=0, y0=-field_radius, x1=0, y1=field_radius,
                  line=dict(color="green", width=1))

    for v in sim.vehicles:
        color = 'red' if any(v.id in w for w in warnings) else 'cyan'
        icon = "⚠️" if color == 'red' else "🚗"

        # Trail
        xs, ys = zip(*v.trail)
        fig.add_trace(go.Scatter(
            x=xs, y=ys,
            mode='lines',
            line=dict(color=color, width=2),
            opacity=0.6,
            showlegend=False
        ))

        # Arrow
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

        fig.add_trace(go.Scatter(
            x=[v.x], y=[v.y],
            mode='markers+text',
            marker=dict(size=12, color=color),
            text=[f"{icon} {v.id}"],
            textposition="top center",
            name=f"Vehicle {v.id}"
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

# ---------------------------------------------
# 🔄 Initial Frame
# ---------------------------------------------
messages, warnings = sim.simulate(do_move=False)
draw_radar(messages, warnings)

# ---------------------------------------------
# ▶️ Simulation Loop
# ---------------------------------------------
if st.session_state.running:
    while True:
        messages, warnings = sim.simulate(do_move=True)
        draw_radar(messages, warnings)
        time.sleep(loop_speed)

# ---------------------------------------------
# 📊 Architecture Preview
# ---------------------------------------------
with st.container():
    st.subheader("🧬 System Architecture")
    st.markdown("Here's how the communication mesh works across all vehicle nodes.")
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Vehicle_to_Vehicle_Communication_model.png/1200px-Vehicle_to_Vehicle_Communication_model.png", caption="Prototype Mesh Communication Model", use_column_width=True)

# ---------------------------------------------
# 📩 Footer
# ---------------------------------------------
st.markdown("---")
st.markdown("""
<center>
<p style='font-size: 0.9em;'>Made with ❤️ by Team V2Sense | For Dyson Award Submission 2025</p>
<p>
    <a href='https://github.com/YOUR_REPO' target='_blank'>🌐 GitHub</a> |
    <a href='mailto:contact@v2sense.com'>📧 Contact</a>
</p>
</center>
""", unsafe_allow_html=True)
