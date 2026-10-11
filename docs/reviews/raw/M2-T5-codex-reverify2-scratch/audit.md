# Independent T5 round-2 audit

Snapshot supplied as 344f95a; there is no .git directory in this snapshot, so the commit identity is supplied rather than independently verified. No implementation edits were made. Review scripts and reports are under review_scratch.

## Gates

All seven requested commands passed. pytest.log: 818 tests, two existing overflow warnings. Lint/format passed before adding scratch scripts: all checks passed, 134 files formatted. m2.log/m2.json: 206 checks, provisional, PASS. m1.log/m1.json: approved M1 gates PASS. determinism.log: cross-process hashes identical. cross_platform.log: exact Darwin x86_64 golden match and numerical gates PASS. gmat.log: GMAT M1 gates PASS.

## Probe method and artifacts

fast.py, extra.py and targeted.py adapt the prior executable probes to Gates and the 206-check full Proof. All runs and independent DOP853 reference states are cached, not validator results. Copies are mutated deterministically for main, replay, control and auxiliary runs. Full checks are recomputed for each mutation. Event/result mutations can expose a validation gap without claiming the mutant passes all simulator unit tests. Exceptions reject a mutant and are not counted as false passes.

new_probes.py/new-results.json and more.py/more-results.json extend the inventory. extrema.json separately audits all six missions with sparse-sample extrema. numerical.py/numerical.json changes the production powered derivative in memory, independently of the reference. No source patch or checkout was made.

## Status of F5-F15

- F5 resolved: double-duration O3 rejected.
- F6 resolved for telemetry: all O6/O8 variants audited. The literal 630 s mutation is now a no-op: O8 no longer emits StateSampled at 630 s. The adapted 660 s auxiliary probe and its regression reject corruption.
- F7 resolved: coast-only initial/sample/final trajectory corruption rejected by independent O4, with O5 also applied.
- F8 partially resolved: previous deleted collections/status/time/plan-body mutants rejected. Additional receipt fields and returned plan fields remain unchecked (F16).
- F9 resolved: intermediate pending IDs, engine state, mass and sensed delta-v mutants rejected.
- F10 resolved: reverse acceleration at 610 s rejected against independent reference velocity.
- F11 resolved: ignition state, thrust unit vector, transition total masses and depletion residual mutants rejected. Degenerate zero ignition vectors can raise instead of return a failed check; the scaled nondegenerate probe rejects numerically.
- F12 resolved for event plans and D1a: planned duration/consumption/timing bound, ignition cause, configured budget and correlated 10 us cutoff shift rejected. Returned plans have F16 gaps.
- F13 specified configuration/issuer/schema-error/invalid-intent fields resolved. Free-text detail remains ungated; receipt/event diagnostic reconciliation has F16 gaps.
- F14 partially resolved: orbit deletion/count/number/time and sampled altitude gross mutants rejected, but extrema can understate tick-history extrema (F17).
- F15 resolved: missing O4 fails thresholds_cover_all_metrics, even with no unused configured entries.

## Regression sensitivity

The 818-test clean run includes every new regression. revert_plugin.py disables the corresponding new validator paths in memory, per test; for checks with overlapping detection it disables the overlapping path too. These are selective check removals, not a historical source checkout. reversions.log: 37 failures and 5 passes across 42 selected regression cases; each F5-F14 family has at least one assertion failure. Remaining passes show overlapping older gates. revert-F15.log: its regression fails when _ungated is disabled. These establish that every finding family has a sensitive regression, not that every parameter is uniquely dependent on its designated check.

## Complete consumer inventory

