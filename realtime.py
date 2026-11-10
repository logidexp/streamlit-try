import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(
    page_title="Live Data Center Monitoring",
    layout="wide"
)

st.title("Live Data Center Monitoring")
st.caption("Synthetic Data — Demonstration Only")

if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(
        columns=["timestamp", "power_mw"]
    )

@st.fragment(run_every="200ms")
def live_dashboard():
    power = float(np.random.uniform(10, 18))
    capacity = 20.0
    utilization = power / capacity * 100

    new_row = pd.DataFrame([{
        "timestamp": datetime.now(),
        "power_mw": power
    }])

    st.session_state.history = pd.concat(
        [st.session_state.history, new_row],
        ignore_index=True
    ).tail(100)

    col1, col2, col3 = st.columns(3)

    col1.metric("Current Power", f"{power:.2f} MW")
    col2.metric("Power Capacity", f"{capacity:.2f} MW")
    col3.metric("Utilization", f"{utilization:.1f}%")

    st.line_chart(
        st.session_state.history.set_index("timestamp"),
        y="power_mw"
    )

live_dashboard()