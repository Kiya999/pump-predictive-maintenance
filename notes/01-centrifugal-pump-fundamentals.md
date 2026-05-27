# Centrifugal Pump Fundamentals

## 1. Impeller Mechanics

- Fluid enters at impeller eye (center) axially
- Impeller vanes (curved blades) spin fluid outward via centrifugal force
- Kinetic energy (velocity) converts to pressure energy in volute (spiral casing)
- Higher rotational speed = higher pressure at discharge
- Absolute velocity of fluid leaving impeller = vector sum of tangential velocity and relative velocity along vane

| Component | Role |
|---|---|
| Eye | Low-pressure zone, draws fluid in |
| Vanes | Curved blades that impart angular momentum to fluid |
| Volute | Spiral shape, converts velocity head to pressure head via area expansion |
| Diffuser (multistage pumps) | Stationary vaned ring that recovers kinetic energy as pressure before next stage |
| Wear rings | Replaceable rings at impeller eye and casing to control internal leakage |
| Shaft sleeve | Protects shaft from wear at seal area |

| Stage | State |
|---|---|
| Suction inlet to Eye | Low pressure, low velocity |
| Across Vanes | Pressure increases, velocity increases |
| Volute to Discharge | Velocity decreases, pressure increases (Bernoulli recovery) |

Euler pump equation: H_theoretical = (u2 x v_u2 - u1 x v_u1) / g

where u = tangential blade velocity, v_u = tangential component of absolute velocity

Actual head is lower than theoretical due to:
- Hydraulic losses (friction, shock, recirculation)
- Slip factor (fluid does not follow vane angle perfectly at exit)
- Leakage losses through wear ring clearances

---

## 2. Pump Curves (Head vs Flow)

Head (H): Energy per unit weight of fluid (meters of liquid column) - independent of fluid density
Flow (Q): Volume per unit time (m3/h or gpm)

Pump curve shape: Head DECREASES as flow INCREASES (drooping characteristic)

System curve: Head LOSS increases with flow squared (parabolic: H_loss = k x Q^2)

| Term | Definition |
|---|---|
| Operating point | Intersection of pump curve and system curve; actual flow and head delivered |
| Shut-off head | Head at zero flow (pump running, discharge valve closed) |
| Run-out point | Maximum flow at minimum head (end of pump curve) |
| Flat curve | Small head change over wide flow range (good for variable demand) |
| Steep curve | Large head change per unit flow change (good for systems with high friction variation) |
| Drooping curve | Curve has a dip near shut-off; can cause unstable operation if two pumps in parallel |
| Stable curve | Head decreases continuously as flow increases (preferred) |

Pump curve obtained via test: ISO 9906 or Hydraulic Institute standards specify test methods and tolerances.

Multiple speeds produce a family of curves. Higher speed shifts curve up and to the right.

---

## 3. Best Efficiency Point (BEP)

- Flow rate where peak hydraulic efficiency occurs
- Typically 80-90% of flow at run-out, not a percentage of pump's maximum flow range. It is a single point on the H-Q curve, not a flow range.
- Design point: lowest internal losses, minimum radial load

| Problem | Cause | Mechanism |
|---|---|---|
| Radial thrust imbalance | Operating away from BEP | Asymmetric pressure distribution around volute |
| Shaft deflection | Operating away from BEP | Uneven radial loads bend shaft |
| Bearing wear | Operating away from BEP | Cyclic stress from shaft deflection |
| Vibration | Operating away from BEP | Flow separation, recirculation at impeller inlet/exit |
| Cavitation risk | Operating below BEP | Internal recirculation at low flow causes local pressure drop |
| Temperature rise | Operating near shut-off | Low flow, same power input heats fluid |

Rule: Select pumps so operating point falls within 70-110% of BEP flow

| Efficiency range (typical) | Pump size |
|---|---|
| 50-65% | Small pumps (under 5 HP) |
| 65-80% | Medium pumps (5-50 HP) |
| 80-88% | Large pumps (over 50 HP) |
| 88-93% | Very large engineered pumps (over 500 HP) |

---

## 4. Affinity Laws

For the SAME pump at DIFFERENT speeds (N = rotational speed):

