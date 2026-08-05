# Configuration Reference

This document lists every tunable parameter across all modules in the pump predictive maintenance pipeline. Values are organized by source module.

## USGS Weather Analysis

### usgs_weather_analysis.py

| Parameter | Type | Default | Valid Range | Description |
|-----------|------|---------|-------------|-------------|
| DC_LAT | float | 38.9072 | N/A | Latitude for Open-Meteo weather lookup (Washington, DC) |
| DC_LON | float | -77.0369 | N/A | Longitude for Open-Meteo weather lookup (Washington, DC) |
| SITE_ID | string | '01646500' | USGS 8-digit site code | USGS gauge: Potomac River near Washington, DC (Little Falls) |
| START_DATE | string | '2025-02-01' | YYYY-MM-DD | Fixed start date for reproducible data window |
| END_DATE | string | '2026-02-01' | YYYY-MM-DD | Fixed end date for reproducible data window |
| OUTPUT_DIR | string | 'output' | valid path | Directory for all output files (plots, CSV, results) |
| RESAMPLE_FREQ | string | '1H' | pandas resample freq | Time frequency for resampling raw streamflow data |
| GAP_THRESHOLD_MIN | int | 15 | 1-1440 | Threshold in minutes for flagging gaps in data |
| LAG_TARGETS_HOURS | list[int] | [0, 6, 12, 24] | N/A | Specific lag hours to compute correlation at |
| MAX_LAG_HOURS | int | 72 | 1-360 | Maximum lag window to search for correlation peaks |

### run_quality_usgs.py

| Parameter | Type | Default | Valid Range | Description |
|-----------|------|---------|-------------|-------------|
| SITE_ID | string | '01646500' | USGS 8-digit site code | USGS gauge for quality assessment |
| START_DATE | string | '2025-07-14' | YYYY-MM-DD | Fixed start date for reproducible data window |
| END_DATE | string | '2026-07-14' | YYYY-MM-DD | Fixed end date for reproducible data window |
| RAW_CSV_PATH | string | 'output/usgs_raw.csv' | valid path | Path to cached raw streamflow CSV |
| DATA_QUALITY_SUBDIR_PATH | string | 'output/data_quality' | valid path | Directory for quality report outputs |
| IQR_MULTIPLIER | float | 1.5 | 0.5-3.0 | IQR fence multiplier for outlier detection |

## ETL Pipeline

### etl_config.py

