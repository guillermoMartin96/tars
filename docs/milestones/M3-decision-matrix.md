# M3 planning decision matrix

**As of:** 2026-10-15, second planning checkpoint (after review 02). This is an index: each Decision Request's Resolution is authoritative, and this file only points to it. Nothing here is implemented.

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

## DR-0024: G1 physical models and constants
| Item | Decision | Status | Source | Also recorded in |
|---|---|---|---|---|
| Q1 | J2 = 1.0826261739e-3, EGM2008 tide-free | APPROVED | I-1 §1 | SCI-0013 |
| Q2 | J2 reference radius = WGS 84 a; stop condition checked, not met (§3.5) | APPROVED | I-1 §1 | SCI-0013 |
| Q3 | GM = WGS 84 3.986004418e14; SCI-0005 historical correction note | APPROVED; note added | I-1 §1, §4 | SCI-0005 (appended note) |
| Q4 | Earth-fixed +Z is the common axis of J2, the ellipsoid and atmosphere rotation; Earth-fixed and inertial representations distinct; correct transformations; conventions and tests FC-1…FC-9 recorded | APPROVED w/ constraints | I-2 §1 | SCI-0013/0014/0017 status updates; ADR-0009 item 14 |
| Q4 realization | Placement of +Z_EF in the inertial frame (J-ax-1 vs pole of date); Earth rotation angle θ(t) | **OPEN** | — | DR-0028 |
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
| Item | Question | Status |
|---|---|---|
| A | +Z_EF placement: J-ax-1 (model-defined, coincident with inertial z) / J-ax-2 / J-ax-3 | **OPEN**; recommendation A1 |
| B | Earth rotation angle θ(t) for Earth-fixed outputs | **OPEN**; recommendation B1 (none in M3) |

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

## Gates
| Gate | State |
|---|---|
| Planning merge | Needs the Tech Lead's explicit checkpoint approval (I-2 §7). Section 7 of I-1 alone no longer suffices |
| T0 | Needs the explicit checkpoint approval and the planning merge (I-1 §8, narrowed by I-2 §7) |
| T1 and later | NOT AUTHORIZED; blocked also on DR-0028 |
