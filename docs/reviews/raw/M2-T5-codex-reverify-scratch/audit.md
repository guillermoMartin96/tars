# T5 independent re-verification at supplied f5f3866 snapshot

No implementation files were edited. All intentional review artifacts are here.

## Commands

All seven requested commands exited 0. gate0.log: 772 tests passed (two existing overflow warnings); gate1.log: lint/format; gate2.log and m2.json: 76 checks passed; gate3.log and m1.json: M1 Proof; gate4.log: cross-process replay; gate5.log: golden M1 comparison; gate6.log: GMAT M1 comparison.

## Prior findings

sweep.py, sweep-results.json and sweep.log: rotated initial orbit rejected by O4/O8; 3000 s stop rejected by outcomes/O4/O8; active-stop bogus completion rejected; missing depletion event rejected.

fast.py/fast-results.json: actual main-run powered sample at 660 s rejected. targeted.py/targeted-results.json: literal old 630 s sample mutant still passes all 76 checks. The main scenarios sample at 600 and 660 s, not 630 s. The literal mutant affects the O8 auxiliary runs (with_dt uses every-tick telemetry), which are checked only for final-position convergence. It therefore exposes remaining F3 coverage, not a failure of the new main-run O4 sample comparison.

fix-tests.log: seven new regression test cases pass. revert_tests.py selectively disables each fix in memory: revert-F1.log, revert-F2.log, revert-F3.log and revert-F4.log contain the expected failing regression tests. old_m2.py was reconstructed from the supplied fix diff only in scratch. No source checkout was reverted.

## Mutation evidence

Every successful mutation in fast-results.json, extra-results.json and targeted-results.json passed all 76 full checks, including O6/O8, exact checks, replay, control, boundary and unused thresholds. This does not assert that a permanently patched simulator would pass every existing unit test. The harness caches unmodified run outputs and the deterministic DOP853 reference, then changes fresh result/event-list copies; it does not cache computed validator results. Reference caches include scenario hash, independent initial state and all mark times. Mutations are consistently applied to replay/control calls, so those checks cannot hide a deterministic defect.

fast.py covers individual fields; extra.py covers correlated depletion-time mutation, non-O6 ignition-state corruption and O3 wrong duration; targeted.py isolates nonfinal propulsion mutations from unrelated idle/boundary constraints and tests missing O4 thresholds plus a corrupt powered sample. receipt-cli/ contains a real CLI output with commands=[] although the log contains CommandAccepted and its complete burn; CLI exited 0.

## Complete consumer inventory

- All event envelopes: types/order, tick/time equality, monotonic ticks, engine report tick, uniqueness, sampling cadence are checked. Typed schemas constrain syntax/finite values; no independent schema-version/type audit is performed by m2 Proof. Unknown body event types cause an exception rather than a false PASS.
- SimulationStarted: r/v independent O4 checks on physics missions; identity, hash, software, epoch, time scale, seed, constants, forces, integrator and dt unchecked. No physical reference on empty/no-propulsion variants.
- SpacecraftConfigured: dry/propellant mass, thrust/Isp/g0, exhaust velocity and mdot exact independent comparisons; direction laws and timing budget unchecked.
- CommandAccepted: ID, burn sequence, tick, declared status, ignition/duration/direction/policy checked. Issuer unchecked. Planned duration/consumption and timing bound unchecked. Cutoff/cause largely self-consistency with lifecycle events; depleted cutoff not independently checked against D1a time.
- CommandRejected: ID (with schema-invalid exception), tick, reason and valid intent checked. Issuer/detail/schema errors unchecked. Schema-invalid intent check covers only ignition/direction, not duration/policy.
- BurnStarted: IDs, direction, commanded times, ignition time and report tick checked. Planned cutoff self-consistent with acceptance; planned cause unchecked. r/v used by O6/O7 but not independently tested at ignition; unit vector and total mass unchecked. Propellant only reconciled against cutoff consumption (or final active accounting in main missions), not independently at all transitions.
- BurnEnded: IDs, cause, direction, ignition, commanded/executed duration, plan cutoff consistency, report tick, used propellant, sensed/reported rocket delta-v, r/v reference and plane/sign tests checked. Planned used propellant and total mass unchecked; remaining propellant linked to start and depletion bound, not independent general mass-state expectation.
- PropellantDepleted: exact adjacency, matching IDs/time and report envelope checked. Residual payload unchecked.
- StateSampled: exact cadence; r/v independently checked only in physics main missions. altitude unchecked. Auxiliary O8/O6 samples not checked.
- PropulsionSampled: cadence, mass identity/nonnegativity/nonincrease, idle constancy, cumulative endpoint accounting and acceleration magnitude checked. Exact independently predicted schedule only at final sample. Intermediate powered propellant/delta-v not independently predicted. Direction only checked on ticks with StateSampled; disabling engine flag bypasses magnitude/direction checks.
- OrbitCompleted: order/envelope only. Presence, numbering and interpolated crossing time unchecked against trajectory, RunResult crossings or completion count.
- SimulationCompleted: success/cause and requested duration checked; r/v independently checked on physics missions and exact final-state consistency on all. Orbit count and altitude extrema unchecked.
- ValidationResult: generated from Check, not expected simulator output. An inserted event does not quietly pass the event-rank checker.
- RunResult: unsubmitted IDs independently checked; final tick/r/v and selected final propulsion fields reconciled. receipts, samples, crossings, initial, status/cause, final.t, final propulsion time/direction/plan bodies and returned scenario are not fully reconciled. Proof report consumes status/receipts/final time. CLI consumes receipts/crossings and event completion fields without added validation.
- Thresholds: unknown group/scope and unknown non-null metric fail; unused configured group/scope fails in full mode. Mission overrides merge correctly. Guard does not require mandatory groups/metrics, so removing O4 disables its gates with zero unused entries. Null values filter out and no limits on a group means unconditional numerical PASS. Existing committed non-null limits remain provisional and materially gate reference errors; no weakening was found in supplied fix diff.
- O3: textbook expectation uses reported cutoff time rather than requested duration. Doubling schedule_burn duration for FreeSpace passes all checks.
- O4: independent circular initial state, scenario horizon and independent burn predictions are sound for physics main missions; simulator time labels of cutoffs can disagree with the reference comparison time.
- O5: documented cutoff-state exception; coast arcs checked, powered intervals deliberately excluded.
- O6: documented ignition-state exception; five variants use simulator start/end states without complete per-run contract/reference checks.
- O8: independent reference horizon and dt choices sound, but auxiliary outputs besides final position are unchecked.

## Records and scope

Fresh values agree with VAL-0013 at published precision. measurement.log disproves the statement that all largest sample errors occur at the horizon endpoint: prograde maximum 0.29057399969309866 m occurs at 53400 s; final error at 53700 s is 0.290344132191698 m. The same wording appears in m2.json limit_basis; it is not a justification to change the conservative 0.6 m limit.

F1/F2/F4 fixes and their new tests are accurately described. F3 description must qualify main mission samples versus auxiliary study samples. The old review verdict remains FAIL pending re-verification.

M1 thresholds, gates and platform-specific golden handling preserved; DR-0017 timing delta-v remains separate from trajectory error; FU-1 retained; no T6 GMAT M2 reference, T7 threshold approval or T8 final Proof was introduced.
