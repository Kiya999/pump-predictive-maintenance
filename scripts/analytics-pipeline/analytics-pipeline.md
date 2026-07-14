# Analytics Pipeline

## Run Order

Prerequisite: `etl_pipeline.db` must exist (run ETL pipeline first).

Library files (never run directly - imported by other scripts):
- baseline.py
- anomaly_detection.py
- environmental_correlation.py

Standalone scripts - no interdependencies, can run in any order:
1. data_dictionary.py                   # schema/value-range documentation (Excel)
2. pf_alignment.py                      # static reference matrix (no DB read)
3. alarm_analytics.py                   # alarm log metrics + test-case validation
4. validate_baseline.py                 # sanity-checks baseline methods on 1 healthy + 1 degrading asset
5. test_anomaly_detection.py            # visualizes raw detection flags on the 3 failure scenarios
6. analyze_detection_performance.py     # main analysis: lead times, FP rates, trend detection

Notes:
- None of these scripts read another script's output; they all read directly from etl_pipeline.db.
- analyze_detection_performance.py is the most comprehensive and slowest; run it last if you want the freshest final numbers.
- If output/ folder is deleted, all 6 standalone scripts must be rerun to repopulate it; order among them doesn't matter functionally.