| Parameter | Type | Default | Valid Range | Description |
|-----------|------|---------|-------------|-------------|
| sources.historian.path | string | '../historian-generator/output/synthetic_historian_10x365_1min.csv' | file path | Historian CSV export location |
| sources.historian.frequency | string | '1min' | '1min' or pandas freq | Resample frequency ('1min' = no resampling) |
| sources.historian.timestamp_col | string | 'timestamp' | column name | Historian timestamp column name in raw CSV |
| sources.historian.tz | string | 'UTC' | timezone | Timezone of raw historian timestamps |
| sources.historian.datetime_cols | list[str] | ['timestamp'] | list of column names | All datetime columns in historian CSV to parse |
| sources.alarm_log.path | string | '../historian-generator/output/alarm_log.csv' | file path | Alarm log CSV export location |
| sources.alarm_log.frequency | string | None | None or pandas freq | Resample frequency (None = no resampling for event data) |
| sources.alarm_log.timestamp_col | string | 'activation_time' | column name | Primary timestamp column for alarm events in raw CSV |
| sources.alarm_log.tz | string | 'UTC' | timezone | Timezone of raw alarm timestamps |
| sources.alarm_log.datetime_cols | list[str] | ['activation_time', 'ack_time', 'clear_time'] | list of column names | All datetime columns in alarm CSV to parse |
| sources.environmental.path | string | '../usgs-weather-analysis/output/usgs_raw.csv' | file path | Environmental CSV export location |
| sources.environmental.frequency | string | '5min' | pandas freq or None | Resample frequency |
| sources.environmental.timestamp_col | string | 'datetime' | column name | Environmental timestamp column name in raw CSV |
| sources.environmental.tz | string | 'UTC' | timezone | Timezone of environmental timestamps |
| sources.environmental.datetime_cols | list[str] | ['datetime'] | list of column names | All datetime columns in environmental CSV to parse |
| output.database_path | string | 'output/etl_pipeline.db' | file path | SQLite database output location |
| output.log_path | string | 'output/etl_pipeline.log' | file path | ETL execution log location |
| unit_conversions | dict | {'P-0700': {...}} | asset-specific dicts | Per-asset unit conversion factors (e.g., kPa to bar). Nested structure: asset_id -> column_name -> {factor: float} |
| column_mappings.historian | dict | (see etl_config.py) | source_col: dest_col pairs | Map raw historian CSV column names to standard schema names |
| column_mappings.alarm_log | dict | (see etl_config.py) | source_col: dest_col pairs | Map raw alarm CSV column names to standard schema names |
| column_mappings.environmental | dict | (see etl_config.py) | source_col: dest_col pairs | Map raw environmental CSV column names to standard schema names |
| quality_report_paths.historian | string | '../historian-generator/output/data_quality/historian_quality_report.json' | file path | Quality report JSON for historian data (output of data_quality.assess_quality) |
| quality_report_paths.alarm_log | string | '../historian-generator/output/data_quality/alarm_log_quality_report.json' | file path | Quality report JSON for alarm log data |
| quality_report_paths.environmental | string | '../usgs-weather-analysis/output/data_quality/usgs_quality_report.json' | file path | Quality report JSON for environmental data |

## Shared Utilities

### data_quality.py

Located in `scripts/utils/data_quality.py`. Used by all quality assessment scripts (run_quality_usgs.py, run_quality_historian.py, run_quality_alarm_log.py).

| Parameter | Type | Default | Valid Range | Description |
|-----------|------|---------|-------------|-------------|
| iqr_multiplier (in assess_quality config) | float | 1.5 | 0.5-3.0 | IQR fence multiplier for outlier detection (1.5 is standard) |

Note: Gap threshold (1.5x expected frequency), timestamp regularity tolerance (10%), and unit consistency ratio (10x deviation) are hardcoded constants in data_quality.py. Adjust these by editing the source code if needed for your data profile.

## Historian Generator

### historian_config.py

