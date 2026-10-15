# RES-0001: Flight-software language and architecture assessment (Rust, C, hybrid)

**Status:** Research only. No implementation is authorized. Decision record: [ADR-0008](../decisions/0008-flight-software-architecture-proposed.md). Its direction was accepted by the Tech Lead on 2026-10-15 (TL-1…TL-9); the language is deferred; open items are AT-1…AT-7. See §12.  
**Requested by:** Guillermo (Tech Lead), 2026-10-14, together with the M2 T8 authorization.  
**Author:** implementing engineer (Level 1).  
**Repository state assessed:** branch `milestone-2-propulsion-f90f9ba4` at `963dbe7` (T7 accepted).  
**Independence:** this research does not gate M2 or T8. An unresolved decision here blocks nothing in M2.

## How to read this document
Every substantive claim carries a tag:

| Tag | Meaning |
|---|---|
| **[F-repo]** | Demonstrated fact about this repository: a file, a measurement in a VAL record, or a command output. The source is cited. |
| **[F-ext]** | Fact from an external source, cited in §11. Vendor claims are marked as vendor claims. |
| **[A]** | Engineering assumption: plausible but not demonstrated here. |
| **[R]** | Recommendation. |

## 0. Correction to the request's premise
The request describes "the existing C simulation core" and frames Option A as "continue in C" and Option B as "preserve validated numerical code in C".

**[F-repo]** The repository contains no C, C++ or Rust source. `git ls-files` lists 508 `.py` files and no `.c`, `.h`, `.cpp` or `.rs` files. The simulator is Python 3.12 with NumPy and Pydantic (`pyproject.toml`; ADR-0001). The validators use SciPy, a dev dependency.

So no validated C code exists to preserve. The validated numerical asset is the **Python implementation plus its validation apparatus**:
- the M1 and M2 Proofs and the GMAT references;
- the reference snapshot (DR-0021);
- the approved thresholds.

This document evaluates the three options in that light:
- **Option A** becomes "write a new flight core in C";
- **Option B** becomes "a new hybrid C/Rust flight core";
- **Option C** becomes "an incremental Rust (`no_std`) flight core";

and in every option the Python simulator remains the reference and the Mission Laboratory. The comparison criteria are those requested. The Tech Lead should confirm this reading, or say whether a C core is intended to exist elsewhere (§10, U1).

## 1. Current architecture (A)

### 1.1 Module inventory
**[F-repo]** Line counts are from `wc -l` at `963dbe7`.

| Area | Modules | Lines | Role |
|---|---|---|---|
| Physics and integration | `sim/integrators.py` (RK4), `sim/forces.py` (point-mass gravity, superposition), `sim/state.py` (frozen snapshots), `sim/constants.py` | 195 | Fixed-step RK4, dt = 10 s (ADR-0004); a = −μr/\|r\|³ (SCI-0001) |
| Orbital mechanics | `astro/elements.py`, `astro/kepler.py` | 266 | Elements and a universal-variable Kepler propagator, used by validation and events |
| Propulsion and maneuvers | `sim/propulsion.py` | 623 | `EngineSpec`, `TankSpec`, mass flow F/(Isp·g0), VNB prograde/retrograde, `plan_burn` (cutoff, depletion, DR-0017 timing-Δv bound) |
| Simulator | `sim/simulator.py` | 552 | Owns y = [r, v, m_prop, Δv_sensed]. Engine state machine, RK4 sub-steps split at engine events, atomic ticks, `submit()` → `CommandReceipt`, ascending-node detection by cubic Hermite |
| Commands | `sim/commands.py` | 189 | Strict Pydantic `BurnCommand` (schema v1), rejection codes |
| Events and serialization | `events/schema.py`, `sim/burn_events.py` | 493 | Strict Pydantic event models; JSONL |
| Scenario execution | `sim/scenario.py`, `sim/runner.py` | 636 | Scenario v1/v2 parsing, command timeline, stop conditions, event emission order |
| Validation | `validation/*.py` (m2, gmat, gmat_m2, reference_snapshot, m2_cross_platform, thresholds, …) | ≈ 5 600 | Oracles O1–O9, audits, GMAT comparison, the snapshot, the cross-platform gate |
| Tools | `toolbox/validators/*`, `toolbox/scripts/*` | — | Proof runners, GMAT workflows, determinism |

### 1.2 Properties relevant to embedded execution

