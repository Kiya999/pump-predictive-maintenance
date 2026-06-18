# Anomaly Detection Methods for Pump SCADA Data - Literature Notes

## 1. Moleda et al. (2020), Predictive Maintenance of Boiler Feed Water Pumps Using SCADA Data

### Summary

| Attribute | Value |
|---|---|
| Domain | Boiler feed water pump, coal power plant |
| Data | 22 sensors, 1-min sampling, 4.5 years |
| Baseline method | Multi-signal linear regression with 30-day rolling window |
| Threshold method | NRE with 3-sigma warning, 6-sigma failure |
| Key finding | Detected relief valve leak 3 months before recorded failure |

---

### Baseline Methods

- Each sensor signal predicted from all other correlated sensor readings using linear regression
- Training window of 30 days (1440 rows per day), re-estimated at each time quantum
- Rationale: pump operates under variable load ranges, atmospheric conditions, and material types. Correlated sensors shift together, so regression adjusts baseline to current operating state automatically
- Alternative polynomial degrees tested; degree=1 (linear) gave best fit. Higher polynomial degrees reduced accuracy (overfitting)
- Bag of models: k regression models, each for one signal, only those with R^2 above threshold tau_2 are kept
- Training set size tradeoff: larger set = smaller approximation error; smaller set = faster adaptation after overhauls

---

### Detection Thresholds

| Threshold | Criterion | Justification |
|---|---|---|
| 1st level (warning) | NRE_max > 3 | Three-sigma rule: 99.73% of values within 3-sigma for normal distribution |
| 2nd level (failure) | NRE_max > 6 | Chebyshev inequality: at least 88.8% of cases within properly calculated 3-sigma, even for non-normal distributions |

NRE = (|actual - predicted| - MAE) / RMSE

The maximum NRE across all signals identifies the sensor most likely causing the anomaly, enabling root cause localization.

---

### Operational Variability Handling

- Regression-based baseline handles variability implicitly: all correlated signals shift with load or operating state changes, so the expected value adjusts
- Operating state detection: threshold on pump power supply current (>1 A) to distinguish running vs. stopped
- Training window continuously re-estimated to track gradual machine changes (e.g., after overhauls)
- Sensitivity noted: method very sensitive to sensor failures (bad signal poisons the regression), requiring data cleaning before training

---

## 2. Shaikh et al. (2025), Unsupervised detection of faults in industrial pumps from multivariate time series

### Summary

| Attribute | Value |
|---|---|
| Domain | Centrifugal process pump, paperboard mill |
| Data | 7 sensors, 5-min resampled, 1 year |
| Baseline method | Rolling statistical features (mean, std, slope) + spectral + lag features, 100-min windows |
| Threshold method | Unsupervised model anomaly scores scaled 0-1 via sigmoid |
| Key finding | CNN Autoencoder best F1=0.440; Isolation Forest fastest at 0.039s per window |

---

### Baseline Methods

- Feature engineering per 100-min window: rolling means and stds over 30-min and 60-min horizons, linear regression slopes (trend), FFT spectral energy, lagged values for autocorrelation
- Each window becomes a 77-dimensional feature vector
- Robust scaling using median and IQR (not mean and std) to protect against outliers
- Segmentation into micro-windows of 20 timesteps (100 min) with 30% overlap
- Five unsupervised models compared: LOF, Isolation Forest, LSTM Autoencoder, 1D CNN Autoencoder, hybrid ensemble

---

### Detection Thresholds

- Raw anomaly scores normalized to 0-1 range using sigmoid function
- Tiered severity scale: 1-2 (future inspection ticket), 3 (scheduled maintenance), 4-5 (immediate alert)
- Threshold optimized via validation F1-score maximization
- No fixed statistical threshold (like z-score). Threshold depends on model calibration
- False positive cost estimated at $2500 per incident (context-dependent in practice)

---

### Operational Variability Handling

- Sliding windows with rolling features adapt to non-stationary operational regimes
- Trend features (linear regression slope) capture gradual drift
- 100-min window chosen with experts as tradeoff: long enough to capture fault precursors (1-3 hours), short enough to maintain signal-to-noise ratio
- Component analysis: removing lag features caused biggest F1 drop (from 0.400 to 0.368), confirming temporal dependencies are critical for capture degradation patterns under varying operations

---

## 3. Key Implications

| Design Decision | Implication |
|---|---|
| 3-sigma threshold justification | Moleda et al. provide formal justification (Chebyshev inequality) for using mean + N*std as control limits. This can be utilized in our work to present a statistically grounded method for threshold selection in anomaly detection. |
| 30-day training window | Moleda et al. found 30 days was the tradeoff point where MAE and R^2 stabilize. Our 365-day dataset supports longer windows. We can use the pre-failure period for baseline training. |
| Regression vs. time-of-day baseline | Moleda uses multi-signal regression. We have time-of-day and operational-state. these can be used and are alternatives that do not require correlated signals. |
| Robust scaling | Shaikh paper confirms median/IQR scaling (not mean/std) is preferred when outliers may be present in baseline training data. We should use this for our preprocessing. |
| False positive cost framing | Shaikh gives $2500/FP benchmark but notes real cost depends on production state. This is useful when we tune thresholds later in our analysis. |
| Lead time measurement | Shaikh defines lead time as time between first anomaly detection and documented failure. We should use the same approach later. |

---

## 4. Limitations

| Limitation | Source | Impact |
|---|---|---|
| Regression baseline requires correlated signals | Moleda | Method fails if signals are independent. Check correlation matrix before applying. We have time-of-day baseline that avoids this assumption. |
| Only 5 failure events | Shaikh | Weak ground truth limits statistical significance. We have a synthetic dataset with 3 known failure scenarios and precise P-F intervals, which gives stronger ground truth. |
| No explicit diurnal handling | Both papers | Neither method addresses the hour-of-day baseline. We can implement this ourselves as an addition |
| Lab settings vs. field | Moleda | Real plant data but only one pump unit. Our synthetic dataset has 10 assets with controlled failure injection which gives us more variety. |

---