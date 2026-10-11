# Independent T5 round-3 audit

Snapshot identity 21dac47 is supplied; this snapshot has no Git metadata to authenticate it. No implementation source was changed. All reviewer files are under review_scratch. The local .ruff.toml excludes only generated reviewer scripts, so repository lint/format checks cover the same 134 files as the previous review.

## Probe method

The previous complete field inventory was read and checked against current consumers. fast.py, extra.py, targeted.py, new_probes.py and more.py replay the prior executable mutations against the complete 206-check Proof, including auxiliary and boundary runs. Runs and independent reference states are cached; validator outcomes are recomputed. Baseline copies contain separate event/sample/receipt/crossing collections. Exceptions are rejection, never evidence of a false pass. The literal 630 s probe remains a no-op because this telemetry sample does not exist; the adapted 660 s probe and active propulsion samples are also tested.

complete_plans.py independently changes every field of every accepted receipt plan and every final active/pending plan across the six missions and four boundary variants. It also tests schema versions 999, True, 1.0, '1' and None. All 167 mutations are rejected.

## F16-F18 and regression sensitivity

- F16: commands reconcile with raw scenario intent (including default policy), invalid commands carry no parsed command; detail/schema diagnostics reconcile with events; rejections cannot carry a plan or burn ID. Every BurnPlan field reconciles with independently predicted burns and already-audited acceptance events. Returned scenario equality is checked by complete canonical configuration hash. Full-proof probes and the 167-case independent sweep cover receipt and snapshot fields.
- F17: completion minima/maxima now have absolute, two-sided error gates against DOP853 dense output at every executed tick, including tick zero, bounded by the requested horizon. Sample-only extrema are rejected.
- F18: integer schema version 1 is required, and every serialized event must round-trip through the schema. Full-proof version-999 mutation and the additional version-type sweep are rejected.

old_m2.py is reconstructed by reversing the m2.py portion of T5-fix3.diff in scratch. revert_plugin.py substitutes the exact historical relevant function into the current module, without writing implementation files. F16's nine new parametrized cases all fail with old check_result_consistency; F17's new sample-only-extrema regression fails with old orbit_checks; F18's new version regression fails with old check_event_order. This is function-level historical reversion, rather than a repository checkout. F17's historical function emits historical metric names, so its regression demonstrates sensitivity to removal of the new gated extrema metrics; the separate full-proof sample-extrema mutation demonstrates the current gate numerically.

## Complete consumer inventory

- Envelopes: type/order, uniqueness, tick/time consistency, physical reporting tick and sample cadence checked exactly. Integer schema version and serialized schema revalidation now checked. Unknown/invalid bodies reject, possibly by exception.
- SimulationStarted: scenario identity/hash, version, epoch/time scale, seed, constants, models, integrator, dt/tick/time against inputs; initial r/v independently against the specified circular orbit.
- SpacecraftConfigured: physical constants and derived mass flow/exhaust speed exact; direction laws and DR-0017 configured budget exact.
- CommandAccepted: identifiers, sequence, issuer, status, reporting tick/time, intent, represented ignition/cutoff/duration/cause, consumption and timing error independently checked. Lifecycle copies reconciled.
- CommandRejected: ID/readability, tick/time, reason and valid intent exact; issuer/schema diagnostics against declared inputs; schema-invalid intent null. Human-readable detail is reconciled with the returned receipt, but its wording has no independent physics oracle.
- BurnStarted: IDs, direction, commanded timing, physical time/report tick, planned cutoff/cause, independent state O4, predicted propellant, total-mass identity and unit thrust vector checked.
- BurnEnded: IDs, cause/direction, requested/executed durations, cutoff/report tick, consumption/residual/mass, planned consumption, sensed/reported delta-v, independent O4 state and O7 direction/plane checked.
- PropellantDepleted: required bidirectional adjacency, identifiers, physical/report time and residual equality with independently checked BurnEnded; D1a residual bound retained.
- StateSampled: cadence and returned snapshots exact; all r/v independently O4, including auxiliary runs; altitude equals norm(r)-R.
- PropulsionSampled: cadence, mass identity, positivity/nonincrease, idle constancy, acceleration magnitude and independent burning direction; predicted active/pending schedule, mass and cumulative sensed delta-v checked at every tick. Raw delta-v remains report-only, analytic Simpson-excess gate applies.
- OrbitCompleted: count/number/returned crossing list exact; crossing within reported tick; independent crossing count and coast crossing-time gates. Powered crossing time remains count-only; the supplied reference missions have no node crossing during a burn. This existing limitation matters when generalizing missions.
- SimulationCompleted: success/cause/requested executed horizon, state/result/sample agreement, independent horizon state and orbit count. Extrema now match independent tick-history extrema in both directions, and still bracket telemetry.
- RunResult: complete scenario, receipt status/IDs/issuer/reason/burn/tick/time/command/diagnostics/plan, samples, crossings, initial/final state and time, status/cause/unsubmitted IDs; final propulsion physical fields/schedule/direction and every active/pending plan field checked.
- CLI: production summary builder reconciled with event receipts/final propulsion. Proof report fields derive from audited outputs; burn table fields have event/physics checks.
- Thresholds: unknown entries/metrics, unused configured scopes, missing/null required metrics fail. Explicit report-only entries do not remove required aggregate gates.
- O3: independently requested interval; ignition/cutoff exact; mass/velocity round-off and position order checked. Double-duration simulator mutant rejected.
- O4: independent initial condition, horizon and burn predictions; all samples/transitions and burning directions covered.
- O5/O6: documented own-cutoff/own-ignition choices retained; O4 independently gates the physical states. Every O6 auxiliary output audited.
- O8: independent dt/horizon and all auxiliary outputs audited; telemetry remains 60 s.

