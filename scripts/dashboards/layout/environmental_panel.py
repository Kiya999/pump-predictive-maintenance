# environmental_panel.py
from dash import html, dcc
from layout.panel_styles import PANEL_STYLE, PANEL_TITLE_STYLE

def create_environmental_panel():
    return html.Div([
        html.H2("Environmental Context", style=PANEL_TITLE_STYLE),
        html.Div([
            html.Div([
                html.Span("Correlation:", style={"fontWeight": "bold", "fontSize": "12px"}),
                html.Span(
                    id="env-correlation-stat",
                    children="--",
                    style={
                        "fontSize": "16px",
                        "fontWeight": "bold",
                        "color": "#2c3e50",
                        "marginLeft": "8px",
                    }
                ),
            ], style={"display": "flex", "alignItems": "center"}),
            html.Div(
                id="env-overlap-message",
                children="",
                style={"fontSize": "11px", "color": "#7f8c8d", "marginTop": "4px"}
            ),
        ], style={
            "padding": "8px",
            "backgroundColor": "#ecf0f1",
            "borderRadius": "4px",
            "marginBottom": "8px",
            "border": "1px solid #bdc3c7"
        }),
        dcc.Graph(id="env-overlay-chart", style={"flex": 1, "minWidth": 0}),
        html.Div(
            id="env-data-alert",
            children="",
            style={
                "padding": "6px",
                "marginTop": "6px",
                "backgroundColor": "#fdeef4",
                "color": "#c0392b",
                "borderRadius": "4px",
                "display": "none",
                "fontSize": "11px"
            }
        ),
    ], style=PANEL_STYLE)