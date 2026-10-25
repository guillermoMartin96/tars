# Decision Request: M3 atmosphere validity boundary, decay termination, and the Q10 table residuals

**Status:** RESOLVED WITH CONDITIONS (Tech Lead, 2026-10-15, "M3 planning checkpoint continuation", section 2). A: termination altitude APPROVED WITH CONDITIONS. B: atmosphere table CONDITIONAL APPROVAL. Open sub-items and T0 obligations are listed in the Resolution; no numerical altitude is approved. Where the body below differs from the Resolution, the Resolution governs. **Update (2026-10-25, append-only): A-4, A-5, A-6, A-s and B-4 DECIDED by the owner under I-26** (DR-0029 P1–P5; Resolution, "I-26 note"). No numerical altitude is approved.  
**Requested from:** Guillermo / Tech Lead  
**Date:** 2026-10-15  
**Related milestone/issue:**
- M3, Option A. Raised by the resolutions of DR-0024 (Q8, Q10) and DR-0026 (Q-G3-6), as those resolutions require.
- Source keys are defined in DR-0024 §3.1.

Nothing here is implemented. No value below is a default.

## Problem
Two numerical questions were deliberately left open when G1–G3 were resolved:
- **A. Where a decaying M3 run ends.** The owner approved the principle: no indefinite extrapolation below the modelled domain; an explicit validity boundary and a re-entry/termination event; no invented universal altitude. The number, and how it is set, are undecided.
- **B. Three cells of the atmosphere table** that the Q10 check could not confirm against an author-published source (DR-0024 §3.4).

Neither blocks T0, which uses them only as explicit, labelled spike inputs. A blocks T2/T3 (drag integration, end conditions). B blocks pinning the M3 dataset identity (T2).

## Constraints
- Preserve the source model faithfully (DR-0024 Q5a). No value is altered to force continuity.
- Do not invent a numerical altitude to close a decision.
- Scenario parameters are explicit inputs; constants and datasets are pinned (DR-0024, DR-0026).
- M1/M2 behaviour, including the `impact` end at spherical altitude ≤ 0 (SCI-0006), is unchanged.

## A. Validity boundary and termination
### Facts
- **The table's modelled domain** starts at the 0 km band (0.010 km in the author's file) and has no upper limit: the top band applies above its base [GMAT-UG; DR-0024 §3.4]. Geodetic height is never below spherical altitude for a point outside the ellipsoid, because the ellipsoid lies inside the sphere of radius a. So for committed states the v1/v2 `impact` rule (spherical altitude ≤ 0) is reached no later than geodetic height 0.
- **RK4 intermediate stages** can evaluate states slightly below a committed state's height. A density function that raises an exception there would turn a legitimate final step into a failure. The behaviour below the lower edge must therefore be defined explicitly.
- **The drag model's physical assumptions** (free-molecular flow, constant C_d, rigid body) fail well above the ground. The project holds **no cited source** for a specific altitude at which they fail. Altitudes commonly used as conventions exist (for example a re-entry "entry interface" and the 100 km Kármán line), but none has been read and verified for this request, so none is proposed.

### Options
- **A1 — A mandatory per-scenario v3 field** (for example `altitude_floor_m`, geodetic) with no default. Reaching it ends the run with a defined outcome (`reentry`, per DR-0026). Each scenario's value cites its basis.
  - Pros: no universal number; validation scenarios state what they assume.
  - Cons: every drag scenario must justify a value.
- **A2 — One pinned project-wide floor** in the physics configuration (part of `physics_id`), with a cited basis chosen by the owner.
  - Pros: one identity, consistent across scenarios.
  - Cons: needs a defensible source now.
- **A3 — The table's lower edge only (0 km geodetic) plus the existing `impact`.**
  - Pros: uses only the source's own domain.
  - Cons: integrates drag through altitudes where its assumptions fail, which the owner's principle discourages.
