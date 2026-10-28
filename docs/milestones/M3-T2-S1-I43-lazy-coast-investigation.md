# M3 T2 S1, I-43: lazy coast context investigation (R-02) — STOPPED for an owner decision

Status: **investigation only; proposal v3 NOT formed, NOT reviewed.** I-43 §2: "If the two
requirements cannot both be satisfied, identify the precise conflict and STOP for an owner
decision. Do not silently weaken U-1." They cannot both be satisfied (§4). No Codex review of a v3
was run, because no v3 exists to review. **S1 is NOT IMPLEMENTED, NOT ACCEPTED, NOT MERGED.**

Evidence: `docs/science/experiments/m3-t2/s1-i43/` (scripts as `.py.txt`, variant patches, outputs).
Same host only (macOS x86_64, CPython 3.12.15, NumPy 2.5.3); scratch source trees only.

## 1. The problem (R-02, Review 02)

v2's coast closure computes `mass = dry + max(float(y[_PROP]), 0.0)` before the legacy force call.
BASE's coast closure never reads `y[_PROP]`. When a custom integrator hands the derivative a float64
ndarray subclass, the new read dispatches to the subclass and can warn or raise where BASE commits.

## 2. Variants built (scratch trees; relative to v2)

| Variant | Coast closure | `ForceContext` | Patch |
|---|---|---|---|
| **v3-L** (Option 1 as selected) | `ForceContext.lazy(lambda: dry + max(float(y[_PROP]), 0.0))`: no read of `y` at construction | new `lazy(source)`: on every read of `total_mass_kg`, calls `source()`, converts with `_owned_float`, validates | `v3L-vs-v2.patch` |
| **v3-S** (control: owned snapshot) | `prop = float(np.ndarray.__getitem__(y, _PROP))`; `ForceContext.deferred(dry + max(prop, 0.0))` | unchanged from v2 | `v3S-vs-v2.patch` |

`np.ndarray.__getitem__(y, 6)` is the base-class C indexer: for any float64 ndarray (including
subclasses) it returns the stored binary64 element without calling a subclass `__getitem__`,
without mask handling, and without warnings. Both variants stay inside the OD-5 regions and the four
allowlisted paths (v3-L adds a `Callable` import and a `_source` slot in `forces.py`).

## 3. Compatibility matrix (dt = 0.5, zero force, finite state; `probe_i43.py.txt`, `probe_ooc.py.txt`)

Part A is everything an S1 caller can observe (the legacy adapter never reads the context):
outcome, tick, committed `r`/`v`/propellant hex, warnings — once recording warnings, once with
warnings raised as errors.

| Stage handed to the coast derivative | Contract | BASE | v2 | v3-L | v3-S |
|---|---|---|---|---|---|
| standard RK4 float64 ndarray | supported | commit | = | = | = |
| float64 `MaskedArray`, propellant masked | supported | commit, no warning | **`UserWarning`**; as error: **not committed** | = | = |
| float64 subclass, `__getitem__(6)` raises | supported | commit | **`LookupError`, not committed** | = | = |
| integrator writes the stage after the call | supported | commit | = | = | = |
| one buffer reused for all RK4 stages | supported | commit | = | = | = |
| RK4 stages as row views of a 2-D workspace | supported | commit | = | = | = |
| object dtype, propellant `None` | out of contract | commit | **`TypeError`, not committed** | = | **`TypeError`, not committed** |
| Python `list` | out of contract | commit | = | = | **`TypeError` (descriptor), not committed** |
| float32 ndarray | out of contract | commit | = | = | = |

"=" means byte-identical to BASE (outcome, state hex, warnings). Also identical to BASE for both
variants: the 26 880-case main corpus (sha256 `e0309486…a814`) and the 26 112-line stage-writer corpus
(`3310fd90…0415`); all 78 v2 S1 tests pass on both (`verify_variants.txt`).

Part B reads the captured coast contexts after the step (a recording adapter stands in for the
consumer that S2+ would add). Stage mass at the call was 1300.0 kg in every case.

| Case | v2 (eager owned, read-validated) | v3-L (lazy) | v3-S (raw owned snapshot) |
|---|---|---|---|
| RK4: read, read again, mutate stage prop to −7, read | 1300 / 1300 / 1300 | 1300 / 1300 / **1000** for stages 2–4 (stage 1 is the read-only committed state: 1300) | 1300 / 1300 / 1300 |
| integrator writes prop = 123 after the call | 1300 | **1123** (both reads) | 1300 |
| shared buffer (4 stages, 1 array) | 1300 each | 1300 each, then **1000 for all four** after one write | 1300 each |
| row views | 1300 each | **1000** after mutation | 1300 each |
| masked propellant | `ValueError` on read (NaN) | `ValueError` on read **plus `UserWarning` at read time, inside the consumer** | 1300 (raw stored value; mask ignored) |
| raising `__getitem__` | step fails before any read | **`LookupError` raised at read time, inside the consumer** | 1300 |
| object `None` | step fails | **`TypeError` at read time** | step fails |
| stage array kept alive only by the context | no | **yes** | no |