| Law | Formula | Relationship |
|---|---|---|
| Flow | Q2 = Q1 x (N2 / N1) | Linear |
| Head | H2 = H1 x (N2 / N1)^2 | Quadratic |
| Power | P2 = P1 x (N2 / N1)^3 | Cubic |

| Speed change | Flow change | Head change | Power change |
|---|---|---|---|
| -10% (0.9x) | -10% | -19% | -27% |
| -20% (0.8x) | -20% | -36% | -49% |
| -30% (0.7x) | -30% | -51% | -66% |
| -50% (0.5x) | -50% | -75% | -88% |
| +10% (1.1x) | +10% | +21% | +33% |

Why Variable Frequency Drive (VFD) save energy: Power drops with cube of speed.

Caution: Affinity laws assume constant efficiency. At speeds below 30% rated, efficiency drops due to leakage losses dominating.

For impeller diameter changes (same speed):

| Law | Formula |
|---|---|
| Flow | Q2 = Q1 x (D2 / D1) |
| Head | H2 = H1 x (D2 / D1)^2 |
| Power | P2 = P1 x (D2 / D1)^3 |

Diameter trimming is always a cut-down from original. Laws are accurate for reductions up to 20-25% of original diameter. Beyond 20% trim, vane exit angle changes and efficiency drops; actual test curves are required.

---

## 5. Motor-Pump Assembly

| Step | Component | Notes |
|---|---|---|
| 1 | VFD | Optional; converts fixed AC to variable frequency and voltage |
| 2 | Motor | Typically 3-phase induction motor (squirrel cage rotor) |
| 3 | Coupling | Flexible or rigid; flexible allows misalignment up to 0.005 in |
| 4 | Pump Shaft | Supported by bearings; diameter sized for torque and deflection |
| 5 | Impeller | Open, semi-open, or enclosed design |
| 6 | Volute | Single or double volute for radial thrust balance |
| 7 | Discharge | Flanged connection to piping |

| Component | Function |
|---|---|
| Motor | Provides rotational power (typically NEMA or IEC frame induction motor) |
| Coupling | Transmits torque, absorbs minor misalignment and axial thermal growth |
| Pump shaft | Transmits rotation to impeller; sized for critical speed margin |
| Mechanical seal | Two flat faces (rotating vs stationary) with thin fluid film; prevents leakage |
| Packing gland | Alternative to seal; uses braided rope compressed around shaft, requires leak for lubrication |
| Bearings | Ball bearings (radial) or angular contact (axial / thrust); grease or oil lubricated |
| Baseplate | Steel frame with machined mounting surfaces; anchors to foundation |
| Back pull-out feature | Allows removing rotating assembly without disturbing piping (standard in ANSI pumps) |

| Water utility component | Purpose | Location |
|---|---|---|
| Suction isolation valve | Allows pump removal without draining suction piping | Between suction source and pump |
| Check valve on discharge | Prevents backflow through idle pump | On discharge piping, after pump |
| Discharge isolation valve | Allows pump servicing without draining discharge piping | After check valve |
| Pressure gauges | Monitor suction and discharge pressure | On suction and discharge nozzles |
| Flow meter | Measure flow rate | On discharge line |
| VFD | Speed control for energy savings and process control | Between power supply and motor |
| Air release valve | Removes air from casing at startup | Top of volute |
| Drain plug | Drains pump for maintenance | Bottom of volute |

---

## 6. System Curve Components

Total system head = static head + friction loss + pressure head

| Component | Behavior | Equation |
|---|---|---|
| Static head | Elevation difference between suction and discharge liquid levels | H_static = Z_discharge - Z_suction |
| Friction loss | Increases with Q^2; pipe length, diameter, roughness, fittings, valves | H_friction = k x Q^2 |
| Pressure head | Any back-pressure in system (tank pressurization, closed loop) | H_pressure = (P_tank) / (rho x g) |

System curve: H_system = H_static + k x Q^2

| Changing condition | Effect on k | Effect on H_static |
|---|---|---|
| Valve opening | Decreases k | None |
| Valve closing | Increases k | None |
| Pipe fouling over time | Increases k | None |
| Parallel pump added | Each pump sees same system curve | None |
| Additional fittings added | Increases k | None |

