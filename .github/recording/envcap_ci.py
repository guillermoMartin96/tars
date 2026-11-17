"""Own-process ENV record for CI recording (envcap_ci 1, v2 draft), derived from harness b2
envcap3.py (sha256 4761df74…) with ONE addition: a "ci" block of the GitHub Actions
run/job/attempt/sha, workspace, temp directory, event and runner identity read from this
process's own environment (values of a fixed list of names only; no environment dump).
Everything below is otherwise unchanged from envcap3.

Original envcap3 docstring follows. Own-process ENV record, preflight harness v3 (derived from the
retained envcap2.py,
sha256 5dfb9f1c…0a42a0f, S3-provenance-contract-recovery-v1/tools/envcap2.py).

Loaded BY PATH (never importable by name) at the END of a Python process, after its payload ran,
from harness/rec/sitecustomize.py (atexit). It runs the existing, unmodified S2 ENV node's
`build_record()` from the subject's own `tests/test_s2_environment_record.py`, giving that module a
temporary stub `tests.conftest` whose only attribute is REPO_ROOT = <subject root>, and restores
sys.modules afterwards. subprocess / platform are NOT patched: the S2 node's probes (git, sw_vers,
sysctl, and platform's `uname -p`) run with the interpreter's own, unmodified subprocess module.

Unchanged from envcap2: the S2 body, its sha256 (json.dumps(sort_keys=True, default=str)), process
identity (executable, libpython, build, flags, pid/ppid, argv, cwd), module origins, independent
uv.lock sha256, presence of fixed variable names and values of a fixed list of path-valued
variables. No environment dump.

Added in v3 (all observed in this same process, none backfilled):
- "harness": path and sha256 of this file and of the sitecustomize that loaded it;
- "spawns": child-process launch events observed by the sitecustomize audit hook (event name,
  phase payload|capture, monotonic order, executable, argv, cwd, whether env was overridden;
  never the env itself). Exit status and output are NOT observable this way (see LIMITATIONS);
- "cwd" falls back to an "[U]" string if os.getcwd() fails at exit.

capture(out_path, subject_root, label, observer, spawns=None, loader=None) writes out_path with
mode "x" (never overwrites).
"""

import hashlib
import importlib.util
import json
import os
import sys
import sysconfig
import types
from datetime import UTC, datetime

NAMES = (
    "VIRTUAL_ENV",
    "PYTHONHOME",
    "PYTHONPATH",
    "PYTHONVERBOSE",
    "PYTHONDONTWRITEBYTECODE",
    "UV_CACHE_DIR",
    "UV_OFFLINE",
    "UV_PYTHON_DOWNLOADS",
    "TMPDIR",
    "PIP_NO_INDEX",
    "PATH",
    "GIT_CEILING_DIRECTORIES",
    "S3REC_DIR",
    "S3REC_SUBJECT",
    "S3REC_LABEL",
    "S3REC_ENVCAP",
    "S3REC_HOOK_MARK",
)
SHOW_VALUES = (
    "VIRTUAL_ENV",
    "PYTHONHOME",
    "PYTHONPATH",
    "PATH",
    "GIT_CEILING_DIRECTORIES",
    "S3REC_SUBJECT",
)
MODULE_PREFIXES = (
    "__main__",
    "tars",
    "tests",
    "s3_",
    "uv_build",
    "pytest",
    "_pytest",
    "numpy",
    "pip",
    "venv",
    "ensurepip",
    "sitecustomize",
    "s3rec_plugin",
    "harmless_backend",
)
LABEL_P5 = "densities are UNVERIFIED ABOVE 1000 KM (P5)"
SCHEMA = "s3-ci-envcap/1"
CI_NAMES = (
    "GITHUB_RUN_ID",
    "GITHUB_RUN_ATTEMPT",
    "GITHUB_JOB",
    "GITHUB_SHA",
    "GITHUB_REF",
    "GITHUB_REPOSITORY",
    "GITHUB_WORKFLOW_REF",
    "GITHUB_WORKSPACE",
    "GITHUB_EVENT_NAME",
    "RUNNER_TEMP",
    "RUNNER_OS",
    "RUNNER_ARCH",
    "RUNNER_NAME",
    "ImageOS",
    "ImageVersion",
)


