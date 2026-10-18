### M3P4-F1 — Pole tilt does not bound ascending-node error
**Severity:** MINOR  
**Category:** Physical correctness  
**Where:** `docs/decisions/requests/DR-0028-m3-earth-fixed-frame-realization.md:74`, “Approximation and limitations”  
**Claim:** The new statement that “node and inclination geometry relative to the true equator are offset by up to the pole offset” gives an incorrect bound for the ascending node.

**Evidence:** Inclination differences from changing the reference pole are bounded by the pole separation; ascending-node longitude differences are not. Independently computed using a common x axis:

```text
Orbit normal h = (sin 30°, 0, cos 30°)
Reference transformation = Rx(−0.15°)
Original ascending-node longitude = 90°
Transformed longitude = 90.2598055437°
Difference = 0.2598055437° > 0.15°
```

Near equatorial orbits, node longitude becomes especially sensitive to the reference pole. [JPL’s orbital-element documentation](https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/FORTRAN/spicelib/oscltx.html) likewise identifies the near-equatorial node singularity.

**Suggested resolution:** Distinguish reference-pole separation, inclination difference, and ascending-node error. Remove the pole-offset bound for the node; describe accumulated trajectory errors as configuration- and duration-dependent.

### M3P4-F2 — Local solar time does not inherently require an Earth rotation angle
**Severity:** MINOR  
**Category:** Physical correctness  
**Where:** `docs/decisions/requests/DR-0028-m3-earth-fixed-frame-realization.md:75`, “No longitude, no ground position”; corresponding SCI-0013 status update 2  
**Claim:** The new limitations text incorrectly makes an Earth rotation angle a prerequisite for local solar time.

**Evidence:** For consistently defined equatorial right ascensions, the solar hour angle at the spacecraft’s subpoint is

```text
λ − λSun = (αspacecraft − θ) − (αSun − θ)
         = αspacecraft − αSun
```

The Earth rotation angle cancels. At the ascending node:

```text
Local solar time = [12 h + (Ω − αSun)/(15°/h)] modulo 24 h
```

A solar ephemeris, time convention, and consistent equatorial reference are needed. A terrestrial longitude is not inherently needed. NASA’s [Mean Local Time of the Ascending Node study, §II](https://ntrs.nasa.gov/api/citations/20080012667/downloads/20080012667.pdf) defines that quantity through the angle between the ascending node and the mean Sun.

M3 does not currently authorize this output, but the stated mathematical reason for excluding it is inaccurate.

**Suggested resolution:** Keep local-solar-time outputs outside M3 scope, while identifying the missing solar/time conventions rather than asserting that an Earth rotation angle is indispensable. Preserve the valid restrictions on terrestrial longitude, geographic ground tracks, and site visibility.

## Summary

**REQUEST_CHANGES** — two MINOR findings; no BLOCKER or MAJOR findings.

Reviewed snapshot: `a97c02fcdb7b0c17400969fda95cc47c438cd1ca`; correction commit: `58f0d18`.

Verified:

- **Scope:** `git diff d92ab89..HEAD --stat` and `--name-only` show **42 files, all under `docs/`**. No changes to production code, tests, scenarios, frozen artifacts, thresholds, goldens, references, or CI configuration. No merge or M3 implementation appears in the reviewed changes.
- **Historical preservation:** Python byte comparisons against `git show` confirm the withdrawn Q4 row matches `23bafd2` exactly after removing Markdown block indentation (**558 bytes**). Revision 1 is unchanged. The abbreviated-quotation replacement is explicitly disclosed.
- **Earlier reviews:** Read all three review records and raw outputs in full. M3P-F1…F5 remain ACCEPTED/corrected; M3P2-F1 remains ACCEPTED with owner resolution; M3P2-F2 remains REJECTED_WITH_REASONING with the prompt correction; M3P2-F3 remains ACCEPTED/corrected; M3P3-F1/F2 remain ACCEPTED with appended resolutions. Earlier record bytes remain preserved.
- **Registers:** Baseline lines remain unchanged: assumptions **208 additions / 0 deletions**; validation **43 / 0**. SCI-0005 and VAL-0007 correction notes remain intact.
- **Mathematics:** Verified `v_B = Rv_A + Ṙr_A`, its angular-velocity reduction, and the identity case. FC-10’s tilted-axis example produced `(0,0,−1)`, versus zero when the derivative is omitted and `(1,0,0)` from the fixed-z shortcut; finite-difference error was **1.67×10⁻¹¹**. No improperly dropped revision-1 requirement was identified.
- **Physics:** J-ax-1 is coherent; atmospheric co-rotation remains air motion with the pinned rate. Sampled J2 covariance and geodetic-height invariance errors were **2.00×10⁻¹⁵ m/s²** and **1.86×10⁻⁹ m**.
- **Atmosphere:** All **27** boundary jumps recomputed within **1.11×10⁻¹⁶**. The residual-consequences script reproduced its committed JSON byte-for-byte.
- **Decisions:** Approvals and OPEN/DEFERRED items remain distinguished, including the listed DR-0027 items, G2 deferrals, Q9 values, unauthorized telemetry, and unauthorized Earth-orientation implementation. Constants, retention rules, T0 checkpoint obligations, and T1/T2 restrictions remain represented. ADR-0009 item 17 is design evidence only.
- **Local validation:** M1 Proof **7/7**, M2 Proof **228/228**, both committed GMAT comparisons, M1 determinism, and golden comparison passed; golden position/velocity differences were zero. Ruff lint and formatting passed. Full pytest was interrupted after **262 passed in 173.02 s**; it was not completed.
- **CI limitation:** `gh run list --repo guillermoMartin96/tars --commit 8496ac1 …` failed to connect to GitHub. Individual remote-job conclusions and the three-platform CI gate were not independently verified.

**The planning branch is not ready to be presented to the Tech Lead for planning-checkpoint acceptance as documentation evidence until the two MINOR inaccuracies are resolved.**