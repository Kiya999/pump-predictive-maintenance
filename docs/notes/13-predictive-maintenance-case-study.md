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

## Cross-Case Synthesis (case studies 1-3)

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

---

## Case Study 4: Kaggle Pump Sensor Dataset
**Kaggle dataset: https://www.kaggle.com/datasets/nphantawee/pump-sensor-data/data**

### 1. Utility scale

| Attribute | Value |
|---|---|
| Facility context | Water pump system serving a small residential area |
| System failures in prior year | 7 |
| Sensor count | 52 sensor series, all raw values |
| Row count | 220,320 |
| Time span | April to August (5 months) |

### 2. Data and quality issues

| Item | Details |
|---|---|
| Target variable | machine status: Normal (205,836 rows), Recovering (14,477 rows), Broken (7 rows) |
| Sensor identity | Not documented. Cannot map signals to physical parameters or failure modes. |
| Missing values | Several sensors have significant gaps. One sensor is entirely empty. |
| Class imbalance | Only 7 Broken samples across 5 months. Insufficient for supervised learning on that class. |
| Single pump system | One pump assembly. Generalizability to other pump types unknown. |

### 3. Common preprocessing steps

| Step | Description |
|---|---|
| Drop empty sensors | Sensors with 100% missing values removed |
| Remove low-variance sensors | Sensors with near-zero variance removed |
| Gap filling | Consecutive NaN gaps up to 30 timesteps forward-filled |
| Label shifting | Labels shifted by 10 minutes to create a prediction horizon |

### 4. Typical analytical approaches

| Method | Details |
|---|---|
| Random Forest | Trained on a subset of highest-separation sensors. Macro F1-score above 0.99 on held-out test data. |
| LSTM | Two LSTM layers. Predicted recovering phase 10 minutes ahead. Training accuracy near 99% but class imbalance makes accuracy misleading. Validation requires F1, ROC, Kappa. |
| Feature engineering | Distance from Normal class mean used as engineered feature. Mean aggregation over 10-minute windows improved performance. |

---

## Case Study 5: Enhancing Predictive Maintenance in Automotive Industry
**Mahale Y.; Kolhar S.; More A.S. Enhancing Predictive Maintenance in Automotive Industry: Addressing Class Imbalance Using Advanced Machine Learning Techniques.**

### 1. Utility scale

| Attribute | Value |
|---|---|
| Domain | Automotive on-board diagnostics (OBD-II) |
| Facility context | Fleet vehicle diagnostics and engine performance monitoring |
| Data source | Kaggle OBD-II crowdsourced dataset |
| Dataset size | 47,514 rows; 33 diagnostic features |
| Failure scope | Engine fault detection (binary classification) |
| Class distribution (raw) | 16.3% failure instances; 83.7% normal operation |

### 2. Data sources

| Source | Details |
|---|---|
| OBD-II sensors | Engine speed (RPM), coolant temperature, engine load, throttle position, intake manifold pressure, engine runtime |
| Target variable | Binary: Engine fault (1) or normal operation (0) |
| Preprocessing | Missing value imputation (linear interpolation, mean, KNN, forward/backward fill); outlier detection via IQR; z-score normalization |
| Feature selection | Domain-driven attribute subset selection; final set focused on engine performance indicators |

### 3. Analytical methods: Class imbalance handling

| Technique | Approach | Purpose |
|---|---|---|
| SMOTE | Synthetic Minority Oversampling Technique; generates synthetic failure samples via interpolation | Balances class distribution from 16.3%/83.7% to 50%/50% for training |
| Ensemble methods | Balanced Random Forest, RUSBoost, Easy Ensemble, Balanced Bagging | Combine resampling and boosting/bagging to improve minority class detection |
| Cost-sensitive learning | Assigns higher misclassification cost to minority class; tested with SVM, logistic regression, decision tree, XGBoost, LightGBM, AdaBoost | Penalizes false negatives more heavily than false positives |
| Comparison baseline | Standard classifiers without imbalance handling | Establishes improvement magnitude from each technique |

**Evaluation approach:** 
Precision, recall, F1-score, and ROC-AUC were used as primary metrics rather than accuracy alone, since accuracy is misleading for imbalanced binary classification.

### 4. Quantified outcomes

**SMOTE Performance (Ablation Study):**
SMOTE application showed statistically significant improvement in F1-score (t = 8.6572, p = 0.0010) and ROC-AUC (t = 7.7971, p = 0.0015) across models tested. SMOTE-based Random Forest achieved F1-score of 0.9954.

**Ensemble Methods (Table 7 summary):**
- Balanced Random Forest: F1 = 0.9914, ROC-AUC = 0.9999
- RUSBoost: F1 = 0.9996, ROC-AUC = 1.0000
- Easy Ensemble: F1 = 1.0000, ROC-AUC = 1.0000 
- Balanced Bagging: F1 = 0.9988, ROC-AUC = 1.0000

**Cost-Sensitive Learning (Table 8 summary):**
- XGBoost: Precision = 1.0, Recall = 1.0, F1 = 1.0, ROC-AUC = 1.0 
- LightGBM: F1 = 0.9926, ROC-AUC = 0.9985
- AdaBoost: F1 = 1.0000, ROC-AUC = 0.9998
- Other cost-sensitive models (SVM, LR, DT): F1 range 0.9712–0.9822