def _sha(path):
    try:
        with open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()
    except OSError as exc:
        return f"[U] unavailable: {type(exc).__name__}: {exc}"


def _origins():
    """__file__ of loaded modules whose top-level name starts with one of MODULE_PREFIXES."""
    out = {}
    for name, mod in list(sys.modules.items()):
        if name.split(".")[0].startswith(MODULE_PREFIXES):
            f = getattr(mod, "__file__", None)
            if isinstance(f, str):
                out[name] = os.path.realpath(f)
    return dict(sorted(out.items()))


def capture(out_path, subject_root, label, observer, spawns=None, loader=None):
    saved = {k: sys.modules.get(k) for k in ("tests", "tests.conftest")}
    origins_before = _origins()
    pkg = types.ModuleType("tests")
    pkg.__path__ = []
    conf = types.ModuleType("tests.conftest")
    from pathlib import Path

    conf.REPO_ROOT = Path(subject_root)
    sys.modules["tests"], sys.modules["tests.conftest"] = pkg, conf
    src = os.path.join(subject_root, "tests", "test_s2_environment_record.py")
    try:
        spec = importlib.util.spec_from_file_location("_s2_env_record_from_subject", src)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        rec = mod.build_record()
        s2_text = json.dumps(rec, sort_keys=True, default=str)
        s2 = {
            "S2-ENV-RECORD body sha256": hashlib.sha256(s2_text.encode()).hexdigest(),
            "body": rec,
            "module": src,
            "module_sha256": _sha(src),
        }
    except BaseException as exc:  # recorded, never repaired
        s2 = {
            "error": f"{type(exc).__qualname__}: {exc}",
            "module": src,
            "module_sha256": _sha(src),
        }
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
        sys.modules.pop("_s2_env_record_from_subject", None)
    cfg = sysconfig.get_config_vars()
    lib = os.path.join(cfg.get("LIBDIR") or "", cfg.get("LDLIBRARY") or "")
    exe = os.path.realpath(sys.executable)
    try:
        cwd = os.getcwd()
    except OSError as exc:
        cwd = f"[U] unavailable: {type(exc).__name__}: {exc}"
    here = os.path.realpath(__file__)
    out = {
        "schema": SCHEMA,
        "record": "own-process ENV (S2 ENV node build_record + process identity)",
        "observer": observer,
        "label": label,
        "utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pid": os.getpid(),
        "parent_test_node": os.environ.get("PYTEST_CURRENT_TEST"),
        "ppid": os.getppid(),
        "argv": sys.argv,
        "orig_argv": getattr(sys, "orig_argv", None),
        "cwd": cwd,
        "sys.executable": sys.executable,
        "executable_realpath": exe,
        "executable_sha256": _sha(exe),
        "sys.version": sys.version,
        "sys.prefix": sys.prefix,
        "sys.base_prefix": sys.base_prefix,
        "in_venv": sys.prefix != sys.base_prefix,
        "sys.flags": {
            k: getattr(sys.flags, k)
            for k in dir(sys.flags)
            if not k.startswith("_") and isinstance(getattr(sys.flags, k), int)
        },
        "Py_ENABLE_SHARED": cfg.get("Py_ENABLE_SHARED"),
        "libpython": lib,
        "libpython_realpath": os.path.realpath(lib),
        "libpython_sha256": _sha(lib) if cfg.get("Py_ENABLE_SHARED") else "not a shared build",
        "sys.path": sys.path,
        "module_origins_at_capture": origins_before,
        "subject_root": str(subject_root),
        "subject_uv_lock_sha256_independent": _sha(os.path.join(subject_root, "uv.lock")),
        "env_names_present": sorted(n for n in NAMES if n in os.environ),
        "env_values": {n: os.environ[n] for n in SHOW_VALUES if n in os.environ},
        "s2_env_record": s2,
        "label_p5": LABEL_P5,
        "harness": {
            "envcap": here,
            "envcap_sha256": _sha(here),
            "loader": loader,
            "loader_sha256": _sha(loader) if loader else None,
        },
        "spawns": list(spawns) if spawns is not None else "[U] no spawn observer supplied",
        "ci": {n: os.environ.get(n) for n in CI_NAMES},
    }
    text = json.dumps(out, indent=1, sort_keys=True, default=str)
    with open(out_path, "x", encoding="utf-8") as fh:
        fh.write(text + "\n")
