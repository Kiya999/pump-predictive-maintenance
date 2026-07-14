# app.py

import os
import sys
from sqlalchemy import create_engine
import dash
from dash import html, dcc

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(project_root, 'analytics-pipeline'))

from layout.header import create_header
from layout.asset_overview_panel import create_asset_overview_panel
from layout.historian_trends_panel import create_historian_trends_panel
from layout.alarm_analysis_panel import create_alarm_analysis_panel
from layout.environmental_panel import create_environmental_panel
from layout.motor_monitoring_panel import create_motor_monitoring_panel

from callbacks import environmental_callbacks
from callbacks import asset_overview_callbacks
from callbacks import historian_trends_callbacks
from callbacks import alarm_analysis_callbacks
from callbacks import baseline_cache_callbacks


db_path = os.path.join(os.path.dirname(__file__), "..", "etl-pipeline", "output", "etl_pipeline.db")

if not os.path.exists(db_path):
    print(f"Error: database not found at {db_path}")
    sys.exit(1)

engine = create_engine(f"sqlite:///{db_path}")
environmental_callbacks.set_engine(engine)
asset_overview_callbacks.set_engine(engine)
historian_trends_callbacks.set_engine(engine)
alarm_analysis_callbacks.set_engine(engine)
baseline_cache_callbacks.set_engine(engine)

app = dash.Dash(__name__)
app.title = "Pump & Motor Monitoring"

app.layout = html.Div([
    create_header(),

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
            create_alarm_analysis_panel(),
            create_environmental_panel(),
        ], style={"display": "flex", "gap": 15, "marginBottom": 15}),

        # Row 4: Motor Monitoring placeholder
        html.Div([
            create_motor_monitoring_panel(),
        ], style={"display": "flex", "gap": 15}),
    ], style={"maxWidth": 1800, "margin": "0 auto", "padding": "20px"}),

], style={"fontFamily": "sans-serif", "backgroundColor": "#ecf0f1", "minHeight": "100vh"})

if __name__ == "__main__":
    print("Starting app at http://127.0.0.1:8050")
    app.run(debug=True, host="127.0.0.1", port=8050)
