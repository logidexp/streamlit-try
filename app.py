from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Capacity planner", layout="wide")
sites = pd.read_csv(Path(__file__).with_name("facilities.csv")).set_index("facility")
resources = [
    ("Power", "power_used_mw", "power_capacity_mw", "expansion_power_mw", "MW electrical"),
    ("Cooling", "cooling_used_mw", "cooling_capacity_mw", "expansion_cooling_mw", "MW thermal"),
    ("Racks", "racks_used", "racks_capacity", "expansion_racks", "racks"),
]

st.title("Data center capacity planner")
st.caption("Six fictional facilities • Monthly projections from current demand")
growth_adjustment = st.sidebar.slider("Annual growth adjustment (percentage points)", -5, 15, 0)
horizon = st.sidebar.slider("Forecast horizon (months)", 12, 60, 36, step=6)
expanded = st.sidebar.checkbox("Add planned expansions at month 0")
facility = st.sidebar.selectbox("Forecast facility", sites.index)
st.header("Portfolio today")
cards = st.columns(3)
rows = []
for card, (label, used, capacity, addition, unit) in zip(cards, resources):
    available = sites[capacity] + (sites[addition] if expanded else 0)
    utilization = sites[used] / available
    card.metric(f"{label} utilization", f"{sites[used].sum() / available.sum():.1%}")
    card.caption(f"{sites[used].sum():g} of {available.sum():g} {unit}")
    for name, share in utilization.items():
        rows.append({"Facility": name, "Resource": label, "Utilization (%)": share * 100})

st.header("Facility comparison")
comparison = px.bar(pd.DataFrame(rows), x="Facility", y="Utilization (%)",
                    color="Resource", barmode="group")
comparison.update_yaxes(range=[0, 105])
st.plotly_chart(comparison, use_container_width=True)

site = sites.loc[facility]
rate = (site.annual_growth_pct + growth_adjustment) / 100
st.header(f"{facility} forecast")
st.caption(f"Annual compound growth {rate:.1%} • Capacity held constant over {horizon} months")
breaches = {}
tabs = st.tabs([resource[0] for resource in resources])
for tab, (label, used, capacity, addition, unit) in zip(tabs, resources):
    limit = site[capacity] + (site[addition] if expanded else 0)
    months = range(horizon + 1)
    demand = [site[used] * (1 + rate) ** (month / 12) for month in months]
    crossing = next((m for m in months if demand[m] > limit), None)
    if crossing is not None:
        breaches[label] = crossing
    with tab:
        chart = px.line(pd.DataFrame({"Month": months, "Demand": demand, "Capacity": limit}),
                        x="Month", y=["Demand", "Capacity"],
                        labels={"value": unit, "variable": "Series"})
        chart.update_yaxes(rangemode="tozero")
        st.plotly_chart(chart, use_container_width=True, key=label)
if breaches:
    first = min(breaches.values())
    labels = ", ".join(label for label, month in breaches.items() if month == first)
    st.warning(f"First capacity overrun at {facility}: {labels} in month {first}.")
else:
    st.success(f"All three resources stay within capacity through month {horizon}.")