## 4. U-1 snapshot analysis: the precise conflict

U-1: "Context is frozen: assignment and deletion raise; mass is converted to owned binary64 (T1 R2-F2
pattern); non-finite or non-positive mass rejected". The T1 R2-F2 pattern is the correction of
"accepted NumPy parameters stored by reference and not converted to binary64"
(`docs/milestones/M3-T1-report.md`). Packet r2 §3: the context is "Built in the simulator's derivative
closures from the stage state".

- An **owned snapshot** taken at construction needs the stage propellant's value at construction,
  i.e. a read of `y[_PROP]` in the coast closure.
- **Option 1** (the R-02 remedy as selected) is that the coast closure performs **no** such read.

These are mutually exclusive for the coast closure. v3-L satisfies Option 1 and BASE compatibility
(every Part A row, including the out-of-contract ones) but not U-1: the context holds a reference to
mutable stage storage (the R2-F2 anti-pattern); its value is the stage's value **at read time**, not at
the derivative call (1123 / 1000 vs 1300); contexts sharing a buffer are aliased; repeated reads differ
across a mutation; the stage array's lifetime is extended; and the subclass's warning or exception is
moved from the closure into whichever consumer first reads the mass. In S1 nothing reads, so none of
this is observable today; the first S2 consumer (drag) would observe it.

v3-S satisfies U-1 (owned binary64 at construction; immune to later writes, aliasing and lifetime
issues; no dispatch, so no warning or exception for any float64 ndarray subclass) and closes R-02 for
every **supported** input. It is not Option 1 (it reads the propellant, without dispatch), it changes
two **out-of-contract** inputs (object dtype; `list`: an exception where BASE commits), and it reads a
masked propellant's stored value rather than treating the mask as "no value".

## 5. Tests drafted (scratch; `test_s1_r02_draft.py.txt`, `draft_tests.txt`)

| Draft test | BASE | v2 | v3-L | v3-S |
|---|---|---|---|---|
| T-07 (l) R-02 regression: masked / raising `__getitem__` stage, warnings as errors, tick commits | pass | **fail** (`UserWarning`, `LookupError`) | pass | pass |
| T-04 snapshot: coast mass equals the stage mass at the call, on repeated reads, after post-call writes and with a shared buffer | **fail** (AttributeError: no context at BASE) | pass | **fail** (assertion: 1123 / 1000 ≠ 1300) | pass |

Every failure is for its intended reason. The existing 78 v2 tests do **not** distinguish v3-L from
v3-S: without the snapshot test, U-1's snapshot property is untested. A mutant "reintroduce the
premature coast read" is v2's coast line itself; T-07 (l) kills it. A mutant "make the coast context
lazy" is v3-L; the snapshot test kills it. The mutation campaign script (I-42/I-43) is not yet
adapted to either variant's anchors.

## 6. Not done (because of the STOP)

No proposal v3; no Codex review of a v3; no M1/M2 Proof, T0, T1 or full-suite run on v3-L or v3-S;
no mutation campaign on them. Done on both: Part A/B matrix, out-of-contract controls, both corpora,
78 S1 tests, draft T-07 (l) and snapshot tests. R-01 closure and the I-42 regression results are
unaffected (they concern the powered closure and v2).

## 7. Decision needed (owner)

1. **v3-S** (owned raw snapshot): keeps U-1 as written and closes R-02 for supported inputs; requires
   accepting that it is not Option 1 and authorizing the out-of-contract deltas (object dtype, `list`)
   or declaring such stages unsupported; and confirming that the masked case reads the stored value.
2. **v3-L** (Option 1 as selected): keeps BASE behaviour on every input; requires an explicit U-1
   amendment for coast contexts (mass evaluated at read time from the referenced stage, not an owned
   snapshot), with the aliasing, lifetime and read-time warning/exception consequences above recorded
   for S2 consumers.
3. Another direction the owner specifies (for example a hybrid: v3-S for float64 ndarrays and v3-L
   for anything else, which keeps BASE behaviour on every input but reintroduces lazy semantics for
   out-of-contract stages).

The implementer recommends **(1) v3-S**, with object-dtype and non-ndarray stages declared outside the
supported Integrator contract (they are outside the `NDArray[np.float64]` annotation), because it
satisfies U-1 without amendment and its only deltas are on inputs the contract already excludes.
