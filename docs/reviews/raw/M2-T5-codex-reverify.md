### F5 — O3 evaluates the reference at an unverified cutoff time
**Severity:** Medium  
**Claim:** O3 can accept a burn lasting twice the requested duration because its analytic expectation uses the simulator’s reported cutoff time.  
**Evidence:** `extra.py`, mutation `O3.double_commanded_duration`, doubles `schedule_burn` duration only for `FreeSpace`. All **76 Proof checks pass**.  
**Suggested fix:** Verify ignition, cutoff and executed duration independently from the requested interval before evaluating the closed form.

### F6 — Auxiliary study telemetry remains unchecked
**Severity:** Medium  
**Claim:** The original F3 powered-sample mutation still passes in O8 auxiliary runs. Their telemetry receives no trajectory or consistency checks.  
**Evidence:** `targeted.py`, mutation `F3.literal_630_auxiliary_samples`, doubles sample positions at 630 s and passes **76/76** checks. The main missions sample at 600/660 s; the affected 630 s samples belong to auxiliary runs. Corrupting the main sample at 660 s is correctly rejected.  
**Suggested fix:** Apply applicable contract, telemetry-reference and result-consistency checks to auxiliary runs, including O6/O8 variants.

### F7 — Missions without burns have no independent trajectory gate
**Severity:** High  
**Claim:** The empty-tank and no-propulsion missions can report grossly incorrect trajectories while passing every check. Their control runs repeat the same error.  
**Evidence:** `fast.py`, mutation `NoBurn.double_all_states`, doubles all reported position/velocity vectors in these missions and updates the returned final state consistently. All **76 checks pass**.  
**Suggested fix:** Run an independent coast reference and initial-state checks on these missions too.

### F8 — Returned results are only partially reconciled with events
**Severity:** Medium  
**Claim:** Validated events can accompany contradictory `RunResult` fields and misleading Proof or CLI summaries.  
**Evidence:** Separate `fast.py` mutations delete `receipts`, `samples`, `crossing_times` or `initial`; change returned status/cause; corrupt `final.t` or propulsion time; and remove propulsion plan bodies. Each passes **76/76**. `targeted.py` also produces a successful CLI summary with `commands=[]` despite an accepted-command event and complete burn.  
**Suggested fix:** Reconcile all returned fields with scenario expectations and event records, including receipt payloads, snapshots, crossings, times and propulsion plans.

### F9 — Intermediate propulsion telemetry lacks independent expectations
**Severity:** Medium  
**Claim:** Accounting checks constrain endpoints and monotonicity but permit incorrect intermediate mass, sensed Δv and engine schedules.  
**Evidence:** Separate `targeted.py` mutations report bogus pending IDs at 120 s, sensed Δv of 999 m/s during a burn, one kilogram too little propellant with consistent total mass/acceleration, or an idle engine during powered ticks. Each passes **76/76**.  
**Suggested fix:** Predict schedule, propellant and cumulative Δv at every propulsion sample from accepted commands and elapsed burn time.

### F10 — Thrust direction is unchecked between state samples
**Severity:** Medium  
**Claim:** The direction check silently skips propulsion samples without a matching `StateSampled`.  
**Evidence:** `fast.py`, mutation `PropulsionSampled.nongrid_direction`, reverses thrust acceleration at 610 s while preserving its magnitude. All **76 checks pass**.  
**Suggested fix:** Obtain an independently referenced velocity at every burning propulsion sample and check the acceleration direction there.

### F11 — Burn-transition physical payloads escape validation
**Severity:** Medium  
**Claim:** Ignition states, transition masses, thrust vectors and depletion residual payloads can contradict validated physics.  
**Evidence:** `extra.py` scales ignition position/velocity by `1.000001` in depletion/invalid-command missions. Separate `fast.py` mutations set ignition thrust vectors to zero, transition total masses to 999 kg, or depletion residuals to 999 kg. Each passes **76/76**.  
**Suggested fix:** Reference ignition states independently; check transition mass identities and expected remaining propellant; reconcile thrust vectors and depletion residuals with corresponding state/outcome fields.

