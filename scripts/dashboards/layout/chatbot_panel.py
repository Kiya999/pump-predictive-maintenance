# chatbot_panel.py
from dash import html, dcc
from dashboard_config import AVAILABLE_OLLAMA_MODELS, DEFAULT_OLLAMA_MODEL

def create_chatbot_panel():
    return html.Div([
        html.H2("Ask About This Fleet", style={"marginTop": 0}),

        html.Div([
            html.Span("Note: ", style={"fontWeight": "bold"}),
            html.Span(
                "Answers are only as accurate as the source documents provided.",
                style={"color": "#7f8c8d"}
            ),
        ], style={
            "fontSize": 12,
            "padding": "8px 10px",
            "backgroundColor": "#fdf6e3",
            "borderLeft": "3px solid #f39c12",
            "marginBottom": 12,
        }),

        html.Div([
            html.Label("Model:", style={"fontSize": 12, "fontWeight": "bold", "marginRight": 8}),
            dcc.Dropdown(
                id="chatbot-model-selector",
                options=[{"label": label, "value": tag} for label, tag in AVAILABLE_OLLAMA_MODELS],
                value=DEFAULT_OLLAMA_MODEL,
                clearable=False,
                style={"width": 280, "display": "inline-block", "fontSize": 12},
            ),
        ], style={"marginBottom": 12, "display": "flex", "alignItems": "center"}),
            
        dcc.Store(id="chatbot-history-store", data=[], storage_type="memory"),

        html.Div(id="chatbot-history-display", style={
            "maxHeight": 260,
            "overflowY": "auto",
            "padding": 10,
            "backgroundColor": "#f9f9f9",
            "borderRadius": 6,
            "marginBottom": 10,
            "fontSize": 13,
        }),

        html.Div([
            dcc.Textarea(
                id="chatbot-input",
                placeholder="e.g. What is the bearing failure lead time for P-0100?",
                style={"width": "100%", "height": 60, "fontSize": 13},
            ),
            html.Button(
                "Ask",
                id="chatbot-submit-btn",
                n_clicks=0,
                style={
                    "marginTop": 8,
                    "padding": "6px 18px",
                    "backgroundColor": "#2980b9",
                    "color": "white",
                    "border": "none",
                    "borderRadius": 4,
                    "cursor": "pointer",
                },
            ),
        ]),

        dcc.Loading(
            id="chatbot-loading",
            type="dot",
            children=html.Div(id="chatbot-loading-anchor"),
        ),

    ], style={
        "flex": 1,
        "minWidth": 0,
        "padding": 20,
        "backgroundColor": "#ffffff",
        "borderRadius": 8,
        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
    })
