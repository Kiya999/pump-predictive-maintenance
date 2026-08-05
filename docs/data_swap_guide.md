# Data Swap Guide: Connecting Real Client Data

This guide explains how to replace the synthetic dataset with real client data sources. Follow this for each data source, then verify the swap.

## Overview

The current system sources data from three synthetic pipelines:
1. USGS streamflow and weather (environmental context)
2. Historian generator (simulated pump historian time series)
3. Alarm log generator (simulated alarm events)

To connect real data, you replace the generators and loaders, keeping the ETL, analytics, and dashboard layers unchanged.

## USGS Weather Data (Environmental Context)

### Current Synthetic Source

- `scripts/usgs-weather-analysis/usgs_weather_analysis.py` downloads real USGS streamflow for gauge 01646500 (Potomac River)
- Real data, not synthetic. No replacement needed for this source unless you want a different gauge

### How to Point to Different USGS Gauge

If your client operates in a different region with a different USGS gauge:

1. Open `scripts/usgs-weather-analysis/usgs_weather_analysis.py`
2. Replace:
   - SITE_ID: Change from '01646500' to your 8-digit USGS gauge code
   - DC_LAT, DC_LON: Update to your location coordinates (used for Open-Meteo weather API)

3. Run: `python usgs_weather_analysis.py`
4. Verify: Check that `output/combined_data.csv` has rows with non-null datetime, precip_mm, and temp_c

See Configuration Reference for all tunable parameters in this module.

### Expected Schema for combined_data.csv

```
datetime,01646500_cfs,temp_c,precip_mm
2025-05-25 00:00,12345.5,15.2,0.0
2025-05-25 01:00,12340.1,15.1,0.2
...
```

## Historian Data (Pump Signals)

### Current Synthetic Source

- `scripts/historian-generator/historian_generator.py` generates synthetic data via `HistorianConfig` dataclass
- Outputs: CSV and SQLite database with 10 assets, 1-minute resolution, 365 days
- Includes 3 simulated failure scenarios: bearing (P-0100), cavitation (P-0300), insulation (P-0500)
- Injects data quality issues: gaps, duplicate timestamps, unit mismatch on P-0700

### Scripts in historian-generator folder

Historian and alarm log generation scripts. Both are synthetic; skip these when using real client data.

**Historian Generation:**
- **historian_generator.py**: Main generation script. Outputs CSV_PATH and DB_PATH from `historian_config.py`
- **historian_config.py**: Configuration file with simulation parameters, failure scenarios, output paths.
- **verify_historian_output.py**: Validation script. Runs physical plausibility checks (pump physics, correlations, ranges), generates 5 plots per asset.
- **visualize_failure_scenarios.py**: Plots failure scenarios (primary + secondary signals with P-F markers).
- **run_quality_historian.py**: Quality assessment script. Runs completeness, gap, duplicate, outlier, and unit-consistency checks against the generated CSV. Writes JSON and text reports.

**Alarm Log Generation:**
- **alarm_log_generator.py**: Main generation script. Generates alarms via `alarm_log_config.py` parameters. Outputs CSV_PATH from alarm_log_config.
- **alarm_log_config.py**: Configuration file with alarm parameters, priority distributions, test case timings, and ISA-18.2 reference.
- **run_quality_alarm_log.py**: Quality assessment script. Runs completeness, duplicate, and outlier checks on the generated CSV. Writes JSON and text reports.

**Testing:**
- **Tests**: Run `python scripts/tests/run_tests.py` to validate generators and data quality functions.

Note: Alarm generation depends on historian configuration (NUM_ASSETS, PERIOD_DAYS, SEED, BASE_TIME, FAILURE_SCENARIOS, AREAS must match historian run for consistency).

### How to Replace with Real PI Historian Export

For real client data, you skip the synthetic generation step and load directly from your historian export.

1. Export from your PI System (or equivalent historian):
   - Format: CSV with columns [timestamp, asset_id, flow_m3h, suction_pressure_bar, disch_pressure_bar, diff_pressure_bar, motor_temp_c, motor_power_kw, vibration_mm_s, speed_rpm]
   - Resolution: 1-minute recommended (can be resampled if coarser)
   - Date range: minimum 30 days, ideally 365 days
   - Nulls in signal columns acceptable. Timestamp and asset_id must not be null.
   - Note: failure_type is synthetic-only metadata. Real historian exports won't have this column; ETL will create it as NULL for all rows.

2. Place the export at: `scripts/historian-generator/output/your_historian_export.csv`

3. Edit `scripts/etl-pipeline/etl_config.py`:
   - Update `sources.historian.path` to point to your CSV
   - Update `sources.historian.timestamp_col` if your timestamp column name differs
   - Update `sources.historian.datetime_cols` to list all columns to parse as datetime
   - If raw column names differ, add mappings to `column_mappings.historian`