- **Sub-question A-s (any option):** density for an intermediate RK4 stage below the lower edge: (i) evaluate the lowest band (the source's own formula) only for intermediate stages, with the committed-state boundary check ending the run; or (ii) fail closed as a run error.

### Recommendation
- **A1, with A-s (i).** A1 avoids inventing a universal number and keeps the decision visible in each scenario.
- The value used by M3 reference scenarios is to be proposed at the T0 checkpoint **only if** a source is found, and otherwise left to owner judgment, explicitly labelled as such.

## B. Q10 residual table cells
### Facts (DR-0024 §3.4; `q10_table_check_results.json`)
| Cell | GMAT R2026a file | Author's `ATMOSEXP.DAT` | Effect |
|---|---|---|---|
| Lowest base altitude | 0.0 km | 0.010 km | Heights below 10 m only. **Corrected (M3P2-F3):** the whole lowest band, 0.010–25 km: GMAT density 0.13785 % lower at every height (ratio exp(0.010/7.249)); below 0.010 km the author's table has no band. See Resolution, "Correction M3P2-F3" |
| 900 km scale height | 181.05 km | 181.045 km | Above 900 km only; 2.8e-5 relative in H |
| 1000 km row | 3.019e-15 kg/m³, 268.00 km | absent | Above 1000 km only |

The printed table was not available to the project.

### Options
- **B1 — Pin the GMAT R2026a file unchanged** as the dataset of record, with provenance "GMAT R2026a, citing Vallado 5th ed. §8.6; 25/28 rows confirmed against the author's data file". Keeps the exact GMAT configuration.
- **B2 — Pin the author's file values** (27 rows; top band 900 km). Loses the exact GMAT match above 900 km; GMAT would need a generated table.
- **B3 — Defer pinning** until a printed copy is checked; restrict M3 reference missions to below 900 km meanwhile.

### Recommendation
- **B1**, together with a request to check the printed table when a copy is available. Any difference found later creates a new dataset identity; it never edits the pinned one.

## Impact
- **Architecture:** A decides one v3 field and one outcome; B decides one dataset digest.
- **Science/validation:** SCI-0015 and SCI-0016 limitations; boundary tests (DR-0025).
- **Dependencies:** none.
- **Development effort:** small.
- **Token/compute impact:** negligible.
- **Reversibility:** high before T2. After T2, a change creates a new `physics_id`.

## Blocked work
- A: T2/T3 end-condition and drag-integration design.
- B: pinning the M3 atmosphere dataset identity (T2).

## Work continuing independently
- T0 spike (authorized), with explicit labelled inputs. *(Narrowed 2026-10-15: T0 needs the Tech Lead's explicit approval of the planning checkpoint as well as the planning merge; continuation instruction, section 7.)*

## Requested response
`A1`/`A2 <value + basis>`/`A3`, `A-s (i)`/`(ii)`, and `B1`/`B2`/`B3`, or `discuss`.

## Resolution
**Decision (Tech Lead, 2026-10-15, "M3 planning checkpoint continuation", section 2):** A APPROVED WITH CONDITIONS; B CONDITIONAL APPROVAL. Recorded by the implementer; no item below was decided by the implementer. Labels: **APPROVED**, **CONDITION** (a requirement attached to the approval), **OPEN** (not decided), **T0** (to be proposed and validated at T0, then decided by the owner).

### A. Termination altitude
| # | Item | Status |
|---|---|---|
| A-1 | **An explicit per-scenario termination altitude is required, with no implicit default** (option A1). A drag scenario without one is invalid; the code supplies no value | APPROVED |
| A-2 | **Units: metres. Altitude convention: geodetic** (height above the WGS 84 ellipsoid, the same height as density, SCI-0017) | APPROVED |
| A-3 | **No universal numerical altitude is approved or invented.** Option A2 (one pinned project-wide floor) is not adopted | APPROVED (as a prohibition) |
| A-4 | **Permitted ranges** of the per-scenario value: proposed and validated at T0 | T0 → owner |
| A-5 | **Event-crossing behaviour:** how a crossing is detected and located between committed states, the outcome name (`reentry` was proposed in DR-0026 §5.6) and its event fields: proposed and validated at T0 | T0 → owner |
| A-6 | **Interactions with the atmospheric-domain boundaries:** the altitude relative to the table's band edges and lower edge, and to the v1/v2 `impact` rule (spherical altitude ≤ 0): proposed and validated at T0 | T0 → owner |
| A-s | Density for an intermediate RK4 stage below the lower edge (sub-question A-s, options (i)/(ii)): **not selected by the owner.** It is part of the domain behaviour the owner requires to be defined explicitly (B4) and of A-5/A-6 | OPEN (T0 → owner) |
| — | Names: the field name `altitude_floor_m` and the outcome name `reentry` remain proposals (DR-0026 §5.6) until the v3 schema is designed | Proposals only |

### B. Atmosphere table
| # | Item | Status |
|---|---|---|
| B-1 | **The GMAT table is pinned verbatim as the initial reference:** GMAT R2026a `data/atmosphere/earth/EarthExponentialAtmosphereData.txt`, 28 rows, **sha256 `75762f679f82e089a4a6eadaa1251c797a2151aab5311b36b2ae96cffefda85e`**. Its source identity (GMAT R2026a, file path, provenance statement citing Vallado 5th ed. §8.6) is preserved with it (option B1) | CONDITIONALLY APPROVED |
| B-2 | **Condition: document the three disputed cells** (0 km base altitude; 900 km scale height; 1000 km row), **the absence of the 1000 km row** from the compared author source (`ATMOSEXP.DAT`, sha256 `d2be19cc360ded6a12dd2a5b1b7c54049fb70e4108b38494b76ba0aa39b0ef4c`, CelesTrak/fundamentals-of-astrodynamics @ `49df0479c950917c0a2c5ac31f2db6477bba57f6`), **and the uncertainty about the printed edition**: GMAT cites the 5th edition (2022) §8.6, while the author's routine that reads the file cites "Vallado 2007, 562, Ex 8-4" (3rd edition). No printed edition has been read (DR-0024 §3.4). Done below, "Disputed cells" | CONDITION; recorded |
| B-3 | **Condition: no silent repair or substitution** of any table value. A different value set is a new dataset identity with its own decision, never an edit of the pinned one | CONDITION |
| B-4 | **Condition: define domain behaviour explicitly**, including what the simulator does when it reaches an unsupported altitude (below the lowest base; above the top base; the 900–1000 km and above-1000 km regions whose cells are disputed or unverifiable). **Not defined yet:** the behaviour is proposed at T0 with A-5/A-6 and decided by the owner before T2. No behaviour (extrapolation, cutoff or error) is a default meanwhile | CONDITION; behaviour OPEN (T0 → owner) |
| B-5 | **Condition: no claim of definitive agreement with the printed textbook** without checking it. Records say "25 of 28 rows identical to the author-published data file", never "verified against Vallado's table" | CONDITION |
| — | Option B2 (the author's values) and option B3 (defer pinning) are not adopted. A later check of a printed edition is allowed and, if it differs, leads to a new dataset identity (B-3) | Not adopted |

### Disputed cells (condition B-2)
Values from `q10_table_check_results.json`; consequences from `q10_residual_consequences_results.json` (both in `docs/science/experiments/m3-planning/`).
| Cell | Pinned (GMAT) | Author's file | Density consequence (GMAT ÷ author − 1) | Status |
|---|---|---|---|---|
| Lowest base altitude | 0.0 km | 0.010 km | **−0.13785 % at every height 0.010–25 km**; below 0.010 km the author's table selects no band. It also sets the 25 km jump (GMAT +1.36e-3; author −1.89e-5) | Disputed; pinned value kept |
| 900 km scale height | 181.05 km | 181.045 km | 0 at 900 km; +7.6e-6 at 950 km; +1.5e-5 just below 1000 km | Disputed (rounding); pinned value kept |
| 1000 km row | 3.019e-15 kg/m³, H 268.00 km | absent | Above 1000 km the two sources use different bands: −7.3e-7 at 1000 km; **+19.6 % at 1100 km, +145 % at 1500 km, +500 % at 2000 km** | Unverifiable from available sources; pinned value kept |
| Printed edition | cites 5th ed. (2022) §8.6 | routine cites 3rd ed. (2007), p. 562, Ex 8-4 | Not checked | Uncertain |

The last row shows why B-4 matters: above 1000 km the pinned table and the compared source differ by tens to hundreds of percent, so "what happens at an unsupported altitude" has numerical consequences, not only formal ones.

### Correction M3P2-F3 (authorized by the Tech Lead, 2026-10-15)
- **Original finding (review 02, MINOR):** DR-0024 §3.4 and this DR's §B said the 0.0 vs 0.010 km base altitude affects "heights below 10 m only".
- **Correction:** it scales the density of the whole lowest band by exp(0.010/7.249) = 1.0013805 (GMAT 0.13785 % lower than the author's file for 0.010 ≤ h < 25 km). The 0–25 km band is therefore **not** confirmed against the author's source. The §B table cell is annotated, not rewritten; DR-0024 §3.4 carries the same correction under its original bullet.
- **Evidence:** closed form above; `q10_residual_consequences.py` (rerun byte-identical) reproduces it at sample heights. Review 02 computed the same ratio independently (1.00138045256944).
- **Residual uncertainty:** which value the printed table carries is unknown. No trajectory effect was simulated, because no planned orbit enters the band.
- **Acceptance impact:** none. No acceptance decision depends on the 0–25 km band. The correction matters to the choice of termination altitude (A-4, A-6) if a scenario's altitude is below 25 km.

**Reasoning/notes:**
- The owner's two conditions on no default and no universal number (A-1, A-3) mean T0 can propose ranges and behaviour, but cannot choose a scenario's value for it.
- B pins the GMAT bytes because the exact-configuration GMAT reference uses the identical file (DR-0024 §4.3); the disputed cells are documented, not resolved.

**Follow-up:**
- T0 (once the Tech Lead approves this checkpoint): A-4, A-5, A-6, A-s and B-4 proposals, with evidence.
- Before T2: owner decisions on those proposals.
- Any check of a printed edition: recorded as a new finding; a difference creates a new dataset identity (B-3).
- *(T0 note, 2026-10-18, append-only.)* The T0 proposals for A-4, A-5, A-6, A-s and B-4 are in **DR-0029** (P1–P5), status OPEN. Evidence: VAL-0019. Every item above keeps its status (T0 → owner, OPEN, CONDITION); no termination altitude or domain behaviour is decided.

### I-26 note (2026-10-25, append-only): owner decisions on A-4, A-5, A-6, A-s and B-4
Authority: "TARS — Authorization I-26: M3 Owner Decision Recording, Gate Amendment, and T2 Authorization Preparation" (owner/Tech Lead, 2026-10-25), §2. The owner's text is recorded verbatim in DR-0029 (P1–P5), which this note points to. The tables above are kept as written; where they say "T0 → owner" or "OPEN" for these items, this note governs.

| # | Was | Now | Decision (DR-0029 section) |
|---|---|---|---|
| A-4 | T0 → owner | **DECIDED** | P1: A4-b. Clause 1, a − b < h_f < h_geod(initial). Clause 2, ρ(h_f)·V_b·dt/B_min ≤ κ, with κ = 0.01, v̂ = V_b and B_min from the dry mass. A necessary admissibility screen, not a sufficient stability or accuracy guarantee; it bounds the drag velocity-Jacobian contribution only. κ is an owner-selected engineering constant. **A-3 stands: no numerical altitude is approved**; the admitted values follow each scenario's B_min and dt |
| A-5 | T0 → owner | **DECIDED** | P2: A5-b. Committed-state detection, plus a scalar cubic-Hermite crossing time that is not a state; the run ends at the committed state; no step splitting; missed dips a documented limitation, with no perturbed-motion bound claimed |
| A-6 | T0 → owner | **DECIDED** | P3: precedence `non_finite` → `reentry` → `impact` → `escape`; `impact` kept as the legacy backstop; termination from geodetic height, independent of band selection; published discontinuities preserved |
| A-s | OPEN (T0 → owner) | **DECIDED** | P4: option (ii), fail closed. Every finite geodetic height below 0 m raises a typed atmosphere-domain error, guarded in metres before any conversion; −0.0 in range; non-finite heights a distinct error; no partial commit |
| B-4 | CONDITION; behaviour OPEN | **DECIDED** (the behaviour is now defined, as the condition requires; its implementation is still T2's) | P5: the DR-0029 region table with the owner's wording amendment. Above 1000 km the top band is extrapolated and labelled unverified; no zero-density cutoff and no upper-domain failure; no continuity imposed at any base (the 1000 km base keeps its ≈ −1.598e-5 jump) |
| Names | Proposals only | Unchanged for field names | The owner's P3 text uses the outcome `reentry`. Whether that fixes the contract identifier is confirmed at T3 contract design (open-issues register OI-23). `altitude_floor_m` stays a proposal |

- **Unchanged:** A-1, A-2, A-3; B-1 (CONDITIONALLY APPROVED), B-2, B-3 and B-5. The pinned table and its digest are unchanged.
- **Implementation:** A-4 … A-6 are T3 work; A-s and B-4 are T2 component behaviour. **Neither is authorized by I-26.**
