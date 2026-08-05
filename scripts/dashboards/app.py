# app.py

import os
import sys
from sqlalchemy import create_engine
import dash
from dash import html, dcc, callback, Output, Input, DiskcacheManager
import pandas as pd
import diskcache

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(project_root, 'analytics-pipeline'))

from layout.header import create_header
from layout.date_subsample_panel import create_date_subsample_panel
from layout.asset_overview_panel import create_asset_overview_panel
from layout.historian_trends_panel import create_historian_trends_panel
from layout.alarm_analysis_panel import create_alarm_analysis_panel
from layout.environmental_panel import create_environmental_panel
from layout.motor_monitoring_panel import create_motor_monitoring_panel
from layout.detection_performance_panel import create_detection_performance_panel
from layout.isa_alarm_panel import create_isa_alarm_panel
from layout.kpi_header_panel import create_kpi_header_panel
from layout.chatbot_panel import create_chatbot_panel
from layout.hero_metrics_panel import create_hero_metrics_panel
from layout.maintenance_comparison_panel import create_maintenance_comparison_panel

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
from callbacks import hero_metrics_callbacks  # noqa: F401
from callbacks import maintenance_comparison_callbacks

from dashboard_config import DB_PATH, APP_TITLE, APP_HOST, APP_PORT, APP_DEBUG, MAX_WIDTH, FONT_FAMILY

if not os.path.exists(DB_PATH):
    print(f"Error: database not found at {DB_PATH}")
    sys.exit(1)

def validate_db_schema(engine):
    """Ensure database has required tables and columns."""
    required_tables = {
        "historian_clean": ["asset_id", "timestamp", "flow_m3h", "diff_pressure_bar",
                           "motor_temp_c", "vibration_mm_s", "motor_power_kw", "speed_rpm", "failure_type", "quality_flag"],
        "alarm_log_clean": ["asset_id", "timestamp", "alarm_tag", "priority", "alarm_description",
                           "duration_min", "ack_time", "clear_time", "area", "alarm_type", "operator_id", "is_test_case", "quality_flag"],
        "environmental_clean": ["timestamp", "discharge_cfs", "quality_flag"],
    }

    for table, cols in required_tables.items():
        result = pd.read_sql(f"PRAGMA table_info({table})", engine)
        if result.empty:
            raise ValueError(f"Required table not found: {table}")

        existing_cols = set(result["name"].values)
        missing = [c for c in cols if c not in existing_cols]
        if missing:
            raise ValueError(f"Table {table} missing columns: {missing}")

engine = create_engine(f"sqlite:///{DB_PATH}")
validate_db_schema(engine)

environmental_callbacks.set_engine(engine)
asset_overview_callbacks.set_engine(engine)
historian_trends_callbacks.set_engine(engine)
alarm_analysis_callbacks.set_engine(engine)
baseline_cache_callbacks.set_engine(engine)
motor_monitoring_callbacks.set_engine(engine)
kpi_header_callbacks.set_engine(engine)
maintenance_comparison_callbacks.set_engine(engine)

cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheManager(cache)

app = dash.Dash(__name__, background_callback_manager=background_callback_manager)
app.title = APP_TITLE

app.layout = html.Div([
    create_header(),

    html.Div(id="debug-store-display", style={"marginBottom": 10, "display": "none"}),

    dcc.Store(id="baseline-store", data={}, storage_type="memory"),
    dcc.Store(id="chatbot-pending-trigger", data=None, storage_type="memory"),

    html.Div([
        html.Div([
            # Top: Date Range & Subsample Panel
            create_date_subsample_panel(),

            # Bottom: Chatbot Panel (fills remaining space)
            create_chatbot_panel(),
        ], style={
            "width": "20%",
            "height": "calc(100vh - 140px)",
            "borderRight": "1px solid #bdc3c7",
            "backgroundColor": "#ffffff",
            "overflowY": "auto",
            "display": "flex",
            "flexDirection": "column",
            "padding": "0",
            "boxSizing": "border-box",
        }),

        html.Div([
            # Row 0: Hero Metrics (50%) + Maintenance Comparison (50%)
            html.Div([
                html.Div([create_hero_metrics_panel()], style={"flex": 1, "minWidth": 0}),
                html.Div([create_maintenance_comparison_panel()], style={"flex": 1, "minWidth": 0}),
            ], style={"display": "flex", "gap": "12px", "marginBottom": "12px"}),

            # Row 1: ISA (50%) + KPI (50%)
            html.Div([
                html.Div([create_isa_alarm_panel()], style={"flex": 1, "minWidth": 0}),
                html.Div([create_kpi_header_panel()], style={"flex": 1, "minWidth": 0}),
            ], style={"display": "flex", "gap": "12px", "marginBottom": "12px"}),

            # Row 2: Asset Overview (full width)
            html.Div([
                create_asset_overview_panel(),
            ], style={"marginBottom": "12px"}),

            # Row 3: Historian Trends (full width)
            html.Div([
                create_historian_trends_panel(),
            ], style={"marginBottom": "12px"}),

            # Row 4: Motor Monitoring (50%) + Environmental (50%)
            html.Div([
                html.Div([create_motor_monitoring_panel()], style={"flex": 1, "minWidth": 0}),
                html.Div([create_environmental_panel()], style={"flex": 1, "minWidth": 0}),
            ], style={"display": "flex", "gap": "12px", "marginBottom": "12px"}),

            # Row 6: Detection Performance (50%) + Alarm Analysis (50%)
            html.Div([
                html.Div([create_detection_performance_panel()], style={"flex": 1, "minWidth": 0}),
                html.Div([create_alarm_analysis_panel()], style={"flex": 1, "minWidth": 0}),
            ], style={"display": "flex", "gap": "12px", "marginBottom": "12px"}),


        ], style={
            "flex": 1,
            "minWidth": 0,
            "padding": "12px",
            "fontFamily": FONT_FAMILY,
            "color": "#2c3e50",
            "overflowY": "auto",
            "boxSizing": "border-box",
        }),

    ], style={
        "display": "flex",
        "height": "calc(100vh - 140px)",
        "gap": "0",
    }),

], style={
    "fontFamily": FONT_FAMILY,
    "backgroundColor": "#f5f6fa",
    "minHeight": "100vh",
    "margin": 0,
    "padding": 0,
})

@callback(
    Output("debug-store-display", "children"),
    Input("baseline-store", "data"),
)
def debug_store(store_data):
    if not store_data:
        return "Store is empty"

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