Series pumps: Total head = sum of individual heads at same flow. Used for high head applications.
Parallel pumps: Total flow = sum of individual flows at that head. Each pump operates at the same head determined by the system curve.

---

## 7. NPSH (Net Positive Suction Head)

| Term | Definition |
|---|---|
| NPSHa (available) | Absolute pressure at pump suction minus vapor pressure of fluid at pumping temperature |
| NPSHr (required) | Minimum NPSH needed to prevent cavitation; published by manufacturer |
| NPSH margin | NPSHa minus NPSHr; minimum recommended = 0.5 to 1.0 m (varies by application) |

Cavitation prevention rule: NPSHa > NPSHr

| NPSHa component | Symbol | Notes |
|---|---|---|
| Atmospheric pressure | P_atm | 10.33 m of water at sea level; decreases with altitude |
| Static suction head | H_static_suction | Positive if liquid level is above pump centerline (flooded suction); negative if below (lift condition) |
| Suction friction loss | H_friction_suction | Depends on suction pipe size, length, fittings; larger pipe reduces loss |
| Vapor pressure | P_vapor | Increases with fluid temperature; boiling point = NPSHa approaches zero |

Formula: NPSHa = P_atm + H_static_suction - H_friction_suction - P_vapor (all in meters of head)

Note: For a closed suction tank under pressure, replace P_atm with the absolute pressure (gauge pressure + atmospheric) in the tank.

NPSHa - NPSHr = NPSH margin

| Cavitation stage | Observable symptoms |
|---|---|
| Incipient | Tiny bubbles form; no performance loss; crackling sounds |
| Developed | Bubbles collapse violently; noise, vibration, head drop |
| Severe | Impeller pitting, blade erosion, bearing damage, catastrophic failure |

Design rules:
- Keep suction pipe at least one size larger than pump suction nozzle
- Minimize fittings and valves on suction side
- Keep suction line length as short as possible
- Avoid high points where air can pocket in suction piping
- Hot water requires larger NPSH margin (higher vapor pressure)

---

## 8. Pump Types Comparison

| Type | Head range | Flow range | Specific speed range | Best for |
|---|---|---|---|---|
| Single-stage centrifugal | Low-med (up to 100 m) | Med-high (10-10000 m3/h) | 500-3000 | Water supply, HVAC, irrigation |
| Multistage centrifugal | High (100-2000 m) | Low-med (1-500 m3/h) | 500-1500 | Boiler feed, high-rise buildings, reverse osmosis |
| End suction (ANSI) | Low-med (up to 150 m) | Med (1-2000 m3/h) | 500-2500 | General industrial, chemical processing |
| Split case (horizontal) | Med (up to 200 m) | High (100-100000 m3/h) | 1000-3000 | Large water utilities, cooling water |
| Vertical turbine | Med-high (up to 500 m) | Med (1-5000 m3/h) | 1000-4000 | Wells, reservoirs, deep pits |
| Self-priming | Low-med (up to 50 m) | Med (1-500 m3/h) | 1000-2000 | Intermittent service, portable pumps |
| Axial flow (propeller) | Low (under 15 m) | Very high (1000-100000 m3/h) | 4000-10000 | Drainage, low head irrigation |
| Mixed flow | Low-med (up to 30 m) | High (100-10000 m3/h) | 3000-6000 | Stormwater, large volume low head |

Specific speed (ns): characteristic coefficient derived from similarity conditions that allows comparison of impellers of different sizes.

ns = N x sqrt(Q) / H^(3/4)

where N in rpm, Q in m3/s, H in m. For double-entry impellers, use Q for one impeller half. The dimensionless alternative (ns*) uses rad/s for N and includes g.

| ns range | Impeller type |
|---|---|
| Under 2000 | Radial flow (centrifugal) |
| 2000-4000 | Mixed flow (diagonal) |
| Over 4000 | Axial flow |

Conversion between unit systems: Ns (US) = ns x 51.6, K (dimensionless) = ns / 52.9

---

## 9. Key Equations Summary

