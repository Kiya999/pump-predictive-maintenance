# detection_performance_panel.py
from dash import html


def create_detection_performance_panel():
    return html.Div([
        html.H2("Detection Performance & Validation", style={"marginTop": 0}),

        html.Div([
            html.Span("Note: ", style={"fontWeight": "bold"}),
            html.Span(
                "These results come from a validation run against three "
                "synthetic failure scenarios (one instance each), not live "
                "detection. See caveat on sample size in the trend section "
                "below.",
                style={"color": "#7f8c8d"}
            ),
        ], style={
            "fontSize": 12, "padding": "8px 10px", "backgroundColor": "#fdf6e3",
            "borderLeft": "3px solid #f39c12", "marginBottom": 15,
        }),

        html.Div(id="detection-performance-kpi-row", style={
            "display": "flex", "gap": 10, "marginBottom": 15, "flexWrap": "wrap"
        }),

        html.H4("Lead time vs P-F interval, by scenario and method"),
        html.Div(id="lead-time-table"),

        html.H4("False positive rate by method (healthy assets)", style={"marginTop": 20}),
        html.Div(id="fp-rate-table"),

        html.H4("Trend significance (bearing scenario, Mann-Kendall)", style={"marginTop": 20}),
        html.Div(id="trend-detection-summary", style={"fontSize": 13}),

    ], style={
        "flex": 1, "minWidth": 0, "padding": 20, "backgroundColor": "#ffffff",
        "borderRadius": 8, "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
    })
