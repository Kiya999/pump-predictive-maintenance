# chatbot_panel.py
from dash import html, dcc
from dashboard_config import AVAILABLE_OLLAMA_MODELS, DEFAULT_OLLAMA_MODEL

SUGGESTED_QUESTIONS = [
    "How many assets are monitored?",
    "What is the problem with P-0100?",
    "Which pumps are healthy?",
    "Tell me about P-0300's cavitation issue.",
    # "What are the top alarm signatures for bearing wear?",
]

def create_chatbot_panel():
    return html.Div([
        html.H2("Fleet Assistant", style={"marginTop": 0, "marginBottom": "10px", "fontSize": "14px", "fontWeight": "600"}),

        html.Div([
            html.Label("Model:", style={"fontSize": "11px", "fontWeight": "bold", "marginBottom": "4px", "display": "block"}),
            dcc.Dropdown(
                id="chatbot-model-selector",
                options=[{"label": label, "value": tag} for label, tag in AVAILABLE_OLLAMA_MODELS],
                value=DEFAULT_OLLAMA_MODEL,
                clearable=False,
                style={"fontSize": "11px"},
            ),
        ], style={"marginBottom": "10px"}),

        dcc.Store(id="chatbot-history-store", data=[], storage_type="memory"),

        html.Div(id="chatbot-history-display", style={
            "maxHeight": "200px",
            "overflowY": "auto",
            "padding": "8px",
            "backgroundColor": "#f9f9f9",
            "borderRadius": "4px",
            "marginBottom": "10px",
            "fontSize": "11px",
            "border": "1px solid #ecf0f1",
            "flex": 1,
        }),

        html.Div([
            html.Label("Quick questions:", style={"fontSize": "10px", "fontWeight": "bold", "color": "#7f8c8d", "marginBottom": "4px", "display": "block"}),
            html.Div([
                html.Button(
                    q,
                    id={"type": "suggested-question", "index": i},
                    n_clicks=0,
                    style={
                        "display": "block",
                        "width": "100%",
                        "padding": "5px 8px",
                        "margin": "2px 0",
                        "backgroundColor": "#ecf0f1",
                        "color": "#2c3e50",
                        "border": "1px solid #bdc3c7",
                        "borderRadius": "3px",
                        "cursor": "pointer",
                        "fontSize": "10px",
                        "textAlign": "left",
                        "whiteSpace": "normal",

                    }
                )
                for i, q in enumerate(SUGGESTED_QUESTIONS)
            ], style={"marginBottom": "8px"}),
        ], style={"padding": "8px", "backgroundColor": "#fafafa", "borderRadius": "4px", "marginBottom": "10px", "flex": "0 0 auto"}),

        html.Div([
            dcc.Textarea(
                id="chatbot-input",
                placeholder="Type your question...",
                style={
                    "width": "100%",
                    "height": "60px",
                    "fontSize": "11px",
                    "padding": "6px",
                    "borderRadius": "3px",
                    "border": "1px solid #bdc3c7",
                    "fontFamily": "sans-serif",
                    "resize": "vertical",
                    "boxSizing": "border-box",
                },
            ),
            html.Button(
                "Send",
                id="chatbot-send-button",
                n_clicks=0,
                style={
                    "width": "100%",
                    "padding": "6px",
                    "marginTop": "6px",
                    "backgroundColor": "#2980b9",
                    "color": "white",
                    "border": "none",
                    "borderRadius": "3px",
                    "cursor": "pointer",
                    "fontSize": "11px",
                    "fontWeight": "bold",
                }
            ),
        ], style={"marginBottom": "8px", "flex": "0 0 auto"}),

    ], style={
        "display": "flex",
        "flexDirection": "column",
        "height": "100%",
        "padding": "10px",
    })