4. Run ETL: `python scripts/etl-pipeline/etl.py`

5. Verify: Check `scripts/etl-pipeline/output/etl_pipeline.db` exists and has 3 tables: historian_clean, alarm_log_clean, environmental_clean

See Configuration Reference for all etl_config.py tunable parameters.

For a structured completeness/outlier report on real data (optional): Run `scripts/historian-generator/run_quality_historian.py`. It writes historian_quality_report.txt and .json to output/data_quality/.

For validation plots on real data (optional): Run `scripts/historian-generator/verify_historian_output.py` to generate the same plots. Real data will show actual failure patterns, not the synthetic ones.

Note: Failure scenario visualization (visualize_failure_scenarios.py) requires the failure_type column and is only meaningful for synthetic data. Skip this script for real client data. The validation plots from verify_historian_output.py work with real or synthetic data.

### Expected Schema for Historian CSV

Your raw CSV columns must include these (names can differ, then map in config):

```
timestamp,asset_id,flow_m3h,suction_pressure_bar,disch_pressure_bar,diff_pressure_bar,motor_temp_c,motor_power_kw,vibration_mm_s,speed_rpm
2025-05-25 00:00:00,P-0100,145.2,2.3,3.1,0.8,35.1,25.5,4.2,1750
2025-05-25 00:01:00,P-0100,145.1,2.3,3.1,0.8,35.0,25.4,4.1,1750
...
```

Standard units: flow in m3/h, pressure in bar, temperature in Celsius, vibration in mm/s, speed in rpm.

## Alarm Log Data (Events)

### Current Synthetic Source

- `scripts/historian-generator/alarm_log_generator.py` generates 10,000+ alarm events across 10 assets with realistic nuisance and critical alarm patterns

### How to Replace with Real Alarm Exports

1. Export from your SCADA/alarm management system:
   - Format: CSV with columns [activation_time, asset_id, alarm_tag, alarm_description, alarm_type, priority, ack_time, clear_time, duration_min, area, operator_id, is_test_case]
   - Priority coding: 1-2 = critical, 3-5 = nuisance (adjust thresholds in dashboard Alarm Analysis panel if needed)
   - Test case column: is_test_case (empty for normal, "YES" for synthetic validation cases like chattering, stale, cascade)
   - Date range: match your historian export date range
   - Nulls acceptable in: ack_time, clear_time, operator_id. Must not be null: activation_time, asset_id.
   - Note: is_test_case and area are synthetic-only columns. Real SCADA exports typically omit these; if present, they may be NULL or empty.

2. Place the export at: `scripts/historian-generator/output/your_alarm_export.csv`

3. Edit `scripts/etl-pipeline/etl_config.py`:
   - Update `sources.alarm_log.path` to point to your CSV
   - Update `sources.alarm_log.timestamp_col` if your primary timestamp is named differently (e.g., "event_time" instead of "activation_time")
   - Update `sources.alarm_log.datetime_cols` to list all datetime columns in your export
   - If column names differ, add mappings to `column_mappings.alarm_log`

4. Run ETL: `python scripts/etl-pipeline/etl.py`

5. Verify: Check that `alarm_log_clean` table in database has rows matching your export.

For a completeness/outlier report on real data (optional): Run `scripts/historian-generator/run_quality_alarm_log.py`. It writes alarm_log_quality_report.txt and .json to output/data_quality/.

### Expected Schema for Alarm CSV

Your raw CSV columns must include these (names can differ, then map in config):

```
activation_time,asset_id,alarm_tag,alarm_description,alarm_type,priority,ack_time,clear_time,duration_min,area,operator_id,is_test_case
2025-05-25 08:15:00,P-0100,FLOW_LOW,Discharge below minimum,nuisance,3,2025-05-25 08:20:00,2025-05-25 08:25:00,5,Pump Room,op_001,false
2025-05-25 09:30:00,P-0100,TEMP_HIGH,Bearing temperature above setpoint,critical,1,,2025-05-25 09:35:00,5,Pump Room,,false
...
```
Standard: priority 1-2 = critical, 3-5 = nuisance. Ack_time and clear_time can be NULL.

## ETL Pipeline Layers

The ETL pipeline processes data through three stages:

**Extract**: Read historian, alarm, and environmental CSVs.

**Transform**: Normalize timestamps, resample, apply unit conversions, rename columns, add quality flags based on data quality assessment reports, and flag rows with missing or outlier values.

**Load**: Create SQLite database schema and insert cleaned data.

The pipeline logs all row counts and errors to the pipeline_runs table for audit trail. Check output/etl_pipeline.log and the pipeline_runs table for details if something fails.

## Database Schema

ETL creates four tables in the SQLite database.