### F12 — Accepted plans and timing claims are insufficiently verified
**Severity:** Medium  
**Claim:** Several planned quantities are unchecked, and correlated depletion timestamps can disagree with the independently predicted cutoff.  
**Evidence:** Separate mutations pass **76/76** with planned duration/consumption or reported timing Δv set to 999, an incorrect ignition planned cause, or a bogus configured timing budget. `extra.py` also shifts the depletion cutoff and correlated plan/event times by **10 µs**, beyond D1a’s representability allowance, while every check passes. O4 compares the cutoff state at the predicted time rather than verifying its reported time.  
**Suggested fix:** Independently verify complete plans, timing bounds and D1a cutoff timing. Reconcile every copy across acceptance, ignition, cutoff and depletion events.

### F13 — Configuration identity and rejection provenance are unchecked
**Severity:** Low  
**Claim:** The Proof accepts misleading configuration/provenance fields and schema-invalid receipts that echo forbidden intent.  
**Evidence:** `fast.py` mutations independently change every start metadata field, configured direction laws, receipt issuers and schema-error lists; all pass **76/76**. `targeted.py` also passes with non-null duration or policy on schema-invalid rejection events.  
**Suggested fix:** Compare configuration/provenance with scenario inputs and enforce the complete schema-invalid intent and diagnostic contract.

### F14 — Orbit and altitude reporting can be fabricated
**Severity:** Medium  
**Claim:** Orbit events, completion counts and altitude reporting lack independent or exact consistency checks.  
**Evidence:** Separate `fast.py` mutations delete every `OrbitCompleted`, set crossing times to −999 s, change orbit numbers/counts to 999, or corrupt sampled altitude and completion extrema. Each passes **76/76**.  
**Suggested fix:** Verify crossings and counts against the trajectory and returned crossing list; derive sampled altitude from position and validate extrema against the appropriate trajectory history.

### F15 — The unused-threshold guard does not detect missing gates
**Severity:** Medium  
**Claim:** Omitting a required threshold group silently disables its numerical gates while `thresholds_all_consumed` passes.  
**Evidence:** `targeted.py`, mutation `Threshold.missing_O4_and_corrupt_powered`, removes `o4_reference` from a scratch threshold file and doubles powered sample positions in the slice missions. All **76 checks pass**, with zero unused entries.  
**Suggested fix:** Require the mandatory groups and gated metrics for each exercised oracle, alongside the existing unknown/unused-entry checks.

### Summary

**Verdict: FAIL.**

- **F1:** Resolved; rotated initial state rejected.
- **F2:** Resolved; substituted 3000 s stop rejected.
- **F3:** Partially resolved. Main powered samples and bogus active-stop completion are rejected; the literal 630 s auxiliary-sample probe still passes, as F6 demonstrates.
- **F4:** Resolved; deleted depletion events rejected.

All seven requested commands passed: **772 tests**, lint/format, M2 Proof, M1 Proof, determinism, cross-platform comparison and GMAT M1 comparison. Seven new regression cases pass normally and fail under isolated in-memory reversions of their corresponding fixes.

Thresholds remain provisional; no weakening was found. M1 gates and platform-specific golden handling remain preserved. DR-0017’s Δv bound remains separate from trajectory error, FU-1 remains recorded, and no T6–T8 scope was introduced.

Fresh measurements agree with VAL-0013 at published precision. One factual correction is needed in VAL-0013 and `m2.json limit_basis`: the prograde maximum sample error occurs at **53,400 s**—0.290574 m—rather than at the 53,700 s endpoint, whose error is 0.290344 m. The review record’s F3 description also needs the auxiliary-run qualification above.

Executable probes, logs and the complete field inventory are in [review_scratch/audit.md](/private/tmp/claude-501/-Users-guillermomartin--superset-worktrees-tars-actually-splash-f90f9ba4/70aaf0ee-578a-4f8e-b31a-278306be87a9/scratchpad/t5-snap2/review_scratch/audit.md). No implementation fixes were made.