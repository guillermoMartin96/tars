# M3 planning decision matrix

**As of:** 2026-10-17, eleventh planning checkpoint (review 11 corrections M3P11-F1 and M3P11-F2; no decision changed). Earlier: 2026-10-17, tenth planning checkpoint (review 10 correction M3P10-F1 and classification of the 18 assertions for M3P10-F2; no decision changed). Earlier: 2026-10-17, ninth planning checkpoint (review 09 corrections M3P9-F1/F2 and E3/E4 coverage for M3P9-F3; no decision changed). Earlier: 2026-10-16, eighth planning checkpoint (review 08 correction M3P8-F1; no decision changed). Earlier: 2026-10-16, seventh planning checkpoint (review 07 correction M3P7-F1; no decision changed). Earlier: 2026-10-16, sixth planning checkpoint (review 06 corrections M3P6-F1..F3; no decision changed). Earlier: 2026-10-16, fifth planning checkpoint (review 05 correction M3P5-F1; no decision changed). Earlier: 2026-10-16, fourth planning checkpoint (review 04 corrections M3P4-F1/F2; no decision changed). Earlier: 2026-10-15, third planning checkpoint (after review 03 and the DR-0028 decision). Earlier statuses that changed are shown as "was → now". This is an index: each Decision Request's Resolution is authoritative, and this file only points to it. Nothing here is implemented.

**Status labels:**
- **APPROVED:** owner decision.
- **APPROVED w/ constraints:** owner decision with conditions attached.
- **OPEN:** not decided.
- **DEFERRED:** decided later, at a named point.
- **T0 → owner:** proposed and validated at T0, then decided by the owner.
- **NOT AUTHORIZED:** explicitly not permitted.

No OPEN or DEFERRED item has a default.

**Instruction sources:**
- **I-1:** "M3 planning decision checkpoint" (Tech Lead, 2026-10-15), sections 1–8.
- **I-2:** "M3 planning checkpoint continuation" (Tech Lead, 2026-10-15), sections 1–7.
- **I-3:** "M3 Planning — Resolve Review 03 and DR-0028" (Tech Lead, 2026-10-15), sections 1–8.
- **I-4:** "M3 Planning — Review 04 Corrections and Final Verification" (Tech Lead, 2026-10-16), sections 1–7.
- **I-5:** "M3 Planning — M3P5-F1 Correction and Review 06" (Tech Lead, 2026-10-16), sections 1–7.
- **I-6:** "Continue M3 planning on `milestone-3-planning` from commit `dcabcb2`" (Tech Lead, 2026-10-16), sections 1–6.
- **I-7:** "Continue the TARS spacecraft simulator M3 planning work from branch `milestone-3-planning`, currently at commit `0dac6d3`" (Tech Lead, 2026-10-16), sections 1–6.
- **I-8:** "Continue TARS M3 planning from `milestone-3-planning` at `0ac630b`" (Tech Lead, 2026-10-16), sections 1–8.
- **I-9:** "I-9 — M3 Planning Verification Hardening and Codex Review 10" (Tech Lead, 2026-10-17), sections 1–10.
- **I-10:** "I-10 — Resolve M3P10-F1 and authorize Review 11" (Tech Lead, 2026-10-17), sections 1–10.
- **I-11:** "I-11 — Resolve Review 11 Findings and Authorize Review 12" (Tech Lead, 2026-10-17), sections 1–10.

