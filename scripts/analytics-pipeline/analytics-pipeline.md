# Analytics Pipeline

## Run Order

Prerequisite: `etl_pipeline.db` must exist (run ETL pipeline first).

Library files (never run directly - imported by other scripts):
- baseline.py                           # used by verify_baseline.py and analyze_detection_performance.py
- anomaly_detection.py                  # used by verify_anomaly_detection.py and analyze_detection_performance.py
- environmental_correlation.py          # utilities for future asset-level analysis

Standalone scripts - no interdependencies, can run in any order:
1. data_dictionary.py                   # schema/value-range documentation (Excel)
2. pf_alignment.py                      # static reference matrix (no DB read)
3. alarm_analytics.py                   # alarm log metrics + test-case validation
4. verify_baseline.py                   # sanity-checks baseline methods on 1 healthy + 1 degrading asset
5. verify_anomaly_detection.py          # visualizes raw detection flags on the 3 failure scenarios
6. analyze_detection_performance.py     # main analysis: lead times, FP rates, trend detection (synthetic data only)

Notes:
- None of these scripts read another script's output; they all read directly from etl_pipeline.db.
- analyze_detection_performance.py requires synthetic failure timing metadata (RAMP_INFO_DAYS, PF_INTERVALS_HOURS) and won't produce meaningful results on real client data.
- analyze_detection_performance.py is the most comprehensive and slowest; run it last if you want the freshest final numbers.
- If output/ folder is deleted, all 6 standalone scripts must be rerun to repopulate it; order among them doesn't matter functionally.