| Parameter | Type | Default | Valid Range | Description |
|-----------|------|---------|-------------|-------------|
| OUTPUT_DIR | string | 'output' | valid path | Root output directory for all historian generator outputs |
| CSV_PATH | string | 'output/synthetic_historian_10x365_1min.csv' | file path | Output CSV file path (historian time series) |
| DB_PATH | string | 'output/synthetic_historian.db' | file path | Output SQLite database file path |
| FAILURE_SCENARIOS_DIR | string | 'output/failure_scenarios' | valid path | Directory for failure scenario plots (via visualize_failure_scenarios.py) |
| HISTORIAN_VALIDATION_DIR | string | 'output/historian_validation' | valid path | Directory for validation plots (via verify_historian_output.py) |
| BASE_TIME | datetime | 2025-01-01 | N/A | Start timestamp for simulation |
| NUM_ASSETS | int | 10 | 1-N | Number of pump assets to generate |
| PERIOD_DAYS | int | 365 | 1-N | Simulation duration (days) |
| FREQ_MIN | int | 1 | 1-N | Sampling frequency (minutes) |
| NOISE_LEVEL | float | 0.02 | 0-0.5 | Noise amplitude as fraction of nominal signal |
| DRIFT_RATE | float | 0.001 | 0-0.1 | Long-term drift per day (multiplicative) |
| SEASON_AMP | float | 0.3 | 0-0.5 | Seasonal amplitude: +/-amp% around 0.7 baseline |
| SEED | int | 42 | 0-N | Random seed for reproducibility |
| GAP_FRACTION | float | 0.001 | 0-0.01 | Fraction of rows to remove per asset (data quality issue) |
| DUPLICATE_PER_ASSET | int | 3 | 0-N | Number of duplicate timestamps per asset (data quality issue) |
| UNIT_MISMATCH_ASSET | string | 'P-0700' | asset_id | Asset that gets pressures in kPa instead of bar (data quality issue) |
| THERMAL_TAU_MIN | float | 15 | 1-60 | Time constant (minutes) for motor thermal inertia low-pass filter |
| IQR_MULTIPLIER | float | 1.5 | 0.5-3.0 | IQR fence multiplier used by run_quality_historian.py |
| DAY_HOURS | tuple[int] | (8, 20) | 0-23 | Hour range considered daytime for demand comparison in verify_historian_output.py |
| NIGHT_HOURS | tuple[int] | (0, 5) | 0-23 | Hour range considered nighttime for demand comparison in verify_historian_output.py |
| PUMP_CURVE_SAMPLE_STRIDE | int | 100 | 1-N | Row stride for downsampling pump curve scatter plot in verify_historian_output.py |
| FLOW_BIN_COUNT | int | 20 | 1-N | Number of bins for flow-vs-vibration profile in verify_historian_output.py |
| SIGNAL_COLUMNS | list[str] | [flow_m3h, suction_pressure_bar, ...] | N/A | List of 8 signal column names generated for each asset |
| PRESSURE_COLUMNS | list[str] | [suction_pressure_bar, disch_pressure_bar, diff_pressure_bar] | N/A | Pressure columns checked for unit consistency by run_quality_historian.py |
| FAILURE_SIGNAL_MAP | dict | (see source code) | N/A | Maps failure scenario types to primary/secondary signals and labels for visualization/verification plots |
| FAILURE_SCENARIOS | list[dict] | (see table below) | N/A | List of failure scenario definitions (P-0100 bearing, P-0300 cavitation, P-0500 insulation) |
| AREAS | list[str] | (10 area names) | N/A | Operational area names assigned round-robin to assets |
| PUMP_CURVES | list[dict] | (see source code) | N/A | 10 pump models (Grundfos NK/NKE series): 2900 RPM (6 models) and 1450 RPM (4 models) |

### Failure Scenarios (from FAILURE_SCENARIOS list)

| Asset | Scenario Type | Start Day | Ramp Duration | Severity | Description |
|-------|---------------|-----------|----------------|----------|-------------|
| P-0100 | bearing | 100 | 260 days | 4.0 | Bearing wear: vibration ramp, temperature drift after day 160 |
| P-0300 | cavitation | 200 | 60 days | 3.0 | Cavitation: dP spikes, flow noise, vibration increase |
| P-0500 | insulation | 150 | 120 days | 3.5 | Insulation degradation: temperature and power drift, no vibration change |

### HistorianConfig (dataclass in historian_generator.py)

| Parameter | Type | Default | Valid Range | Description |
|-----------|------|---------|-------------|-------------|
| num_assets | int | 10 | 1-N | Number of pump assets to generate |
| period_days | int | 365 | 1-N | Simulation duration (days) |
| freq_min | int | 1 | 1-N | Sampling frequency (minutes) |
| noise_level | float | 0.02 | 0-0.5 | Noise amplitude as fraction of nominal signal |
| drift_rate | float | 0.001 | 0-0.1 | Long-term drift per day (multiplicative) |
| season_amp | float | 0.3 | 0-0.5 | Seasonal amplitude: +/-amp% around 0.7 baseline |
| base_time | datetime | 2025-01-01 | N/A | Start timestamp for simulation |
| seed | int | 42 | 0-N | Random seed for reproducibility |
| failure_scenarios | list[dict] | (from config) | list of dicts | Failure scenario definitions to inject |
| gap_fraction | float | 0.001 | 0-0.01 | Fraction of rows to remove per asset (data quality issue) |
| duplicate_per_asset | int | 3 | 0-N | Number of duplicate timestamps per asset (data quality issue) |
| unit_mismatch_asset | string | 'P-0700' | asset_id | Asset to apply kPa/bar unit mismatch |
| thermal_tau_min | float | 15 | 1-60 | Motor thermal time constant (minutes) |

