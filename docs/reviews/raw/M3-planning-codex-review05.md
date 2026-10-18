### M3P5-F1 — Signed first-order formulas contradict the specified passive rotation

**Severity:** MINOR  
**Category:** Mathematical consistency  
**Where:** `docs/decisions/requests/DR-0028-m3-earth-fixed-frame-realization.md`, Resolution amendment 1, item 1, first-order estimates; associated node-sensitivity experiment.

**Claim:** The signs of both signed estimates are reversed relative to the experiment’s convention and the preserved counterexample.

**Evidence:** The amendment gives:

```text
Δi ≈ δ cos(Ω − φ)
ΔΩ ≈ −δ cot i sin(Ω − φ)
```

The script specifies passive component transformation `R = Rot(e, −δ)`, where `e = (cos φ, sin φ, 0)`. With

```text
h_A = (sin i sin Ω, −sin i cos Ω, cos i)
h_B = h_A − δ(e × h_A) + O(δ²),
```

and changes defined as B minus A, differentiation instead yields:

```text
Δi ≈ −δ cos(Ω − φ)
ΔΩ ≈ +δ cot i sin(Ω − φ).
```

Independent direct-matrix calculations in `review_scratch/independent.py` produced:

```text
i = 30°, φ = 0°, δ = 0.15°, R = Rx(−δ)

Ω = 0°:
  computed Δi       = −0.150000000000°
  printed estimate = +0.150000000000°

Ω = 90°:
  computed ΔΩ      = +0.259805543688°
  printed estimate = −0.259807621135°
```

The latter is the preserved review-04 example itself. Its positive change contradicts the signed formula immediately above it.

The script correctly computes the magnitude results, but `compare()` takes absolute values of both changes. Consequently, its sweeps cannot detect these sign errors.

**Suggested resolution:** Append a correction explicitly defining changes as B minus A and correcting both signs for the existing passive-rotation convention. Add signed known-answer comparisons to the research evidence. Preserve the original formulas through the required amendment history.

## Summary

**REQUEST_CHANGES** — one MINOR finding.

Reviewed HEAD: `1c53d0e77c1075f8afb22a4ce5182edd78821f3f`; correction commit: `b411b5f784830f6bb21c3840e9baa9aa1cb7cdbe`. The supplied clone has detached HEAD.

Verified independently:

- **Node geometry:** The spherical triangle inequality gives the exact bound `|Δi| ≤ δ`. The node-point displacement magnitude is first-order `δ|sin(Ω−φ)|/sin i`; the longitude-change magnitude is `δ|cot i sin(Ω−φ)|`. Their envelopes, conditioning limits, angular dimensions, and dependence on longitude-origin convention are otherwise correctly distinguished.
- **Required reproduction:** Ran `.venv/bin/python -I docs/science/experiments/m3-planning/dr0028_node_sensitivity.py review_scratch/node.json`; `cmp` confirmed byte-identical committed output. Independently obtained node longitude **90.259805543688°**, node-point shift **0.299997943861°**, and inclination change **0.000340085438°**. Near-equatorial sweep results reproduce **29.999773°**, **89.499998°** with one undefined node, and **180°**.
- **Solar time:** Independently verified cancellation in `(α_sc−θ)−(α_Sun−θ)` and the noon-offset time conversion. Retrieved the [McKinley paper, §II](https://ntrs.nasa.gov/api/citations/20080012667/downloads/20080012667.pdf) and confirmed the quoted MLTAN definition. The missing solar ephemeris, ephemeris-time connection and mean-Sun convention are accurately identified. Geographic restrictions and implementation prohibitions remain intact.
- **History and regressions:** Read all four review records and raw outputs in full. Earlier findings and dispositions remain recorded. Byte checks confirmed their previous contents remain preserved, baseline register lines remain unchanged, and the withdrawn Q4 quotation matches its historical **558 bytes**. Register diffs are **218 additions/0 deletions** and **43/0**.
- **Atmosphere:** Independently recomputed all **27** boundary jumps, agreeing within **1.11×10⁻¹⁶**. Recomputed lowest-band ratio **1.0013804525694443**. The residual-consequences script reproduced its JSON byte-for-byte.
- **Consistency and scope:** `git diff d92ab89..HEAD --stat`, name checks, and protected-path comparisons show **47 changed files, all under `docs/`**. No merge, production implementation or frozen-contract change appears. Removed lines since `16b6888` are limited to three index/status lines. J-ax-1, identity transformation, atmospheric co-rotation, FC-1…FC-10, constants, table evidence, retention rules and deferred decisions remain intact.
- **Local validation:** M1 Proof **7/7**, M2 Proof **228/228**, golden-state comparison with zero position/velocity differences, and both committed GMAT comparisons passed. Ruff lint and formatting passed. Full pytest and three-platform execution were not rerun. Git whitespace checks reported Markdown hard-break spaces; excluding those, the check passed.
- **CI limitation:** `gh run list … --commit b411b5f…` failed connecting to GitHub. Final-commit remote job conclusions remain unverified.

Remaining gates:

- **T0:** Planning acceptance, explicit merge/T0 authorization, and successful planning merge remain required.
- **T1:** Requires the T0 evidence/review checkpoint and separate authorization; DR-0028 no longer blocks it.
- **T2:** Additionally requires owner decisions on DR-0027 A-4/A-5/A-6/A-s/B-4. T0-checkpoint reference-method, mission, geodetic-source and scenario-value deferrals remain deferred. Snapshot treatment remains deferred to T4; numerical thresholds require later measured evidence.

**The planning package is not ready to be presented to the Tech Lead for planning acceptance as documentation evidence until M3P5-F1 is resolved.**