# DR-0029 P10 — Owner Decision Packet: identity of the pinned J2 value

**Status:** PREPARED FOR OWNER DECISION. **P10 is not decided.** This packet analyses the existing proposal; it decides nothing, changes no production code and does not start T1.  
**Authority:** "I-15 — M3 Transition: Resolve DR-0029 P10 Before T1" (Tech Lead, 2026-10-22). *Numbering note:* the T0 spike authorization of 2026-10-18 ("TARS — M3 T0 Reference-Configuration Spike Authorization", cited in DR-0029) was also numbered I-15. This packet refers to the 2026-10-22 authorization only.  
**Baseline:** `origin/main` = `5fded7c6df50d60564f2bd025aeaf9dab4f541cd` (T0 ACCEPTED, I-13; MERGED by fast-forward, I-14).  
**Evidence labels:** **[T0]** measured in the accepted T0 spike; **[source]** taken from a cited source; **[derived]** computed by reasoning, not measured; **[new, unreviewed]** measured for this packet by `docs/science/experiments/m3-p10/p10_probe.py.txt` (output `p10_probe_output.txt`). It is not part of T0's accepted evidence and has not been independently reviewed.

## 1. Baseline verification (2026-10-22)
| Check | Result |
|---|---|
| `origin/main` | `5fded7c6df50d60564f2bd025aeaf9dab4f541cd` |
| Working tree | clean before this packet |
| T0 history in `main` | `86df2c3`, `3c565e6` (reviewed checkpoint), `095956e` (dossier), `5fded7c` (I-13 record) are ancestors; 32 commits `86df2c3..5fded7c` |
| Review 10 | `docs/reviews/M3-T0-review-10.md`: `VERDICT: PASS (unconditional)`, no new findings |
| I-13 record | `docs/reviews/M3-T0-acceptance-dossier.md` § "Owner acceptance (I-13)" present, unmodified |
| CI on `main` | run 39827298093 at `5fded7c`, four jobs green |
| Branch protection on `main` | none (unchanged; not touched) |

**Merge-status update (append-only):** recorded in the acceptance dossier (§ "Merge status (I-14)"), the T0 report (status update) and the T0 decision matrix (status note). The I-13 "NOT MERGED" wording is preserved as historical.

## 2. Exact text being decided
DR-0029 §P10 (unchanged since T0, quoted verbatim):

> **Evidence.** DR-0024 Q1 records "J2 = 1.0826261739e-3 (= −√5 × −0.484165143790815e-3)". The two are not the same double: −√5 C̄20 = 1.0826261738522227e-3, a relative difference of −4.4e-11 (`t0_model.J2_FROM_C20`). A generated `.cof` carries C̄20.
>
> **Options**
> - **(a)** Pin C̄20 (the NGA source value) and derive J2.
> - **(b)** Pin the decimal J2 and write C̄20 = −J2/√5 into the `.cof`.
>
> **Trajectory effect.** Negligible: about 6.7 m × (4.4e-11 / 8.6e-6) ≈ 3e-5 m [derived from the VAL-0018 tide-system sensitivity]. The physics identity (DR-0026) must still contain exactly one of them.
>
> **Recommendation.** (a), because the source publishes C̄20.

T0 decision matrix row: "Which representation of the approved J2 is the pinned identity?" — "Does not reopen DR-0024 Q1"; "Prerequisite for T1, and (I-15 §6) for T2"; "Reversible before T1. After T1 a change is a new physics identity."

**The question in one line:** DR-0024 Q1 (APPROVED) writes the same J2 two ways that differ by 220 334 ulps. Which one is the value, and which is a derived or display form?

## 3. Why T1 depends on it
- T1 is "J2 force model, pure; analytic unit tests" (M3 proposal). It adds the first J2 constant to the centralized constants module, where a test already enforces that pinned literals appear only there (`src/tars/sim/constants.py`, DR-0003).
- Whatever T1 writes there becomes the value later hashed into `physics_id` (ADR-0009 item 4, DR-0026 Q-G3-2), written into the GMAT `.cof` (DR-0025 Q8) and used by every M3 reference. ADR-0009 requires exactly one canonical value.
- The analytic tests themselves (secular rates, conservation) do not care which of the two values is used. **The dependency is on the pinned identity and its provenance, not on the physics of the tests.**
- The gate is the Tech Lead's (T0 matrix, "Dependency statement": "P10 is a prerequisite for T1").