| Property | Finding | Tag |
|---|---|---|
| Language and runtime | CPython 3.12, NumPy 2.x, Pydantic 2.x; garbage-collected | [F-repo] `pyproject.toml`, `uv.lock` |
| Threading | None. No `threading`, `multiprocessing` or `asyncio` in `sim/`, `astro/` or `events/` | [F-repo] grep |
| OS dependencies in the core | None in `sim/` and `astro/`: no file I/O, wall clock or environment reads. Time is `tick·dt` from an integer counter (ADR-0002). File I/O lives in the runner and CLI. `subprocess` and `platform` appear only in validation, for git and host identity | [F-repo] grep; `simulator.py` `t` property |
| Heap allocation per step | Yes. Every RK4 stage allocates NumPy arrays (`np.concatenate` in the derivative, array arithmetic in `RK4.step`). Snapshots copy arrays | [F-repo] `simulator.py` `_powered_derivative`, `integrators.py` |
| Bounded data structures | **No.** The pending-burn list, the set of used command IDs (`_used_command_ids`) and the runner's in-memory event list (`RunResult.events`) all grow without a fixed bound | [F-repo] `simulator.py` `__init__`, `runner.py` |
| Bounded loops | Mostly. One loop in `plan_burn` lowers the cutoff one ulp at a time until it is at or before depletion. Termination is argued and observed (≤ 1 iteration over 20 080 cases), not proven with a static bound | [F-repo] `propulsion.py` ≈ l. 430 |
| Floating point | IEEE-754 binary64 throughout. The DR-0017 timing logic depends on binary64: `math.nextafter`, `math.ulp`, `frexp`, `ldexp` | [F-repo] `propulsion.py` |
| Transcendental and library math | `math.log` (rocket equation), `sqrt`, trigonometry (elements, initial state), `np.linalg.norm` (gravity, pointing, finiteness checks) | [F-repo] grep |
| Cross-platform reproducibility | Not bit-identical across platforms. M2 final-state drift is ≤ 7.23e-6 m and 8.43e-9 m/s across Linux x86_64, macOS x86_64 and macOS arm64 (VAL-0017). Same-platform replay is byte-identical (DR-0006). The same CI label can give different last bits (M1-D4, runner CPU variability) | [F-repo] VAL-0005, VAL-0016, VAL-0017 |
| Source of the cross-platform drift | Not isolated. Plausible contributors: libm `log`/trigonometry differing in the last ulp, and NumPy SIMD/BLAS dispatch in `norm` and `dot` differing by CPU | [A] |
| Error handling | Python exceptions (`FloatingPointError`, `BurnRejectedError`) with atomic rollback of a tick. Non-finite states are rejected | [F-repo] `simulator.py` `step` |
| Authority boundary | Agents and the scenario only *submit* commands; nothing else can mutate r, v, mass or propellant. This is tested by the architecture scan and P8 | [F-repo] `validation/architecture.py`, M2 P8 |
| Sensors and actuators | None. Telemetry is the truth state (M2 non-goal) | [F-repo] M2 plan §2 |

### 1.3 Which parts could realistically run on constrained hardware
**[A]** Classification by algorithmic nature, assuming a re-implementation without Python, NumPy or Pydantic:

| Component | Embedded candidate? | Reason |
|---|---|---|
| RK4 step, point-mass gravity, thrust acceleration, mass flow | **Yes** | Fixed arithmetic per step, a 3–8 element state, no allocation needed |
| Pointing laws (prograde/retrograde) | **Yes** | One normalization |
| Engine state machine, event-time computation, `plan_burn` | **Yes, after bounding** | Needs a fixed-capacity burn queue and a proven bound on the ulp loop (or a closed form) |
| Command validation and rejection codes | **Yes, re-specified** | The validation *rules* port; the Pydantic/JSON parsing does not. A flight interface would use a fixed binary command format |
| Ascending-node detection (Hermite root) | Possibly | Fixed iterations; needed only if onboard event detection is a requirement |
| Elements and universal-variable Kepler | Possibly | Iterative solvers need iteration caps; useful for onboard prediction |
| Scenario parsing, runner, JSONL events | **No** (ground) | Text formats, unbounded logs; a flight system would emit fixed-size telemetry frames |
| Validation, GMAT, reference snapshot, DOP853 | **No** (ground) | SciPy, large data, host tools; this is verification infrastructure |
| A future AI crew or Navigator | **No** (ground or high-level processor) | LLM inference is outside any embedded flight-core budget |

The candidate flight subset is small: about 1 000 of the ≈ 8 600 lines under `src/`. Even that subset is not embedded-ready: allocation per step, unbounded structures and exception-based control flow.