**Key finding:** Ensemble methods and cost-sensitive learning outperformed SMOTE-only approaches. Tree-based ensembles (especially XGBoost and Easy Ensemble) achieved highest detection metrics.

### 5. Implementation challenges and insights

| Challenge | Observation |
|---|---|
| SMOTE limitations | Generates synthetic samples that may not represent real failure modes; assumes linear separability, which limits its effectiveness on non-linear patterns; introduces synthetic noise that can cause overfitting |
| Perfect scores concern | Two methods (Easy Ensemble, XGBoost) achieved metrics = 1.0, suggesting potential overfitting or test-set leakage |
| Ensemble computational cost | Bagging and boosting methods require significant computational resources; RUSBoost and Easy Ensemble require training multiple models in sequence|
| Feature importance and interpretability | XGBoost feature importance analysis identified most influential OBD parameters; SHAP and LIME explanations provided local and global interpretability |
| Accuracy as misleading metric | Accuracy alone is inadequate for imbalanced data; F1-score and ROC-AUC are necessary for proper evaluation |
| Generalizability | OBD dataset limited to engine parameters; results may not transfer to other fault types; limited to one domain makes it unclear how well the approach would work elsewhere |

---

# Case Study 6: Implementation of AI-Based Fault Classification and Anomaly Detection in Hydraulic Centrifugal Pumps

**Turk M.C.; Kazemi Z.; Andersen P.R.; Lemming J.; Larsen P.G. Implementation of Artificial Intelligence-Based Fault Classification and Anomaly Detection: A Case Study on Hydraulic Centrifugal Pumps.**

---

## 1. Utility Scale

| Attribute | Value |
|---|---|
| Equipment context | Hydraulic centrifugal pump test stand with configurable inlet/outlet conditions |
| Sensor integration | Custom data logging unit; total cost <$450 |
| Failure scenarios | 12 known scenarios: worn impeller/plate/knives, closed inlet/outlet, 40/50/59 Hz operation, wrong rotation, and idle mode |
| Data frequency | 1 measurement per second; local storage on memory card |
| System scope | Single pump assembly; remote data transfer via GPRS or manual export |

---

## 2. Data Sources

| Source | Details |
|---|---|
| Sensor types | 3-axis vibration (acceleration), pressure, motor voltage (3-phase), motor current (3-phase), enclosure temperature, pump body temperature (cooling channel) |
| Raw data volume | 14 initial channels; reduced to 6 core features via autoencoder |
| Signal processing | FIR filter for noise removal and signal stability |
| Training data | Ordinary operation (2 hours); fault scenarios (5–15 min each, multiple sessions) |
| Class distribution (raw) | Imbalanced: 2-hour normal operation vs. 5–15 min fault scenarios (approx. 8:1 ratio) |

---

## 3. Analytical Methods: Imbalance and Anomaly Handling

| Technique | Approach | Purpose |
|---|---|---|
| Gaussian Noise Addition | Augment minority class samples to achieve balance | Address training set imbalance without synthetic interpolation |
| Autoencoder (AE) | Unsupervised learning on 6 features; encoding dimension = 50 (higher than input to capture patterns) | Compute reconstruction error; threshold separates known scenarios from anomalies |
| Random Forest | 100 estimators; no manual class weighting | Classify known scenarios when reconstruction error is below threshold |
| MLPClassifier | Logistic activation; soft voting ensemble | Capture non-linear decision boundaries missed by RF |
| Voting Classifier (VC) | Soft voting ensemble of RF + MLPClassifier predictions | Leverage complementary strengths for improved precision |

---

## 4. Quantified Outcomes

| Metric | Value | Context |
|---|---|---|
| RF alone (various tests) | 98.7–100% accuracy | Varies with number of fault scenarios in test set |
| MLPClassifier alone | 21.9–100% accuracy | Performance degrades as scenario count increases |
| VC (final validation) | 98.5% minimum accuracy | Extreme test: 16 sessions with 8 scenarios in 2.5 hours; 11/16 detected correctly |
| Unseen scenario detection | Correctly labeled as anomaly | Idle mode with grid power available (not in training set) |
| Failed detections | 5/16 sessions | Sessions 3, 6, 7, 12, 14: rapid state transitions or hybrid scenarios |

---

## 5. Key Implications for Model Design

| Implication | Rationale |
|---|---|
| Two-stage pipeline (AE -> Classifier) separates concerns | Routes unknown faults to anomaly detector; known faults to classifier; avoids forcing unknown patterns into known classes |
| Multimodal sensor fusion improves robustness | Redundancy across vibration, pressure, electrical, and thermal signals; single-sensor approach insufficient |
| Anomaly detection tolerates unlabeled unknowns | No need to balance anomaly class explicitly; reconstruction error provides unsupervised threshold |
| Ensemble prevents single-model bias | RF robust on regular patterns; MLP catches non-linear transitions in fault onset |

---

## 6. Implementation Challenges

| Challenge | Notes |
|---|---|
| Imbalance imposed by safety constraints | Unsafe to run pump with closed outlet >5 min; creates 8:1 imbalance (mitigated via Gaussian noise augmentation rather than SMOTE) |
| Rapid fault state transitions | Model confusion when scenarios change within seconds (sessions 3, 12); requires denser labeling or multi-scale temporal features |
| Anomaly threshold selection | Reconstruction error threshold is implicit; no reported false positive rate on normal operation or stability analysis across pump configurations |
| Generalizability | Single pump, single test setup; no cross-validation on different pump units or real field data |

---