### Output Scripts

**historian_generator.py**: Generates all synthetic time series. Outputs CSV and SQLite database.

**run_quality_historian.py**: Runs completeness, gap, duplicate, outlier, and unit-consistency checks against the generated CSV. Writes JSON and text reports to output/data_quality/.

**verify_historian_output.py**: Validates all assets against pump physics. Generates 5 plots per asset (timeseries, pump curve, correlations, diurnal, weekly).

**visualize_failure_scenarios.py**: Plots primary/secondary signals with P-F markers for the 3 failure assets.

### alarm_log_config.py

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| OUTPUT_DIR | string | 'output' | Root output directory for alarm log CSV |
| CSV_PATH | string | 'output/alarm_log.csv' | Output CSV file path (alarm events) |
| NORMAL_ALARMS_PER_ASSET_PER_DAY | int | 6 | Background alarm rate (normal operation) |
| CHATTERING_EVENTS_COUNT | int | 7 | Number of rapid re-triggers in chattering test case |
| CHATTERING_INTERVAL_MIN | float | 1.2 | Minutes between chattering events |
| CHATTERING_DURATION_MIN | float | 0.8 | Duration of each chattering event |
| STALE_ALARM_DURATION_MIN | float | 3120.0 | Duration of stale alarm that never clears |
| CASCADE_INTERVAL_SEC | float | 25 | Seconds between cascade batch events |
| CHATTERING_ACK_DELAY_MIN | float | 0.6 | Operator ack delay for chattering test case |
| STALE_ALARM_ACK_DELAY_MIN | float | 4.5 | Operator ack delay for stale alarm test case |
| CASCADE_DURATION_MIN | float | 3.5 | Min duration for cascade batch events |
| CASCADE_DURATION_MAX | float | 25.0 | Max duration for cascade batch events |
| CASCADE_ACK_DELAY_MIN | float | 0.8 | Operator ack delay for cascade test case |
| OPERATORS | list[str] | [OP01, OP02, ...] | Operator IDs for alarm acknowledgment |
| ALARM_TAG_TEMPLATES | dict | (see source) | 8 alarm types with descriptions, priorities, families (vibration, temperature, flow, pressure, current, speed) |
| FAILURE_FAMILY_MAP | dict | (see source) | Maps failure scenarios to alarm families (bearing -> [vibration, temperature], etc.) |
| PRIORITY_DURATION_MEANS | dict | {1: 3, 2: 10, ...} | Mean alarm duration (minutes) by priority level |
| PRIORITY_DURATION_STDS | dict | {1: 1, 2: 4, ...} | Std dev of alarm duration (minutes) by priority level |
| ISA_18_2_ALARMS_PER_ASSET_PER_DAY_MAX | int | 144 | ISA-18.2 benchmark: max alarms/asset/day (>1 per 10 min) |

Note: alarm_log_generator.py pulls NUM_ASSETS, PERIOD_DAYS, FAILURE_SCENARIOS, AREAS, SEED, BASE_TIME from historian_config.py for alignment.

### run_quality_alarm_log.py

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| IQR_MULTIPLIER | float | 1.5 | IQR fence multiplier for outlier detection in priority and duration_min columns |

### Test Cases (Synthetic Validation Patterns)

Three test case types are injected into the alarm log to validate alarm analysis pipeline:

| Test Type | Asset | Trigger | Pattern | Purpose |
|-----------|-------|---------|---------|---------|
| Chattering | P-0100 | Day 5, 08:30 | 7 VI_HI alarms in ~8 minutes, each lasting 0.8 min | Detect rapid re-triggers (nuisance pattern) |
| Stale | P-0200 | Day 10, 02:00 | FI_LO alarm never clears (3120 min / 2+ days) | Detect uncleared alarms (operator miss) |
| Cascade | P-0300 | Day 15, 14:22:30 | 5 pressure/flow/vibration alarms within 2 minutes | Detect correlated batch failures |

