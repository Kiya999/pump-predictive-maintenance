# dashboard_config.py
"""
Dashboard configuration: database path, app settings.
"""
import os

## Database
_script_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_script_dir, "..", "etl-pipeline", "output", "etl_pipeline.db")
DB_PATH = os.path.abspath(DB_PATH)

## App Settings (tunable)
APP_TITLE = "Pump and Motor Monitoring"
APP_HOST = "127.0.0.1"
APP_PORT = 8050
APP_DEBUG = True

## Unit System (tunable: "metric" or "imperial")
UNITS = "imperial"

## Layout (tunable)
MAX_WIDTH = 1800
FONT_FAMILY = "Segoe UI, sans-serif"
BG_COLOR = "#ecf0f1"

## Date Range Defaults (tunable)
DEFAULT_START_DATE = "2025-03-31"
DEFAULT_END_DATE = "2025-04-14"

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
    "isa_validation_results": "isa_validation_results.json",
}

## Chatbot
CHATBOT_DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "chatbot-docs")
OLLAMA_HOST = "http://localhost:11434"
AVAILABLE_OLLAMA_MODELS = [
    # ("llama3.2:1b (fastest)", "llama3.2:1b"),
    ("llama3.2:3b", "llama3.2:3b"),
    ("gemma3:4b", "gemma3:4b"),
]
DEFAULT_OLLAMA_MODEL = "llama3.2:3b"

# Tune down if you see slow responses:
CHATBOT_MAX_CHARS_PER_FILE = 10000

CHATBOT_REQUEST_TIMEOUT_S = 30
