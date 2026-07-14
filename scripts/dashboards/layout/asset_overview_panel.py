# asset_overview_panel.py
from dash import html

def create_asset_overview_panel():
    return html.Div([
        html.H2("Asset Overview", style={"marginTop": 0}),

        html.Div(
            id="asset-overview-content",
            children=html.P("", style={"color": "#7f8c8d"}),
        ),

    ], style={
        # "flex": 1,
        "minWidth": 0,
        "padding": "20px",
        "backgroundColor": "#ffffff",
        "borderRadius": "8px",
        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
        "minHeight": "auto",
    })