## DR-0024: G1 physical models and constants
| Item | Decision | Status | Source | Also recorded in |
|---|---|---|---|---|
| Q1 | J2 = 1.0826261739e-3, EGM2008 tide-free | APPROVED | I-1 §1 | SCI-0013 |
| Q2 | J2 reference radius = WGS 84 a; stop condition checked, not met (§3.5) | APPROVED | I-1 §1 | SCI-0013 |
| Q3 | GM = WGS 84 3.986004418e14; SCI-0005 historical correction note | APPROVED; note added | I-1 §1, §4 | SCI-0005 (appended note) |
| Q4 | Earth-fixed +Z is the common axis of J2, the ellipsoid and atmosphere rotation; Earth-fixed and inertial representations distinct; correct transformations; conventions and tests FC-1…FC-9 recorded | APPROVED w/ constraints | I-2 §1 | SCI-0013/0014/0017 status updates; ADR-0009 item 14 |
| Q4 realization | J-ax-1: a non-rotating Earth-axis-aligned model; +Z coincides with the spin axis by assumption and is fixed in the inertial frame; identity transformation (zero derivative); no Earth rotation angle; not a terrestrial frame. Conventions revision 2, FC-1…FC-10 | was OPEN → **APPROVED** | I-3 §2, §3 | DR-0028; SCI-0013/0014/0017 status update 2; ADR-0009 item 17 |
| Q5 | Piecewise Vallado/GMAT table (A2); one-band subset retained for tests; A4 deferred | APPROVED | I-1 §1 | SCI-0015 |
| Q5a | Values preserved as published; discontinuities documented, quantified, tested at every boundary | APPROVED | I-1 §1 | SCI-0015; DR-0025 principle 5 |
| Q6 | Density height = geodetic, WGS 84 | APPROVED | I-1 §1 | SCI-0017 |
| Q7 | v_rel = v − ω_E × r, ω_E = 7.292115e-5 rad/s | APPROVED | I-1 §1 | SCI-0014 |
| Q8 | No indefinite extrapolation below the domain; explicit boundary and termination event | APPROVED (principle) | I-1 §1 | DR-0027 A |
| Q9 | C_d, A, initial mass, initial state are explicit scenario inputs | APPROVED (principle); values DEFERRED to T0 checkpoint | I-1 §1 | SCI-0016 |
| Q10 | Verified against the author's data file and errata; 25/28 identical; printed table not checked | Verification done; dataset CONDITIONALLY APPROVED | I-1 §1; I-2 §2 | DR-0027 B |
| — | Constants are pinned physics configuration; drag uses current total mass | APPROVED | I-1 §1 | DR-0026; ADR-0009 |

## DR-0025: G2 validation strategy
| Item | Decision | Status | Source |
|---|---|---|---|
| Principles 1–9 | Evidence classes; GMAT independence conditions; DOP853 partially independent; no blind M2 order rule; discontinuity-appropriate evidence; dt = 10 s provisional; no thresholds in planning; M1/M2 exact reproduction; VAL-0007 note | APPROVED | I-1 §2 |
| Q-G2-1 | GMAT exact-configuration method | DEFERRED (T0 checkpoint) | I-1 §2 |
| Q-G2-2 | Classification approved; identity-check sub-rule | APPROVED; sub-rule PROPOSED | I-1 §2 |
| Q-G2-3 | (a) order gates on smooth configurations only; (c), (d) excluded; (b) not approved | APPROVED (a) | I-1 §2 |
| Q-G2-4 | dt = 10 s PROVISIONAL | APPROVED | I-1 §2 |
| Q-G2-5 | Reference missions | DEFERRED (T0 checkpoint) | I-1 §2 |
| Q-G2-6 | M3 reference-snapshot treatment | DEFERRED (T4) | I-1 §2 |
| Q-G2-7 | Source of geodetic-height test points | DEFERRED (T0 checkpoint) | I-1 §2 |
| Q-G2-8 | VAL-0007 historical correction note | APPROVED; done | I-1 §2, §4 |
| Thresholds | M3 numerical acceptance thresholds | Not approved (later threshold DR, G4) | I-1 §2 |

