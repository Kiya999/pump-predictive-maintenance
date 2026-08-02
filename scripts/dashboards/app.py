# app.py

import os
import sys
from sqlalchemy import create_engine
import dash
from dash import html, dcc, callback, Output, Input

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(project_root, 'analytics-pipeline'))

from layout.header import create_header
from layout.asset_overview_panel import create_asset_overview_panel
from layout.historian_trends_panel import create_historian_trends_panel
from layout.alarm_analysis_panel import create_alarm_analysis_panel
from layout.environmental_panel import create_environmental_panel
from layout.motor_monitoring_panel import create_motor_monitoring_panel
from layout.detection_performance_panel import create_detection_performance_panel
from layout.isa_alarm_panel import create_isa_alarm_panel
from layout.kpi_header_panel import create_kpi_header_panel
from layout.chatbot_panel import create_chatbot_panel

from callbacks import environmental_callbacks
from callbacks import asset_overview_callbacks
from callbacks import historian_trends_callbacks
from callbacks import alarm_analysis_callbacks
from callbacks import baseline_cache_callbacks
from callbacks import motor_monitoring_callbacks
from callbacks import detection_performance_callbacks  # noqa: F401
from callbacks import isa_alarm_callbacks  # noqa: F401
from callbacks import kpi_header_callbacks
from callbacks import chatbot_callbacks  # noqa: F401  (registers its @callback on import; no engine needed)

from dashboard_config import DB_PATH, APP_TITLE, APP_HOST, APP_PORT, APP_DEBUG, MAX_WIDTH, FONT_FAMILY

if not os.path.exists(DB_PATH):
    print(f"Error: database not found at {DB_PATH}")
    sys.exit(1)

engine = create_engine(f"sqlite:///{DB_PATH}")
environmental_callbacks.set_engine(engine)
asset_overview_callbacks.set_engine(engine)
historian_trends_callbacks.set_engine(engine)
alarm_analysis_callbacks.set_engine(engine)
baseline_cache_callbacks.set_engine(engine)
motor_monitoring_callbacks.set_engine(engine)
kpi_header_callbacks.set_engine(engine)

app = dash.Dash(__name__)
app.title = APP_TITLE

app.layout = html.Div([
    create_header(),

    html.Div(id="debug-store-display", style={"marginBottom": 10}),

    dcc.Store(id="baseline-store", data={}, storage_type="memory"),

    html.Div([
        # Row 1: Asset Overview (grid of 10 cards)
        html.Div([
            create_asset_overview_panel(),
        ], style={"marginBottom": 15}),

        # Row 2: Historian Trends (4-signal panel)
        html.Div([
            create_historian_trends_panel(),
        ], style={"marginBottom": 15}),

        # Row 3: Alarm Analysis + Environmental Context
        html.Div([
            html.Div([create_alarm_analysis_panel()], style={"flex": 2, "minWidth": 0}),
            html.Div([create_environmental_panel(), create_detection_performance_panel(), create_isa_alarm_panel(), create_kpi_header_panel()], style={"flex": 1, "minWidth": 0}),
        ], style={"display": "flex", "gap": 15, "marginBottom": 15}),
        
        # Row 4: Motor Monitoring
        html.Div([
            create_motor_monitoring_panel(),
        ], style={"display": "flex", "gap": 15, "marginBottom": 15}),

        # Row 5: Chatbot 
        html.Div([
            create_chatbot_panel(),
        ], style={"display": "flex", "gap": 15, "marginBottom": 15}),
        
    ], style={"maxWidth": MAX_WIDTH, "margin": "0 auto", "padding": "20px", "fontFamily": FONT_FAMILY, "color": "#2c3e50"}),

], style={"fontFamily": "sans-serif", "backgroundColor": "#ecf0f1", "minHeight": "100vh"})

@callback(
    Output("debug-store-display", "children"),
    Input("baseline-store", "data"),
)
def debug_store(store_data):
    if not store_data:
        return "Store is empty"
    
    # Show first 5 keys and sample of first signal
    keys = list(store_data.keys())[:5]
    preview = {k: list(store_data[k].get("flow_m3h", {}).keys()) if isinstance(store_data[k], dict) else "error" 
               for k in keys}
    
    return html.Div([
        html.H4("Debug: Baseline Store Contents"),
        html.Pre(f"Total cache entries: {len(store_data)}"),
        html.Pre(f"Sample keys: {keys}"),
        html.Pre(f"flow_m3h sub-keys (first entry): {preview[keys[0]] if keys else 'N/A'}"),
    ], style={"backgroundColor": "#fff3cd", "padding": "10px", "fontSize": 11, "whiteSpace": "pre-wrap"})


if __name__ == "__main__":
    print(f"Starting app at http://{APP_HOST}:{APP_PORT}")
    app.run(debug=APP_DEBUG, host=APP_HOST, port=APP_PORT)
