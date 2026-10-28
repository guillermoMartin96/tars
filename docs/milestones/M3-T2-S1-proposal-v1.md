<!-- Verbatim record of I-41 proposal v1 (sha256 d2fe9b38f340f18c91fa02df4f8cff9e95ad9b3465278aa40420a48e78be0151 of the body below this comment block). Reviewed by Codex round 1: REQUEST_CHANGES (R-01 MAJOR), see docs/reviews/M3-T2-S1-proposal-review-01.md. Superseded by v2. Not authorization. -->

# I-41 proposal: S1 with option B for the coast closure only (for owner approval; NOT implemented)

Status: proposal and scratch prototype only. Nothing is committed to the S1 branch. PC-7(S1) remains as
granted by I-40 (record `c91a3ef`, `docs/milestones/M3-T2-S1-authorization.md`), amended only as I-41 decides.

## 1. Owner decision being implemented (I-41)

"Option 2: Option B for the coast closure only, subject to verification that it preserves existing
finite-`dt` behavior." Option B as recorded in I-39A §5 (record `c91a3ef`, §2): "**B:** mass validated
when a consumer reads it; zero behaviour change; U-1 reads 'rejected on use'". Option A (I-40 OD-2):
"ForceContext validates `total_mass_kg` at construction according to the literal U-1 / packet-r2 §3 contract."

Interpretation proposed:
- `ForceContext(m)` validates at construction (option A). Used by the powered closure.
- `ForceContext.deferred(m)` converts m to an owned binary64 at construction (type errors still raise
  immediately) and rejects a non-finite or non-positive m when `total_mass_kg` is read, on every read,
  never caching, repairing or coercing it. Used by the coast closure only.
- `ForceContext()` / `ForceContext(None)`: absent mass (OD-4), read as `None`.
- The legacy adapter never reads the context. Therefore in S1 no production path reads a coast mass.

## 2. Proposed change (exact; scratch prototype patch `prototype.patch`)

`src/tars/sim/forces.py` (additive, appended): `ForceContext` (with `deferred`), `ContextForceModel`
(Protocol), `LegacyForceAdapter`.

`src/tars/sim/simulator.py` (only the OD-5 regions):
- import line: `from tars.sim.forces import ForceContext, ForceModel, LegacyForceAdapter`;
- `_derivative`: `LegacyForceAdapter(self._force_model).acceleration(t, r, v, ForceContext())`;
- `_powered_derivative`: `force_model = LegacyForceAdapter(self._force_model)`;
  - coast: `mass = spacecraft.dry_mass_kg + max(float(y[_PROP]), 0.0)`; `ctx = ForceContext.deferred(mass)`;
    force call `force_model.acceleration(t, r, v, ctx)`; the returned expression is otherwise unchanged;
  - powered: `a = force_model.acceleration(t, r, v, ForceContext(mass)) + thrust` (same position, after
    the finiteness check, the F/m check, `law.direction` and `thrust_acceleration`).

## 3. Why no observable behaviour changes (argument; evidence in §4)

1. Adapter: returns `self.model.acceleration(t, r, v)` directly; same argument objects, same result object,
   exceptions propagate untouched (no try/except).
2. M1 path: `ForceContext()` performs no float operation and cannot raise.
3. Coast: the added operations are a Python-float addition, `max` and `float()` of a NumPy float64; none
   raises (Python float `+` overflows to inf without raising). `deferred` performs `_owned_float` on a
   built-in float (cannot raise) and stores it. Nothing reads it. So a coast stage with NaN propellant
   (any coast sub-step of infinite length: dt = +inf, or finite dt with an overflowing tick end
   `(tick + 1) * dt`) proceeds exactly as at BASE.
4. Powered: the context is built from the existing `mass` after the finiteness check. There, y is finite;
   propellant at any stage is `p0 + c·h·(−ṁ)` with finite h > 0, so it is finite and ≤ p0 (p0 ≤ the loaded
   propellant), or −inf only if y is already non-finite (rejected earlier). Hence
   `dry ≤ mass ≤ fl(dry + p_loaded)`, which `SpacecraftSpec` requires finite; dry > 0. `ForceContext(mass)`
   cannot raise. (Corollary: building it earlier, or deferred, is unobservable: mutants M-14, M-19.)
