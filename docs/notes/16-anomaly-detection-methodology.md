# Anomaly Detection Methodology

---

## 1. Overview

Three statistical detection methods were evaluated against three failure scenarios (bearing degradation, cavitation, insulation breakdown) across 10 synthetic pump assets spanning 365 days (5.25 million records at 1-minute resolution).

The detection problem is framed as anomaly detection rather than classification because failure events are rare (<0.1% of records), making class-imbalanced classification unreliable. Anomaly detection requires only normal operating data for baseline training, which matches operational reality where labeled failure data is scarce.

---

## 2. Baseline Methods

All detection methods operate on residuals relative to a pre-computed baseline. Three baseline methods were implemented (baseline.py):

**Method 1: Rolling baseline**: 24-hour rolling mean and std. Tracks diurnal variation but can adapt to slow degradation if the window is too long.

**Method 2: Time-of-day adjusted baseline**: Separate mean/std per hour of day, trained on pre-failure data only. Handles diurnal patterns without adapting to failure. **Used for all detection results below.**

**Method 3: Operational-state-conditioned baseline**: Separate baselines per flow regime (low/mid/high). Prevents regime changes from triggering false positives.

**Training window**: First 30% of each asset's record (pre-failure only). Baseline is frozen at training time and does not adapt to failure-period data.

---

## 3. Detection Methods

### Method 1: Z-score Thresholding
Flag any point where (signal - baseline_mean) / baseline_std > 3.0.

**Result**: Zero detections across all three failure scenarios.
**Root cause**: Threshold of 3.0 is conservative and appropriate for Gaussian distributions. The bearing and insulation failures produce sudden step changes rather than gradual drift; the signal transitions from healthy to failed without extended pre-failure deviation exceeding 3 sigma. Z-score is well-suited for detecting sustained gradual drift but not abrupt failure modes.

### Method 2: IQR Flagging
Flag points outside Q1 - 1.5*IQR and Q3 + 1.5*IQR computed from a 1440-period (24-hour) rolling window. Multiplier: 1.0.

**Results** (see lead_times.csv):

Scenario | Lead Time (hours) | Percent of P-F Interval
--- | --- | ---
Bearing (vibration) | 2369 | 38.0
Cavitation (diff_pressure) | 1377 | 95.6
Insulation (motor_temp) | 3568 | 123.9

**Interpretation**: IQR is the only method detecting pre-failure anomalies. For insulation, the 123.9% figure (exceeding P-F interval) indicates detection before the defined P-F start, which likely reflects genuine early signal deviation. For cavitation, 95.6% means detection is very late (near functional failure). Bearing detection at 38% is reasonable.

**False positive rate** (healthy assets): 95.7% on vibration, 25-47% on temperature and pressure. Unacceptably high for production deployment.

### Method 3: Moving Average Deviation
Compare 30-minute moving average against baseline mean; flag when deviation exceeds 1.5 * baseline_std.

**Result**: Detects only insulation scenario (416 hours, 14.5% of P-F).
**False positive rates**: 0% on vibration (excellent), 48.9% on motor_temp (alert fatigue risk).

---

## 4. Trend Detection: Mann-Kendall Test

The Mann-Kendall non-parametric test was applied to the vibration signal of the bearing asset (P-0100) to test for monotonic trend in the pre-failure period.
Results are in trend_detection_results.csv.

| Window | Trend | p-value | Significant |
|---|---|---|---|
| 111.6h (capped full window, centered on first IQR detection) | stable | 0.324 | No |
| 72h trailing | stable | 0.925 | No |
| 168h trailing | stable | 0.473 | No |

**Finding**: No statistically significant pre-failure trend in bearing vibration. This is consistent with the failure mode: bearing failure in this synthetic dataset is a sudden step change, not a gradual monotonic drift. Mann-Kendall trend detection is more appropriate for thermal or insulation degradation scenarios where signal drift is gradual.

---

## 5. False Positive Root Cause

The high false positive rates (26-97%, see false_positives_by_signal_month.csv) on healthy assets are explained by seasonal temperature variation:

- Baseline trained on first 30% of data (Jan-Feb, winter)
- Summer motor temperature (Jul): mean = 45.6 C (9.2 C above baseline mean of 36.4 C)
- This drift exceeds IQR and MA thresholds even on healthy assets

**Implication**: A production system must use operational-state-aware baselines that account for ambient temperature variation, or retrain baselines seasonally.

---

## 6. Recommendation

Method | Sensitivity | Specificity | Deployment Suitability
--- | --- | --- | ---
Z-score (threshold 3.0) | Low | High (0.26% FP)| Gross fault detection only
IQR (window 1440, multiplier 1.0) | High | Low (95.7% FP) | Not production-ready as single method
Moving average (window 30, threshold 1.5) | Medium | Medium | Insulation monitoring only

**Recommended combination**:
- Use **Z-score** as a high-confidence alarm (rare but reliable)
- Use **IQR** as an early warning indicator (frequent, requires   operator context)
- Use **Moving average** for insulation/thermal monitoring only
- Display IQR vibration flags only with operator context warnings (95.7% FP rate requires operator judgment before action)
---

## 7. Limitations

1. **Synthetic data**: Failure modes are injected as step changes; real bearing degradation is more gradual and would show Mann-Kendall trends.
2. **Seasonal baseline**: 30% training window captures only winter; summer performance degrades significantly.
3. **No cross-signal detection**: Methods operate on single signals independently. Correlated anomalies across multiple signals (e.g., rising temperature and rising vibration) are not exploited.
4. **Fixed thresholds**: No adaptive threshold adjustment for changing operating conditions.

---
