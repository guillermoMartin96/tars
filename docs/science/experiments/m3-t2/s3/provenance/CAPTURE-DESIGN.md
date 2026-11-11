# Recording-only capture design and its feasibility (owner instruction §3)

Author design and author evidence. Densities are UNVERIFIED ABOVE 1000 KM (P5).

## 1. Instrumentation (external, recording-only)

| File | Role |
|---|---|
| `tools/envcap2.py` | Builds the own-process record. It is loaded **by path** at the end of a process. It runs the unmodified S2 ENV node's `build_record()` from the subject's own `tests/test_s2_environment_record.py`, using a temporary stub `tests.conftest` with `REPO_ROOT` = the subject (restored afterwards). It adds: executable, libpython, `sys.version`, `sys.flags`, pid/ppid, argv/orig_argv, cwd, the origins of loaded `tars*`/`tests*`/`uv_build`/… modules, and an independent `<subject>/uv.lock` sha256. It writes with mode `x`. There is no environment dump: only fixed names, plus the values of path variables |
| `tools/rec/sitecustomize.py` | Inert unless `S3REC_DIR` is set. At start-up it only registers one `atexit` handler. At exit the handler calls `envcap2.capture`. Every exception goes to `<pid>.error.txt`, and the exit status and stdio are never touched |
| `tools/plugin/s3rec_plugin.py` | Pytest observer (`-p s3rec_plugin`). It writes the complete `S2-ENV-RECORD` warning text and, at session finish, the `__file__` of every loaded `tars*`/`tests*` module. It adds no assertion and changes no outcome |
| `tools/common.py` | Constants, the run-record runner, the BC export with blob verification, and the record-completeness predicate `check_env_record` |

Source hashes are in `FEASIBILITY.json` → `instrumentation` and in the packet manifest.

**Injection points:**
- **Isolated PEP 517 hooks (PK-1/PK-2):** `PYTHONPATH=<tools/rec>` plus `S3REC_*` on the `uv build`
  command. This works only because uv propagates them, which F-1 verified rather than assumed.
  `tools/rec` contains only `sitecustomize.py`; a bytecode cache may appear (see §4).
- **`python -I` children of committed tests (S3-T-02b/c, M-29, S3-T-05b), and the pytest main
  process:** a packet-local venv created from the exact 3.12.15 interpreter. Its `site-packages` holds
  a byte-identical copy of `sitecustomize.py`, plus one `.pth` line naming the worktree venv's
  `site-packages`, so the existing locked packages are reused read-only. `.pth` files inside that
  directory are **not** processed, so the worktree's editable `tars.pth` (→ worktree `src`) is not
  applied. `-I` ignores `PYTHON*` variables but still imports `sitecustomize` from the venv
  `site-packages`, and `os.environ` still carries `S3REC_*`.
- **Driver-controlled processes (PK drivers, PK-4…PK-7 payloads, regression tools):** an explicit
  `finally: envcap2.capture(...)` in the same process, after the payload.
- **PATH** is `/usr/bin:/bin:/usr/sbin:/sbin`, so the `sysctl` CPU probes resolve.
  `GIT_CEILING_DIRECTORIES` is set to the parent of each export or subject, so the `commit` field is
  the legitimate `[U] … not a git repository` (exit 128). It is never the `tars-evidence` HEAD. BC and
  its tree are bound separately, by the per-file blob comparison of each export.

## 2. Feasibility results (`feasibility/run-3/FEASIBILITY.json`, record `records/FEAS-run-3.txt`: all pass)

**F-1, disposable uv_build target.** The build used the exact PK flags (`--force-pep517 --offline
--no-index`, the retained wheel with its hash constraint, `--python` 3.12.15, a fresh cache):
- There is exactly one complete record per hook call. The 4 calls are
  `get_requires_for_build_sdist`, `build_sdist`, `get_requires_for_build_wheel` and `build_wheel`.
  Each is bound to its record through the hook code in that process's `orig_argv`.
- Each record holds: the full S2 body with a verified body hash; the libm set (6235 arguments, 7175
  results); `[O]` CPU brand and features; FP; build config; executable `de2897e0…`, libpython
  `2ecb77ef…`; the lock pin both in the body and independently; `uv_build` imported from that
  build's isolated venv.
- Each hook's `sys.path` = the build venv + the 3.12.15 stdlib + the rec dir. Nothing else.
- The uninstrumented and instrumented builds have equal exit status (0) and byte-identical sdist and
  wheel. Stdout is equal. There was no network line.

**F-2, failing target.** The exit status is identical (non-zero) with and without the recorder, and
records are still written for each hook call.

**F-3, `python -I` children in the venv:**
- `sys.exit(3)`, an uncaught exception, a `print` and four `math.exp` bit patterns each give the
  same exit, stdout and stderr with and without the recorder.
- Each gives one complete record whose `sys.prefix` is the venv.

