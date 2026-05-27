
## P-F Curve Annotated Notes

### Example 1: Rolling element bearing fault in a centrifugal pump

**Source:** PMC / National Library of Medicine, "Monitoring and Predictive Maintenance of Centrifugal Pumps Based on Smart Sensors" (Sensors, MDPI, March 2022). Authors: Chen, Wang, Wang, Li. Available at: https://pmc.ncbi.nlm.nih.gov/articles/PMC8951325/

| Item | Detail |
|------|--------|
| Asset | Grundfos NKE 40-250/255 centrifugal pump, 22 kW, 2940 rpm, cylindrical roller bearing |
| Failure mode | Bearing wear (outer race pitting, peeling, spalling due to poor lubrication or overload) |
| Signal monitored at P | Vibration acceleration via MEMS triaxial sensor mounted on bearing housing. Bearing defect frequencies appear in the vibration spectrum as characteristic peaks. Temperature rise is a secondary indicator |
| P-F interval | Not explicitly stated in weeks. The study focuses on detection accuracy, not P-F timeline. However, the paper confirms that bearing wear is a "gradual deterioration" failure suitable for periodic monitoring |
| Action triggered at P | The IoT system generates a fault diagnosis and sends the result to the cloud platform. Equipment managers schedule targeted maintenance before functional failure occurs |
| Detection accuracy | Wired sensors achieved 100% diagnostic accuracy, precision, and recall for bearing faults in the test environment |
| Key finding | Wireless sensors operating on 30-minute upload intervals can still detect bearing wear because it is a progressive, not sudden, failure mode. Wired continuous monitoring detects it earliest |

**Annotation:** This study validates that bearing degradation in centrifugal pumps follows the P-F curve model. The defect progresses from a microscopic spall (detectable by vibration spectrum analysis at point P) to measurable performance loss and eventual seizure (point F). The P-F interval for bearing faults depends on load, speed, and lubrication quality. The practical takeaway: vibration monitoring at the bearing housing, analyzed for characteristic defect frequencies, is the most reliable method for pushing point P to the left and maximizing usable warning time.

---

### Example 2: Cavitation risk in a process water centrifugal pump

**Source:** Pumps & Systems magazine, "Case Study: Sensorless Pump Performance & Condition Monitoring" (June 2025). Available at: https://www.pumpsandsystems.com/case-study-sensorless-pump-performance-condition-monitoring

| Item | Detail |
|------|--------|
| Asset | Process water centrifugal pump, 110 kW motor, nominal flow 421.5 m3/h at BEP |
| Failure mode | Cavitation risk caused by operating far below BEP (actual flow 90-115 m3/h vs design 421.5 m3/h). Low-flow, high-head conditions create flow irregularities that induce cavitation |
| Signal monitored at P | Broadband noise in the power spectral density (PSD) of motor current, detected by electrical signature analysis (ESA). No physical flow or pressure sensors needed |
| P-F interval | Not explicitly quantified in the case study text. The study focuses on detection and correction, not timeline measurement |
| Action triggered at P | The monitoring system flagged cavitation risk, low efficiency (40-60%), and component wear risk. The recommended action was replacement of the oversized pump with a correctly sized unit (215 m3/h nominal, 55 kW nominal, 81.3% efficiency at BEP) |
| Outcome | Projected annual savings of 338,173 kWh (56% reduction), $30,435/year at $0.09/kWh, 1.28-year payback period, 78% ROI |
| Secondary indicators | Low efficiency (40-60%), elevated motor input power (68.58 kW at 83 m3/h), mechanical stress on bearings and seals |

**Annotation:** This is a practical example of the P-F curve applied to cavitation. Point P was detected as broadband noise in the electrical signature, well before audible cavitation or visible impeller damage occurred. The P-F interval for cavitation depends on flow conditions and fluid properties. Operating at 20-27% of BEP flow accelerates the progression from P (first detectable signal) to F (functional failure via impeller erosion, bearing damage, or seal leakage). The case demonstrates that early detection at P allows planned replacement rather than emergency repair.
