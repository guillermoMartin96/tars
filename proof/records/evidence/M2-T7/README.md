# M2 T7 three-platform measurement bundles (VAL-0016, DR-0023)

Collected with `toolbox/scripts/m2_t7_measure.py collect` at revision `2870392`, from a clean tree on every platform with identical input digests. Aggregated with `analyze` into `analysis.json`.

| Platform (DR-0008 matrix) | Bundles | Hosts |
|---|---|---|
| macOS x86_64 (reference host) | `reference-host` | Intel i9-9880H, macOS, NumPy SIMD X86_V3, Accelerate |
| Linux x86_64 (GitHub `ubuntu-latest`) | `ubuntu-latest-<run>` x5 | EPYC 7763 (no AVX-512), Xeon Platinum 8573, EPYC 9V74 x2, EPYC 9V45 |
| macOS arm64 (GitHub `macos-latest`) | `macos-latest-<run>` x5 | Apple M1 (virtual) |

Workflow runs (tags `t7-measure-1` to `-5`): 38490602383, 38490603373, 38490605790, 38492699696, 38492704906.

Each directory holds:
- `bundle.json`: the environment, input digests, determinism results, mission final states, M1 cross-platform result, the commands with exit codes, and output digests;
- `m2_proof.json`: the full M2 Proof report;
- `deviation.json`: the verify-mode reference deviation.

The record-mode reference files (`record.json.gz`, about 7 MB each) are not committed. Their sha256 digests are in each `bundle.json` (`outputs_sha256`). They stay in the workflow artifacts (`t7-<os>-<run>`), and the reference host's copy is in `runs/t7/reference-host/`.

To reproduce on any platform:

```sh
uv sync --locked
uv run python toolbox/scripts/m2_t7_measure.py collect --out <dir> --label <label>
uv run python toolbox/scripts/m2_t7_measure.py analyze --out <dir> <bundle dirs...>
```
