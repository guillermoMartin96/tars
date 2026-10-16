# M3 planning checkpoint — independent review 04

**Scope:** the corrections authorized by the Tech Lead's instruction "M3 Planning — Resolve Review 03 and DR-0028" (I-3), commit `58f0d18`: the DR-0028 resolution (J-ax-1), the M3P3-F1 correction (DR-0024 Q4 conventions revision 2, FC-1…FC-10), the M3P3-F2 correction (verbatim withdrawn Q4 row), and the affected SCI entries, ADR-0009, decision matrix and milestone documents. No M3 implementation exists.  
**Reviewer:** Codex (separate provider), session `01a142d0-dc1c-7c51-a6a0-6fc43c59e3d1`, at `a97c02f`, on a git clone with metadata.  
**Prompt:** `raw/M3-planning-codex-review04-prompt.md`. It carries I-1 §1–8, I-2 §1–7 and I-3 §1–8 verbatim, plus the full review history. **Raw output:** `raw/M3-planning-codex-review04.md`.  
**Instruction for this outcome (I-3 §6):** "If Codex returns REQUEST_CHANGES, record every finding and stop without implementing further fixes." **No finding below has been applied.** The planning branch is not merged, T0 has not begun, and M3 planning is not accepted.

## Verdict
**REQUEST_CHANGES:** two MINOR findings, no BLOCKER or MAJOR. Both findings concern limitation statements added to DR-0028 (and SCI-0013) in `58f0d18`. Neither concerns a decision, a constant, the frame mathematics or historical records.

**The reviewer confirmed:**
- **Scope:** 42 files, all under `docs/`.
- **Historical preservation:** the withdrawn Q4 row matches `23bafd2` byte-for-byte (558 bytes, after removing the block indentation). Revision 1 is unchanged, and the pointer replacement is disclosed.
- **Earlier findings:** all of them (M3P-F1…F5, M3P2-F1…F3, M3P3-F1/F2) are intact with their dispositions.
- **Registers:** additions only (208/0 and 43/0); SCI-0005 and VAL-0007 notes intact.
- **Mathematics:**
  - verified v_B = R v_A + Ṙ r_A and the identity case;
  - FC-10 example: (0,0,−1), vs 0 when the derivative term is omitted and (1,0,0) for the fixed-z shortcut;
  - finite-difference error 1.67e-11.
- **Physics:** J-ax-1 is coherent and co-rotation is treated as air motion. J2 covariance error 2.0e-15 m/s²; geodetic-height invariance error 1.86e-9 m.
- **Atmosphere:** 27 boundary jumps within 1.11e-16; the residual script reproduces its committed output byte-for-byte.
- **Decisions:** approvals and OPEN, DEFERRED and NOT AUTHORIZED items correctly distinguished; constants and retention rule unchanged. ADR-0009 item 17 is a design record only.
- **Local checks:** M1 Proof 7/7, M2 Proof 228/228, GMAT comparisons, M1 determinism, golden zero difference, Ruff.
- **Not verified by the reviewer:** full pytest (interrupted after 262 passed) and remote CI (no network).

## Dispositions (recorded; none applied)
| ID | Severity | Category | Finding | Disposition | Proposed change (not made) |
|---|---|---|---|---|---|
| M3P4-F1 | MINOR | Physical correctness | DR-0028 "Approximation and limitations" says "node and inclination geometry relative to the true equator are offset by up to the pole offset". The inclination difference is bounded by the pole separation, but the ascending-node difference is not: Codex computed 0.2598° for a 0.15° pole tilt at i = 30°, and the node becomes singular near-equatorially | **ACCEPTED.** Correct: a pole tilt δ changes the node longitude by roughly δ/sin i, which is unbounded as i → 0. The implementer's sentence was not sourced and is wrong for the node | Distinguish pole separation, inclination difference and node difference. Remove the pole-offset bound for the node. Describe the accumulated trajectory error as configuration- and duration-dependent, citing the measured VAL-0018 values |
| M3P4-F2 | MINOR | Physical correctness | DR-0028 "No longitude, no ground position" and SCI-0013 status update 2 list local solar time among the outputs that need an Earth rotation angle. The solar hour angle at the subpoint is α_sc − α_Sun, in which the rotation angle cancels. Local solar time needs a solar ephemeris, a time convention and a consistent equatorial reference, not a terrestrial longitude | **ACCEPTED.** Correct: the Earth rotation angle cancels in the hour-angle difference | Keep local solar time out of M3 scope, but give the correct reason (no solar ephemeris or time convention in M3). Keep the valid restrictions on longitude, geographic ground tracks and site visibility. Apply in DR-0028 and SCI-0013 as append-only corrections |