| Quantity | Formula | Units | Notes |
|---|---|---|---|
| Hydraulic power | P_h = rho x g x Q x H | Watts | Power transferred to fluid |
| Shaft power | P_s = P_h / eta | Watts | Power drawn by pump from motor |
| Efficiency | eta = P_h / P_s x 100% | % | Typically 60-90% |
| Motor power input | P_e = P_s / eta_motor | Watts | Electrical power drawn from grid |
| Specific speed | ns = N x sqrt(Q) / H^(3/4) | dimensionless | N in rpm, Q in m3/s, H in m |
| Suction specific speed | S = N x sqrt(Q) / NPSHr^(3/4) | dimensionless | High S (over 200) = wider operating range |
| Affinity law Q | Q2 = Q1 x (N2 / N1) | m3/s or gpm | Same impeller, different speed |
| Affinity law H | H2 = H1 x (N2 / N1)^2 | m or ft | |
| Affinity law P | P2 = P1 x (N2 / N1)^3 | W or hp | |
| Affinity law Q (diameter) | Q2 = Q1 x (D2 / D1) | m3/s or gpm | Same speed, trimmed impeller |
| Affinity law H (diameter) | H2 = H1 x (D2 / D1)^2 | m or ft | |
| Affinity law P (diameter) | P2 = P1 x (D2 / D1)^3 | W or hp | |
| Euler head | H_th = (u2 x v_u2 - u1 x v_u1) / g | m | Theoretical head from momentum transfer |
| NPSHa | NPSHa = P_atm + H_static_suction - H_friction_suction - P_vapor | m | All terms in meters of fluid head |
| System curve | H_sys = H_static + k x Q^2 | m | k = friction coefficient |
| Pump total head | H = (P_discharge - P_suction) / (rho x g) + (v_d^2 - v_s^2) / (2 x g) + (Z_d - Z_s) | m | Measured from pressure gauges |

Unit conversions:
- 1 m head = 9.81 kPa (for water)
- 1 HP = 746 W
- 1 m3/h = 4.403 gpm
- 1 m = 3.281 ft
- rho_water = 1000 kg/m3 at 4 deg C
- g = 9.81 m/s2

---

## 10. Common Mistakes to Avoid

| Mistake | Consequence | Prevention |
|---|---|---|
| Selecting pump based on max efficiency alone | NPSHr may exceed NPSHa at BEP; cavitation guaranteed | Always verify NPSHa > NPSHr at operating flow |
| Operating pump with discharge valve closed for long periods | Fluid heats up, can boil inside casing; seal damage | Install minimum flow recirculation line |
| Ignoring minimum flow requirements | Recirculation at impeller inlet causes noise, vibration, erosion | Use minimum flow bypass line |
| Parallel pumps without check valves | Backflow through idle pump spins it backward | Install individual check valves on each pump discharge |
| Oversizing pump | Operates far left of BEP; high radial load, vibration, premature bearing failure | Select pump so operating point is 70-110% of BEP flow |
| Confusing pump head with pressure | Head is independent of fluid density; pressure = rho x g x H. A pump produces same head for water or oil, but different pressure | Always think in head, not pressure |
| Suction pipe smaller than pump suction nozzle | High friction loss lowers NPSHa; cavitation risk | Suction pipe should be at least same size, preferably one size larger |
| Neglecting altitude correction | Above sea level, atmospheric pressure is lower; NPSHa drops | Subtract correction: 1.2 m per 100 m elevation |
| Installing pump above liquid level without foot valve | Pump loses prime; air enters suction line | Use foot valve or self-priming pump; ensure flooded suction where possible |
| Running pump at run-out (max flow) for extended periods | High vibration, high power draw, low efficiency, cavitation at impeller exit | Stay within manufacturer's recommended operating range |
| Ignoring specific speed in pump selection | Wrong geometry for application; low efficiency, narrow operating range | Select pump type based on ns range for your Q and H |
| Using affinity laws for large diameter trims | Beyond 20% trim, vane exit angle changes; laws inaccurate | Use actual test curves for trimmed impellers |

---

## Terminology Reference

### Fluid Mechanics and Impeller Concepts

