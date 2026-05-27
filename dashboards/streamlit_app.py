# streamlit_app.py
### Run in terminal: streamlit run streamlit_app.py
# Opens at http://localhost:8501

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from data_loader import load_combined

st.set_page_config(page_title="Potomac Dashboard", layout="wide")
st.title("Potomac River Discharge — Little Falls, DC")

@st.cache_data
def load_data():
    return load_combined()

with st.spinner("Loading..."):
    df = load_data()

st.sidebar.header("Controls")
min_d, max_d = df.index.min().date(), df.index.max().date()

start = st.sidebar.date_input("Start", min_d, min_value=min_d, max_value=max_d)
end = st.sidebar.date_input("End", max_d, min_value=min_d, max_value=max_d)

st.sidebar.subheader("Series")
show_q = st.sidebar.checkbox("Discharge", value=True)
show_temp = st.sidebar.checkbox("Temperature")
show_precip = st.sidebar.checkbox("Precipitation")

resample = st.sidebar.selectbox("Resample",
    ["None", "Daily", "Weekly", "Monthly"])

mask = (df.index >= pd.Timestamp(start)) & (df.index <= pd.Timestamp(end) + pd.Timedelta(days=1))
d = df.loc[mask].copy()

res_map = {"Daily": "1D", "Weekly": "1W", "Monthly": "1ME"}
if resample != "None":
    d = d.resample(res_map[resample]).mean()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Mean", f"{d['discharge_cfs'].mean():.0f} cfs")
c2.metric("Max", f"{d['discharge_cfs'].max():.0f} cfs")
c3.metric("Min", f"{d['discharge_cfs'].min():.0f} cfs")
c4.metric("Records", f"{len(d):,}")

has_w = show_temp or show_precip
show_any = show_q or has_w

if not show_any:
    st.info("Select at least one series to display.")
else:
    fig = make_subplots(specs=[[{'secondary_y': has_w}]])

    if show_q:
        fig.add_trace(go.Scatter(x=d.index, y=d['discharge_cfs'],
            name='Discharge (cfs)', line=dict(color='#2980b9', width=1.5)),
            secondary_y=False)

    if show_temp:
        fig.add_trace(go.Scatter(x=d.index, y=d['temp_c'],
            name='Temp (C)', line=dict(color='#e74c3c', width=1, dash='dash')),
            secondary_y=True)

    if show_precip:
        fig.add_trace(go.Bar(x=d.index, y=d['precip_mm'],
            name='Precip (mm)', marker=dict(color='#27ae60', opacity=0.3)),
            secondary_y=True)

    fig.update_layout(title=f'{start} to {end}', hovermode='x unified',
                      template='plotly_white', height=500)
    fig.update_yaxes(title_text='Discharge (cfs)', secondary_y=False)
    if has_w:
        fig.update_yaxes(title_text='Weather', secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)

with st.expander("Raw data"):
    st.dataframe(d.style.format({'discharge_cfs': '{:.0f}',
        'temp_c': '{:.1f}', 'precip_mm': '{:.1f}'}))