### 1.4 Embedded-readiness gaps
These hold whatever the language:
1. **G1. No requirements.** No target processor, memory budget, real-time deadline, mission phase or sensor suite is defined. Every embedded choice below is therefore provisional. [F-repo] No roadmap document exists (M2 plan §1.2).
2. **G2. Unbounded state.** The burn queue, the command-ID history and the event log need fixed capacities and defined overflow behavior. [F-repo]
3. **G3. Allocation in the hot path.** The NumPy temporaries in every RK4 stage. [F-repo]
4. **G4. Exceptions as control flow.** A flight core needs explicit result codes and a defined safe state. [F-repo]
5. **G5. Proven loop bounds.** The `plan_burn` ulp loop needs a proven bound. [F-repo]
6. **G6. Float precision assumption.** The model and the DR-0017 timing logic assume binary64. Many microcontroller FPUs are single-precision only (§4.3). [F-repo] / [F-ext]
7. **G7. Truth-state telemetry.** There are no sensor models, estimation or fault detection. A Flight Core is a navigation and control system, which M2 does not have. [F-repo]
8. **G8. Text interfaces.** Commands and events are JSON. A flight link needs fixed-size binary framing with integrity checks. [F-repo]

## 2. Options (B)

### 2.1 What each option means here
- **A — C flight core.** Write the flight subset anew in C (for example C11 under MISRA C:2023), using the Python simulator as the reference. Expose a C ABI that the Python harness can call (`ctypes`/`cffi`) for differential tests.
- **B — Hybrid C/Rust.** Numerical kernels (RK4, gravity, propulsion math) in C. Command validation, state machine, fault management and interfaces in Rust. A defined FFI boundary between them.
- **C — Incremental Rust.** Port the flight subset component by component into a `no_std`, heap-free Rust crate. Optional `alloc` only in host builds. Python bindings (for example PyO3) or a CLI that emits the existing JSONL contract allow differential testing against the Python reference.

### 2.2 Comparison
Ratings are relative within this project (+ better, 0 neutral, − worse), followed by the reasoning.

| Criterion | A — C | B — Hybrid | C — Rust |
|---|---|---|---|
| **Firmware suitability** | + Universal toolchains. Long flight heritage: NASA cFS on 40+ missions [F-ext 5]; JPL flight software is C/C++ [F-ext 6] | 0 Both toolchains needed on the target | + `no_std` bare-metal targets are Tier 2 for Cortex-M, Cortex-R, RISC-V and AArch64 [F-ext 1]. Less flight heritage: ESA studies, not mission-standard [F-ext 7] |
| **Memory safety** | − Bounds, lifetime and aliasing safety rest on discipline, MISRA and analyzers | 0 Rust parts safe; C parts and the FFI boundary are not | + Safe Rust excludes data races and use-after-free at compile time; `unsafe` is confined and auditable [A: standard Rust property] |
| **Deterministic execution** | + No hidden runtime | 0 Two runtimes; panics must not cross the FFI (UB) [F-ext 8] | + No runtime or GC. `panic = abort` and a custom panic handler give a defined failure path [F-ext 8] |
| **Numerical reproducibility** | − C permits FP contraction (`FP_CONTRACT`; GCC defaults to `-ffp-contract=fast` outside ISO modes [F-ext 9]). Results can change with flags unless pinned | − Inherits the C caveat, plus two compilers | + Rust specifies IEEE-754 results for basic operations, `sqrt` and `mul_add`. Fusing a·b + c is not permitted implicitly [F-ext 2]. Transcendentals (`ln`, `sin`) are **not** specified: they come from the platform libm or the `libm` crate [F-ext 2, 3] |
| **Real-time constraints** | + Mature WCET and stack analyzers | 0 Analysis spans two languages | 0 RTIC and Embassy exist [F-ext 10]; Rust-specific WCET tooling is less mature [A] |
| **Toolchain and targets** | + Every candidate processor, qualified compilers widely available | − Two qualified toolchains | 0 LLVM targets only. Qualified compiler: Ferrocene, TÜV SÜD-qualified for ISO 26262 ASIL D, IEC 61508 SIL 3 and IEC 62304 Class C; DO-178C DAL C is a stated customer-certification target, not a qualification (vendor claims) [F-ext 4]. SPARC/LEON (common in European space) is Tier 3 [F-ext 1] |
| **Interop with existing code** | 0 The existing code is Python: C is easy to call via `ctypes`/`cffi` | 0 Same | 0 PyO3 or a C ABI (`extern "C"`) via `cbindgen`. Both are mature [A] |
| **Testing and formal verification** | + Frama-C, Astrée, Polyspace, CBMC (mature) [A] | 0 Must cover both languages | + Kani (CBMC-based bounded model checking, with contracts and loop contracts) [F-ext 11]. Proptest/fuzzing are easy. Embedded-specific Kani use is little documented [F-ext 11] |
| **Long-term maintenance** | − Safety rests on reviewers and tools | − Two languages, an FFI and two build systems: the highest cognitive load for a small team | + One language for the flight core; the Python lab stays separate |
| **Migration cost and regression risk** | 0 New code either way; the Python reference stays | − Highest: two ports plus an FFI | 0 New code either way; the increments match the module boundaries |

