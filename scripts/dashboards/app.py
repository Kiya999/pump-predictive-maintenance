# app.py

import os
import sys
from sqlalchemy import create_engine
import dash
from dash import html

from layout.header import create_header
from layout.asset_overview_panel import create_asset_overview_panel
from layout.historian_trends_panel import create_historian_trends_panel
from layout.alarm_analysis_panel import create_alarm_analysis_panel
from layout.environmental_panel import create_environmental_panel
from callbacks import environmental_callbacks


db_path = os.path.join(os.path.dirname(__file__), "..", "etl-pipeline", "output", "etl_pipeline.db")

if not os.path.exists(db_path):
    print(f"Error: database not found at {db_path}")
    sys.exit(1)

engine = create_engine(f"sqlite:///{db_path}")
environmental_callbacks.set_engine(engine)

app = dash.Dash(__name__)
app.title = "Pump & Motor Monitoring"

app.layout = html.Div([
    create_header(),

    html.Div([
        # Row 1: Asset Overview + Historian Trends
        html.Div([
            create_asset_overview_panel(),
            create_historian_trends_panel(),
        ], style={"display": "flex", "gap": 15, "marginBottom": 15}),

        # Row 2: Alarm Analysis + Environmental Context
        html.Div([
            create_alarm_analysis_panel(),
            create_environmental_panel(),
        ], style={"display": "flex", "gap": 15}),
    ], style={"maxWidth": 1800, "margin": "0 auto", "padding": "20px"}),

], style={"fontFamily": "sans-serif", "backgroundColor": "#ecf0f1", "minHeight": "100vh"})

if __name__ == "__main__":
    print("Starting app at http://127.0.0.1:8050")
    app.run(debug=True, host="127.0.0.1", port=8050)