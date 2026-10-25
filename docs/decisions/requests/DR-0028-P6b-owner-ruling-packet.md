# DR-0028 P6(b): owner scope-ruling packet (GMAT's reported axis in a validator)

**Status:** PREPARED FOR OWNER RULING. **Nothing here is decided.** DR-0028's Resolution, including "No additional Earth-orientation implementation is authorized", is unchanged.  
**Prepared under:** "TARS — Authorization I-26: M3 Owner Decision Recording, Gate Amendment, and T2 Authorization Preparation" (owner/Tech Lead, 2026-10-25), §2 P6: "Do not silently decide DR-0028 P6(b). Prepare a separate, explicit owner ruling on whether driving the validator with GMAT's reported axis is within the previously approved Earth-orientation scope."  
**Date:** 2026-10-25  
**Related:** DR-0028 Resolution and "T0 note"; DR-0029 P6 (method (d) PROVISIONALLY SELECTED; register P6-U4, P6-U5); DR-0025 Q-G2-1; `docs/milestones/M3-decision-matrix.md`, DR-0028 rows.

## 1. Question for the owner
Is driving a **validator** reference (validation code, never the simulator) with GMAT R2026a's reported Earth-fixed +Z axis **inside** the Earth-orientation scope approved in DR-0028, or **outside** it?

## 2. The recorded scope
- DR-0028 Resolution, decision A (J-ax-1): the model's +Z is fixed in the M3 inertial frame by assumption. R-1: "No time-dependent Earth orientation, precession, nutation or polar motion".
- DR-0028 Resolution, last row: "**No additional Earth-orientation implementation is authorized**" (NOT AUTHORIZED). The planning matrix records it as "Any additional Earth-orientation implementation (rotation angle, pole of date, EOP)" (I-3 §2, §7). A second row adds "Solar ephemeris, Earth-orientation provider, local-solar-time output" (I-4 §1).
- **Neither text says whether the prohibition covers validation code or only the simulator.** That is the gap this ruling closes.

## 3. What option (b) would put in a validator (DR-0029 P6, T0 evidence)
- **Source:** GMAT's axis-probe report (two point-mass spacecraft on non-coplanar orbits, reported in GMAT TOE and GMAT EarthFixed). One orbit plane leaves the out-of-plane component undetermined.
- **Model:** a least-squares fit u(t) = Σ c_k φ_k with φ = [1, t/t_end, (t/t_end)², cos ω_E t, sin ω_E t] (15 unknowns). Without the diurnal pair the fit leaves 0.986 m RMS; with it, 7.8e-5 m.
- **Use:** the validator's J2 and ellipsoid are evaluated about the time-dependent fitted pole u(t), so the J2 link compares like with like.
- **Result [measured, T0]:** GMAT against the spike driven by GMAT's axis, J2 only, `NutationUpdateInterval` = 0: **0.076 mm**. Under J-ax-1: 0.192 m final and 1.03 m maximum.
- **Dependencies:** GMAT's EOP file (sha256 `52c95d68…`, data to 2026-09-14). A different EOP file gives a different axis.
- **The simulator is untouched:** it stays J-ax-1 under every option below.

## 4. Options
| | R-a: inside scope | R-b: outside scope | R-c: outside the current scope, but granted as a narrow explicit extension |
|---|---|---|---|
| Ruling | (b) is GMAT output consumed as data, not an Earth-orientation implementation | The prohibition covers any time-dependent pole wherever it is coded | The prohibition is read as covering validators. The owner grants a stated exception |
| J2 link in T5 | (b), 0.076 mm class | (a), with a derived Earth-orientation bound still to be written (J-ax-1 residuals 0.19–0.58 m final, ≤ 1.08 m maximum), or (c) informational | (b), only within the exception's conditions |
| Boundary | Weakest. A fitted time-dependent pole exists in the repository under an interpretation, not a decision | Strongest. No orientation model anywhere | Explicit. The orientation code exists, but only where the exception allows it, and the exception is recorded |
| Cost | Lowest | The (a) bound needs a derivation (the interval-0 geodetic part is not yet bounded), and the J2 link stays at the decimetre level | One more recorded decision; the conditions must be checked in T5 review |
| Possible conditions (for R-c; none proposed as decided) | — | — | Validator side only (`tars.validation` or `toolbox/`), never `tars.sim`. The axis is derived only from committed GMAT output, with the report and EOP digests recorded. Two non-coplanar orbits, with the diurnal term. The fit residual is reported. The J2 link only, never the geodetic-drag link (P6-U1 … P6-U3 stay escalated). Labelled as a GMAT-matched diagnostic configuration, not as a terrestrial frame (DR-0028 R-2) |

## 5. Implementer's recommendation [judgment]
- **R-c if the owner wants an exact J2 link in T5; otherwise R-b.**
- Not R-a. The DR-0028 prohibition was written broadly ("any additional Earth-orientation implementation … pole of date"). A fitted, time-dependent pole is that kind of implementation, whatever directory it lives in. Ruling it inside scope by interpretation would leave the boundary unclear for later work. R-c gets the same technical benefit, and keeps the boundary explicit and reviewable.
- **Confidence:** medium. This is a scope and governance question, not a physics question; the technical facts above are measured.

## 6. What the ruling affects
- **Affects:** P6-U4 and P6-U5 (DR-0029 P6), the T5 J2 GMAT link.
- **Does not affect:** T2, T3 or T4; the simulator's frame (J-ax-1 under every option); P6-U1 … P6-U3 (the geodetic-drag escalation), which no option resolves; X-1 (NOT AUTHORIZED).
- **Requested response:** R-a, R-b or R-c (with its conditions), or `discuss`.