### 2.3 Observations that dominate the comparison
1. **No C asset exists, so Option B loses its main justification** [F-repo]. B's benefit is "preserve validated C". Its costs (two languages, an FFI with unwinding hazards, two qualification paths) remain.
2. **Reproducibility depends on the target FPU and the math library at least as much as on the language** [F-ext 2, 3, 12]. A Rust or C core can reproduce the Python reference *bit-for-bit* only for the operations IEEE-754 pins down (+, −, ×, ÷, `sqrt`, explicit `fma`), in the same order. `ln` and trigonometry need a single shared implementation (for example the same correctly-rounded or `libm` port) on both sides, or a measured tolerance.
3. **Heritage and qualification favor C today; memory safety and specified floating-point favor Rust** [F-ext 2, 4, 5]. Neither wins on every criterion.
4. **The Python reference is the most valuable asset** [F-repo]. It is validated against GMAT, DOP853 and analytic oracles at approved thresholds. Every option should keep it as the numerical oracle, not replace it.

## 3. Proposed long-term architecture (C)

### 3.1 Partition
```
┌──────────────────────────── GROUND / HOST ────────────────────────────┐
│  AI Navigator (advisory)        Mission Laboratory (Python)            │
│  plans, explains, proposes  ──► high-fidelity sim, branching,          │
│  CommandProposal (no authority)  maneuver comparison, GMAT, oracles    │
│            │                              ▲                            │
│            ▼                              │ differential tests         │
│  Authorization layer (crew roles,          │ (same scenario, same       │
│  permissions; deterministic, LLM-free)     │  commands, compared        │
│            │ signed/validated command      │  events)                   │
└────────────┼──────────────────────────────┼────────────────────────────┘
             ▼                              │
┌──────────── FLIGHT CORE (deterministic, bounded) ───────────────────────┐
│ command validation → engine state machine → guidance/control laws     │
│ navigation state (estimator, later) → fault management / safe modes   │
│ fixed-capacity queues, no heap, fixed-step integration, result codes  │
└────────────┬────────────────────────────────────────────────────────────┘
             ▼
┌──────────── HARDWARE ABSTRACTION ──────────────────────────────────────┐
│ traits/interfaces: Clock, Thruster/Valve, IMU/GNSS, Radio, Watchdog,   │
│ NVM. Implementations: simulated (SIL, backed by the Mission Lab),      │
│ then real drivers (HIL/flight).                                        │
└────────────────────────────────────────────────────────────────────────┘
Verification infrastructure spans all layers: oracles, the snapshot, Proof, CI matrix.
```

### 3.2 Layer responsibilities and boundaries [R]
| Layer | Owns | Must not | Language (proposed) |
|---|---|---|---|
| **Flight Core** | Accepting or rejecting commands against hard limits (propellant, timing, engine state). Executing approved maneuvers. Safe modes. The onboard navigation state | Allocate after initialization; call into AI; depend on wall-clock OS services except through the HAL | Decided at the reconsideration point (§8). Rust `no_std` is preferred if adopted |
| **Mission Laboratory** | Truth simulation, scenario branching, maneuver trade studies, GMAT and DOP853 references, the Proof | Run onboard; be bounded-resource | Python (current) |
| **AI Navigator** | Proposals, explanations, plan comparison | Hold write authority; bypass validation; mutate flight state | Provider-independent agent layer (architecture invariant 4) |
| **Hardware Abstraction** | Device interfaces, time source, watchdog | Contain guidance logic | Same language as the Flight Core |
| **Verification** | Differential tests, oracles, SIL/HIL harnesses, evidence | Become the source of truth for physics (GMAT and analytic oracles are) | Python plus target-language test harnesses |

