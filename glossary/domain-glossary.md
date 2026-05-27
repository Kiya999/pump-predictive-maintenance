# Domain Glossary

## Pump Fundamentals Terms

**Affinity laws**
Set of mathematical relationships that predict how a centrifugal pump's performance changes when its rotational speed changes. Flow is proportional to speed, head is proportional to speed squared, and power is proportional to speed cubed. This means cutting speed by 20% reduces power demand by nearly 50%, which is why variable frequency drives save so much energy.

**Best Efficiency Point (BEP)**
The flow rate at which a pump converts input power to hydraulic power most efficiently. Every pump has a specific BEP, typically marked on its published performance curve. Operating far from BEP causes vibration, bearing wear, and shaft deflection.

**Cavitation**
Formation and collapse of vapor bubbles inside a pump when local pressure drops below the fluid's vapor pressure, typically at the impeller eye or vane inlet. These bubbles implode violently against metal surfaces, eroding material over time. Cavitation sounds like gravel passing through the pump and causes rapid impeller damage if not corrected.

**Coupling**
Mechanical component that connects the motor shaft to the pump shaft to transmit torque. Flexible couplings compensate for minor misalignment between the motor and pump. Some designs include spacer sleeves so the pump can be removed without disturbing the motor or piping.

**Discharge head**
Pressure measured at the pump outlet nozzle, expressed as height of liquid column. It is the sum of static lift, friction losses, and any pressure in the receiving vessel. Discharge head together with suction head determines total dynamic head.

**Duty point**
The specific combination of flow and head at which a pump actually operates in a given system, found at the intersection of the pump curve and system curve. This point should fall near the pump's best efficiency point for reliable long-term operation. If the duty point drifts outside the allowable operating range, the pump will experience increased wear or premature failure.

**Flow rate**
Volume of fluid delivered by the pump per unit time, typically measured in cubic meters per hour or gallons per minute. The pump's flow rate is determined by the intersection of its head-capacity curve with the system's resistance curve. Different flow rates are specified depending on context: nominal flow, flow at BEP, minimum continuous flow, and maximum allowable flow.

**Head**
Energy per unit weight of fluid imparted by the pump, expressed as height of liquid column in meters, independent of fluid density. It represents the pump's ability to push fluid against elevation difference, friction, and pressure. A pump generating 50 meters of head can lift water 50 meters vertically, but the actual discharge pressure in psi depends on fluid density.

**Impeller**
Rotating component inside the pump fitted with curved vanes that accelerates fluid outward by centrifugal force. Fluid enters the impeller at the eye, the low-pressure zone at its center, and is thrown radially outward through the vanes. Impellers can be open, semi-open, or closed depending on whether they have front and rear shrouds.

**Mechanical seal**
Device that seals the rotating shaft where it passes through the stationary pump casing, preventing fluid from leaking out. Two precision-flat faces, one rotating with the shaft and one stationary, slide against each other with a microscopic film of fluid for lubrication. Compared to older gland packings, mechanical seals leak much less and require no adjustment.

**Motor-pump assembly**
Complete unit consisting of an electric motor connected to a pump through a coupling, mounted on a common baseplate. In water utility applications, this assembly typically includes a three-phase induction motor, flexible coupling, and centrifugal pump with suction and discharge flanges. The motor and pump shafts must be precisely aligned during installation to prevent vibration and bearing failure.

**Net Positive Suction Head (NPSH)**
Measure of the pressure available at the pump suction, relative to the fluid's vapor pressure, to prevent cavitation. The system provides NPSHa (available), and the pump requires NPSHr (required) as published by the manufacturer. If NPSHa drops below NPSHr, the pump will cavitate and sustain damage.

**Pump curve**
Graph published by the manufacturer showing how a pump's head, power consumption, efficiency, and NPSHr vary across its flow range at a fixed rotational speed. The head typically decreases as flow increases, forming a downward-sloping line. The curve is the pump's performance fingerprint and is used to select the right pump for a given system.

