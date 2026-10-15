# ADR-0008: Flight-software architecture and implementation language

**Status:** Proposed. Not approved, and no implementation is authorized.  
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

## Decision (proposed)
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

## Requested response
- Approve or amend items 1–4.
- Answer RES-0001 §10 U1–U5. U1 confirms that no external C core exists; U2 names the assurance standard; U3 maps the trigger to a milestone.
- Optionally authorize the host-only spike (RES-0001 §7, step 1) as a separate task.

## Related
- Decision Request: none yet. Raise one if a spike or Step 0 work is authorized.
- Architecture: `playbook/architecture.md` invariants 1–5; ADR-0001, ADR-0002, ADR-0004, ADR-0007; DR-0013, DR-0014 §6, DR-0017, DR-0023.
- Proof: M2 Proof (P1–P12) as the equivalence gate.