### 3.3 Advisory AI versus deterministic flight authority [R]
This extends invariants 1–3 (`playbook/architecture.md`) and DR-0014 §6.
1. The AI Navigator emits a **`CommandProposal`**, a data object. Proposals carry no authority.
2. An **authorization layer** turns a proposal into a command. It is deterministic, LLM-free and role-based (crew permissions, invariant 2), and it records who authorized what. Today's `issuer` field is provenance only and carries no authority (DR-0014). This layer would be new, crew-milestone work, and needs its own DR.
3. The Flight Core **re-validates every command** against its own hard limits, whatever authorization it carries. That mirrors today's `submit()`: rejection leaves state bit-identical.
4. Flight Core limits (propellant reserve, maximum burn duration, keep-out conditions) are **configuration under change control**, never adjustable by the AI.
5. Fault management and safe modes can **override** any command. The AI cannot override them.
6. Every proposal, authorization, acceptance, rejection and override is a machine-readable event (invariant 5). That makes AI influence auditable after the fact.

### 3.4 How Rust could serve the Flight Core alone [R]
- A `tars-flight` crate, `#![no_std]`, no `alloc` in flight builds: fixed-capacity queues (for example `heapless`) and plain `f64` arrays.
- A `std` host feature adds Python bindings (PyO3) or a CLI that emits the **existing JSONL event contract**. The Mission Lab and Proof then run unchanged against the Rust core.
- The Mission Lab and the AI Navigator stay Python, or whatever the agent layer chooses. They talk to the Flight Core only through the command and telemetry interface, never through shared memory or internal state.
- Assumption to verify [A]: `audit_run()` consumes `RunResult.events` (event objects, `validation/m2.py`). Events round-trip through JSONL (P9), so a JSONL adapter should allow the M2 validators to audit an external core's output. This has not been tried.

## 4. Firmware considerations (D)

### 4.1 `no_std`, optional `alloc`, and memory bounds
- `no_std` code uses `core`. A bare-metal binary must supply its own panic handler [F-ext 8].
- `alloc` is optional. A flight build can exclude it, and the absence of heap use is then a property the compiler enforces [A: standard Rust property].
- Holzmann's Power of Ten rule 3 forbids dynamic allocation after initialization, so that memory use can be verified and stack bounds derived statically (no recursion) [F-ext 13]. Rust without `alloc`, or C under MISRA, can both meet it.
- For TARS: G2 and G3 (§1.4) must be closed by design whatever the language.

### 4.2 Floating point on embedded targets
- On stable Rust (as of the sources found), `f64::sqrt`, `ln` and `sin` are inherent methods in `std` only. `no_std` code uses the `libm` crate, or `core_maths` backed by it. Free functions such as `core::f64::math::sqrt` are nightly-only [F-ext 3]. Check the current stable status before any decision.
- The Cortex-M4F FPU is single-precision only, so binary64 is emulated in software and is slow. The Cortex-M7 FPU options are none, FPv5-SP or FPv5-DP; double precision is optional silicon [F-ext 12].
- **Consequence for TARS** [R]: the processor must be chosen with **hardware binary64** (for example an M7 with FPv5-DP, a Cortex-R5F or Cortex-A, or an RV32/RV64 core with the D extension). Otherwise the numerical model must be re-derived and re-validated in binary32, which would be a new science/validation decision: the DR-0017 timing bound and the snapshot tolerances assume binary64.
- Denormals: Rust specifies no flush-to-zero by default. 32-bit ARM NEON SIMD flushes to zero [F-ext 2]. Auto-vectorization on such targets must be controlled.

### 4.3 Fixed-step versus adaptive integration [R]
- The Flight Core should stay **fixed-step**, as it is today (ADR-0004), with step splitting at known event times (DR-0013 3A). Cost per step is bounded, so WCET is analyzable.
- Adaptive integrators (DOP853 and similar) belong in the Mission Lab, where they already serve as the independent reference.
- The current design is already flight-friendly here: events are known in advance, there is no root-finding inside the integrator, and time is `tick·dt` from an integer [F-repo].

### 4.4 CPU and memory budgets [A, to be measured]
- One powered RK4 step is four derivative evaluations, each a few dozen floating-point operations including a `sqrt`, a division and a normalization. That is negligible on any FPU-equipped MCU at the 10 s or 1 s rates used today.
- The budget will be driven by future estimation (Kalman filters, matrix operations), not by propagation.
- No numbers are claimed here. A budget needs requirements (G1) and a measurement on candidate hardware.