### Signal Columns Generated (8 per asset, plus 4 metadata)

Flow rate, suction pressure, discharge pressure, differential pressure, motor temperature, motor power, vibration, pump speed. Plus: timestamp, asset_id, area (operational area), pump_model.

### Tests

Run all tests from `scripts/tests/`: `python run_tests.py`

Tests validate historian generation, alarm log generation, and data quality functions. See test files for detailed coverage.

## Analytics Pipeline

### analytics_config.py

**Output Paths:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| OUTPUT_DIR | string | 'output' | Root output directory for all analysis outputs |
| DETECTION_PERFORMANCE_DIR | string | 'output/detection_performance' | Detection performance reports subdirectory |
| TREND_OUTPUT_DIR | string | 'output/detection_performance/trend_detection' | Trend detection plots subdirectory |
| BASELINE_VALIDATION_DIR | string | 'output/baseline_validation' | Baseline validation plots subdirectory |
| ANOMALY_DETECTION_DIR | string | 'output/anomaly_detection' | Anomaly detection output subdirectory |

**Database:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| ETL_PIPELINE_PATH | string | ../etl-pipeline/output/etl_pipeline.db | Path to ETL database |
| CLEAN_TABLES | list[str] | ['historian_clean', 'alarm_log_clean', 'environmental_clean'] | Tables to document and analyze |
| ALARM_TABLE | string | 'alarm_log_clean' | Alarm log table name |
| ANALYSIS_TABLE | string | 'historian_clean' | Historian table name |

**Output Files:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| OUTPUT_FILES | dict | (see source) | Mapping of output file keys to filenames (pf_alignment, data_dictionary, alarm reports) |
| ANALYSIS_OUTPUT_FILES | dict | (see source) | Mapping of analysis output file keys to filenames (lead_times, false_positives, trend results) |

**Detection Method Parameters (tunable):**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| DETECTION_METHODS | dict | {'Z-score': {threshold: 3.0}, 'IQR': {window_periods: 1440, multiplier: 1.0}, 'Moving avg': {window_periods: 30, threshold: 1.5}} | Detection thresholds for anomaly detection |

**Persistence Detection Parameters (tunable):**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| PERSISTENCE_MIN_DURATION_HOURS | int | 6 | Minimum duration to flag as persistent anomaly |
| PERSISTENCE_THRESHOLD | float | 0.7 | Fraction of windows that must be flagged to count as persistent (70%) |
| SAMPLING_FREQ_MINUTES | int | 1 | Sampling frequency for baseline calculations |

**Trend Analysis Parameters (tunable):**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| MANN_KENDALL_ALPHA | float | 0.05 | Significance threshold for Mann-Kendall trend test (p < 0.05 = significant) |
| MAX_TREND_WINDOW | int | 10000 | Maximum samples to prevent RAM explosion |
| TREND_ANALYSIS_WINDOWS_HOURS | list[int] | [72, 168] | Time windows for trend detection analysis (hours) |
| TREND_HTML_TEMPLATE | string | 'bearing_trend_{window_hours}h.html' | Output filename template for trend plots |

**Baseline Fitting Parameters (tunable):**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| BASELINE_WINDOW_HOURS | int | 24 | Rolling baseline window size |
| BASELINE_NUM_STD | int | 3 | Number of standard deviations for control limits |
| BASELINE_TRAINING_FRACTION | float | 0.3 | Fraction of data to use for training baseline fit |
| MIN_TRAINING_HOURS | int | 24 | Minimum training data required (hours) |

