import streamlit as st
import plotly.graph_objects as go
import time
from world_simulator import WorldSimulator

# ---- Streamlit Setup ----
st.set_page_config(page_title="🚗 V2Sense: Live Radar", layout="wide")
st.title("🚗 V2Sense: Vehicle-to-Vehicle Collision Prediction Mesh (Live Radar UI)")

# ---- Simulation Parameters ----
vehicle_count = st.sidebar.slider("Number of Vehicles", 2, 10, 4)
speed_min = st.sidebar.slider("Min Speed", 5, 15, 8)
speed_max = st.sidebar.slider("Max Speed", 15, 30, 20)
field_radius = 100
frame_delay = 0.5  # seconds

# ---- Initialize Simulation State ----
if "sim" not in st.session_state:
    st.session_state.sim = WorldSimulator(
        num_vehicles=vehicle_count,
        speed_min=speed_min,
        speed_max=speed_max
    )

sim = st.session_state.sim

# ---- Start Button ----
if st.button("▶️ Start Simulation"):
    for frame in range(500):  # simulate for 500 frames max
        st.empty()  # Clear streamlit internal cache to refresh chart

        messages, warnings = sim.simulate()

        # ---- Plotly Radar Setup ----
        fig = go.Figure()

        # Radar ring
        fig.add_shape(
            type="circle",
            x0=-field_radius, y0=-field_radius,
            x1=field_radius, y1=field_radius,
            xref="x", yref="y",
            line=dict(color="lightgreen", width=1)
        )

        # Plot all vehicles
        for v in sim.vehicles:
            color = 'red' if any(v.id in w for w in warnings) else 'cyan'
            fig.add_trace(go.Scatter(
                x=[v.x], y=[v.y],
                mode='markers+text',
                marker=dict(size=12, color=color),
                text=[v.id],
                textposition="top center"
            ))

        # Draw lines between predicted collisions
        for warning in warnings:
            if "between" in warning:
                parts = warning.split("between ")[1].split(" and ")
                id1, id2 = parts[0], parts[1]
                v1 = next((v for v in sim.vehicles if v.id == id1), None)
                v2 = next((v for v in sim.vehicles if v.id == id2), None)
                if v1 and v2:
                    fig.add_trace(go.Scatter(
                        x=[v1.x, v2.x],
                        y=[v1.y, v2.y],
                        mode='lines',
                        line=dict(color='red', dash='dash')
                    ))

        # Chart layout
        fig.update_layout(
            xaxis=dict(range=[-field_radius-20, field_radius+20], showgrid=False, visible=False),
            yaxis=dict(range=[-field_radius-20, field_radius+20], showgrid=False, visible=False),
            height=600,
            plot_bgcolor='black',
            paper_bgcolor='black',
            font=dict(color='white'),
            title="📡 Live Vehicle Radar",
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

        # Vehicle broadcasts
        with st.expander("📋 Vehicle Broadcasts"):
            for msg in messages:
                st.json(msg)

        # Collision alerts
        st.subheader("⚠️ Collision Alerts")
        if warnings:
            for w in warnings:
                st.error(w)
        else:
            st.success("No imminent collisions detected.")

        # Pause for a frame
        time.sleep(frame_delay)

        # Refresh the page (automatically reruns loop)
        st.rerun()
