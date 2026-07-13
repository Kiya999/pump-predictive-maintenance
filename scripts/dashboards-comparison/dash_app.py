# dash_app.py
# open http://localhost:8501/ to visualize
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_loader import load_combined

print("Loading...")
df = load_combined()

app = dash.Dash(__name__)
app.title = "Potomac Dashboard"

app.layout = html.Div([
    html.H1("Potomac River Discharge — Little Falls, DC",
            style={'textAlign': 'center'}),

    html.Div([
        html.Div([html.H3(f"{df['discharge_cfs'].mean():.0f}"), html.P("Mean (cfs)")],
                 style={'display': 'inline-block', 'padding': '10px 20px'}),
        html.Div([html.H3(f"{df['discharge_cfs'].max():.0f}"), html.P("Max (cfs)")],
                 style={'display': 'inline-block', 'padding': '10px 20px'}),
        html.Div([html.H3(f"{df['discharge_cfs'].min():.0f}"), html.P("Min (cfs)")],
                 style={'display': 'inline-block', 'padding': '10px 20px'}),
        html.Div([html.H3(f"{len(df)}"), html.P("Records")],
                 style={'display': 'inline-block', 'padding': '10px 20px'}),
    ], style={'textAlign': 'center'}),

    html.Div([
        dcc.DatePickerRange(id='date-range',
            start_date=df.index.min(), end_date=df.index.max()),
        html.Label("Series:"),
        dcc.Checklist(id='toggle',
            options=[{'label': ' Discharge', 'value': 'q'},
                     {'label': ' Temp', 'value': 'temp'},
                     {'label': ' Precip', 'value': 'precip'}],
            value=['q'], inline=True),
    ]),

    dcc.Graph(id='main-chart', style={'height': '550px'}),
])

@app.callback(
    Output('main-chart', 'figure'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('toggle', 'value')]
)
def update_chart(start_date, end_date, toggles):
    if start_date is None:
        start_date = df.index.min()
    if end_date is None:
        end_date = df.index.max()

    mask = (df.index >= start_date) & (df.index <= end_date)
    d = df.loc[mask].copy()
    if d.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data in selected range",
                           xref="paper", yref="paper",
                           x=0.5, y=0.5, showarrow=False)
        fig.update_layout(height=500)
        return fig

    has_w = any(v in toggles for v in ['temp', 'precip'])
    fig = make_subplots(specs=[[{'secondary_y': has_w}]])

    if 'q' in toggles:
        fig.add_trace(
            go.Scatter(x=d.index, y=d['discharge_cfs'], name='Discharge (cfs)',
                       line=dict(color='#2980b9', width=1.5)), secondary_y=False)

    if 'temp' in toggles:
        fig.add_trace(
            go.Scatter(x=d.index, y=d['temp_c'], name='Temp (C)',
                       line=dict(color='#e74c3c', width=1, dash='dash')),
            secondary_y=True)

    if 'precip' in toggles:
        fig.add_trace(
            go.Bar(x=d.index, y=d['precip_mm'], name='Precip (mm)',
                   marker=dict(color='#27ae60', opacity=0.3)),
            secondary_y=True)

    fig.update_layout(title=f'{start_date} to {end_date}',
                      hovermode='x unified', template='plotly_white',
                      height=500)
    fig.update_yaxes(title_text='Discharge (cfs)', secondary_y=False)
    if has_w:
        fig.update_yaxes(title_text='Weather', secondary_y=True)
    return fig

if __name__ == '__main__':
    app.run(debug=True)