### 4.5 Watchdogs and fault recovery [R]
Common practice, not yet project requirements:
- an independent hardware watchdog serviced only by the healthy main loop;
- defined safe states (engine off, valves closed);
- `panic = abort` mapped to a safe-state reset path;
- persistent fault counters;
- a reboot loop that ends in safe mode.

The current atomic-tick design (a failed step changes nothing) is a useful pattern to keep [F-repo].

### 4.6 Hardware abstraction [R]
- Define HAL interfaces as traits (Rust; `embedded-hal` 1.0 is stable with no 2.0 planned [F-ext 10]) or as function tables (C).
- Implement each interface twice: **simulated**, backed by the Mission Lab's truth state (SIL), and **real** (HIL and flight).
- The Flight Core sees only the interfaces.

### 4.7 Cross-compilation and targets
- Bare-metal Rust targets `thumbv7em-none-eabihf`, `thumbv8m.main-none-eabihf`, `armv7r-none-eabihf`, `riscv32imac/imafc-unknown-none-elf` and `aarch64-unknown-none` are Tier 2: "guaranteed to build", without guaranteed automated tests [F-ext 1].
- `sparc-unknown-none-elf` (LEON-class) is Tier 3 [F-ext 1].
- **No processor is selected here** (task constraint). Selection needs a requirements-based DR.

### 4.8 Safe C/Rust interoperability (relevant to B, and to C via `extern "C"` APIs)
- Unwinding across an FFI boundary with a non-unwinding ABI is undefined behavior. With `panic = abort` the optimizer assumes no unwinding [F-ext 8].
- Practice: a flat `extern "C"` API, plain-old-data structs (`#[repr(C)]`), explicit error codes, no panics across the boundary, and generated headers (`cbindgen`/`bindgen`) checked in CI [A].

### 4.9 Host-based and hardware-in-the-loop verification [R]
1. **Host differential tests:** the Flight Core compiled for the host runs every M2 scenario; events are compared with the Python reference (§6).
2. **SIL:** the Flight Core drives the simulated HAL; the Mission Lab provides truth.
3. **Processor-in-the-loop:** the same core cross-compiled and run on target silicon (or QEMU) with recorded inputs; outputs are compared bit-for-bit against the host build of the same core.
4. **HIL:** real I/O with a simulated environment. Only once hardware exists.

## 5. Proposed module boundaries [R]
| Future crate/module | Ported from | Contents | Excluded |
|---|---|---|---|
| `flight::dynamics` | `sim/integrators.py`, `sim/forces.py` | RK4 on a fixed-size state, point-mass gravity, thrust acceleration | NumPy, generic force composition beyond a fixed list |
| `flight::propulsion` | `sim/propulsion.py` | Mass flow, rocket equation, pointing laws, `plan_burn` with a proven loop bound, timing-Δv bound | Pydantic validation messages (replaced by codes) |
| `flight::engine` | `sim/simulator.py` (engine cursor, step splitting) | Engine state machine, fixed-capacity burn queue, atomic tick | Node detection (unless required), snapshots as Python objects |
| `flight::commands` | `sim/commands.py` | Binary command struct, validation, rejection codes (the same 10 codes) | JSON parsing |
| `flight::telemetry` | `events/schema.py` (subset) | Fixed-size telemetry records mappable to today's events | JSONL writing (ground side) |
| `flight::hal` | (new) | Clock, thruster, sensors, watchdog, NVM | — |
| `lab` (Python, unchanged) | everything else | Scenarios, runner, validation, GMAT, snapshot, AI Navigator later | — |

## 6. Numerical-equivalence verification strategy [R]
Three layers, from strictest to loosest:
1. **Bit-identical kernels (same host).**
   - For code using only IEEE-pinned operations (RK4 arithmetic, gravity with `sqrt`, thrust F/m), the new core and a *scalar* Python reference must agree bit-for-bit on the same host, provided the operation order is identical and no contraction occurs.
   - NumPy's vectorized `norm` and `dot` may not be order-identical. A scalar reference mode, or a documented tolerance, may be needed. To be demonstrated, not assumed [A].
2. **Shared transcendental implementation.**
   - `ln` (rocket equation, timing bound) and trigonometry must use the same implementation on both sides (for example both calling the same `libm` port), or be gated by measured tolerances.
3. **Proof-level equivalence.**
   - The new core runs the canonical M2 missions. Its JSONL events go through the **unchanged** M2 Proof: O1–O9, the contract checks, the reference snapshot and the golden cross-platform gate.
   - Using the existing cross-platform bound (≤ 1e-4 m, ≤ 1e-7 m/s, DR-0023) as a *cross-implementation* bound would be a **new use of an approved threshold**. **Tech Lead decision (2026-10-15): not permitted without independent justification** (ADR-0008 TL-7).