**Analysis Limits (tunable):**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| MAX_HEALTHY_ASSETS | int | 5 | Analyze false positive rates on first N healthy assets |
| MAX_SEASONAL_ANALYSIS_ASSETS | int | 1 | Show seasonal breakdown for first N assets |
| DOWNSAMPLE_FACTOR | int | 60 | Plot every Nth sample for performance |
| ANOMALY_ROLLING_PLOT_WINDOW_HOURS | int | 24 | Rolling window for anomaly plot visualization (hours) |

**Alarm Benchmarks (tunable):**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| ISA_CHATTER_MAX_EVENTS | int | 3 | Max events in window to not trigger chattering flag |
| ISA_CHATTER_WINDOW_MIN | int | 5 | Time window for chattering detection (minutes) |
| STALE_ALARM_HOURS | int | 24 | Threshold for alarm to be considered stale |
| CLUSTER_WINDOW_MIN | int | 30 | Time window for clustering alarms (minutes) |
| ISA_DAILY_RATE_TARGET | int | 144 | ISA-18.2 benchmark: max alarms/asset/day |

**Column Definitions:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| HISTORIAN_NEEDED_COLS_DETECTION | list[str] | [asset_id, timestamp, failure_type, vibration_mm_s, diff_pressure_bar, motor_temp_c, flow_m3h] | Required historian columns for anomaly detection |
| BASELINE_VALIDATION_SIGNAL_COLS | list[str] | [flow_m3h, vibration_mm_s] | Signals for baseline validation |
| BASELINE_VALIDATION_NEEDED_COLS | list[str] | [asset_id, timestamp, failure_type, flow_m3h, vibration_mm_s] | Required columns for baseline validation |
| ANOMALY_DETECTION_NEEDED_COLS | list[str] | [asset_id, timestamp, failure_type, vibration_mm_s, diff_pressure_bar, motor_temp_c, flow_m3h] | Required columns for anomaly detection |
| HEALTHY_SIGNAL_COLS | list[str] | [vibration_mm_s, motor_temp_c, diff_pressure_bar] | Signals to analyze for false positives |

**Alarm Test Cases (synthetic data only):**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| ALARM_TEST_CASE_VALUE | string | "YES" | Value in is_test_case column to mark synthetic test alarms |
| ALARM_TEST_CASES | dict | {chattering: P-0100, stale: P-0200, cluster: P-0300} | Test case definitions for synthetic validation |

**Failure Scenario Reference (synthetic data only):**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| FAILURE_SCENARIOS | list[tuple] | (bearing, cavitation, insulation) | Failure scenario mappings for performance analysis |
| PF_INTERVALS_HOURS | dict | {bearing: 6240, cavitation: 1440, insulation: 2880} | P-F intervals for failure scenarios (hours) |
| RAMP_INFO_DAYS | dict | {bearing: {start_day: 100, ramp_days: 260}, ...} | Ramp timing for failure injections |

**Failure Type Definitions:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| FAILURE_TYPE_HEALTHY | string | "none" | Canonical value for healthy/normal operation |
| FAILURE_TYPE_HEALTHY_VARIANTS | list[str] | [none, None, pass, "", N/A, NA] | Defensive variants when importing data |

### pf_alignment.py

Generates P-F alignment matrix: failure modes vs detection sources. Outputs CSV and formatted Excel with signal strength ratings and P-F lead time estimates. Reference only, no configuration beyond analytics_config.py paths.

### data_dictionary.py

Generates data dictionary Excel from ETL database schema. Documents all columns in historian_clean, alarm_log_clean, environmental_clean. Includes data types, units, sources, null handling, and actual value ranges fetched from database.

Uses: ETL_PIPELINE_PATH, CLEAN_TABLES, OUTPUT_DIR, OUTPUT_FILES from analytics_config.py

### alarm_analytics.py

Computes alarm log metrics and detects patterns. Class-based design: AlarmAnalytics loads alarm_log_clean table and provides methods for rate analysis, chattering detection, stale alarm detection, alarm clustering, time-to-acknowledge computation. Validates synthetic test cases.

