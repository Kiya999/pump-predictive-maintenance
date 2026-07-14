# environmental_panel.py
from dash import html, dcc

def create_environmental_panel():
    return html.Div([
        html.H2("Environmental Context", style={"marginTop": 20}),

        html.Div([
            html.Div([
                html.Span("Correlation (Overlap):", style={"fontWeight": "bold"}),
                html.Span(
                    id="env-correlation-stat",
                    children="--",
                    style={
                        "fontSize": 24,
                        "fontWeight": "bold",
                        "color": "#2c3e50",
                        "marginLeft": 15,
                        "fontFamily": "monospace"
                    }
                ),
            ], style={"display": "flex", "alignItems": "center"}),

            html.Div(
                id="env-overlap-message",
                children="",
                style={"fontSize": 12, "color": "#7f8c8d", "marginTop": 8}
            ),
        ], style={
            "padding": 15,
            "backgroundColor": "#ecf0f1",
            "borderRadius": 5,
            "marginBottom": 15,
            "border": "1px solid #bdc3c7"
        }),

        dcc.Graph(id="env-overlay-chart", style={"height": "450px"}),

        html.Div(
            id="env-data-alert",
            children="",
            style={
                "padding": 12,
                "marginTop": 15,
                "backgroundColor": "#fdeef4",
                "color": "#c0392b",
                "borderRadius": 5,
                "display": "none",
                "fontSize": 13
            }
        ),

    ], style={
        "flex": 1,
        "minWidth": 0,
        "padding": "20px",
        "backgroundColor": "#ffffff",
        "borderRadius": "8px",
        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
    })
