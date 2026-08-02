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
DEFAULT_START_DATE = "2025-03-31"
DEFAULT_END_DATE = "2025-04-14"



## Add this key to the existing OUTPUT_FILES dict in analytics_config.py:
OUTPUT_FILES = {
    "pf_alignment_csv": "pf_alignment_matrix.csv",
    "pf_alignment_excel": "pf_alignment_matrix.xlsx",
    "data_dictionary_excel": "data_dictionary.xlsx",
    "alarm_rate_daily": "alarm_rate_daily.csv",
    "alarm_frequency_top10": "alarm_frequency_top10.csv",
    "alarm_avg_time_to_ack": "alarm_avg_time_to_ack.csv",
    "alarm_stale_events": "alarm_stale_events.csv",
    "alarm_chattering_events": "alarm_chattering_events.csv",
    "alarm_clusters": "alarm_clusters.csv",
    "isa_validation_results": "isa_validation_results.json",  # NEW
}



## Chatbot
CHATBOT_DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "glossary") # lets test with this directory first. it has only one single file in it.
OLLAMA_HOST = "http://localhost:11434"
AVAILABLE_OLLAMA_MODELS = [
    ("Qwen2.5 3B (1.9GB, fastest)", "qwen2.5:3b"),
    ("Qwen3 8B (5.2GB, reasoning)", "qwen3:8b"),
]
DEFAULT_OLLAMA_MODEL = "qwen2.5:3b"

# Tune down if you see slow responses:
CHATBOT_MAX_CHARS_PER_FILE = 4000  

CHATBOT_REQUEST_TIMEOUT_S = 30