Tunable parameters (from analytics_config.py): ISA_CHATTER_MAX_EVENTS, ISA_CHATTER_WINDOW_MIN, STALE_ALARM_HOURS, CLUSTER_WINDOW_MIN, ISA_DAILY_RATE_TARGET.

### baseline.py

Internal utility class for baseline fitting. Not run standalone. Used by anomaly detection to fit and apply baseline methods (rolling window, hourly, state-based). Methods accept tunable parameters from config (BASELINE_WINDOW_HOURS, BASELINE_NUM_STD, BASELINE_TRAINING_FRACTION).

Uses: SAMPLING_FREQ_MINUTES from analytics_config.py

### anomaly_detection.py

Internal utility class for anomaly detection. Not run standalone. Provides three detection methods (Z-score, IQR, moving average) and utilities for persistence filtering and Mann-Kendall trend detection. Methods: zscore(), iqr(), moving_average(), persistent_detection(), lead_time_hours(), detect_trend().

Uses: BASELINE_NUM_STD from analytics_config.py. Hardcoded constant: NUMERICAL_EPSILON = 1e-8 (numerical stability).

### environmental_correlation.py

Utility functions for environmental analysis. Not run standalone. Computes Pearson correlation between historian signals and USGS streamflow. Functions: find_overlap_window(), compute_overlap_correlation(). No configuration needed.

### verify_baseline.py

Verification script. Validates baseline fitting on healthy and degrading assets. Generates control limit plots (rolling, hourly, state-based methods) for one healthy and one degrading asset pair. Shows pre/post-failure detection capability. Run: `python verify_baseline.py`. Outputs HTML plots to BASELINE_VALIDATION_DIR.

Uses: BASELINE_VALIDATION_DIR, BASELINE_WINDOW_HOURS, BASELINE_NUM_STD, BASELINE_VALIDATION_SIGNAL_COLS, FAILURE_TYPE_HEALTHY_VARIANTS from analytics_config.py.

### verify_anomaly_detection.py

Verification script. Validates anomaly detection methods on failure scenarios. Runs Z-score, IQR, and moving average detection on bearing/cavitation/insulation failures. Generates 4-subplot plots showing signal, baseline, and detection flags by method. Run: `python verify_anomaly_detection.py`. Outputs HTML plots to ANOMALY_DETECTION_DIR.

Uses: ANOMALY_DETECTION_DIR, DETECTION_METHODS, BASELINE_WINDOW_HOURS, BASELINE_NUM_STD, ANOMALY_DETECTION_NEEDED_COLS, FAILURE_SCENARIOS from analytics_config.py.

### analyze_detection_performance.py

Analysis script. Computes three performance analyses using the three synthetic failure scenarios (bearing, cavitation, insulation): (1) detection lead time vs P-F interval for Z-score, IQR, and moving average methods, (2) false positive rate on healthy assets across HEALTHY_SIGNAL_COLS by month, including seasonal baseline mismatch root cause breakdown, (3) Mann-Kendall trend detection on the bearing degradation signal at multiple time windows. Derives MIN_TRAINING_SAMPLES and PLOT_ROLLING_WINDOW at module level from MIN_TRAINING_HOURS/ANOMALY_ROLLING_PLOT_WINDOW_HOURS and SAMPLING_FREQ_MINUTES. Run: `python analyze_detection_performance.py`. Outputs CSVs to DETECTION_PERFORMANCE_DIR and trend plots to TREND_OUTPUT_DIR.

Uses: see analytics_config.py.

Depends on baseline.py and anomaly_detection.py.

## Dashboard

*To be populated later*

## Notes

- Boolean/flag parameters default to False unless noted
- All file paths are relative to the script location unless absolute paths are provided
- Numeric ranges assume sensible operational bounds; actual valid range depends on data context
- Parameters affecting data quality thresholds (IQR_MULTIPLIER, GAP_THRESHOLD_MIN) should be tuned based on pilot testing with real client data
