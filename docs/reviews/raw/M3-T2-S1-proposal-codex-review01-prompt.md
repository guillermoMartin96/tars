# Independent review: TARS M3 T2 S1, I-41 "option B for the coast closure only" proposal

You are an independent reviewer from a different provider than the implementer. You review a
**proposal and its scratch prototype**, not committed work. Review is evidence, not authority.

## Setup and rules
- Working directory: a fresh clone of the repository pinned at BASE
  `ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd` (`uv sync --locked` done; run Python with
  `uv run python -B ...` or `.venv/bin/python -B ...`).
- Materials in `review_scratch/pkg/` (sha256 in `SHA256SUMS`, verify first):
  - `I-41-proposal.md`: the proposal under review;
  - `prototype.patch`: the scratch prototype (src/tars/sim/forces.py, src/tars/sim/simulator.py, two new test files), relative to BASE;
  - `harness.py`, `mutate.py`, `ast_identity.py`: the implementer's evidence scripts;
  - `M3-T2-S1-authorization.md`: the owner's I-40 authorization record (commit `c91a3ef`), including the approved I-39A §4 proposal text and the I-39A §5 option definitions.
- Do **not** modify any tracked file of the clone. Work only inside `review_scratch/` (e.g. copy
  `src/` to `review_scratch/proto/src` and apply the patch there, run with `PYTHONPATH`). Use
  `PYTHONDONTWRITEBYTECODE=1` and `python -B`. No network.
- Do not fix anything. Report.

## Owner decisions (verbatim excerpts)
I-40 OD-2: "**APPROVED — Option A.** ForceContext validates `total_mass_kg` at construction according to
the literal U-1 / packet-r2 §3 contract. I explicitly authorize only the characterized failure-path delta
described in §8 for T-07(a) and T-07(b) on the direct `Simulator` API when `dt = +inf`. … That
authorization does **not** extend to any other behavioral difference. Validated scenarios must continue to
reject non-finite `dt_s`. Any T-07 difference other than the specifically recorded T-07(a)/(b) delta is a
mandatory STOP. Do not modify `Simulator.__init__` to reject non-finite `dt` as part of S1."

I-40 OD-5: permitted `simulator.py` changes are limited to necessary imports, `Simulator._derivative`,
`Simulator._powered_derivative` and the closures within them.

I-41 (owner, amending I-40): "I select **Option 2: Option B for the coast closure only**, subject to
verification that it preserves existing finite-`dt` behavior. … Preserve the original OD-2 authorization
for T-07(a)/(b), where `dt = +inf`. For finite `dt`, including cases where `(tick + 1) * dt` overflows to
`+inf`, preserve BASE's observable behavior. The specific regression case discovered in I-40 must remain:
`dt = 1e308`; Zero-force model; Direct Simulator API; Failure at tick 2; Expected exception:
`FloatingPointError`; Expected classification: `non_finite`. Do not convert this failure into `ValueError`."

Option B as recorded (I-39A §5): "mass validated when a consumer reads it; zero behaviour change; U-1 reads
'rejected on use'".

Strategy U-1: "Context is frozen: assignment and deletion raise; mass is converted to owned binary64 (T1
R2-F2 pattern); non-finite or non-positive mass rejected". Packet r2 §3 ForceContext: "Frozen; carries the
stage total mass as owned binary64. Built in the simulator's derivative closures from the stage state
(dry + max(prop, 0)). Non-finite or non-positive mass rejected". DQ-3 (a): "Existing M1/M2 behavior must
remain byte-identical on the specified same-platform regression gates. No change to tick logic, engine
scheduling, step splitting or atomicity is approved by this decision."

## What to evaluate
1. **Finite-dt overflow counterexample, independently.** Write your own probe (do not reuse `harness.py`)
   that reproduces, at BASE and with the patch applied: finite dt (1e308 and others you choose), a
   zero-force legacy model, direct `Simulator` API, a burn inside tick 2 so the last coast sub-step has
   infinite length. Confirm or refute: BASE raises `FloatingPointError("non-finite state produced at tick
   2")`; the prototype raises the identical exception; an option-A variant (coast built with
   `ForceContext(mass)`) raises `ValueError`. Check `src/tars/sim/runner.py` classification.
2. **Exception compatibility.** Search for any direct-API or scenario input for which the prototype's
   exception type, message, cause/context chain, timing (tick, sub-step, RK4 stage) or atomicity differs
   from BASE. Try to break the proposal's §3 argument (especially §3.4: the powered mass can never be
   invalid; and §3.5: dt = +inf admits no burn). Consider OverflowError/ZeroDivisionError conversion in
   `Simulator.step`, warnings, `KeyboardInterrupt`/`BaseException`, NumPy scalar types, subnormals, −0.0.
3. **Numerical behaviour.** Confirm no floating-point operation contributing to a returned derivative is
   added, removed or reordered; same-platform bit identity on M1/M2 paths (spot-check with your own runs).
4. **Authorization boundaries.** Is the proposal within I-40 + I-41 (allowlisted paths, OD-5 regions, no
   composite/ordering/identifiers/DL-5/CI/dependency/threshold change)? Is the option-B reading of U-1 for
   the coast closure faithful to I-41? Are the proposal's §6 owner points complete and correct (for example
   the I-39A §10 mutant "powered context built before the finiteness check → T-07(d)" being equivalent)?
5. **Test plan.** Are the proposed tests and mutants sufficient and load-bearing? Any mutant that should
   be killed but is not? (You may run `mutate.py` or your own mutants in scratch.)

## Output
Final message: `VERDICT: PASS` or `VERDICT: REQUEST_CHANGES`, then a findings table
(ID, severity BLOCKER/MAJOR/MINOR/NOTE, location, finding, evidence/reproduction), then a short section
per evaluation item 1–5 with what you ran and observed. BLOCKER = Critical, MAJOR = High. PASS requires
0 BLOCKER and 0 MAJOR. Save your scripts and outputs under `review_scratch/reviewer/`.
