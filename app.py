import streamlit as st
import plotly.graph_objects as go
import time
from world_simulator import WorldSimulator

st.set_page_config(page_title="V2Sense Radar UI", layout="wide")
st.title("🚗 V2Sense: Vehicle-to-Vehicle Collision Prediction Mesh (Plotly Radar)")

# Initialize simulation
if "sim" not in st.session_state:
    st.session_state.sim = WorldSimulator(num_vehicles=4)

sim = st.session_state.sim
messages, warnings = sim.simulate()

# Setup Plotly radar-like chart
fig = go.Figure()

# Radar circle
fig.add_shape(type="circle", xref="x", yref="y",
              x0=-100, y0=-100, x1=100, y1=100,
              line_color="lightgreen")

# Add vehicle positions
for v in sim.vehicles:
    color = 'red' if any(v.id in w for w in warnings) else 'cyan'
    fig.add_trace(go.Scatter(
        x=[v.x], y=[v.y],
        mode='markers+text',
        marker=dict(size=14, color=color),
        text=[v.id],
        textposition="top center",
        name=f"Vehicle {v.id}"
    ))

fig.update_layout(
    xaxis=dict(range=[-120, 120], zeroline=False, showgrid=False, visible=False),
    yaxis=dict(range=[-120, 120], zeroline=False, showgrid=False, visible=False),
    height=600,
    plot_bgcolor='black',
    paper_bgcolor='black',
    font=dict(color='white'),
    title="📡 Real-Time V2V Radar Tracking",
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# Vehicle data
with st.expander("📋 Vehicle Broadcasts"):
    for msg in messages:
        st.json(msg)

# Alerts section
st.subheader("⚠️ Collision Alerts")
if warnings:
    for w in warnings:
        st.error(w)
else:
    st.success("No imminent collisions detected.")

# Auto-refresh logic (safe)
if st.button("🔁 Refresh Simulation"):
    st.rerun()