Supporting practices:
- golden vectors exported from the reference snapshot;
- property tests (rejection leaves state unchanged; propellant never negative);
- Kani proofs of panic-freedom and loop bounds for `plan_burn`-class code;
- the same tests on host, QEMU and target (processor-in-the-loop).

## 7. Incremental migration strategy [R]
Gated, each step reversible, the Python reference never removed:
1. **Step 0 (now, Python, no new language).** Close the language-independent gaps that also improve the simulator:
   - fixed capacities and overflow behavior (G2);
   - a proven bound or closed form for the ulp loop (G5);
   - an explicit command/telemetry binary schema *design* (G8, design only).

   Each needs its own approval, because it changes approved behavior or contracts.
2. **Step 1 (spike, after an approved DR).** A host-only `std` Rust (or C) port of `flight::dynamics` plus `flight::propulsion`. Differential tests at layers 1–2 of §6. No production use. Measure bit agreement and effort.
3. **Step 2.** Add `flight::engine` and `flight::commands`. Emit JSONL through a host adapter; run the unchanged M2 Proof (layer 3).
4. **Step 3.** A `no_std` build of the same crate for one candidate target class, under QEMU, after a requirements-based target DR. Processor-in-the-loop comparison.
5. **Step 4.** HAL and SIL integration; watchdog and safe modes.
6. **Step 5.** HIL, once hardware exists.

## 8. When to reconsider [R]
No roadmap document exists [F-repo, M2 plan §1.2], so the trigger is stated as conditions rather than a milestone number.

Reconsider the language decision at the **first milestone that meets all of these**:
- it introduces onboard-relevant functionality: closed-loop guidance or control, navigation with sensor models, or fault management;
- target-hardware or real-time requirements exist (G1).

It should also be no earlier than:
- the M2 merge;
- the definition of the crew authority boundary (the authorization layer in §3.3), because the Flight Core interface depends on it.

If the AI-crew milestone comes first, that milestone should define the `CommandProposal` and authorization boundary in Python. That boundary is language-independent and is the most valuable preparation.

The Tech Lead is asked to map this trigger to a milestone number (§10, U3).