## Numerical basis and reference horizon

measure.py integrates an independently written point-gravity/thrust/mass RHS with tighter DOP853 settings (rtol 2.3e-14, atol 1e-10). It splits only at physical burn discontinuities, independently of the production reference's many mark boundaries. Dense output is evaluated at all executed ticks, and the number of evaluated ticks is asserted equal to final_tick+1. Across all 28 main/O6/O8/boundary runs, maximum completion-extrema error is 0.006291532889 m. 0.013 m is approximately 2.066x measured; the maximum disagreement between the two reference segmentations is 1.5181e-7 m. This confirms the stated 6.3e-3 m basis. The new gate is stricter than the old 0.6 m outward-only allowance; no threshold weakening appears in fix3.

horizon.py removes only the new horizon filter, leaving dense extrema enabled. Extrema extend beyond early stops by 18.7495 m (inside burn) or 50.5987 m (before/at ignition), while requested endpoint states remain equal. horizon-gates.json repeats actual audit checks: current early-stop gates pass, filter-reverted gates fail with 18.7501/50.5987 m errors; cutoff-stop remains unchanged. Reference integration is clipped to max(requested marks).

numerical.py repeats the physical 1 ppm mass-flow and sensed-integrand mutations. Simpson error/bound ratios for clean O6 variants are 0.6244, 0.9690, 0.9872, 0.9847, 0.9808. Mutated excess relative errors are about 4.799e-9 and 1e-6 respectively, over 1e-12. The analytic truncation allowance remains separate from the DR-0017 timing bound and from trajectory error.

## Scope

M2 thresholds remain provisional with null approvals. The full diff does not change M1 threshold/golden files or simulation implementations, and the M1/golden commands confirm preserved behavior. DR-0017 remains its own per-burn timing-induced delta-v bound, not an O4/O5/O8 trajectory bound. FU-1 remains open for T7, including its 11-15 micrometre reference-floor consideration. No O9/T6 reference generator, T7 approval or T8 milestone result is claimed or introduced. Same-tick next-tick reporting remains in both explicit regression tests and the full Proof's contract gate.

## Required commands

- PYTHONPATH=src .venv/bin/python -m pytest -q -p no:cacheprovider: 829 passed, two pre-existing overflow warnings.
- .venv/bin/ruff check . and .venv/bin/ruff format --check .: passed; 134 files already formatted. Reviewer scratch files are excluded by scratch-local configuration.
- m2_proof.py --out review_scratch/m2.json: 206 checks, PASS, provisional.
- m1_proof.py --out review_scratch/m1.json: PASS, approved M1 thresholds.
- determinism.py: identical cross-process SHA-256, 7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4.
- cross_platform.py: PASS; Darwin x86_64 platform-specific golden bit-identical, zero final position/velocity difference.
- gmat_m1.py compare: PASS; approved M1 gates, GMAT R2026a.

These commands complete successfully with no implementation changes. Their stdout/stderr is retained in corresponding .log files.

Additional F17 sensitivity: revert_semantic.py retains the old one-sided apsides calculations but maps their metric names to the current names, so the new 0.013 m thresholds still apply. The sample-only-extrema regression also fails under this semantic reversion (revert-F17-semantic.log). Thus sensitivity is not merely caused by historical metric-name changes.

## Final probe result and verdict

All five complete-Proof probe scripts finished: 88 runs total, comprising two clean baselines, one known no-op (nonexistent 630 s StateSampled), and 85 mutating probes. All 85 mutating probes reject: 83 fail gates, two zero ignition-state probes raise; the nondegenerate scaled-ignition probe also fails gates. No remaining substantive false pass was demonstrated. The separate 167-case plan/version sweep likewise rejects every mutation. Rejected free-text-only event-detail edits now fail receipt reconciliation; independently prescribing human-readable wording remains outside the numeric oracle.

Verdict: PASS for T5 at this supplied snapshot. F16, F17 and F18 resolved. All requested gates pass. This does not approve M2's provisional thresholds or claim completion of T6-T8. Full inventory limitations on powered node crossing timing and human-readable diagnostic wording remain documented above.
