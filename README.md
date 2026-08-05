# Pump Predictive Maintenance

A condition monitoring pipeline for water utility pump assets. Built during my summer internship at DC Water (2026) to prototype alarm analytics, anomaly detection, and dashboard workflows.

## What this does

Water utilities operate pump assets at booster stations, chemical dosing, and filtration plants. This project provides a testbed to validate detection algorithms, tune alarm thresholds, and measure failure detection lead time before deploying to production systems.

The pipeline:
1. Generates realistic synthetic pump historian data with injected failure scenarios
2. Creates synthetic alarm logs with test cases (chattering, stale alarms, cascades)
3. Normalizes data via ETL, applies unit conversions and quality flags
4. Analyzes alarm performance, baselines, and anomaly detection
5. Visualizes results in interactive dashboards

## Key features

- Synthetic pump data: 10 assets over 1 year at 1-minute resolution, based on pump curves and thermal models
- Test case validation: bearing wear, cavitation, and insulation failures
- Multi-method anomaly detection: Z-score, IQR, and moving average with measured lead times and false-positive rates against synthetic failure ground truth
- Environmental context: correlates pump flow to streamflow; analyzes seasonal drift
- Hourly and weekend-aware baselines for anomaly detection with caching
- ISA-18.2 testing: tracks alarm rates against industry standards (10 alarms/asset/day target)
- Metric and imperial unit conversion: toggle between unit systems via config
- Quality-aware ETL: flags missing data, outliers, duplicates
- Interactive dashboards: KPI monitoring, alarm analysis, detection performance, environmental correlation

## Quick start

### Prerequisites
- Python 3.8+
- Dependencies in `requirements.txt`

### Installation
```bash
git clone https://github.com/Kiya999/pump-predictive-maintenance
cd pump-predictive-maintenance
pip install -r requirements.txt
```

### Run the pipeline

1. Generate synthetic data
```bash
python scripts/historian-generator/historian_generator.py
python scripts/historian-generator/alarm_log_generator.py
```

2. Run ETL
```bash
python scripts/etl-pipeline/etl.py
```
This produces `scripts/etl-pipeline/output/etl_pipeline.db` with three normalized tables.

3. Run analytics
```bash
cd scripts/analytics-pipeline
python analyze_detection_performance.py
python alarm_analytics.py
```
See `analytics-pipeline.md` for configuration options.

4. Launch dashboards
```bash
python scripts/dashboards/app.py
```
Open http://localhost:8050 in your browser.

## Data model

The ETL produces three tables in SQLite:

| Table | Records | Purpose |
|-------|---------|---------|
| `historian_clean` | ~525k (10 assets x 365 days x 1 min) | SCADA signals (flow, pressures, temp, vibration, power) with failure labels |
| `alarm_log_clean` | ~2k | Alarm events with priority levels and acknowledgment times |
| `environmental_clean` | ~525k | USGS streamflow context |

## Project structure

- `docs/` - design notes, pipeline diagrams, configuration reference, data swap guidance
- `glossary/` - pump and monitoring terminology
- `references/` - papers, standards, pump curve data, literature
- `scripts/`
  - `historian-generator/` - synthetic pump data and alarm log generation
  - `etl-pipeline/` - extract, transform, load to SQLite with quality flags
  - `analytics-pipeline/` - baseline fitting, anomaly detection, alarm performance analysis
  - `dashboards/` - Dash app with callbacks and layouts
  - `usgs-weather-analysis/` - streamflow and weather context
  - `bearing-analysis/` - bearing signal workflows
  - `tests/` - validation scripts
  - `utils/` - shared helpers for data quality and pipeline support

## Using your own data

Once you validate the pipeline on synthetic data, you can swap in production historian, alarm, and environmental sources.

See `docs/data_swap_guide.md` for CSV schema mappings, unit conversion setup, timezone handling, and quality flag integration.

## References

Standards and data sources used in this project:
- ISA-18.2 Alarm Management guidelines
- Grundfos pump curve and efficiency data
- USGS National Water Information System
