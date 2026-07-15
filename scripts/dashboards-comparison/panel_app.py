# panel_app.py
### Although we used axiswise=True, all of the series use the same y axis, which is not good.
# open http://localhost:57792/ to visualize
import panel as pn
import holoviews as hv
import pandas as pd

from data_loader import load_combined

pn.extension()
hv.extension('bokeh')

print("Loading...")
df = load_combined()

date_slider = pn.widgets.DateRangeSlider(
    name='Date range',
    start=df.index.min(), end=df.index.max(),
    value=(df.index.min(), df.index.max()))

series_cb = pn.widgets.CheckBoxGroup(
    name='Series', value=['Discharge'],
    options=['Discharge', 'Temperature', 'Precipitation'], inline=True)

agg_sel = pn.widgets.Select(name='Resample',
    value='Hourly', options=['Hourly', 'Daily', 'Weekly', 'Monthly'])

def plot_curve(date_range, series, agg):
    start, end = date_range
    mask = (df.index >= pd.Timestamp(start)) & (df.index <= pd.Timestamp(end))
    d = df.loc[mask].copy()

    agg_map = {'Hourly': '1H', 'Daily': '1D', 'Weekly': '1W', 'Monthly': '1ME'}
    if agg != 'Hourly':
        d = d.resample(agg_map[agg]).mean()

    if d.empty or len(series) == 0:
        return hv.Curve([]).opts(title="No data")

    overlay = None
    if 'Discharge' in series:
        overlay = hv.Curve((d.index, d['discharge_cfs']), 'Date', 'Discharge (cfs)').opts(
            color='steelblue', line_width=1.5, responsive=True,
            height=500, yaxis='left',
            axiswise=True)

    if 'Temperature' in series:
        t = hv.Curve((d.index, d['temp_c']), 'Date', 'Temp (C)').opts(
            color='crimson', line_dash='dashed', yaxis='right',
            axiswise=True)
        overlay = (overlay * t) if overlay else t

    if 'Precipitation' in series:
        p = hv.Bars((d.index, d['precip_mm']), 'Date', 'Precip (mm)').opts(
            color='green', alpha=0.3, yaxis='left',
            axiswise=True)
        overlay = (overlay * p) if overlay else p

    title_str = f'{start} to {end}'
    return overlay.opts(axiswise=True, title=title_str)

def stats(date_range):
    start, end = date_range
    mask = (df.index >= pd.Timestamp(start)) & (df.index <= pd.Timestamp(end))
    d = df.loc[mask]
    return pn.pane.Str(
        f"Records: {len(d)} | Mean: {d['discharge_cfs'].mean():.0f} | "
        f"Max: {d['discharge_cfs'].max():.0f} | Min: {d['discharge_cfs'].min():.0f}")

dashboard = pn.Column(
    pn.pane.Markdown("# Potomac River Discharge"),
    pn.Row(
        pn.Column(pn.WidgetBox("## Controls", date_slider, series_cb, agg_sel),
                  pn.bind(stats, date_slider.param.value)),
        pn.pane.HoloViews(pn.bind(plot_curve, date_slider.param.value,
                                   series_cb.param.value, agg_sel.param.value),
                          sizing_mode='stretch_both'),
        sizing_mode='stretch_both'),
    sizing_mode='stretch_both'
)

if __name__ == '__main__':
    dashboard.servable()
    pn.serve(dashboard, show=False, port=57792)