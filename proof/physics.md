# Physics Proof

For each meaningful physics capability:
- [ ] Analytical/known-case unit tests exist where practical.
- [ ] Integration behavior is tested.
- [ ] Relevant conservation/invariant/error checks are measured where applicable.
- [ ] Reference validation is performed against GMAT initially when applicable.
- [ ] Reference configuration/version is recorded so comparison is reproducible.
- [ ] Material discrepancies are classified and documented.
- [ ] Tolerances are explicit and justified.
- [ ] Scientific assumptions have registry entries and authoritative sources.
- [ ] Questionable requirements discovered by validation are escalated with a recommendation rather than silently changed.

## Prototype Milestone 1 target scaffold
When Milestone 1 (Earth + spacecraft + gravity) is implemented, its Proof should include at minimum:
- stable propagation for 10 simulated orbits under the chosen prototype model;
- measured orbital-period error against a trusted reference configuration;
- measured orbital-state drift/error appropriate to the selected integrator/model;
- documented explanation for meaningful GMAT discrepancy;
- no unexplained numerical instability.

Exact tolerances must be established from justified model/validation work, not invented here in advance.

## Milestone 1 implementation
- Thresholds (versioned): `proof/thresholds/m1.json` (status and approval recorded in the file; see DR-0008).
- Validators: `toolbox/validators/m1_proof.py`, `toolbox/validators/determinism.py`, `toolbox/scripts/gmat_m1.py compare`.
- Proof record: `proof/records/M1-orbit.md`.

## Milestone 2 draft scaffold (pending approval)
The draft M2 Proof requirements P1–P12 are in [`docs/milestones/M2-propulsion.md`](../docs/milestones/M2-propulsion.md) §10. Oracles and threshold method are in DR-0015.
- Nothing here is approved yet.
- M2 thresholds will live in `proof/thresholds/m2.json` after a measurement-based threshold DR.
- M1 thresholds and gates are unchanged and remain required (P10).