## Validation evidence at the reviewed commits (implementer)
Recorded in the checkpoint report: the Proof in an isolated clone at `58f0d18`, and CI for `58f0d18` and `a97c02f`.

## Status after this review
- Not an unconditional PASS, so the I-3 §6 stop condition applies. **No planning acceptance report has been prepared, the branch is not ready for acceptance, it is not merged, and T0, T1 and T2 have not started.**
- **Returned to the Tech Lead:** authorization to correct M3P4-F1 and M3P4-F2, and whether to run another review round.

## Resolution of findings (appended 2026-10-16; the sections above are unchanged)
**Authority:** the Tech Lead's instruction "M3 Planning — Review 04 Corrections and Final Verification" (2026-10-16), referred to as **I-4**. Section 1 authorizes:
- the M3P4-F1 and M3P4-F2 corrections;
- one further independent Codex review (review 05).

It does not authorize a merge, T0 or any implementation.

### M3P4-F1 (MINOR): pole tilt does not bound the ascending-node error
- **Original finding:** DR-0028 said node and inclination geometry are "offset by up to the pole offset". Codex showed a node-longitude change of 0.2598° for a 0.15° tilt at i = 30°. Disposition at review time: ACCEPTED.
- **Refinement of the review-time disposition.** That disposition wrote that the node longitude changes by "roughly δ/sin i". More precisely, to first order:
  - the node *point* moves along the orbit by up to δ/sin i;
  - the node *longitude*, with frame-carried x axes, moves by up to δ|cot i|. That is never more than δ/sin i.
  - Codex's 0.2598° equals δ cot 30°. Both measures are unbounded as i → 0.
- **Authorized decision (I-4 §1):**
  - inclination bounded by the tilt;
  - node amplified by about tilt/sin i away from singular configurations;
  - near-equatorial nodes poorly conditioned or undefined;
  - the counterexample preserved and its assumptions verified;
  - geometric bounds distinguished from approximations.
- **Exact correction:**
  - **DR-0028 "Resolution amendment 1", item 1** (appended). It contains the exact geometric bound |Δi| ≤ δ; first-order estimates for Δi, the node-point shift and the node longitude, each labelled as an approximation with its validity condition; the longitude-origin dependence; the review-04 example with its assumptions; near-equatorial values; and a trajectory statement limited to the measured VAL-0018 values.
  - The original DR-0028 bullet is kept, with a pointer.
  - **SCI-0013 status update 3** (appended).
  - **DR-0024 amendment-log entry** for the §11 sentence "node and ground-track geometry differ … by about 0.15° of pole offset". The §11 sentence itself is kept.
- **Evidence:** `docs/science/experiments/m3-planning/dr0028_node_sensitivity.py`, output `dr0028_node_sensitivity_results.json`. It is standard-library geometry, and a rerun is byte-identical.
  - The review example is reproduced as 90.2598055437°.
  - The largest |Δi|/δ over all sweeps is 1.0.
  - The swept node maxima agree with |cot i| and 1/sin i to within 0.4 %.
- **Residual uncertainty:** none on the geometry. The real-Earth tilt δ(t) is taken from DR-0024 §3.3 and was not re-derived.
- **Changes an acceptance decision?** No.

### M3P4-F2 (MINOR): local solar time does not need an Earth rotation angle
- **Original finding:** DR-0028 and SCI-0013 listed local solar time among the outputs that need an Earth rotation angle. Disposition at review time: ACCEPTED.
- **Authorized decision (I-4 §1):**
  - record that the rotation terms cancel in the solar hour angle;
  - record that M3 lacks the solar ephemeris and time convention;
  - keep local solar time out of scope;
  - authorize no solar ephemeris, orientation provider or local-solar-time implementation.
- **Exact correction:**
  - **DR-0028 "Resolution amendment 1", item 2** (appended). It contains the derivation H = (α_sc − θ) − (α_Sun − θ) = α_sc − α_Sun; the MLTAN definition quoted from [McK] §II; what M3 lacks (solar ephemeris, a time convention connecting simulation time to it, a mean-Sun convention); the fact that no M3 force needs it; and the scope and non-authorization.
  - The restriction on longitude, ground tracks and visibility is kept.
  - The original bullet is kept, with a pointer. SCI-0013 status update 3 records the same correction.
- **Evidence:** the derivation above. The source PDF was read on 2026-10-16 (sha256 recorded in DR-0028).
- **Residual uncertainty:** none.
- **Changes an acceptance decision?** No.
