| Item | Status | Evidence |
|---|---|---|
| REV-T3-01 | RESOLVED | All ten rejection codes leave state, schedule, counter, committed propellant and `_used_command_ids` unchanged (`review_scratch/deep.out`). Rejected IDs can be reused. |
| REV-T3-02 | PARTIAL | Original forged-copy and mutable-subclass probes now reject; ordinary commands are copied independently. An overridden `model_dump()` still bypasses validation and preserves aliases; exceptions also escape. See N1–N2. |
| REV-T3-03 | RESOLVED | Rejected events retain validated intent and bounded schema errors. Thrust telemetry matches the simulator RHS for prograde and retrograde; outcome mutations change execution fields while planned consumption stays fixed. |
| REV-T3-04 | RESOLVED | Original malformed-Unicode submissions produce serializable rejection events. Direct event construction has a separate remaining gap, N3. |
| REV-T3-05 | RESOLVED | Exact T2 scheduling signature restored. Engine-level burns have null command IDs; submitted burns share the deterministic burn sequence. |
| REV-T3-06 | RESOLVED | Adapted probes reject boolean/float M2 versions and malformed correlation IDs. M1 version behavior remains unchanged. |
| REV-T3-07 | RESOLVED | Negative tests now use valid controls, change one property and assert precise validation errors. |
| Versioned machine-readable schemas | PASS | Version fields, discriminated parser and all seven M2 event round-trips verified. |
| Exact approved rejection codes | PASS | Exactly ten codes; every code independently exercised. |
| Stable correlation IDs | PARTIAL | Normal paths satisfy uniqueness and deterministic numbering; N1 bypasses the command boundary. |
| Intent separate from outcomes | PASS | Rejected intent preserved; executed duration, consumption and Δv derive from transitions. |
| Immutable, deterministic records | PARTIAL | Normal M2 records use immutable tuples; separate processes produce identical event hashes. N1 retains mutable command contents; N3 admits unwritable records. |
| T2/M1 compatibility | PASS | Full regression suite passes; M1 proof passes and golden hash remains `7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4`. |
| Permissions and architectural scope | PASS | Fix diff adds no AI permissions, provider dependencies or runner emission wiring. |
| Contract accuracy | PARTIAL | “Every submission” is canonically copied and “never raises” remain false. Precedence also omits the early propulsion-configuration check, N4. |
| Surviving mutant equivalence | QUALIFIED | Removing the issuer validator is redundant under current Pydantic validation. Removing Unicode sanitization preserves the tested rejection paths, but is **not globally equivalent**: the direct `safe_text('\ud800')` contract fails (`review_scratch/mutants.out`). |

### N1 — Overridden model dumping restores the validation and aliasing bypass

**Severity:** High  
**Claim:** `parse_command()` trusts a virtual `model_dump()` result; Pydantic then accepts returned command instances without revalidation.

**Evidence:** In `review_scratch/edge.py.txt`, a `BurnCommand` subclass defines `model_dump(...): return self`. After `model_copy(update={'schema_version': 2, 'issuer': []})`, submission is **accepted**, and `receipt.command is payload` is **True**. The simulator schedules the burn; converting its receipt subsequently fails event validation. Boundary: `src/tars/sim/commands.py:121–123`.

**Suggested fix:** Extract untrusted model data without relying on caller-controlled dumping, enforce the exact field set, and validate a plain mapping into a fresh exact `BurnCommand`. Test overridden dumping and serializers.

### N2 — Payload failures still escape `submit()`

**Severity:** Medium  
**Claim:** The promised rejection receipt is not guaranteed for malformed Python payload types.

**Evidence:** `review_scratch/edge.out` records escaping `RuntimeError` from a model’s overridden `model_dump()`. A malformed dictionary subclass whose `get()` raises also escapes through `readable_field()`. The latter runs while constructing a rejection, outside the parsing guard (`simulator.py:370–375`, `commands.py:133`).

**Suggested fix:** Contain ordinary payload-processing exceptions across parsing, diagnostic extraction and echo extraction; return a minimal `schema_invalid` receipt when extraction fails. Preserve process-control exceptions.

### N3 — M2 event strings can validate but fail serialization

**Severity:** Medium  
**Claim:** Normal validated M2 event construction still admits invalid Unicode in unconstrained string fields.

**Evidence:** `review_scratch/edge.out` demonstrates accepted lone surrogates in `CommandAccepted.issuer`, `CommandRejected.issuer` and `CommandRejected.detail`, followed by `PydanticSerializationError`. `review_scratch/deep.out` reproduces this for `SpacecraftConfigured.direction_laws`. `schema_errors` likewise uses unconstrained strings. Normal converter output passes the original Unicode probes.

**Suggested fix:** Apply valid-Unicode validation to every free-form M2 event string, including tuple elements. Test direct model construction and serialization. Keep M1 schemas unchanged.

### N4 — Documented rejection precedence omits configuration checking

**Severity:** Low  
**Claim:** The contract’s stated ordering does not match submission without propulsion.

**Evidence:** `_schedule()` checks `_spacecraft is None` before duration and chronology. Thus a schema-valid non-positive-duration command submitted without propulsion receives `no_propulsion_configured`, whereas the contract lists non-positive duration as the next rule after duplicate ID.

**Suggested fix:** Document where `no_propulsion_configured` takes precedence and add a combined-failure assertion, preserving approved T2 behavior.

**T3 verdict: FAIL** — Ran the requested pytest (**542 passed**), Ruff checks (**passed; 123 files**), determinism (**golden hash preserved**), M1 proof (**all gates passed**), adapted original probes, expanded boundary/atomicity/telemetry probes and isolated mutant checks. Artifacts are under `review_scratch/`; Git metadata is absent, so supplied commit identity could not be independently verified.