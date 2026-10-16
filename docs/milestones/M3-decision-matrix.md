# M3 planning decision matrix

**As of:** 2026-10-16, fifth planning checkpoint (review 05 correction M3P5-F1; no decision changed). Earlier: 2026-10-16, fourth planning checkpoint (review 04 corrections M3P4-F1/F2; no decision changed). Earlier: 2026-10-15, third planning checkpoint (after review 03 and the DR-0028 decision). Earlier statuses that changed are shown as "was → now". This is an index: each Decision Request's Resolution is authoritative, and this file only points to it. Nothing here is implemented.

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
| M3P6-F1 | MINOR | ACCEPTED; **not applied** (I-5 §5 stop) | Pending | `docs/reviews/M3-planning-review-06.md`. DR-0028 amendment 2: the exact line-of-nodes result (Δi = −δ, ΔΩ = 0) needs the domain 0 < i − δ < π |
| M3P6-F2 | MINOR | ACCEPTED; **not applied** | Pending | Same record. Verification script: E5's 180° node jump is reported, not asserted |
| M3P6-F3 | MINOR | ACCEPTED; **not applied** | Pending | Same record. Verification script: `wrap()` returns [−π, π), declared (−π, π] |

## Gates
| Gate | State |
|---|---|
| Planning merge | Needs the Tech Lead's explicit checkpoint approval (I-2 §7). Section 7 of I-1 alone no longer suffices |
| T0 | Needs the explicit checkpoint approval and the planning merge (I-1 §8, narrowed by I-2 §7) |
| T1 and later | NOT AUTHORIZED. Was also blocked on DR-0028; that block is lifted by the J-ax-1 decision. T2 still depends on the DR-0027 T0 proposals (A-4, A-5, A-6, A-s, B-4) and the T0-checkpoint deferrals |