## 9. Risks
| Risk | Option(s) | Mitigation |
|---|---|---|
| Premature port: the flight core fixes interfaces before requirements exist | all | Step 0 only; port after G1 |
| Two numerical implementations drift apart silently | all | §6 layers; Python remains the oracle; CI differential gate |
| Single-precision target forces re-validation | all | Require hardware binary64 in target selection, or re-validate (new DR) |
| Rust qualification is not yet at DO-178C or ECSS level (vendor states DAL C as a customer-certification target) | C | Choose the assurance standard first; keep the C-ABI option open |
| FFI unwinding or aliasing UB | B (and C's C-ABI) | Flat C API, `panic = abort`, no panics across the boundary |
| Team skill concentration (one language today) | B, C | Spike first; measure effort before committing |
| Scope creep into flight work during simulator milestones | all | Separate authorization; this document authorizes nothing |

## 10. Assumptions and unresolved decisions
**Assumptions [A]**:
- A1. TARS may eventually need software running on spacecraft-class hardware. The task says "eventual", and no requirement documents it.
- A2. The flight subset is the propulsion, dynamics, engine and command logic. The validation and lab code never fly.
- A3. A JSONL adapter can feed an external core's events into the M2 validators. Not yet verified.
- A4. CPU budgets are dominated by future estimation, not propagation. Not measured.

**Unresolved decisions for the Tech Lead**:
- **U1. Resolved (Tech Lead, 2026-10-15):** the repository is Python-based, with no C or Rust implementation. Options A and B would mean new code.
- **U2. Open** (ADR-0008 AT-4). Which assurance standard applies, if any: ECSS-E-ST-40C/Q-ST-80C, DO-178C or NASA-STD-8739.8. This drives the toolchain choice more than language features do.
- **U3. Open** (ADR-0008 AT-7). Map the reconsideration trigger (§8) to a roadmap milestone. A roadmap document would be needed.
- **U4. Resolved (Tech Lead, 2026-10-15):** existing cross-platform limits are **not** reused as cross-language thresholds without independent justification (ADR-0008 TL-7; the method is AT-3).
- **U5. Partly resolved (Tech Lead, 2026-10-15):** language-independent architectural preparation and documentation are permitted (TL-8). Step 0 items that change validated behavior still need separate approval (ADR-0008 AT-6).

## 11. Sources
External sources were consulted on 2026-10-14. Vendor statements are vendor claims.
1. Rust project, *Platform Support* (target tiers): https://doc.rust-lang.org/rustc/platform-support.html
2. Rust RFC 3514, *Float semantics*: https://rust-lang.github.io/rfcs/3514-float-semantics.html
3. `core_float_math` and `core::f64::math::sqrt` (nightly): https://doc.rust-lang.org/core/f64/math/fn.sqrt.html; `libm` crate: https://www.rustmax.net/api/rustmax/libm/
4. Ferrous Systems, Ferrocene release notes 26.02.0 (qualification scope): https://ferrous-systems.com/blog/ferrocene-26-02-0/; Ferrocene 25.05.0: https://ferrous-systems.com/blog/ferrocene-25-05-0/; Business Wire, IEC 61508 SIL 2 core-library subset (2025-12-03): https://www.businesswire.com/news/home/20251203818102/en
5. R. Landau (NASA), *cFS Overview*, ELISA workshop 2024: https://directory.elisa.tech/workshops/2024-12-Maryland/cFS-Overview-Richard-Landau-NASA.pdf; USU SmallSat 2024 F´/cFS comparison: https://digitalcommons.usu.edu/smallsat/2024/all2024/206
6. JPL research poster R19120 (2020), Rust/Scala investigation for flight software: https://www.jpl.nasa.gov/site/research/media/posters/2020/R19120p.pdf
7. ESA contract 4000140242 (Rust onboard-software study): https://nebula.esa.int/4000140242 and its executive summary https://nebula.esa.int/sites/default/files/neb_tec_study/2416/C4000140242ESR.pdf; *Bringing Rust to Safety-Critical Systems in Space* (arXiv 2405.18135): https://arxiv.org/pdf/2405.18135
8. *The Rust Reference*, Panic chapter (panic strategies, `no_std` panic handler, FFI unwinding): https://doc.rust-lang.org/reference/panic.html
9. GCC mailing list, *Concerns regarding the -ffp-contract=fast default* (2023): https://gcc.gnu.org/pipermail/gcc/2023-September/242497.html
10. Rust Embedded WG, *embedded-hal v1.0*: https://blog.rust-embedded.org/embedded-hal-v1/
11. *Kani: A Model Checker for Rust* (ASE 2026; arXiv 2607.01504): https://arxiv.org/abs/2607.01504
12. Arm, *10 useful tips to using the floating point unit on the Arm Cortex-M4*: https://developer.arm.com/community/arm-community-blogs/b/architectures-and-processors-blog/posts/10-useful-tips-to-using-the-floating-point-unit-on-the-arm-cortex--m4-processor; Cortex-M7 FPv5 SP/DP options (LLVM review D5537): https://reviews.llvm.org/D5537
13. G. J. Holzmann, *The Power of Ten: Rules for Developing Safety-Critical Code* (2006): https://www.cs.otago.ac.nz/cosc345/resources/nasa-10-rules.pdf

Gaps in the sources:
- The DO-178C, ECSS and RTEMS Rust-support statuses were not verified beyond the vendor and ESA summaries above.
- The RTIC and Embassy maturity claims come from secondary sources.
- The tier of `riscv32imac` was taken from the official table (Tier 2); `sparc-unknown-none-elf` is Tier 3.

## 12. Tech Lead decisions (2026-10-15)
Recorded in full in ADR-0008, "Tech Lead decisions".
- **Accepted:**
  - Python remains the reference (TL-1).
  - Rust is the preferred candidate for future Flight Core investigation, not a rewrite (TL-2).
  - The five layers are **Flight Core, Mission Laboratory, AI Navigator, Hardware Abstraction and Ground/Operations** (TL-3).
  - Deterministic authorization stands between AI recommendations and commands (TL-4).
  - Safety and fault handling are independent of AI (TL-5).
  - The language is deferred until hardware, real-time, numerical, memory and assurance requirements exist (TL-6).
  - Platform limits are not reused as cross-language thresholds without justification (TL-7).
  - Language-independent preparation and documentation only (TL-8).
  - No C or Rust implementation (TL-9).
- **Change from this document's proposal:** the fifth layer is Ground/Operations, not Verification Infrastructure. The §3 diagram and §3.2 table above are kept as originally proposed. Where verification sits is open decision ADR-0008 AT-1; the proposal is that it becomes a cross-cutting concern.
- **Still open:** ADR-0008 AT-1…AT-7.