| Term | Definition |
|------|------------|
| **Absolute velocity** | The velocity of the fluid as seen by a stationary observer outside the pump. It is the vector sum of the tangential velocity (from impeller rotation) and the relative velocity (fluid motion along the vane). Understanding this vector addition is essential for applying the Euler pump equation |
| **Relative velocity** | The velocity of the fluid relative to the rotating impeller vane. It represents how the fluid moves along the vane surface as the impeller spins beneath it |
| **Tangential velocity (u)** | The velocity of the impeller vane at a given radius, equal to rotational speed times radius (u = omega x r). It varies from zero at the shaft centerline to maximum at the vane tip. This is the "u" term in the Euler pump equation |
| **Angular momentum** | The rotational equivalent of linear momentum, equal to mass times tangential velocity times radius. The Euler pump equation is derived from the change in angular momentum of the fluid as it passes through the impeller. The impeller imparts angular momentum to the fluid, which then converts to pressure in the volute |
| **Slip factor** | A correction factor accounting for the fact that fluid does not follow the vane angle perfectly at the impeller exit. Due to relative eddies between the vanes, the actual tangential velocity at exit is lower than the ideal value calculated from the vane angle. This reduces the actual head below the Euler theoretical head |
| **Bernoulli's principle** | A fluid mechanics principle stating that as the velocity of a fluid decreases, its pressure increases, assuming no energy is added or removed. In the volute, the expanding cross-section slows the fluid, converting its velocity energy into pressure energy. This is called Bernoulli recovery |
| **Hydraulic losses** | Energy dissipated within the pump that does not contribute to useful head. Three main types: friction losses (fluid rubbing against surfaces), shock losses (flow impacting vanes at off-design conditions), and recirculation losses (fluid flowing backward through clearances). These losses are why actual head is lower than theoretical head |

### Pump Testing and Standards

| Term | Definition |
|------|------------|
| **ISO 9906** | An international standard that specifies test methods for hydraulic performance tests of centrifugal, mixed flow, and axial flow pumps. It defines acceptance grades (1, 2, or 3) with different tolerance bands for head, flow, and efficiency. Grade 1 is the tightest tolerance, used for high-performance or contractually critical pumps |
| **Hydraulic Institute (HI)** | A North American trade association that develops pump standards (ANSI/HI series). Their standards cover pump testing, design, installation, operation, and maintenance. HI 9.6.3, referenced elsewhere, governs operating regions for centrifugal pumps |
| **NEMA** (National Electrical Manufacturers Association) | A US standards organization that defines motor frame sizes, electrical ratings, and performance characteristics (NEMA MG-1). NEMA motors are common in North America and are dimensionally different from IEC motors. They typically have larger frames and different mounting patterns |
| **IEC** (International Electrotechnical Commission) | An international standards organization that defines motor frame sizes and ratings used outside North America. IEC motors have metric dimensions and different power-to-frame-size relationships than NEMA motors. Understanding which standard applies is important for motor replacement and coupling selection |
| **ANSI pumps** (ASME B73.1) | A standard for horizontal end-suction centrifugal pumps used in chemical process industries. These pumps have standardized dimensions for the baseplate, shaft height, flange locations, and seal cavity. This standardization allows interchangeability between manufacturers without modifying piping |

### Pump Construction and Installation