**Shaft**
Cylindrical component that transmits rotational power from the coupling through the pump casing to the impeller. It is supported by bearings and must be stiff enough to resist deflection under load. The shaft is sealed at the point where it passes through the casing to prevent leakage.

**Suction head**
Pressure measured at the pump inlet nozzle, expressed as height of liquid column. It can be positive when the liquid supply is above the pump centerline, or negative (suction lift) when the pump must pull liquid upward from a lower source. Suction conditions directly affect the pump's available NPSH and cavitation risk.

## Failure Mode and Monitoring Terms

**Air gap**
Physical clearance between the motor rotor and stator, typically 0.25 to 2.0 mm depending on motor size. This gap is critical for efficient magnetic flux transfer. Uneven air gap caused by bearing wear or shaft deflection creates unbalanced magnetic pull that increases vibration and accelerates bearing and stator winding damage.

**Angular misalignment**
Condition where the centerlines of motor shaft and pump shaft intersect at an angle rather than being collinear. The coupling must transmit torque while accommodating this angular offset, generating axial forces and bending moments. Vibration spectrum shows high axial vibration at 1x running speed with 180 degree phase difference measured axially across the coupling halves. Axial vibration amplitude typically exceeds radial vibration amplitude.

**Bearing**
Machine element that supports and locates the pump shaft relative to the stationary housing while allowing rotation. Two main types used in centrifugal pumps: rolling element bearings (ball, roller) for smaller pumps and moderate loads, and sleeve bearings (journal) for larger pumps and high radial loads. Bearing failure is the most common mechanical failure mode requiring pump removal from service.

**BEP deviation**
Difference between actual pump operating point and the published Best Efficiency Point flow, expressed as a percentage of BEP flow. Operating at 60% BEP means the pump runs at 40% deviation left of its design point. Deviation beyond 30% in either direction typically places the pump outside the Preferred Operating Region and accelerates wear.

**Current signature**
Time-domain or frequency-domain representation of motor current used for fault detection. In frequency domain, specific sideband patterns around the line frequency indicate rotor bar defects, eccentricity, and load oscillations. High-resolution current signature analysis at 2 kHz or higher sampling rate can detect electrical faults earlier than vibration analysis for some failure modes.

**Electrical Signature Analysis (ESA)**
Condition monitoring technique that analyzes voltage and current signals from the motor control center to detect mechanical and electrical faults without installing sensors on the pump or motor. Transformers, VFDs, and long cables between controller and motor can attenuate or distort the signal. Sensitivity requires the motor load to be steady during measurement.

**Harmonic distortion**
Deviation of voltage or current waveform from a pure sinusoid, quantified as Total Harmonic Distortion in percent of fundamental. IEEE 519-2014 limits voltage THD to 5% at the point of common coupling for systems below 69 kV, with individual harmonics below 3%. Harmonics generated by VFDs, nonlinear loads, and power system resonance cause additional heating in motor windings and rotor bars. NEMA MG-1 permits a voltage waveform deviation factor up to 10%, but sustained THD near that level reduces insulation life and accelerates thermal aging.

**Insulation class (F, H)**
Standardized temperature rating system for motor winding insulation materials defined by NEMA MG-1 and IEC 60085. Class F insulation is rated for 155 C hot-spot temperature with 105 C rise over 40 C ambient. Class H is rated for 180 C hot spot with 125 C rise. A motor rated Class F will fail prematurely if operated continuously above its temperature class limit.

**Insulation resistance**
DC resistance measured between motor windings and ground using a megohmmeter at 500 V or 1000 V, expressed in megohms. Per IEEE 43, minimum acceptable value for a motor winding is 1 Mohm per kV of rated voltage plus 1 Mohm, before temperature correction. A decreasing trend over successive measurements indicates moisture ingress, contamination, or insulation degradation.

