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

**Results**: Detects bearing (96.5% of P-F interval) and insulation (80.6%). No persistent detection for cavitation.
**False positive rate** (healthy assets): ~0.3% on vibration, 0-97% on motor temp (strongly seasonal: near-zero in winter, near-100% in summer), 0-55% on diff pressure (also seasonal). Z-score is highly sensitive to the same seasonal baseline drift described in Section 5.

### Method 2: IQR Flagging
Flag points outside Q1 - 1.0*IQR and Q3 + 1.0*IQR, computed on the residual (signal - baseline), using a 1440-period (24-hour) rolling window.

**Results** (see lead_times.csv):

Scenario | Lead Time (hours) | Percent of P-F Interval
--- | --- | ---
Bearing (vibration) | No persistent detection | -
Cavitation (diff_pressure) | No persistent detection | -
Insulation (motor_temp) | 2819 | 97.9

**Interpretation**: IQR only achieves persistent detection for insulation, arriving very late (97.9% of P-F; essentially at functional failure, not meaningfully early). Bearing and cavitation show no persistent detection under the 6-hour/70%-window persistence rule. For cavitation specifically, this reflects the intermittent-spike nature of the injected fault rather than a detector weakness (see Section 7).

**False positive rate** (healthy assets): ~4.2% on vibration (stable year-round), 1-4% on diff pressure, 1-8% on motor temp (seasonal). Substantially improved from an earlier implementation that computed IQR fences on the near-constant baseline series itself rather than on residuals. That bug produced ~96% FP on vibration.

### Method 3: Moving Average Deviation
Compare 30-minute moving average against baseline mean; flag when deviation exceeds 1.5 * baseline_std.

**Results**: Detects bearing (98.5% of P-F) and insulation (99.1% of P-F), both very late. No persistent detection for cavitation.
**False positive rates**: 0% on vibration (excellent), up to 100% on motor_temp in summer months, up to 92% on diff_pressure; both driven by the same seasonal baseline drift as Z-score.

---

## 4. Trend Detection: Mann-Kendall Test

The Mann-Kendall non-parametric test was applied to the vibration signal of the bearing asset (P-0100) to test for monotonic trend in the pre-failure period.
Results are in trend_detection_results.csv.

| Window | Trend | p-value | Significant |
|---|---|---|---|
| Capped full window, centered on first persistent detection (Z-score used as fallback anchor since IQR shows no persistent bearing detection) | stable | 0.324 | No |
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
Z-score (threshold 3.0) | High for step-change faults, seasonal blind spots | Low in summer (up to 97% FP on temp) | Unreliable without seasonal baseline correction
IQR (window 1440, multiplier 1.0) | Low; only catches late-stage insulation faults | High (~1-4% FP) | Best specificity of the three; recommended as primary flagging method with operator context
Moving average (window 30, threshold 1.5) | High for step-change faults, seasonal blind spots | Low in summer (up to 100% FP on temp) | Same seasonal caveat as Z-score

**Recommended combination**:
- Use **IQR** as the primary flagging method for the dashboard; best specificity, stable across seasons.
- Treat **Z-score** and **Moving average** flags as supplementary only, and discount them heavily May-September given seasonal FP spikes.
- None of the three methods reliably detect cavitation under the current persistence rule; treat cavitation-prone assets as requiring supplementary monitoring (e.g., manual review of intermittent spike patterns).

---

## 7. Limitations

1. **Synthetic data**: Failure modes are injected as step changes; real bearing degradation is more gradual and would show Mann-Kendall trends.
2. **Seasonal baseline**: 30% training window captures only winter; summer performance degrades significantly.
3. **No cross-signal detection**: Methods operate on single signals independently. Correlated anomalies across multiple signals (e.g., rising temperature and rising vibration) are not exploited.
4. **Fixed thresholds**: No adaptive threshold adjustment for changing operating conditions.
5. **Persistence rule vs. intermittent faults**: The 6-hour/70%-window persistence requirement, applied uniformly across all three methods, structurally cannot detect cavitation in this dataset; the injected fault manifests as intermittent pressure spikes rather than a sustained deviation. This is a methodological choice, not necessarily a bug; intermittent fault detection would require a different rule (e.g., spike-frequency counting within a window) rather than sustained-flag persistence.

---