- Envelopes: event type/order, uniqueness, ticks/times, engine report ticks and sampling cadence checked exactly. Schema version is not checked/revalidated (F18). Unknown body types reject by exception.
- SimulationStarted: identity, config hash, software version, epoch/time scale, seed, constants, force models, integrator, dt/tick/time checked against inputs; r/v independently against circular initial state for every mission.
- SpacecraftConfigured: physical vehicle constants/derived quantities exact; direction laws and DR-0017 configured budget exact.
- CommandAccepted: IDs, sequence, issuer, status, tick/time, commanded intent, represented ignition/cutoff/duration/cause, consumption and timing error checked independently/exactly. Every copy in physical event lifecycle checked.
- CommandRejected: ID/readability, tick/time, reason and valid intent exact; issuer/schema errors vs declared inputs; all schema-invalid intent null. Human-readable detail is not independently gated. Returned diagnostic/intent fields are not fully reconciled (F16).
- BurnStarted: IDs, direction, commanded timing and physical event time/report tick exact; planned cutoff/cause independent; r/v independent O4; propellant predicted; total mass identity; unit vector exact relative to independently checked velocity.
- BurnEnded: IDs, cause/direction, commanded/executed durations, represented cutoff/report tick, consumption, remaining propellant, total mass, planned consumption and sensed/reported rocket delta-v checked. State independently O4, and O7 direction/plane gates.
- PropellantDepleted: bidirectional adjacency, IDs/time/report tick and residual equal BurnEnded; latter's remaining propellant independently predicted and D1a bounded.
- StateSampled: cadence and returned snapshot equality exact; every r/v independently O4 on main and auxiliary runs; altitude exact norm(r)-R.
- PropulsionSampled: cadence, mass identity, positivity/nonincrease, idle constancy, magnitude, independent direction at every burning sample, independently predicted engine schedule/propellant/cumulative sensed delta-v, endpoint sums exact or numerical gates. Raw delta-v error report-only, excess error gated.
- OrbitCompleted: numbers/counts/crossing list exact; crossing lies within reported tick; independently located crossings count and coast crossing time gated. Powered crossing intervals are explicitly count-only, not time-gated; supplied missions do not have a crossing inside a burn. This is a limitation if missions are later generalized.
- SimulationCompleted: success/cause/requested horizon, final r/v/result/sample equality, independent horizon state and orbit count checked. Extrema bracket samples and lie inside widened reference apsides, but no two-sided tick-history expectation (F17).
- RunResult: receipts' top-level status/IDs/issuer/reason/burn/tick/time, four accepted plan fields; samples, crossings, initial/final, status/cause/time, final propulsion physical quantities/IDs/direction/plan presence and two snapshot-plan fields reconciled. receipt command/detail/schema_errors, remaining accepted/snapshot plan fields and returned scenario not checked (F16). A rejected receipt's plan is not checked absent.
- CLI: actual propulsion summary builder checked against event receipt projection and final propulsion. Proof report uses audited status/receipt IDs/reasons/final state; burn table fields have physics/event gates.
- Thresholds: unknown entries/metrics fail; unused configured scopes fail in full mode; missing/null gated metrics fail coverage. Explicit report-only metrics and prefixes do not disable required aggregate metrics.
- O3: expectation uses requested interval, and reported ignition/cutoff checked exactly; mass and velocity round-off gates plus position order.
- O4: initial condition/horizon/burn prediction independent, all state samples/transitions/burning directions covered.
- O5/O6: documented own-cutoff/own-ignition exceptions remain; O4 separately gates their physical states. O6 auxiliary outputs audited.
- O8: dt/horizon independent; auxiliary outputs audited; telemetry remains 60 s.

## Numerical bound and threshold bases

For f(t)=F/(m0-mdot*t), f''''=24 F mdot^4/m^5. The one-panel Simpson bound is h^5 max|f''''|/2880. With constant mdot the sensed-dv component of classical RK4 reduces to Simpson, and the derivative maximum is at the end mass. simpson_bound constructs substeps independently from the tick grid and predicted ignition/cutoff, not simulator transition times or mass-flow telemetry. It also truncates at the predicted sample time.

Fresh normal O6 absolute error/bound ratios are about 0.62, 0.97, 0.99, 0.98, 0.98. Bounds range 5.348e-13 to 5.972e-10 m/s. This is conservative and tight, not vacuous. 1 ppm production mass-flow mutant: excess relative error about 4.799e-9 at all five levels, over 1e-12; independent per-sample mass gates also apply. 1 ppm sensed-integrand mutant: excess relative error about 1e-6, rejected by O2 and per-sample accounting. The computed allowance does permit errors within that bound, as any numerical tolerance does. It expands acceptance compared with the raw 1e-12 gate for high-thrust variants, but for a independently derived numerical mechanism, with raw errors retained. VAL-0013 and the review disposition disclose the discovery and changed gate. No arbitrary tuned numerical-limit increase found.

Fresh ignition errors: 0.000690 m / 1.028e-6 m/s; invalid commands 0.007868 m / 9.881e-6 m/s. Direction: 1.31-1.45e-10; invalid commands 1.146e-9. Node time max 3.989e-5 s. These support the stated provisional limits and materially gate mutants. Ignition error being smaller than cutoff error is an observed basis, not a universal theorem. Direction limits are a provisional small-error normalization of velocity limits, supported at the actual burn velocities. The new reference restarts at burning propulsion sample times; fresh values remain within the published precision/reference floor.

Extrema bounds are derived as stated from O4's 0.6 m widening, but gate only outward errors, not accurate reported tick extrema (F17). Per-sample propellant/dv gates use independent analytic accounting and the Simpson allowance and reject physical mutants.

## Scope

Threshold status remains provisional with null approval. M1 files/gates and platform-specific golden handling preserved, confirmed by commands and diff. DR-0017 remains separate from O4/O5/O8 trajectory error. FU-1 retained for T7. No T6-T8 implementation/approval scope introduced. Same-tick submission/ignition reporting remains next-tick, tested by unit tests and full Proof; simulator source is unchanged in the fix diff.