## 4. Alternatives
| Id | Alternative | Status |
|---|---|---|
| **(a)** | Pin C̄20 = −0.484165143790815e-3 (NGA Table 5.1 string) as the source value; J2 = −√5·C̄20 derived in double = 1.0826261738522227e-3; the decimal 1.0826261739e-3 is a display rounding | DR-0029 option |
| **(b)** | Pin J2 = 1.0826261739e-3 (the decimal written in Q1); C̄20 = −J2/√5 derived = −4.841651438121817e-4 for the `.cof` | DR-0029 option |
| (c) | Pin both, each with a stated tolerance | Considered here; **rejected**: violates the one-identity rule ("must still contain exactly one of them") |
| (d) | Defer: T1 takes J2 only as a parameter; pin at T3 with the physics identity | Considered here; **not available without the owner changing the gate** (P10 is the owner's stated T1 prerequisite) |

## 5. Strongest argument for each
- **(a):** The published quantity is C̄20 to 15 significant digits. The decimal J2 is the project's own 11-digit rounding of −√5·C̄20 (DR-0024 lists it as **[NGA] [derived]**). Pinning the source string keeps the provenance exact, and the T0 `.cof` writer already reproduces that string exactly. All accepted T0 evidence was produced with (a).
- **(b):** It is the number written first and in bold in the APPROVED Q1 row; J2 is the quantity the force model, the analytic rate formulas and most textbooks use, so the literal would match the approved text without a derivation step.
- **(c):** None that survives the one-identity rule.
- **(d):** T1's tests are value-independent, so T1 could start without the decision. It only postpones the choice and leaves T1's VAL record on an unpinned value.

## 6. Evidence
| Fact | Label | Supports |
|---|---|---|
| NGA Table 5.1 publishes C̄2,0 = −0.484165143790815e-3 (EGM2008, tide-free); the decimal J2 in DR-0024 is tagged **[derived]** | [source] DR-0024 refs, line 58 | (a) |
| −√5·C̄20 in double = 1.0826261738522227e-3; the decimal 1.0826261739e-3 differs by −4.413e-11 relative (220 334 ulps) | [T0] `t0_model.J2_FROM_C20`; recomputed [new, unreviewed] | that P10 is a real choice |
| fl(−√5·C̄20) is within 1.4e-16 relative (< 1 ulp) of the exact product of the decimal strings (60-digit decimal) | [new, unreviewed] | (a) is faithful to the source |
| The derivation uses only `sqrt` and one multiplication, which IEEE 754 requires to be correctly rounded; it does not use a libm transcendental, so it does **not** inherit A-FP-2 | [derived]; cross-platform not measured (single-host limitation stands) | (a) determinism |
| The T0 `.cof` writer (`t0_gmat.cof`, format `.14e`) prints C̄20 as `-4.84165143790815e-04`, which reads back to the identical double | [T0 code]; checked [new, unreviewed] | (a) works with the existing generator |
| Under (b), the same `.14e` writer prints −J2/√5 as `-4.84165143812182e-04`; reading it back gives −√5·C̄20 = 1.0826261739000007e-3 ≠ the pinned J2 (a few ulps). A 17-digit (`repr`) print round-trips in Python | [new, unreviewed] | against (b), unless the generator changes; GMAT's parsing of a 17-digit coefficient is **not measured** |
| Every T0 run that used J2 (GMAT `.cof`, spike, P1 floors via `J2_FROM_C20`, the Review checks) used representation (a) | [T0] | (a): T0 evidence applies directly; (b): T0 J2-dependent numbers are for a slightly different J2 |
| Trajectory effect of (a) vs (b), M1 orbit, J2 only, 53 700 s: DOP853 3.20e-5 m final / 3.21e-5 m max; RK4 dt 10 s 3.48e-5 m | [new, unreviewed]; agrees with DR-0029's [derived] ≈ 3e-5 m | neither: below every proposed gate, but **not below** the P6 (b) diagnostic match (7.6e-5 m) |

**What T0 established vs what remains uncertified.** T0 established the two doubles and their difference, and that its own pipeline used (a) consistently. The trajectory effect was only *derived* in T0; the 3.2e-5 m measurement above is new and unreviewed, sampled on one orbit, one host, and is not a bound. T0's acceptance does not turn either into a proof.

## 7. Safety and correctness
- Neither option is physically unsafe: the difference (4.4e-11 relative) is far below the EGM2008 tide-free vs IERS spread (0.25–7.4 m in the planning experiment) that Q1 already settled.
- **The real correctness risk is inconsistency, not the choice.** If the simulator and the GMAT `.cof` use different representations, a 3.2e-5 m offset appears. That is 42 % of the 0.076 mm J2 match that underlies P6 option (b), so a mixed identity could falsely fail, or be absorbed into, a tight exact-configuration J2 link. Whichever option is chosen must be applied to both sides.
- (b) with the current `.14e` generator would create exactly that inconsistency (few-ulp level) unless the generator format changes.

## 8. Implementation consequences for T1 (description only; nothing implemented)
- **(a):** one new constants entry with the C̄20 literal and its source; J2 computed from it (or stored as the derived double with a test that it equals −√5·C̄20 exactly); a test that the decimal 1.0826261739e-3 agrees to < 5e-11 relative as a display check. T1's VAL record cites NGA Table 5.1 directly. The existing `.cof` format needs no change for T4/T5.
- **(b):** one J2 literal; C̄20 derived as −J2/√5 where needed. The `.cof` generator used later must print at least 17 significant digits, and T4/T5 must verify that GMAT reads it to the same double. T1's VAL record cites DR-0024 Q1 and the derivation.
- Either: no change to v1/v2, M1/M2 goldens or `EARTH_J2_APPROX` (informational, M1).

## 9. Validation consequences
- **(a):** the constant is checked by identity: literal = NGA string; J2 = −√5·C̄20 bit-for-bit. All T0 J2-dependent evidence (P1 floors, GMAT J2 runs) stays directly applicable.
- **(b):** identity checks on the J2 literal; T0's J2-dependent numbers apply only up to the 4.4e-11 relative offset. The P1 floors are quoted at 2 dp and are very unlikely to move, but statements such as "unchanged to the last bit" were made for (a) and would need recomputation before being reused under (b).
- Either: how constants are verified ("by identity, not by trajectory gates") is DR-0025 Q-G2-2's sub-rule, still PROPOSED. T1 should not present its constant test as satisfying that rule.

## 10. Reversibility and migration cost
| When changed | Cost |
|---|---|
| Before T1 | None |
| After T1, before any M3 reference (T3) | Small: one constant, its tests, the T1 VAL record |
| After M3 references and GMAT gates exist | Moderate: new `physics_id`; every M3 golden changes at ~3e-5 m and must be regenerated; GMAT `.cof` regenerated; v1/v2 and M1/M2 unaffected |

## 11. Interactions with open decisions
| Item | Interaction | Effect on P10 |
|---|---|---|
| DR-0024 Q1 (APPROVED) | Q1 contains both representations; P10 chooses which is canonical. Under (a) the decimal becomes a display rounding; under (b) the parenthetical "=" becomes "≈" | Requires the owner to state that P10 interprets, and does not reopen, Q1 (the owner is the decider, so this is a condition, not a block) |
| DR-0029 P1–P9 | None of P1–P9 takes J2's value as an input. P1's derived floors were computed with (a) | No dependency; (b) adds a recomputation task for P1 evidence reuse |
| DR-0029 P6 / DR-0025 Q-G2-1 (escalated) | The `.cof` carries C̄20 under every P6 option; P6 (a)/(b)/(d) are all indifferent to P10 provided both sides are consistent. The escalated geodetic-drag item is independent of J2's value | No dependency; consistency constraint only |
| DR-0028 P6(b) scope ruling | Concerns the axis, not the J2 magnitude | None |
| DR-0025 Q-G2-2 sub-rule (PROPOSED) | Concerns how the constant is verified, not which value | None; T1 must not claim it |
| DR-0026 / ADR-0009 physics identity | Requires exactly one canonical value; P10 supplies it. The serialization format is T3 design | P10 feeds it; no dependency |
| M3 planning gate (T0 matrix, I-15 §6 of 2026-10-18) | P10 before T1; P1–P10 before T2 | Defines P10's urgency only |

## 12. Independence classification: **CONDITIONALLY INDEPENDENT**
P10 needs no other open decision or investigation to be completed first; it is not BLOCKED. It is classified conditional rather than fully independent because a safe decision must state three constraints:
1. **Q1 interpretation:** the decision records that it selects the canonical representation within DR-0024 Q1 and does not reopen Q1's value or tide system.
2. **Single, consistent identity:** the chosen representation is the only pinned value, and every consumer (simulator constants, physics identity, generated `.cof`, references) derives from it.
3. **No borrowed certification:** the decision rests on provenance, not on the trajectory effect; the 3.2e-5 m figure stays an unreviewed sample, and DR-0025 Q-G2-2 stays open.

None of A-FP-2, E4b, the missing combined J2-plus-drag missed-crossing bound, the single-host limitation, the unreproduced 5 287-point search or the sampled M3 claim bears on P10: they concern drag, termination and floating-point envelopes, not the value of J2. They remain unresolved and are not weakened by deciding P10.

## 13. Unresolved uncertainty
- GMAT's internal handling of a normalized C̄20 (its own unnormalization) is not inspected; T0 shows end-to-end agreement to 0.076 mm under (a) only.
- Whether GMAT parses a 17-digit coefficient exactly (relevant to (b) only) is not measured.
- Cross-platform behaviour of the derivation rests on IEEE 754 correctly rounded `sqrt`, not on a measurement (single host).
- The trajectory-effect measurement is one orbit, one host, unreviewed.

## 14. Recommendation
**Option (a): pin C̄20 = −0.484165143790815e-3 (NGA.STND.0036 Table 5.1, EGM2008 tide-free) as the source value; J2 = −√5·C̄20 is derived (1.0826261738522227e-3 in IEEE double); 1.0826261739e-3 is its 11-digit display form.**

Rationale, in order of weight: (1) it pins the value the source actually publishes, so provenance is exact rather than a project rounding; (2) all accepted T0 evidence already uses it, so nothing T0 established needs re-derivation; (3) the existing `.cof` generator carries it exactly, whereas (b) breaks the round-trip with the current format; (4) the derivation uses only correctly rounded operations, adding no libm assumption. The strongest counter-argument, that (b) matches the bold Q1 literal, is answered by recording that Q1's decimal is the display form of the derived value.

## 15. Proposed owner decision wording
> **DR-0029 P10 — DECIDED: option (a).** The pinned identity of the approved J2 (DR-0024 Q1) is the EGM2008 tide-free normalized coefficient C̄2,0 = −0.484165143790815e-3 from NGA.STND.0036 Table 5.1. J2 is derived as −√5·C̄2,0 (IEEE double 1.0826261738522227e-3); the decimal 1.0826261739e-3 in Q1 is its rounded display form. This selects a representation within Q1 and does not reopen Q1's value or tide system. Every consumer (simulator constants, physics identity, generated GMAT coefficient file, references) derives from this single value. This decision does not decide DR-0029 P1–P9, DR-0025 Q-G2-1/P6 or Q-G2-2, or DR-0028 P6(b), and does not authorize T1.

(For option (b), replace the first two sentences with: "The pinned identity is J2 = 1.0826261739e-3 (decimal, DR-0024 Q1). C̄2,0 is derived as −J2/√5 and written to any generated coefficient file with at least 17 significant digits, verified to read back to the same double.")

## 16. What each choice means for T1
| | (a) | (b) |
|---|---|---|
| Constant added | C̄20 literal + derived J2 | J2 literal |
| Extra T1 tests | J2 = −√5·C̄20 bit-for-bit; decimal display check | C̄20 derivation round-trip if T1 exposes it |
| T0 evidence reuse | direct | up to 4.4e-11 relative; "last-bit" statements recomputed before reuse |
| Later T4/T5 work | none for the `.cof` | 17-digit `.cof` and a GMAT read-back check |
| Scope of T1 | unchanged | unchanged |

Under either choice T1 still needs its own authorization. Nothing here creates a T1 branch or touches production code.

## 17. Remaining unresolved items (unchanged by this packet)
- DR-0029 P1–P9 (P1–P10 gate T2); DR-0028 P6(b) scope ruling; DR-0025 Q-G2-1/P6 geodetic-drag discrepancy ESCALATED_FOR_INVESTIGATION; DR-0025 Q-G2-2 sub-rule PROPOSED; Q-G2-4 dt PROVISIONAL.
- A-FP-2 and E4b; no certified combined J2-plus-drag missed-crossing bound; single-host validation; the unreproduced 5 287-point search; the sampled, non-proof M3 claim.
- T1 authorization.