**Minimum continuous stable flow**
Lowest flow at which a pump can operate continuously without experiencing damaging recirculation, excessive vibration, or temperature rise. Specified by the manufacturer based on pump specific speed and design. Operating below this flow requires a recirculation line or automatic minimum flow bypass valve to protect the pump.

**Motor winding**
Copper wire coils placed in the stator slots that carry current to produce the magnetic field that drives the rotor. Windings are insulated with varnish, enamel, and slot liners rated to a specific temperature class (F or H). The first few turns near the line terminal experience the highest voltage stress and are the most common location for incipient winding faults.

**NPSH margin**
Difference between NPSHa (available from the system) and NPSHr (required by the pump), expressed in meters. A margin of at least 0.5 to 1.0 m is recommended for safe operation. Margin below 0.5 m places the pump in the cavitation risk zone. Margin is dynamic, changing with fluid temperature, suction tank level, and strainer cleanliness.

**Parallel misalignment**
Condition where motor shaft and pump shaft centerlines are offset by a constant distance but remain parallel. The coupling must transmit torque while bridging this offset, generating radial forces that rotate with the shaft. Vibration spectrum shows dominant 2x running speed component in the radial direction, often with 1x and 3x harmonics present. Radial phase difference across the coupling is approximately 180 degrees.

**Partial discharge**
Localized electrical discharge that bridges only part of the insulation between conductors, occurring at voids or defects within the insulation system. Common in medium-voltage motors (1000 V and above). Sustained partial discharge erodes insulation material until complete breakdown occurs. Detection requires specialized high-frequency sensors and phase-resolved analysis.

**Recirculation**
Flow condition where a portion of the pumped fluid reverses direction inside the pump rather than moving from suction to discharge. Suction recirculation occurs at the impeller eye at low flow, causing pre-rotation and localized low-pressure zones. Discharge recirculation occurs at the impeller periphery at very low flow. Both cause pressure fluctuations, vibration, and damage similar to cavitation.

**Rotor bar**
Conductive bar embedded in the rotor core that carries induced current from the stator magnetic field. In squirrel cage induction motors, rotor bars are connected at both ends by shorting rings to form a closed circuit. Bars are typically aluminum in cast rotors or copper in fabricated rotors. Cracking or breakage at the bar-to-ring joint is a common failure mode in frequently started motors.

**Shaft misalignment**
Condition where the centerlines of motor shaft and pump shaft are not collinear within acceptable tolerances. Two components: parallel offset (radial displacement between shaft centerlines) and angular misalignment (angular deviation between shaft axes). Combined misalignment containing both components is the most common field condition. Motor and pump feet must be checked for soft foot before alignment adjustment.

**Stator**
Stationary part of the induction motor consisting of a laminated iron core with copper windings placed in axial slots. The stator core is pressed into the motor frame. Stator windings are the most failure-prone electrical component due to thermal, electrical, ambient, and mechanical (TEAM) stress factors. Stator core lamination shorts can cause local hot spots and winding damage.

**TEAM factors**
Acronym for the four stress categories that cause motor insulation degradation: Thermal (heat), Electrical (voltage stress, surges), Ambient (moisture, chemicals, contamination), and Mechanical (vibration, coil movement, thermal cycling). Every motor winding failure can be traced to one or more of these four factors. Root cause analysis should identify which TEAM factor was the primary driver.

**Thermal imaging**
Non-contact temperature measurement technique using an infrared camera to detect surface temperature patterns on motors, bearings, seals, and electrical connections. Hot spots on motor casing indicate winding overheating or blocked cooling passages. Temperature gradients across coupling indicate misalignment. Uneven bearing housing temperature indicates lubrication starvation or excessive preload.

**Vibration signature**
Frequency spectrum of vibration measured on pump or motor bearing housings, used to identify specific fault types by their characteristic frequency patterns. Running speed peaks indicate imbalance or misalignment. Bearing defect frequencies indicate raceway damage. Broadband elevated noise floor indicates cavitation or recirculation. Vibration signature should be collected at consistent operating points for trend comparison.