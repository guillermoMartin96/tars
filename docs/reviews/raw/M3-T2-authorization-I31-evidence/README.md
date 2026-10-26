# Pre-authorization probes for the T2 implementation authorization packet (I-31)

Research evidence for `docs/milestones/M3-T2-implementation-authorization-packet.md` §6.8. **Not T2 evidence and not a gate.**

- **Host:** macOS x86_64, CPython 3.12.15, the repository's locked environment (`uv sync --locked`) at `main` `0a9c040`.
- **Inputs:** the T0 spike modules in `docs/science/experiments/m3-t0/`, imported read-only with bytecode writing disabled. No tracked file was modified.
- **Run as:** `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I <probe>.py docs/science/experiments/m3-t0` (`hypot_probe` takes no argument).
- **Files:**
  - `premise_probe`: T0 `geodetic_iterative` with traced `math` calls; A-FP-2 premise per call; |ĥ − h_true| against E1's ε_h.
  - `mutant_probe`: 13 mutants of the path (α) sequence against the ε_h gate.
  - `hypot_probe`: `math.hypot` under argument negation and swap.
- **Limits:**
  - The decimal references (T0's `d_sin`, `d_cos`, `d_atan2`) and `t0_oracle.true_height` state their precision but carry no written error bound.
  - Single host; not run on the CI platforms.
- **Source read for the `hypot` argument:** `https://raw.githubusercontent.com/python/cpython/v3.12.15/Modules/mathmodule.c`, sha256 `436a01da195e3c2b9576a4b9188d5d62e9883e62e74f2d60bc55194bfce98281` (`math_hypot`, `vector_norm`, `dl_mul`, `dl_fast_sum`). Not copied here.
