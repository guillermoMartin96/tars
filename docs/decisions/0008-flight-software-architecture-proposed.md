# ADR-0008: Flight-software architecture and implementation language

**Status:** **Direction accepted** by the Tech Lead on 2026-10-15 (items marked ACCEPTED in "Tech Lead decisions"). The implementation language is **deferred**. Items marked PROPOSED remain proposals. **No C or Rust implementation is authorized.**  
**Date:** 2026-10-14  
**Decision owners:** Guillermo (Tech Lead); implementing engineer (proposal)  
**Research:** [RES-0001](../research/RES-0001-flight-software-language-and-architecture.md)

## Context
The Tech Lead asked whether TARS should adopt Rust for future embedded, flight-capable software. Three options were requested: continue in C, hybrid C/Rust, and incremental Rust.

Findings (RES-0001):
- **There is no C code.** The simulator is Python 3.12/NumPy/Pydantic (ADR-0001). Its validated asset is the Python implementation plus the Proof apparatus: GMAT and DOP853 references, the reference snapshot and the approved thresholds (RES-0001 §0).
- **The flight-relevant subset is small,** about 1 000 of ≈ 8 600 source lines: dynamics, propulsion, the engine state machine and command validation. Even that subset is not embedded-ready: heap allocation per RK4 stage, unbounded queues and logs, exception control flow, and one loop whose bound is argued but not proven (RES-0001 §1.4, G2–G5).
- **No flight requirements exist.** There is no target processor, real-time deadline, assurance standard, sensor model or roadmap (G1, G7).
- **Numerical reproducibility depends on the FPU and the math library as much as on the language.** The model assumes binary64; many microcontroller FPUs are single-precision only (RES-0001 §4.2).

## Options considered
- **A — C flight core** (new code; the Python reference stays).
  - Strongest heritage and qualification ecosystem.
  - Memory safety rests on discipline and tooling.
  - FP contraction must be pinned by compiler flags.
- **B — Hybrid C/Rust.**
  - Its main justification, preserving validated C, does not apply: there is none.
  - It carries both toolchains, an FFI with unwinding/UB hazards, and two qualification paths.
- **C — Incremental Rust (`no_std`).**
  - Compile-time memory safety, specified IEEE-754 basic arithmetic with no implicit contraction, heap-free builds, and Kani for bounded proofs.
  - Less flight heritage; compiler qualification currently via Ferrocene (ISO 26262 ASIL D, IEC 61508 SIL 3; DO-178C DAL C stated only as a customer target); LEON/SPARC is Tier 3.
- **D — Defer the language choice and prepare language-independent boundaries now** (added by the engineer).

## Tech Lead decisions (2026-10-15)
The Tech Lead decided the following after RES-0001. Each item is recorded as decided and keeps its status label. The engineer's original proposal follows unchanged under "Decision (as proposed)", so the difference between proposed and accepted stays visible.