### historian_clean
Pump signals. Columns: id, timestamp (UTC), asset_id, flow_m3h, suction_pressure_bar, disch_pressure_bar, diff_pressure_bar, motor_temp_c, motor_power_kw, vibration_mm_s, speed_rpm, failure_type (metadata only), quality_flag. All numeric columns are nullable and ETL preserves real missing values.

### alarm_log_clean
Alarm events. Columns: id, timestamp (UTC), asset_id, alarm_tag, alarm_description, alarm_type, priority, ack_time, clear_time, duration_min, area, operator_id, is_test_case, quality_flag. Ack_time and clear_time are nullable (NULL if not acknowledged or still active).

### environmental_clean
Environmental data. Columns: id, timestamp (UTC), discharge_cfs, quality_flag.

### pipeline_runs
Pipeline execution audit. Columns: run_id, run_timestamp, historian_input_path, alarm_log_input_path, environmental_input_path, historian_rows_in, historian_rows_out, alarm_log_rows_in, alarm_log_rows_out, environmental_rows_in, environmental_rows_out, quality_summary (JSON), errors (JSON), status.

Quality_flag column has values: 'pass', 'missing', 'outlier'. This refers to "data" quality.

## Analytics Pipeline

The analytics pipeline generates reference materials and alarm analysis reports from the ETL-cleaned database.

### Reference & Data Documentation

**pf_alignment.py**: Generates P-F alignment matrix CSV and Excel. Maps 14 pump failure modes to 8 detection data sources (flow, pressure, temperature, power, vibration, ESA, alarms, environmental). Includes signal strength ratings (Strong/Partial/None) and P-F lead time estimates. Reference only, no configuration needed.

**data_dictionary.py**: Generates data dictionary Excel from ETL database schema. Documents all columns in historian_clean, alarm_log_clean, environmental_clean. Includes data types, units, source systems, update frequencies, null handling, and value ranges fetched from database. One sheet per table.

### Alarm Analysis & Detection

**alarm_analytics.py**: Computes alarm metrics and detects patterns. Metrics include daily alarm rate vs ISA-18.2 target (144 alarms/asset/day), top 10 alarms by frequency, average time to acknowledge. Detection includes chattering (rapid re-triggers), stale alarms (uncleared or never cleared), and alarm clusters (multiple distinct alarms within time window). Outputs CSV files for each metric.

Run from command line: `python alarm_analytics.py`. Validates synthetic test cases (chattering P-0100.VI_HI, stale P-0200.FI_LO, cluster P-0300) against is_test_case column.

### Detection Performance Analysis

**analyze_detection_performance.py**: Analyzes detection performance across the three synthetic failure scenarios (bearing, cavitation, insulation). Computes lead time before failure for each detection method (Z-score, IQR, moving average) versus the known P-F interval, false positive rates on healthy assets by signal and month with a seasonal baseline mismatch breakdown, and Mann-Kendall trend significance on the bearing vibration signal. Depends on RAMP_INFO_DAYS and PF_INTERVALS_HOURS reference data tied to known synthetic failure timing; not directly applicable to real client data without equivalent known failure onset dates. Run: `python analyze_detection_performance.py`. Outputs CSVs to DETECTION_PERFORMANCE_DIR and trend plots to TREND_OUTPUT_DIR.

### Utility Modules (Internal)

**baseline.py**: Utility class for baseline fitting. Not run standalone. Used by anomaly detection to fit and apply baseline methods (rolling window, hourly, state-based) for control limits. Methods: fit_rolling(), fit_hourly(), fit_state(), apply_rolling(), apply_hourly(), apply_state().

**environmental_correlation.py**: Utility functions for environmental analysis. Not run standalone. Used by asset-level analysis to compute Pearson correlation between historian signals and environmental discharge (USGS streamflow). Functions: find_overlap_window(), compute_overlap_correlation().

**anomaly_detection.py**: Utility class for anomaly detection. Not run standalone. Three detection methods (Z-score, IQR, moving average) with persistence filtering and Mann-Kendall trend detection for signal degradation analysis. Methods: zscore(), iqr(), moving_average(), persistent_detection(), lead_time_hours(), detect_trend().

### Validation Scripts

**verify_baseline.py**: Validates baseline fitting methods. Compares rolling, hourly, and state-based baselines on one healthy asset (all normal operation) and one degrading asset (with failure injected). Generates 3-subplot plots showing signal, baseline, and control limits. Calculates pre/post-failure violation rates. Run: `python verify_baseline.py`.

**verify_anomaly_detection.py**: Validates anomaly detection methods on failure scenarios. Runs Z-score, IQR, and moving average detection against bearing/cavitation/insulation failures. Generates 4-subplot plots: signal + baseline, then detection severity for each method with anomaly flags overlaid. Shows lead time to first detection vs failure onset. Run: `python verify_anomaly_detection.py`.

### Output Location

All scripts write to output/ directory. Configuration paths in analytics_config.py control output locations.