| Term | Definition |
|------|------------|
| **Packing gland** | An alternative to mechanical seals that uses braided rope-like material (packing) compressed around the shaft by a gland follower. It requires a small controlled leak for lubrication and cooling. Packing is lower cost than mechanical seals but requires periodic adjustment and leaks more visibly. It is still common in older pumps and slurry services |
| **Back pull-out design** | A maintenance feature in which the entire rotating assembly (motor, coupling bracket, shaft, impeller, and bearing housing) can be pulled backward away from the pump casing without disturbing the suction and discharge piping. This is a standard feature in ANSI B73.1 pumps and significantly reduces maintenance downtime |
| **Flexible coupling** | A device connecting motor and pump shafts that transmits torque while accommodating small amounts of parallel misalignment, angular misalignment, and axial thermal growth. Common types include elastomeric (rubber element, most common), grid (spring steel grid, handles shock loads), and disc (metal disc pack, handles high speeds). The coupling does not correct large misalignment; that must be achieved during shaft alignment |
| **Critical speed** | The rotational speed at which the pump shaft's natural frequency coincides with the operating speed, causing resonance and large vibration amplitudes. Pumps are designed so that the operating speed is below the first critical speed (stiff shaft design) or above it with sufficient margin (flexible shaft design). Operating at or near critical speed causes rapid bearing and seal failure |
| **Baseplate** | A steel frame that supports the motor and pump assembly and anchors it to a concrete foundation. The baseplate must be leveled and grouted during installation to prevent distortion when bolted down. Uneven mounting (soft foot) distorts the pump and motor frames, causing misalignment even if the shafts were aligned before bolting |
| **Flooded suction** | A suction condition where the liquid source is located above the pump centerline, so liquid flows into the pump by gravity. This provides positive pressure at the suction nozzle, resulting in higher NPSHa and lower cavitation risk. It is the preferred suction arrangement when site conditions allow |
| **Suction lift** | A suction condition where the liquid source is located below the pump centerline, so the pump must pull liquid upward. This creates negative pressure (vacuum) at the suction nozzle, reducing NPSHa. Each meter of static lift reduces NPSHa by approximately one meter. Suction lift should be avoided whenever possible |
| **Foot valve** | A check valve installed at the bottom of a suction pipe that hangs downward into a liquid source. It allows water to flow upward into the suction pipe but prevents it from draining back when the pump stops. This keeps the suction pipe and pump casing primed (filled with liquid) so the pump can restart without manual priming |
| **Priming** | The process of filling the pump casing and suction pipe with liquid before startup. A centrifugal pump cannot pump air; it must be filled with liquid to develop suction. Priming methods include flooded suction (self-priming by gravity), foot valves (holding prime), vacuum pumps, and self-priming pump designs (which recirculate water to evacuate air) |

### Monitoring and Control

| Term | Definition |
|------|------------|
| **Variable Frequency Drive (VFD)** | An electronic device that controls motor speed by varying the frequency and voltage supplied to the motor. Because pump power varies with the cube of speed (affinity laws), reducing speed with a VFD saves significantly more energy than throttling a discharge valve. VFDs also provide controlled acceleration, reducing mechanical stress during startup |
| **Minimum flow recirculation line** | A bypass pipe that returns a portion of the pump discharge back to the suction source to maintain flow through the pump even when the main discharge valve is closed or partially closed. This prevents overheating, recirculation damage, and cavitation at low flow conditions. The line typically includes an orifice plate or control valve sized for the required minimum flow |
| **Suction specific speed (S)** | A dimensionless parameter (S = N x sqrt(Q) / NPSHr^(3/4)) that characterizes the suction capability of a pump impeller. High values of S (above 200 in US units, above 2.7 in dimensionless) indicate a wider operating range before recirculation begins, but also increase the risk of suction recirculation at low flows. It is used to evaluate how tolerant a pump is to operation away from BEP |

### Power and Efficiency Concepts

| Term | Definition |
|------|------------|
| **Hydraulic power** | The power actually transferred to the fluid, calculated as P_h = rho x g x Q x H. This is the useful output of the pump. It does not account for any internal losses within the pump or motor |
| **Shaft power** (or Brake power) | The mechanical power delivered to the pump shaft by the motor, calculated as P_s = P_h / eta. This is higher than hydraulic power because it includes the pump's internal losses (bearing friction, disk friction, leakage, hydraulic losses). The pump efficiency eta accounts for all these losses |
| **Motor power input** | The electrical power drawn from the power grid, calculated as P_e = P_s / eta_motor. This is higher than shaft power because it includes motor losses (copper losses, iron losses, friction and windage, stray load losses). The ratio of hydraulic power to motor input power is called wire-to-water efficiency |
| **Wire-to-water efficiency** | The overall efficiency from the electrical supply to the hydraulic output, calculated as eta_overall = P_h / P_e. This includes pump losses, motor losses, and VFD losses if present. A typical wire-to-water efficiency for a medium-sized pump-motor system operating at BEP is 65-80%. It is the most meaningful efficiency metric for energy cost analysis |

---
