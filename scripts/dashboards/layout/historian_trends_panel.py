# historian_trends_panel.py
from dash import html

def create_historian_trends_panel():
    return html.Div([
        html.H2("Historian Trends", style={"marginTop": 0}),

        html.Div(
            id="historian-trends-content",
            children=html.P("", style={"color": "#7f8c8d"}),
        ),

    ], style={
        "flex": 1,
        "minWidth": 0,
        "padding": "20px",
        "backgroundColor": "#ffffff",
        "borderRadius": "8px",
        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
        "minHeight": "500px",
    })
