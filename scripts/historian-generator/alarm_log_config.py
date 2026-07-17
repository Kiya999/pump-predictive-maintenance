# alarm_log_config.py
"""Configuration for synthetic alarm log generation."""

import os

## Output Paths
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
CSV_PATH = os.path.join(OUTPUT_DIR, "alarm_log.csv")

## Alarm Generation Parameters (alarm_log_generator.py)
NORMAL_ALARMS_PER_ASSET_PER_DAY = 6
CHATTERING_EVENTS_COUNT = 7
CHATTERING_INTERVAL_MIN = 1.2
CHATTERING_DURATION_MIN = 0.8
STALE_ALARM_DURATION_MIN = 3120.0
CASCADE_BATCH_SIZE = 5
CASCADE_INTERVAL_SEC = 25
OPERATORS = ["OP01", "OP02", "OP03", "OP04", "OP05"]

## Alarm Duration Distribution (alarm_log_generator.py)
PRIORITY_DURATION_MEANS = {1: 3, 2: 10, 3: 25, 4: 60} # Duration means (minutes) by priority
PRIORITY_DURATION_STDS = {1: 1, 2: 4, 3: 10, 4: 30} # Duration stds (minutes) by priority

## Test Case Alarm Parameters (alarm_log_generator.py)
CHATTERING_ACK_DELAY_MIN = 0.6
STALE_ALARM_ACK_DELAY_MIN = 4.5
CASCADE_DURATION_MIN = 3.5
CASCADE_DURATION_MAX = 25.0
CASCADE_ACK_DELAY_MIN = 0.8

## ISA-18.2 Reference (alarm_log_generator.py)
ISA_18_2_ALARMS_PER_ASSET_PER_DAY_MAX = 144


## Alarm Definitions (alarm_log_generator.py)
ALARM_TAG_TEMPLATES = {
    "VI_HI":  {"desc": "Pump vibration high",        "priority": 2, "type": "HI", "family": "vibration"},
    "TI_HI":  {"desc": "Motor temperature high",     "priority": 2, "type": "HI", "family": "temperature"},
    "FI_LO":  {"desc": "Discharge flow low",         "priority": 3, "type": "LO", "family": "flow"},
    "PI_HI":  {"desc": "Discharge pressure high",    "priority": 3, "type": "HI", "family": "pressure"},
    "PI_LO":  {"desc": "Suction pressure low",       "priority": 2, "type": "LO", "family": "pressure"},
    "PDI_HI": {"desc": "Differential pressure high", "priority": 3, "type": "HI", "family": "pressure"},
    "II_HI":  {"desc": "Motor current high",         "priority": 2, "type": "HI", "family": "current"},
    "SI_LO":  {"desc": "Speed low",                  "priority": 4, "type": "LO", "family": "speed"},
}

FAILURE_FAMILY_MAP = {
    "bearing":    ["vibration", "temperature"],
    "cavitation": ["flow", "pressure"],
    "insulation": ["current", "temperature"],
}



## Quality Assessment Parameters (run_quality_alarm_log.py)
IQR_MULTIPLIER = 1.5