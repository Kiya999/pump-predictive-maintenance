# Predictive Maintenance Case Study Annotations

## Case Study 1: Condition-Based Failure-Free Time Estimation of a Pump
**Cwikla G.; Paprocka I. Condition-Based Failure-Free Time Estimation of a Pump. Sensors 2023, 23, 1785.**

### 1. Utility scale

| Attribute | Value |
|---|---|
| Plant type | Wastewater treatment plant (WWTP), raw wastewater pumping station |
| Population served | ~170,000 people plus industrial dischargers |
| Plant capacity | Qd_avg = 51,000 m3/day; Qd_max = 60,000 m3/day; Qh_max (rain) = 5988 m3/h |
| Pumps analyzed | 5 main pumps installed (analysis on Pumps 1-4; Pump 5 auxiliary excluded) |
| Pump model (example) | Xylem Flygt N 3356; motor 90 kW nominal; speed 985 rpm |

### 2. Data sources

| Source | Details |
|---|---|
| SCADA / PLC | Integrated automatic control system; 8 PLCs; fieldbus fiber optic network; archival SCADA records |
| Observations | Main pump: n = 54 (10 days); combined pumps: n = 75 (5 days); other subsets: 30-45 observations |
| Sensors / variables | m = tank level (m); Pr = power (kW); V = voltage (V); F = frequency (Hz); I = current (A); Te = torque (Nm); FT = failure-free time (min) |
| Other logs | Dispatchers' work reports (paper-based, incomplete, non-standardized) |

### 3. Analytical methods

| Item | Details |
|---|---|
| Primary model | Multiple linear regression: FT = b0 + b1*m + b2*Pr + b3*V + b4*F + b5*I + b6*Te |
| Coefficient estimation | (a) Least squares via MS Excel Solver; (b) Genetic Algorithm (GA) implemented in Borland C++ |
| GA parameters tested | Population size (chn) in {100, 200}; generations (in) in {70, 100, 140}; mutation points (mn) in {1,2,3,4,5} |
| GA encoding | Chromosome encodes b0..b6 via sub-chromosomes (sign, integer part, fractional part); custom DNA library |
| GA fitness | F = 0.5*(1 - R^2/R^2_max) + 0.5*(s/s_max) where R^2 = multiple determination, s = standard deviation |
| Model selection criteria | Maximize R^2 and minimize standard deviation s |

### 4. Quantified outcomes

| Metric / experiment | Value |
|---|---|
| Excel Solver (main pump, 10 days, 6 vars) | R^2 = 0.96; s = 29.11 min; dominant coeff b6 (Te) = 0.812 |
| Excel Solver (combined pumps, 5 days, 75 obs) | R^2 = 0.69; s = 467.9 min |
| GA (various runs) | R^2 up to 1.0 in selected runs; s ranged 157-614 min depending on GA constraints |
| Example prediction | FT_hat = 732.13 min; actual failure at 1263 min |
| Key variable influence | Te (torque) and I (current) most strongly correlated with FT |

### 5. Implementation challenges

| Challenge | Notes |
|---|---|
| Small sample sizes | n = 54-75 per experiment; insufficient for robust generalization |
| Non-electronic logs | Maintenance reports paper-based, incomplete, imprecise timestamps |
| Overfitting risk | GA runs produced R^2 near 1.0 but high s remained |
| Model drift | Pump overhauls change performance; retraining required |
| Redundancy masking | Multi-pump configuration can mask single-pump failure signals |

---

## Case Study 2: Wastewater Plant Reliability Prediction Using Machine Learning Classification Algorithms
**Velimirovic L.Z.; Jankovic R.; Velimirovic J.D.; Janjic A. Wastewater Plant Reliability Prediction Using the Machine Learning Classification Algorithms. Symmetry 2021, 13, 1518.**

### 1. Utility scale

| Attribute | Value |
|---|---|
| Facility context | Sewage pumping station (system integrator / manufacturer dataset) |
| Pumps analyzed | 3 sewage pumps (pump 1, pump 2, pump 3) |
| Data period | October 2014 to May 2019 (~4.7 years) |
| Raw records | >28,000 measurements initially; 25,625 after cleaning |

### 2. Data sources

| Source | Details |
|---|---|
| PLC / SCADA sensors | Pump capacity (Q), current (I), high current, low current, nominal current, nominal capacity, inflow, level (lev1), run time, start count |
| Target variable | Binary alarm class: 0 = no alarm (24,330 cases), 1 = alarm (1,295 cases) |
| Sampling / preprocessing | Data averaged to hourly resolution; missing-value rows removed; StandardScaler (z-score) applied |
| Class imbalance handling | RandomUnderSampler then SMOTE; after sampling both classes balanced to 1,818 instances each for training |

### 3. Analytical methods

| Algorithm | Key hyperparameters / selection method |
|---|---|
| MLP (scikit-learn) | Activation: logistic; Solver: Adam; Alpha: 1e-5; Batch size: 64; Hidden layer size: 96 (one layer); parameters via RandomizedSearchCV + StratifiedKFold (10) |
| GBT | n_estimators = 450; max_depth = 20; min_samples_split = 55; min_samples_leaf = 10 |
| KNN | n_neighbors = 14; weights = distance; p = 1 (Manhattan) |
| RF | n_estimators = 100; criterion = entropy |
| Validation | RandomizedSearchCV + 10-fold Stratified CV; evaluation on held-out test set; ROC AUC primary metric |

### 4. Quantified outcomes

