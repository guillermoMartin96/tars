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
