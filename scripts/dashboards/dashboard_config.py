# dashboard_config.py
"""
Dashboard configuration: database path, app settings.
"""

import os

## Database
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "etl-pipeline", "output", "etl_pipeline.db")

## App Settings (tunable)
APP_TITLE = "Pump and Motor Monitoring"
APP_HOST = "127.0.0.1"
APP_PORT = 8050
APP_DEBUG = True

## Layout (tunable)
MAX_WIDTH = 1800
FONT_FAMILY = "Segoe UI, sans-serif"
BG_COLOR = "#ecf0f1"

## Date Range Defaults (tunable)
DEFAULT_START_DATE = "2025-07-21"
DEFAULT_END_DATE = "2025-07-31"