| Metric (test / validation) | MLP | GBT | KNN | RF |
|---|---:|---:|---:|---:|
| Validation accuracy | 0.87 | 0.92 | 0.80 | 0.91 |
| Precision | 0.59 | 0.66 | 0.56 | 0.65 |
| Recall | 0.79 | 0.87 | 0.76 | 0.85 |
| F1-score | 0.61 | 0.71 | 0.51 | 0.69 |
| AUC ROC | 0.793 | 0.869 | 0.759 | 0.850 |
| RS-CV time (s) | 591.9 | 208.6 | 1.905 | 27.99 |
| Training time (s) | 60.07 | 10.57 | 0.03 | 11.83 |
| Test confusion (GBT on test) | TN = 6650; TP = 319; FP = 652; FN = 67 |

### 5. Implementation challenges

| Challenge | Notes |
|---|---|
| Class imbalance | 95% negative (no alarm); mitigated via under-sampling + SMOTE but requires more real positive cases |
| Heterogeneous sampling rates | Sensors recorded at different intervals; hourly averaging reduces sub-hour signal detail |
| Missing values | Row removal reduced effective dataset size |
| Data access | Raw data not publicly available; access via corresponding author or company request |
| Low single-feature predictive power | Maximum single-variable correlation near 0.4; multi-variable models required |
| Computational cost | MLP hyperparameter search and training comparatively expensive |

---

## Case Study 3: Predicting Failures in Water Supply Networks Using Neural Networks
**Medeiros V.d.S.; dos Santos M.D.; Brito A.V. Case Study for Predicting Failures in Water Supply Networks Using Neural Networks. Water 2024, 16, 1455.**

### 1. Utility scale

| Attribute | Value |
|---|---|
| Utility | Companhia de Agua e Esgotos da Paraiba (CAGEPA) |
| City / region | Guarabira, Paraiba, Brazil |
| Water loss context | National WDLI = 40.3%; CAGEPA WDLI = 35.4% |
| Data period | November 2017 to April 2023 (~5.5 years) |
| Dataset size | 1,727 failure samples after preprocessing |

### 2. Data sources

| Source | Details |
|---|---|
| Failure records database | Date, geo-coordinates, failure type (Leak Removal used), address |
| External data | Elevation via Google Maps Elevation API |
| Target variable | days_until_next_failure (numeric: days) |
| Predictor variables | dist_nearest_neighbor (m); elevation (m); qtd_recurrences; days_since_last_failure; qtd_recurs_street; avg_days_btw_failures; variance; standard_deviation; qtd_days_btw_failures |

### 3. Analytical methods

| Item | Details |
|---|---|
| Primary model | Manual MLP (scikit-learn MLPRegressor): 4 hidden layers [128,128,648,550], ReLU activation, 370 iterations, 100 epochs |
| Comparison models | Automated MLP (Keras auto-config), scikit-learn linear regression, Keras DNN, Keras linear regression |
| Train / test split | Training = 1,175 samples (Jan 2018 - Dec 2021); Testing = 552 samples (Jan 2022 - Apr 2023) |
| Evaluation metrics | MAE, MSE, RMSE, MAPE, MedAE, Max Error |

### 4. Quantified outcomes

| Metric (error in days) | Manual MLP | Auto MLP | Linear Regr. | Keras DNN | Keras LR |
|---|---:|---:|---:|---:|---:|
| MAE | 33.85 | 37.06 | 45.34 | 236.10 | 64.08 |
| MSE | 1981.13 | 1994.35 | 3762.60 | 67591.47 | 5740.67 |
| RMSE | 44.51 | 44.66 | 61.34 | 259.98 | 75.77 |
| MAPE (%) | 3.63 | 4.11 | 7.99 | 35.77 | 1.94 |
| MedAE | 28.37 | 30.69 | 34.88 | 248.31 | 74.37 |
| Max Error | 158.48 | 150.88 | 251.06 | 492.20 | 217.66 |
| Prediction error distribution (Manual MLP) | 12.37% error < 5 days; 57.73% error < 30 days; 80.41% error < 45 days; 93.81% error < 90 days |

### 5. Implementation challenges

| Challenge | Notes |
|---|---|
| Data sensitivity and access | Data available only via institutional partnership with CAGEPA |
| Limited feature set | Network structural data (pipe material, diameter, age, EPANET hydraulics) not available |
| Low predictor correlation | Individual predictors have weak correlation with target (max near 0.4) |
| Spatial recurrence definition | Recurrence radius = 50 m (subjective); alternative radii not tested |
| Generalizability | Single-city dataset; external validity to other cities not established |

---

## Cross-Case Synthesis

| Dimension | Cwikla and Paprocka 2023 | Velimirovic et al. 2021 | Medeiros et al. 2024 |
|---|---:|---:|---:|
| Domain | WWTP pump failure-free time | WWTP pump failure classification | Water supply network pipe failure prediction |
| Prediction target | Regression: minutes to failure | Binary classification: alarm or no alarm | Regression: days to next failure |
| Data frequency | Event-based SCADA records (54 events over 10 days) | Hourly averaged sensor data | Daily failure records |
| Sample size | 54-75 observations | 25,625 measurements (1,818 after balancing) | 1,727 failure samples |
| Best algorithm | Multiple linear regression + GA | GBT (AUC=0.869) | Manual MLP (MAE=33.85 days) |
| Best performance metric | R^2=0.96 (Excel) / R^2=1.0 (GA) | AUC=0.869, F1=0.71, Recall=0.87 | MAE=33.85d, MAPE=3.63% |
| Detection lead time | One example predicted 732 min (actual failure at 1263 min); not validated as consistent lead time | Real-time (hourly classification) | 33.85 day average error (80.41% within 45 days) |
| Key implementation barrier | Manual paper-based event logs | Class imbalance (95% / 5%) | Data sensitivity and access restrictions |
| Practical outcome | Prediction enables shift-level maintenance planning based on estimated failure-free time | High-AUC classifier suitable for integration into SCADA supervisory layer | Utility can plan maintenance 33-45 days ahead on average |