| # | Decision | Status |
|---|---|---|
| TL-1 | Python remains the validated simulation and research reference. | **ACCEPTED** |
| TL-2 | Rust is the **preferred candidate for future investigation** of an onboard Flight Core. It is **not** an approved rewrite or migration. | **ACCEPTED** |
| TL-3 | Adopt the five-layer architectural direction: **Flight Core, Mission Laboratory, AI Navigator, Hardware Abstraction, Ground/Operations**. | **ACCEPTED** (differs from the proposal; see AT-1) |
| TL-4 | Deterministic authorization stands between AI recommendations and spacecraft commands. | **ACCEPTED** |
| TL-5 | Flight safety and fault handling are independent of AI decision-making. | **ACCEPTED** |
| TL-6 | Final language selection is deferred until hardware, real-time, numerical, memory and assurance requirements are defined. | **ACCEPTED** |
| TL-7 | Existing cross-platform numerical limits (for example DR-0023's 1e-4 m / 1e-7 m/s) are **not** reused as cross-language acceptance thresholds without independent justification. | **ACCEPTED** (answers RES-0001 U4) |
| TL-8 | Language-independent architectural preparation and documentation are permitted. Nothing else is. | **ACCEPTED** (partly answers RES-0001 U5; see AT-6) |
| TL-9 | No C or Rust implementation is authorized at this checkpoint. | **ACCEPTED** |

Items of the original proposal **not** decided by the Tech Lead remain **PROPOSED**:
- C as the fallback if Rust's qualification or target support is insufficient;
- not recommending a hybrid C/Rust core;
- the JSONL adapter as the cross-implementation Proof path;
- the RES-0001 §7 migration steps 1–5.

### Additional technical decisions this ADR now requires (open, recorded explicitly)
| # | Open decision | Why it is needed | Proposed handling |
|---|---|---|---|
| AT-1 | **Where verification sits.** The accepted fifth layer is Ground/Operations; the proposal's fifth layer was Verification Infrastructure. | Verification (oracles, the snapshot, Proof, SIL/HIL harnesses) must still have an owner | **PROPOSED:** treat verification as a cross-cutting concern spanning all five layers, not a layer. Ground/Operations covers mission control, command uplink, telemetry downlink and operator authorization. Needs confirmation |
| AT-2 | **Where the authorization layer runs** (TL-4): on the ground (Ground/Operations), onboard (in front of the Flight Core), or both | Determines the trust boundary and what the Flight Core must re-validate | Decide with the crew/permissions milestone (DR-0014 §6; architecture invariant 2) |
| AT-3 | **Cross-language acceptance method** (TL-7) | The thresholds must be independently justified | **PROPOSED:** measure the differences on the canonical missions, derive bounds by a documented method, and approve them in a dedicated threshold DR (the DR-0008/DR-0023 precedent). Only after an implementation is authorized |
| AT-4 | **Assurance standard** (RES-0001 U2): ECSS, DO-178C, NASA-STD-8739.8 or none | Drives toolchain qualification more than language features do (TL-6) | Open: Tech Lead |
| AT-5 | **Target hardware and real-time requirements** (G1): processor class, binary64 support, memory and timing budgets | TL-6 precondition | Open: requirements-based DR before any processor or RTOS choice |
| AT-6 | **Scope of "preparation"** (TL-8) | Some preparation would change validated M2 behavior: fixed capacities for the burn queue and command history, a proven loop bound or closed form in `plan_burn` | **PROPOSED:** documentation and design only under TL-8. Any change to simulator behavior, contracts or evidence needs its own approval and a Proof re-run |
| AT-7 | **Milestone for reconsideration** (RES-0001 U3) | No roadmap document exists | Open: Tech Lead |

### Planning constraint (Tech Lead, 2026-10-15; recorded at the M3 planning checkpoint)
| # | Constraint | Status |
|---|---|---|
| PC-1 | "Revisit the language/runtime decision before implementing software intended to cross the boundary from simulator/ground tooling into flight-runtime or embedded execution." | **ACCEPTED** (Tech Lead instruction, 2026-10-15). It complements "Reconsider when" below: PC-1 is a gate before such work starts, independent of milestone numbering |

### Status of AT-1…AT-7 at the M3 planning checkpoint (2026-10-15)
All remain **OPEN**. M3 (J2 + drag, Python only) needs none of them answered. DR-0026 §7 (on `milestone-3-planning`) keeps M3 design within TL-6…TL-9: pure force functions over plain fixed-size data, and a canonical physics identity. No FFI, ABI, adapter or migration.
| # | Status | Change since 27ad862 |
|---|---|---|
| AT-1 | OPEN, investigated as a **hypothesis** (below) | Analysis added; no decision |
| AT-2 | OPEN (BLOCKED ON OWNER; with the crew/permissions milestone) | None |
| AT-3 | OPEN, PROPOSED handling unchanged | None |
| AT-4 | OPEN (BLOCKED ON OWNER) | None |
| AT-5 | OPEN (BLOCKED ON OWNER; requirements-based DR) | None |
| AT-6 | OPEN, PROPOSED handling unchanged | None |
| AT-7 | OPEN (BLOCKED ON OWNER); see PC-1, which now bounds it from the other side | PC-1 recorded |

### AT-1 investigation: "Verification is a cross-cutting concern rather than one of the five runtime layers; Ground/Operations remains the fifth runtime layer" (HYPOTHESIS; not an approved decision)
**Definitions used.**
- A *runtime layer* is a partition of the operating system of systems. It has runtime inputs and outputs, a place on the command/telemetry path, and an owner.
- *Verification* means development-time and acceptance-time evidence: oracles, references, the snapshot, Proof runs, SIL/HIL harnesses, independent review. It is distinct from *runtime assurance*: onboard re-validation of commands, limit monitoring and fault management.

**Evidence for the hypothesis (repository, 2026-10-15).**
1. **Verification already spans every existing component without being on the runtime path.**
   - `tars.validation` and `toolbox/` validate `tars.sim` (dynamics, propulsion), `tars.events` (contracts) and the runner.
   - The static guard `tars.validation.architecture` forbids the physics core from importing `tars.validation`. The dependency points only from verification to what it verifies, which is the defining property of a cross-cutting concern rather than a layer.
2. **Each of the five accepted layers needs its own verification:**
   - Flight Core: unit oracles, Proof, SIL/HIL;
   - Mission Laboratory: references, the snapshot, cross-platform gates;
   - AI Navigator: evaluation harnesses, safety-gate tests;
   - Hardware Abstraction: HIL and interface conformance;
   - Ground/Operations: procedure and command-path validation.

   Placing verification as a peer layer would leave it with no runtime inputs or outputs of its own.
3. **The runtime-assurance functions that look like "verification" already have homes in accepted decisions:**
   - command re-validation and fault handling belong to the Flight Core (TL-5; proposal item 1);
   - authorization belongs where AT-2 places it.

   Moving them into a verification layer would contradict TL-5's independence requirement.

**Evidence against, or risks.**
- **Diffused ownership.** A concern owned by "everyone" can be owned by no one. The mitigation is an explicit verification owner and plan per layer, plus a project-level Proof owner, as `proof/` already provides.
- **HIL/SIL rigs are physical or ground infrastructure.** They might be argued into Ground/Operations, but they serve development and acceptance, not operations.
- **Some standards organize verification as a separate discipline with its own lifecycle artifacts.** This is compatible with a cross-cutting concern; it does not require a runtime layer. Not checked against any specific standard, because AT-4 is open.

**What would confirm or refute it.**
- **Confirm:** when the authorization layer (AT-2) and the Navigator exist, every verification element is either (a) development or acceptance tooling with no runtime path, or (b) runtime assurance already owned by Flight Core or authorization.
- **Refute:** an element that must run in operations on the command/telemetry path and belongs to no accepted layer.

**Engineer's assessment (PROPOSED):** the hypothesis is consistent with the repository's current structure and with TL-3/TL-5. Recommend recording it as the working assumption for documentation, and confirming it at AT-2 time. **Not approved; AT-1 remains open.**

## Decision (as proposed, 2026-10-14)
1. **Adopt the target partition** (RES-0001 §3): Flight Core, Mission Laboratory, AI Navigator, Hardware Abstraction, Verification Infrastructure. Use the advisory/authority rules of §3.3:
   - the AI produces proposals only;
   - a deterministic, role-based authorization layer creates commands;
   - the Flight Core re-validates every command against change-controlled hard limits;
   - fault management can override any command;
   - every step is an event.
2. **Defer the implementation-language decision (Option D).** Introduce no C or Rust now.
3. **At reconsideration, evaluate Option C (Rust `no_std` Flight Core) as the preferred candidate.** The condition is that the chosen assurance standard and target processor are supported:
   - a qualified toolchain for the required level;
   - hardware binary64, or an approved re-validation in binary32.

   Option A is the fallback if they are not. **Option B is not recommended** unless an external C asset (for example a mandated framework) must be integrated, and then only behind a flat C ABI.
4. **The Python simulator remains the numerical reference and Mission Laboratory** in every case. Any Flight Core must pass the unchanged M2 Proof through a JSONL adapter, plus the differential layers of RES-0001 §6.

## Reasoning
- With no requirements (G1), choosing a flight language now would fix interfaces and toolchains without the information that determines them: the assurance standard, the processor and the timing budget.
- The partition and the authority boundary are language-independent and valuable now. They protect architecture invariants 1–3 as the AI crew arrives.
- Rust's specified floating-point semantics and compile-time memory safety fit the project's priorities (correctness, then reproducibility). But the advantage is conditional on qualification and target support, which RES-0001 shows are still maturing for space standards.

## Consequences
### Positive
- No migration cost or regression risk now. M2 and the approved baselines are untouched.
- A clear trigger and a ranked option set for the later decision.

### Negative / tradeoffs
- No early hands-on evidence for Rust effort or bit-agreement. A host-only spike (RES-0001 §7, step 1) would give it, and needs separate authorization.
- The embedded-readiness gaps (G2–G5) remain in the Python core until scheduled.

## Validation
When reconsidered, a decision is justified only with:
- a documented assurance standard and target requirements;
- the results of a host-only spike: bit-agreement per kernel, Proof pass through the adapter, and effort;
- a measured cross-implementation tolerance where bit identity is not achieved.

## Reconsider when
- The first milestone that introduces onboard-relevant functionality (closed-loop guidance/control, navigation with sensors, or fault management) **and** has target-hardware or real-time requirements.
- No earlier than the M2 merge and the definition of the crew authority boundary.
- An external constraint mandates a language or framework (for example cFS or F´ integration, or an agency standard).

## Requested response (original; items TL-1…TL-9 above are now decided)
- Approve or amend items 1–4.
- Answer RES-0001 §10 U1–U5. U1 confirms that no external C core exists; U2 names the assurance standard; U3 maps the trigger to a milestone.
- Optionally authorize the host-only spike (RES-0001 §7, step 1) as a separate task.

## Related
- Decision Request: none yet. Raise one if a spike or Step 0 work is authorized.
- Architecture: `playbook/architecture.md` invariants 1–5; ADR-0001, ADR-0002, ADR-0004, ADR-0007; DR-0013, DR-0014 §6, DR-0017, DR-0023.
- Proof: M2 Proof (P1–P12) as the equivalence gate.