## DR-0026: G3 architecture
| Item | Decision | Status | Source |
|---|---|---|---|
| Q-G3-1…4, 8, 11 | Immutable force context with adapter; density component; `PhysicsConfiguration` + SHA-256 identity; versioned model ids; scenario v3 additive; `PhysicsConfigured`; fail-closed identity; deterministic force order; ADR-0009 | APPROVED | I-1 §3 |
| Q-G3-5 | Model-version retention while any frozen artifact or supported scenario depends on it; no time-based deletion | APPROVED (owner's rule) | I-1 §3 |
| Q-G3-6 | Decay run ends at an explicit event or validity boundary | APPROVED (principle); value: DR-0027 A | I-1 §3 |
| Q-G3-7 | Per-sample environment/drag telemetry | **NOT AUTHORIZED** | I-1 §3 (not addressed); I-2 §3 |
| Q-G3-9 | Two-body specific-energy `escape` kept as an approximate diagnostic; not an exact criterion in perturbed dynamics; not independent authorization for safety-critical actions | APPROVED w/ constraints | I-2 §1 |
| Q-G3-10 | v3 spacecraft may carry mass and drag properties without an engine | APPROVED via D3 (part of the D3 text; review 02 confirmed) | I-1 §3 |
| D4 | General plugin framework | Not adopted | I-1 §3 |
| — | Rust, C, FFI, firmware, RTOS, real-time, embedded | NOT AUTHORIZED | I-1 §3, §5 |

## DR-0027: termination altitude and atmosphere table
| Item | Decision | Status | Source |
|---|---|---|---|
| A-1 | Explicit per-scenario termination altitude; no implicit default | APPROVED | I-2 §2 |
| A-2 | Metres; geodetic | APPROVED | I-2 §2 |
| A-3 | No universal numerical altitude | APPROVED (prohibition) | I-2 §2 |
| A-4 | Permitted ranges | T0 → owner | I-2 §2 |
| A-5 | Event-crossing behaviour (detection, outcome, fields) | T0 → owner | I-2 §2 |
| A-6 | Interaction with atmospheric-domain boundaries and `impact` | T0 → owner | I-2 §2 |
| A-s | Density for RK4 intermediate stages below the lower edge | **OPEN** (T0 → owner) | not selected |
| B-1 | GMAT R2026a table pinned verbatim (sha256 `75762f67…a85e`) as the initial reference | CONDITIONALLY APPROVED | I-2 §2 |
| B-2 | Disputed cells, absent 1000 km row, printed-edition uncertainty documented | CONDITION; done | I-2 §2 |
| B-3 | No silent repair or substitution | CONDITION | I-2 §2 |
| B-4 | Domain behaviour, including unsupported altitudes, defined explicitly | CONDITION; behaviour **OPEN** (T0 → owner) | I-2 §2 |
| B-5 | No claim of agreement with the printed textbook | CONDITION | I-2 §2 |

## DR-0028: Earth-fixed frame realization
| Item | Decision | Status | Source |
|---|---|---|---|
| A | J-ax-1: model +Z coincident with Earth's symmetry/spin axis by assumption, fixed in the M3 inertial frame | was OPEN → **APPROVED** | I-3 §2 |
| B | No Earth rotation angle in M3 (B1) | was OPEN → **APPROVED** | I-3 §2 |
| R-1 | No time-dependent orientation, precession, nutation or polar motion | APPROVED (requirement) | I-3 §2 |
| R-2 | Not identified as a physically accurate rotating terrestrial frame | APPROVED (requirement) | I-3 §2 |
| R-3 | Approximation, limitations and future-capability implications documented | APPROVED; done (DR-0028, SCI-0013). Two limitation statements corrected 2026-10-16 (Resolution amendment 1; SCI-0013 status update 3): node error not bounded by the pole tilt (M3P4-F1); local solar time needs a solar ephemeris and time convention, not an Earth rotation angle (M3P4-F2) | I-3 §2; I-4 §1 |
| R-4 | Architectural extension point for future Earth-fixed transformations | APPROVED; recorded (ADR-0009 item 17), not implemented | I-3 §2 |
| — | Any additional Earth-orientation implementation (rotation angle, pole of date, EOP) | **NOT AUTHORIZED** | I-3 §2, §7 |
| — | Solar ephemeris, Earth-orientation provider, local-solar-time output | **NOT AUTHORIZED** | I-4 §1 |

## Historical corrections and standing decisions
| Item | Status | Source |
|---|---|---|
| SCI-0005 TT/TCG correction note (append-only) | Recorded; no acceptance change | I-1 §4 |
| VAL-0007 GMAT GM provenance note (append-only) | Recorded; no acceptance change | I-1 §4 |
| AC-1 (explicit architecture/runtime decision before flight/embedded/firmware/hardware) | ACCEPTED | I-1 §5 |
| AT-1…AT-7 | OPEN | I-1 §5 |
| `research/flight-software-architecture` | Not merged | I-1 §5 |
| Frozen M1/M2 thresholds, references, goldens, validation semantics | Unchanged | I-1, I-2 §3 |

## Review findings (planning review 02)
| ID | Severity | Disposition | Owner decision | Record |
|---|---|---|---|---|
| M3P2-F1 | BLOCKER | ACCEPTED | Q4 and Q-G3-9 decided explicitly (I-2 §1) | `docs/reviews/M3-planning-review-02.md`, "Resolution of findings" |
| M3P2-F2 | BLOCKER | REJECTED_WITH_REASONING (records); prompt corrected | I-2 §1: next review receives the complete instructions | same |
| M3P2-F3 | MINOR | ACCEPTED | I-2 §1: correction authorized | same |

## Review findings (planning review 03)
| ID | Severity | Disposition | Owner decision | Record |
|---|---|---|---|---|
| M3P3-F1 | MINOR | ACCEPTED; corrected | I-3 §3 | DR-0024 "Q4 coordinate conventions, revision 2" (general relation; FC-1…FC-10); `docs/reviews/M3-planning-review-03.md`, "Resolution of findings" |
| M3P3-F2 | MINOR | ACCEPTED; corrected | I-3 §4 | DR-0024 amendment log (M3P3-F2 entry, complete verbatim row); same review record |

## Review findings (planning review 04)
| ID | Severity | Disposition | Owner decision | Record |
|---|---|---|---|---|
| M3P4-F1 | MINOR | ACCEPTED; corrected | I-4 §1 | DR-0028 "Resolution amendment 1" item 1; SCI-0013 status update 3; DR-0024 amendment log; `docs/reviews/M3-planning-review-04.md`, "Resolution of findings" |
| M3P4-F2 | MINOR | ACCEPTED; corrected | I-4 §1 | DR-0028 "Resolution amendment 1" item 2; SCI-0013 status update 3; same review record |

## Review findings (planning review 05)
| ID | Severity | Disposition | Owner decision | Record |
|---|---|---|---|---|
| M3P5-F1 | MINOR | ACCEPTED; was not applied (I-4 §5 stop) → **corrected** | I-5 §1–2 | DR-0028 "Resolution amendment 2" (signed formulas, convention, verification); `docs/reviews/M3-planning-review-05.md`, "Resolution of findings" |

## Review findings (planning review 06, targeted)
| ID | Severity | Disposition | Owner decision | Record |
|---|---|---|---|---|
| M3P6-F1 | MINOR | ACCEPTED; was not applied (I-5 §5 stop) → **corrected** | I-6 §1 | DR-0028 "Resolution amendment 3" item 1 (full line-of-nodes identity, domain, crossings, endpoints); `docs/reviews/M3-planning-review-06.md`, "Resolution of findings" |
| M3P6-F2 | MINOR | ACCEPTED; was not applied → **corrected** | I-6 §1 | DR-0028 amendment 3 item 2 (E5a/E5b assertions, E5c coverage guard); same record |
| M3P6-F3 | MINOR | ACCEPTED; was not applied → **corrected** | I-6 §1 | DR-0028 amendment 3 item 3 (`wrap()` returns (−π, π], exact); same record |

## Review findings (M3 Planning Review 07, targeted)
Review-06 findings M3P6-F1, F2 and F3: **RESOLVED** (reviewer's dispositions).

| ID | Severity | Disposition | Owner decision | Record |
|---|---|---|---|---|
| M3P7-F1 | MINOR | ACCEPTED; was not applied (I-6 §5 stop) → **corrected** | I-7 §2 | DR-0028 "Resolution amendment 4" (`wrap()` domain = finite floats; NaN and ±∞ raise ValueError; finite behaviour unchanged); `docs/reviews/M3-planning-review-07.md`, "Resolution of findings" |

## Review findings (M3 Planning Review 08)
Review-07 finding M3P7-F1: **RESOLVED** (reviewer's disposition).

| ID | Severity | Disposition | Owner decision | Record |
|---|---|---|---|---|
| M3P8-F1 | MINOR | ACCEPTED; was not applied (I-7 §5 stop) → **corrected** | I-8 §2–§5 | DR-0028 "Resolution amendment 5" (finite validation before every comparison; per-formula minimum valid samples: order 506/532, sign 560/504; bounded audit of E1–E6; 33 entrypoint mutations detected; finite results unchanged); `docs/reviews/M3-planning-review-08.md`, "Resolution of findings". Original record: a non-finite (NaN) first-order prediction skipped the order and sign checks and still passed; there was no per-component coverage requirement. Not a mathematical error |

## Review findings (M3 Planning Review 09)
Review-08 finding M3P8-F1: **RESOLVED** (reviewer's disposition).

| ID | Severity | Disposition | Owner decision | Record |
|---|---|---|---|---|
| M3P9-F1 | MINOR | ACCEPTED; was not applied (I-8 §7 stop) → **corrected** | I-9 §3 | DR-0028 "Resolution amendment 6" (oracle ±∞ mutants for each formula, whole grid and single sample; oracle check weakened to `isnan`/`isinf` detected; finite results unchanged); `docs/reviews/M3-planning-review-09.md`, "Resolution of findings". Original record: weakening the oracle finite check to `isnan()` still passed, because no mutant injected oracle ±∞ |
| M3P9-F2 | MINOR | ACCEPTED; was not applied (I-8 §7 stop) → **corrected** | I-9 §4 | DR-0028 "Resolution amendment 6" (per formula: doubled coefficient designated to the order check, reversed sign to the sign check, 560/504 failures each; order and sign assertion removal for Δi, ΔΩ and both detected); `docs/reviews/M3-planning-review-09.md`, "Resolution of findings". Original record: disabling the order or sign assertion still passed |
| M3P9-F3 | NOTE | ACCEPTED as a NOTE → **E3/E4 mutation coverage added** | I-9 §5 | DR-0028 "Resolution amendment 6" (1 % oracle inclination error designated to E3 and E4; both assertion removals detected; step-size selection documented as intentional, unchanged). The assertion-removal sweep leaves 18 of 35 assertions not individually load-bearing (outside I-9 scope): **open for the Tech Lead** |

## Review findings (M3 Planning Review 10)
Review-09 findings M3P9-F1 and M3P9-F2: **RESOLVED**; M3P9-F3: **RESOLVED (E3/E4 coverage)** (reviewer's dispositions).

| ID | Severity | Disposition | Owner decision | Record |
|---|---|---|---|---|
| M3P10-F1 | MINOR | ACCEPTED; was not applied (I-9 §9 stop) → **corrected** | I-10 §2–§3 | DR-0028 "Resolution amendment 7" (defect record per built-in mutant; six classification categories; "not rejected" requires a completed, exercised mutant; exceptions only by explicit allowance for the E2/E5b wrap guard and the order-estimate math domain error; 13 controls, the five regression controls fail against `896d52d` and pass now); `docs/reviews/M3-planning-review-10.md`, "Resolution of findings". Original record: an unrelated exception inside a built-in mutant counted as evidence of a removed assertion |
| M3P10-F2 | NOTE | ACCEPTED as a NOTE → **classified** | I-10 §4 | DR-0028 "Resolution amendment 7": 6 A (new mutants), 9 B (independent check demonstrated), 3 C (rationale), 0 D; sweep now 23 detected / 12 surviving; `docs/reviews/M3-planning-review-10.md`, "Resolution of findings" |

## Review findings (M3 Planning Review 11)
Review-10 findings M3P10-F1 and M3P10-F2: **NOT RESOLVED** (reviewer's disposition; see M3P11-F1 and M3P11-F2).

| ID | Severity | Disposition | Owner decision | Record |
|---|---|---|---|---|
| M3P11-F1 | MINOR | ACCEPTED; was not applied (I-10 §9 stop) → **corrected** | I-11 §2 | DR-0028 "Resolution amendment 8" (each built-in mutant declares its intended defect; exercised = shown, never missing, nothing else different; every mutation has an exercise predicate established by an independent probe; 23 controls, the four M3P11-F1 regression controls fail against `c16b3b5` and pass now; 109/109 exercised and detected for the intended reason); `docs/reviews/M3-planning-review-11.md`, "Resolution of findings". Original record: verification defect: "defect exercised" accepts any bitwise difference, so a suppressed import failure with a correct, reassociated fallback still counts as detection of an assertion removal that never happened. Not a mathematical error |
| M3P11-F2 | MINOR | ACCEPTED; was not applied (I-10 §9 stop) → **corrected** | I-11 §3 | DR-0028 "Resolution amendment 8": W5, E1, E2e, E5b-nonfinite and E5b-defined reclassified A, each with a built-in mutant; 11 A, 4 B (property-wide arguments), 3 C, 0 D; sweep 28 detected / 7 surviving; `docs/reviews/M3-planning-review-11.md`, "Resolution of findings". Original record: verification defect: five category B assertions (W5, E1, E2e, E5b-nonfinite, E5b-defined) protect defects their stated substitutes miss; the 6 A / 9 B / 3 C classification is not supported. Not a mathematical error |

## Review findings (M3 Planning Review 12)
Review-11 findings M3P11-F1 and M3P11-F2, and review-10 findings M3P10-F1 and M3P10-F2: **NOT RESOLVED** (reviewer's disposition; see M3P12-F1 and M3P12-F2).

| ID | Severity | Disposition | Owner decision | Record |
|---|---|---|---|---|
| M3P12-F1 | MINOR | ACCEPTED; **not applied** (I-11 §9 stop) | Pending | `docs/reviews/M3-planning-review-12.md`. Unsound verification claim: the oracle-values probe observes values only where the finite validation runs, which `check_formulas()` skips after a component's first invalid value, so a first-step-only oracle injection is certified as the all-steps mutation ("missing = 0"). Not a mathematical error |
| M3P12-F2 | MINOR | ACCEPTED; **not applied** (I-11 §9 stop) | Pending | `docs/reviews/M3-planning-review-12.md`. Unsound verification claim: E6-sign's category B premise covers the formula's sign on the first-order grid, which never evaluates E6's tilt (0.15°); a formula sign reversal confined to that tilt passes with only E6-sign removed. The 11 A / 4 B / 3 C classification is not supported for E6-sign. Not a mathematical error |

## Gates
| Gate | State |
|---|---|
| Planning merge | Needs the Tech Lead's explicit checkpoint approval (I-2 §7). Section 7 of I-1 alone no longer suffices |
| T0 | Needs the explicit checkpoint approval and the planning merge (I-1 §8, narrowed by I-2 §7) |
| T1 and later | NOT AUTHORIZED. Was also blocked on DR-0028; that block is lifted by the J-ax-1 decision. T2 still depends on the DR-0027 T0 proposals (A-4, A-5, A-6, A-s, B-4) and the T0-checkpoint deferrals |
