# External Review: M2 Task T2 — propulsion inside the simulator

**Reviewer/model:** OpenAI Codex CLI 0.162.0, model `gpt-6.1-sol`, session `01a12845-1141-7203-972c-88ef85b8afec`. This is a separate provider from the implementer (Claude).  
**Date:** 2026-10-10  
**Reviewed revision:** `ee091df` (branch `milestone-2-propulsion-f90f9ba4`), as a git-archive snapshot without git metadata. Diff `f8e62c4..ee091df`.  
**Scope:**
- T2 code and tests: `src/tars/sim/simulator.py`, the propulsion additions, `tests/test_simulator_propulsion.py`, and the extended M1 public-API allowlist test;
- ADR-0007 T2 implementation notes and VAL-0012;
- checked against DR-0013, DR-0014 (as amended), ADR-0007, SCI-0008…0012, and the architecture and testing playbooks.

**Raw:** `raw/M2-T2-codex.md`. Prompt: `raw/M2-T2-codex-prompt.md`. Reviewer probes and mutation scripts, verbatim: `raw/M2-T2-codex-scratch/`.

## Summary
**Verdict: FAIL.**

The reviewer confirmed:
- nominal physics;
- M1 preservation: it reconstructed the pre-T2 simulator, and the state bytes match with and without a spacecraft at dt = 10, 0.1 and 7/3;
- the 7a4e1877… hash and M1 Proof PASS;
- exact reproduction of VAL-0012;
- an independent DOP853 right-hand side;
- strict `abs=0` comparisons.

It found:
- one transactional defect (F1);
- schema-ordering defects in scheduling (F2);
- an extreme-input representability inconsistency between plan and integration (F3);
- mutable retained event evidence (F4);
- a test gap: transition r/v were never checked (F5).

## Findings

### REV-T2-01 — Failed steps leave the engine schedule partially advanced (F1)
**Severity:** Medium  
**Reviewer claim:**
- Engine transitions are committed before integration succeeds. If a step raises (non-finite state), tick and physical state are unchanged, but the engine is already `BURNING`.
- A retry omits the ignition and burns 3 s instead of 2 s (0.4804 kg vs 0.3203 kg).

**Evidence:** `raw/M2-T2-codex-scratch/probes.py`.  
**Implementer disposition:** `ACCEPTED`  
**Implementer reasoning:** Correct. A tick must be atomic: either everything (state, tick, engine schedule, transitions) advances, or nothing does. This is the simulator-owns-reality invariant applied to the engine state.  
**Resolution/evidence:** pending.

### REV-T2-02 — Scheduling classifies malformed inputs before validating them (F2)
**Severity:** Medium  
**Reviewer claim:**
- `-inf`, `"-1"`, `True`, `np.array(-1)` and `np.bool_(True)` are rejected as `ignition_in_past` instead of `schema_invalid`.
- `10**1000` raises an uncaught `OverflowError`.

**Evidence:** `raw/M2-T2-codex-scratch/probes.py`, `extra_checks.py`.  
**Implementer disposition:** `ACCEPTED`  
**Implementer reasoning:** Correct. The early-ordering checks coerced with `float()` before schema validation. The DR-0014 amendment assigns non-real and non-finite inputs to `schema_invalid`, which must take precedence. The overflow also affects `plan_burn` (`math.isfinite` on a huge int).  
**Resolution/evidence:** pending.

### REV-T2-03 — Represented event interval can disagree materially with planned consumption (F3)
**Severity:** Medium  
**Reviewer claim:**
- At ignition 1e15 s, a 0.1 s burn is represented by events 0.125 s apart (the float64 time resolution at 1e15 s).
- The integration burns 0.125 s, while the plan and the committed propellant assume 0.1 s.
- In the depletion variant, the floor absorbs 0.008 kg, contradicting ADR-0007's "≤ 1e-12 kg". Sensed Δv exceeds the rocket equation.

**Evidence:** `raw/M2-T2-codex-scratch/probe_results.txt`.  
**Implementer disposition:** `ACCEPTED` (with one constant surfaced for Tech Lead confirmation; see resolution)  
**Implementer reasoning:**
- Correct. The plan must describe what is integrated. Absolute event times are float64, so the executable burn interval is `cutoff − ignition`, not the commanded real number.
- Fix: the plan's burn duration and consumption are computed from the represented interval, so plan, integration and propellant accounting agree to round-off.
- A burn whose represented interval differs materially from the intended duration is rejected as `burn_unschedulable`. "Materially" needs an explicit representability rule; see the resolution.

**Resolution/evidence:** pending.

### REV-T2-04 — Retained transition arrays can be made writable and rewritten (F4)
**Severity:** Low  
**Reviewer claim:** `EngineTransition` arrays own their data, so a caller can set `writeable = True` and alter the simulator's retained event evidence. Physical state is unaffected.  
**Evidence:** reviewer snippet in `raw/M2-T2-codex.md`.  
**Implementer disposition:** `ACCEPTED`  
**Implementer reasoning:** Evidence records must be immutable (machine-readable from day one). Back the arrays with immutable storage, so the flag cannot be re-enabled.  
**Resolution/evidence:** pending.

### REV-T2-05 — Tests do not validate transition position and velocity (F5)
**Severity:** Medium  
**Reviewer claim:** replacing the transition r and v with zeros passes all 155 targeted tests.  
**Evidence:** `raw/M2-T2-codex-scratch/mutations.py zero_transition_state`.  
**Implementer disposition:** `ACCEPTED`  
**Implementer reasoning:**
- Correct, and the same lesson as REV-T1-05: every published quantity needs a check that can fail.
- T3 will publish these states as BurnStarted/BurnEnded events.
- Fix: check transition states against the free-space closed form (zero force model) and an independent orbital DOP853 reference, at boundary, interior and multiple-event ticks, and verify that retained records stay stable.

**Resolution/evidence:** pending.

## Proof gate
- [x] All Critical findings resolved (none raised)
- [ ] All High findings resolved (none raised; Medium findings block T2 completion per Tech Lead instruction "fix blocking review findings")
- [x] Every substantive finding has an explicit disposition
- [ ] Accepted fixes re-tested
- [ ] Reviewer re-verification

**Review gate result:** BLOCKED. Fixes in progress.