5. dt = +inf admits no burn: `t = 0·inf = NaN` and every burn is schema-invalid, so the only dt = +inf coast
   paths are T-07 (a)/(b).

Consequence: the OD-2 option-A delta for T-07 (a)/(b) is **not exercised**. Those cases keep their BASE
assertions. The OD-2 authorization remains on record but unused.

## 4. Evidence (scratch prototype at BASE + patch; nothing committed)

- Differential corpus (`harness.py`): 26 880 direct-API configurations (10 dt values including 5e-324,
  1e308, max/2, max and +inf; 21 force models including raising, NaN/inf-returning, mutating, wrong-shape
  doubles; 7 spacecraft including tiny/huge masses and underflowing thrust; 4 initial states; 5 burn
  plans), 3 ticks each plus a retry after any failure; per-step state hex, events, detections, warnings,
  exception type/message/cause/context and post-failure state. BASE vs prototype: byte-identical.
  Sensitivity control: an option-A variant differs in 964 cases (960 at dt = +inf; 4 with finite dt:
  1e308 and 8.98846567431158e307 with the zero-force and list-returning models).
- Validated scenarios: all 5 committed scenarios via `run_mission.py`: output trees byte-identical.
- Proposed tests (§5) green on the prototype (75), T-07 green at BASE (24), T-01…T-06 red at BASE per node
  (51, AttributeError from the absent names; 0 collection errors).
- Mutation campaign: 21 mutants; 19 killed for their declared reason; M-14 and M-19 survive all 75 tests
  and are byte-identical to BASE on the full corpus (equivalent, argument §3.4).
- T-10 AST identity (51 checks) passes; negative control detected. T-11: changed paths within the allowlist.
- R-3 (109 T1 tests; T1 correction checks byte-identical to committed); R-4 and R-1/R-2 results are in
  the I-41 report.

## 5. Proposed tests (replacing the I-39A §9a plan where stated)

- T-07 (a)–(h) unchanged, **with (a)/(b) keeping their BASE assertions** (no replacement assertions).
- New T-07 (i): dt ∈ {1e308, 8.98846567431158e307}, zero-force model, direct API, burn inside tick 2:
  `FloatingPointError("non-finite state produced at tick 2")`, tick 1 committed, state unchanged
  (runner classification `non_finite` by type, `runner.py:252`).
- New T-07 (j): dt = +inf: `t` is NaN and every burn is `schema_invalid` (no split tick).
- T-01 additionally: `deferred` accepts every invalid value at construction and rejects it on every read;
  type errors still at construction.
- T-04 additionally: dry = 1e-3 kg case (makes the clamp observable; at 1000 kg, 1000 − 1e-17 = 1000);
  invalid coast stage mass is carried (NaN) and rejected on read (kills the `max(0.0, x)` swap).
- T-06 fails as a test failure, not by an unrelated exception.
- Mutation list: I-39A §10 plus M-06c, M-07c (coast), M-16 (coast eager), M-17 (`max` order swap), M-18
  (coast absent mass); M-14 and M-19 documented as equivalent survivors.

## 6. Authorization points needing the owner

1. The I-39A §10 row "Powered context built before the finiteness check → killed by T-07 (d)" cannot hold:
   the mutant is equivalent (§3.4). Proposed: document it as an equivalent survivor.
2. T-07 (a)/(b) replacement assertions (I-40 OD-2, §8) are not used; the BASE assertions stay.
3. U-1 / packet r2 §3 ("non-finite or non-positive mass rejected") is satisfied at construction for powered
   and explicit contexts and on read for coast contexts (option B reading, I-41).
4. T-07 gains cases (i), (j); T-01/T-04/T-06 gain the cases above; the mutation list gains five mutants.