**F-4, pytest in the venv:**
- **(a) S2 ENV node.** The unmodified S2 ENV node, run from the BC export, passes. Its warnings-summary
  record parses, its hash verifies, and it is byte-equal to the plugin's copy. It has the `[O]` CPU
  brand, the lock pin and the legitimate `[U]` commit. The main process also gets a complete
  sitecustomize record.
- **(b) Disposable test.** A disposable test spawns a `sys.executable -I` child (the
  committed-test pattern). Both the main process and the child produce complete records.

**Superseded attempts, retained and disclosed:**
- **run-1** (`feasibility/steps`, `feasibility/FEASIBILITY.json`, `records/FEAS-run-1.txt`, exit 1).
  The checker had two defects: it expected the hook name as `uv_build.` in argv, but uv runs
  `import uv_build as backend`; and it expected 2 output files, ignoring the `.gitignore` that uv
  writes. The data showed complete records and identical artifacts.
- **run-2** (`feasibility/run-2`, exit 1). The F0 check found the `rec/__pycache__` bytecode written
  by run-1's hook processes.
- The checker was corrected between runs; the recorder itself was unchanged. The `tools/feasibility.py`
  file in the seal is the run-3 version. Its run-1 sha256 was
  `51730054308682de112f0d283de97ce29d00d23bd49b06ad090c2e24df5e99d9`.

## 3. Execution-to-required-fields map

"ENV" means a complete own-process record that passes `check_env_record`:
- the S2 body verifies;
- libm 6235/7175;
- `[O]` CPU brand and no artificial `[U]`;
- FP and build config;
- executable, libpython and version equal to 3.12.15;
- lock = pin, in the body and independently;
- legitimate `[U]` commit;
- the P5 label.

Every execution also gets a run record: UTC start/end, argv, cwd, the env as passed, exit, and
stdout/stderr files with their sha256.

| Execution | Class (Q-1) | Required own evidence |
|---|---|---|
| `uv build` PK-1, PK-2, wrong-hash control | tool (Rust) | run record; uv version and sha256; inputs/outputs (export tar, sdist in/out, artifacts) by sha256; constraint file; `--python` selection and uv's `Using base executable` line |
| every PK-1/PK-2 hook process | Python build hook | ENV via sitecustomize; one per `Calling uv_build.*` line; `uv_build` origin in the isolated venv |
| stage-1/stage-2 packaging drivers (PK-1 artifact checks, PK-3, PK-8, comparisons) | Python artifact-check driver | ENV via `finally` capture in the driver process itself |
| `uv venv`, `uv pip install` (PK-4 uv route, PK-6 venvs) | tool (Rust) | run record; uv version and sha256; `--python` path; venv `pyvenv.cfg`; installed RECORD |
| `python -m venv` (PK-4 pip route; campaign venv) | Python setup process | ENV via wrapper (recorded although it is setup, never labelled a gate) |
| ensurepip children of `python -m venv` | incidental helper | inventoried by command; no invented ENV |
| `pip install`, `pip --version` (PK-4) | Python installer process | ENV via wrapper |
| PK-5 import, PK-6 tamper imports, PK-7 zipimport | Python import/tamper gate | ENV via wrapper |
| campaign control and each mutant pytest | Python numerical gate | JUnit; the S2 ENV node in the same process (stdout and plugin copies equal); sitecustomize record of the same pid; plugin binding (`tars`/`tests` modules under the subject); independent lock hash; subject manifest versus BC blobs; edits and targets |
| `-I` children spawned by S3-T-02b/c, M-29, S3-T-05b | Python import/tamper outcome | ENV via the venv sitecustomize (own pid; `orig_argv` shows the probe script under that run's tmp) |
| S2 ENV node probes (`sysctl`, `git`, `sw_vers`) | incidental tool children | contents recorded inside the ENV body |
| D regressions: pytest full suite | Python numerical gate | JUnit; S2 ENV node in-process; sitecustomize record |
| D regressions: M1/M2 Proof, determinism, cross-platform, GMAT compare | Python numerical gate (Q-2) | ENV via the venv sitecustomize in the same process; run record; output files by sha256 |
| `ruff`, `git` | tool | run record; tool version and sha256 |
| CI jobs (D, E) | CI gate | run id, job, attempt, `head_sha`, executed status; per-job S2 ENV record extracted from the warnings summary with completeness checks (§13.2) |

## 4. Observation limits

- Non-interference is shown for exit status, artifacts, stdio and `exp` bits only, not proven in
  general. The recorder adds work at interpreter exit, after the payload, in the same process,
  including the S2 subprocess probes and the libm digest.
- A process that ends by `os._exit` or a signal leaves no record. Drivers compare record counts with
  launches.
- Hook processes may write `tools/rec/__pycache__/sitecustomize.cpython-312.pyc` and
  `tools/__pycache__/envcap2.cpython-312.pyc` (compiled from the same sources). These are
  runtime byproducts: excluded from the seal and inventoried.
- The S2 `commit` field is `[U]` by design (an export, not a checkout). Subject identity comes from
  the blob comparison and the export tar sha256.
