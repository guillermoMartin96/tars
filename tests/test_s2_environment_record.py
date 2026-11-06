"""S2 environment record: the r2 §7.1 DL-5 record on every gate-evidence run (D-S2-5 (i)).

It is a record, not a pass/fail gate: it is emitted into the pytest warnings summary, which
every CI job already prints, and copied from the job logs into committed evidence (§3.16,
§3.17). Field kinds: [O] observed by a probe in the process; [P] partly observed or a proxy;
[U] not observable from the process. A probe whose command exits non-zero, or returns
nothing, is recorded as ``[U] unavailable`` with its exit status and diagnostic, never as an
observed empty value (§7.1, I-35).

The libm behaviour digest uses exactly the argument set of ``behaviour_digest()`` in the
I-33 draft (``docs/reviews/raw/M3-T2-packet-r2-I33-evidence/f4_fingerprint.py.txt`` at K,
blob 457dc4bb494146111f7403aa20ad3b3d061ad0f3, lines 56-70), approved for S2's DL-5
recording only (D-S2-5 (i-1)). It hashes 7 175 values (the draft's count formula reports
7 410; the true count is recorded, and r2 is not edited). It observes results on its own
arguments only and proves nothing about other arguments. Recording these fields does not
establish numerical reproducibility.

This module does not import the geodetic component. The test fails only if the record
itself cannot be produced (a missing record is stop 18).
"""

from __future__ import annotations

import ctypes
import ctypes.util
import hashlib
import json
import math
import os
import platform
import struct
import subprocess
import sys
import sysconfig
import warnings

from tests.conftest import REPO_ROOT


class EnvironmentRecord(UserWarning):
    """The S2 DL-5 environment record (report; D-S2-5 (i))."""


def _sha256_file(path: str) -> str:
    try:
        with open(path, "rb") as fh:
            return "[O] " + hashlib.sha256(fh.read()).hexdigest()
    except OSError as exc:
        return f"[U] unavailable: {type(exc).__name__}: {exc}"


def _run(cmd: list[str], kind: str = "[O]") -> str:
    """A probe command; a non-zero exit or empty output is [U] unavailable, with the exit
    status and the diagnostic (stderr)."""
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError) as exc:
        return f"[U] unavailable: {type(exc).__name__}: {exc}"
    out = res.stdout.strip()
    if res.returncode != 0 or not out:
        return (
            f"[U] unavailable: exit status {res.returncode}; "
            f"stderr: {res.stderr.strip()!r}; stdout: {out!r}"
        )
    return f"{kind} {out}"


def _fp_configuration() -> dict[str, object]:
    """Run-time floating-point configuration probes (X-P4 style; operands built at run time
    from strings so they are not folded at compile time). They show the configuration, not
    every operation."""
    h = float.fromhex
    one = h("0x1p+0")
    a = h("0x1.00000004p+0")  # 1 + 2^-30
    c = -h("0x1.00000008p+0")  # -(1 + 2^-29)
    return {
        "[O] round-to-nearest: 1 + 2^-54 == 1 and 1 + 3*2^-54 == 1 + 2^-52": (
            one + h("0x1p-54") == one and one + h("0x3p-54") == h("0x1.0000000000001p+0")
        ),
        "[O] ties to even: 1 + 2^-53 == 1 and (1 + 2^-52) + 2^-53 == 1 + 2^-51": (
            one + h("0x1p-53") == one
            and h("0x1.0000000000001p+0") + h("0x1p-53") == h("0x1.0000000000002p+0")
        ),
        "[O] gradual underflow: 2^-1022 / 2 > 0 and 2^-1074 * 1.0 == 2^-1074 > 0": (
            h("0x1p-1022") / h("0x1p+1") > 0.0
            and h("0x0.0000000000001p-1022") * one == h("0x0.0000000000001p-1022") > 0.0
        ),
        "[O] subnormal tie to even: 2^-1074 / 2 == 0": (
            h("0x0.0000000000001p-1022") / h("0x1p+1") == 0.0
        ),
        "[O] no FMA contraction in Python a*b + c (an exact FMA would give 2^-60)": (
            a * a + c == 0.0
        ),
        "[O] sys.float_info": {
            "mant_dig": sys.float_info.mant_dig,
            "max_exp": sys.float_info.max_exp,
            "min_exp": sys.float_info.min_exp,
            "rounds": sys.float_info.rounds,
        },
        "[O] float_repr_style": sys.float_repr_style,
    }


def _behaviour_digest() -> dict[str, object]:
    """Exactly the I-33 argument set (D-S2-5 (i-1)); the true number of hashed results."""
    args = [i / 64.0 - 1.6 for i in range(205)] + [2.0**-k for k in range(1, 1075, 37)]
    ex = [-(i / 8.0) for i in range(6000)]
    digest = hashlib.sha256()
    hashed = 0
    for x in args:
        digest.update(struct.pack("<dd", math.sin(x), math.cos(x)))
        digest.update(struct.pack("<d", math.atan2(x, 6.4e6)))
        digest.update(struct.pack("<d", math.hypot(x * 6.4e6, 6.4e6 - x)))
        digest.update(struct.pack("<d", math.sqrt(abs(x))))
        hashed += 5
    for x in ex:
        digest.update(struct.pack("<d", math.exp(x)))
        hashed += 1
    return {
        "[O] sha256": digest.hexdigest(),
        "[O] arguments": len(args) + len(ex),
        "[O] results hashed": hashed,
        "note": (
            "I-33 argument set (6 235 arguments); 7 175 results hashed (r2 section 7.1 says "
            "7 410, a count erratum flagged in the S2 proposal, not edited). It changes iff "
            "a result on THESE arguments changes; it says nothing about other arguments."
        ),
    }


def _ci_run_record() -> dict[str, str]:
    """§3.16 run-record fields that the job environment exposes. The job log URL and the
    executed-or-carried-over status are not in the job environment; they are taken from
    the GitHub API when the record is copied into evidence (§3.16)."""
    keys = (
        "GITHUB_ACTIONS",
        "GITHUB_SHA",
        "GITHUB_REF",
        "GITHUB_RUN_ID",
        "GITHUB_RUN_ATTEMPT",
        "GITHUB_RUN_NUMBER",
        "GITHUB_JOB",
        "GITHUB_WORKFLOW",
        "GITHUB_REPOSITORY",
        "GITHUB_SERVER_URL",
        "RUNNER_OS",
        "RUNNER_ARCH",
        "RUNNER_NAME",
        "ImageOS",
        "ImageVersion",
    )
    rec = {k: os.environ[k] for k in keys if k in os.environ}
    if "GITHUB_RUN_ID" in rec and "GITHUB_REPOSITORY" in rec:
        rec["run URL (derived)"] = (
            f"{rec.get('GITHUB_SERVER_URL', 'https://github.com')}/{rec['GITHUB_REPOSITORY']}"
            f"/actions/runs/{rec['GITHUB_RUN_ID']}/attempts/{rec.get('GITHUB_RUN_ATTEMPT', '?')}"
        )
    return rec


def build_record() -> dict[str, object]:
    cfg = sysconfig.get_config_vars()
    exe = os.path.realpath(sys.executable)
    rec: dict[str, object] = {"record": "S2 DL-5 environment record (r2 section 7.1)"}
    rec["run"] = {
        "[O] commit (git rev-parse HEAD)": _run(["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"]),
        "[O] uv.lock sha256": _sha256_file(str(REPO_ROOT / "uv.lock")),
        "ci": _ci_run_record() or "[O] not a CI run (no GITHUB_* variables)",
    }
    ldlib = cfg.get("LDLIBRARY")
    shared = bool(cfg.get("Py_ENABLE_SHARED"))
    rec["python"] = {
        "[O] implementation": sys.implementation.name,
        "[O] sys.version": sys.version,
        "[O] version_info": list(sys.version_info),
        "[O] build": list(platform.python_build()),
        "[O] compiler": platform.python_compiler(),
        "[O] sys.executable": sys.executable,
        "[O] executable realpath": exe,
        "[O] executable sha256": _sha256_file(exe),
        "[P] libpython sha256": (
            _sha256_file(os.path.join(cfg.get("LIBDIR") or "", ldlib or ""))
            if shared and ldlib
            else f"[O] not a shared build (Py_ENABLE_SHARED={cfg.get('Py_ENABLE_SHARED')!r})"
        ),
    }
    rec["build_config [P]"] = {
        k: cfg.get(k)
        for k in ("CC", "CFLAGS", "OPT", "CONFIG_ARGS", "PY_CFLAGS_NODIST", "HOST_GNU_TYPE")
    }
    rec["os"] = {
        "[O] platform.platform()": platform.platform(),
        "[O] uname (node name redacted)": [
            v if i != 1 else "[redacted]" for i, v in enumerate(platform.uname())
        ],
        "[P] libc_ver (empty on macOS)": list(platform.libc_ver()),
    }
    libm: dict[str, object] = {"[P] find_library('m')": ctypes.util.find_library("m")}
    cpu: dict[str, object] = {"[O] machine": platform.machine()}
    if sys.platform == "darwin":
        rec["os"]["[O] sw_vers"] = _run(["sw_vers"])
        libm["[U] libm binary"] = (
            "unavailable: libm is part of libSystem in the dyld shared cache; there is no "
            "file to hash from the process. The OS build (sw_vers) is the only proxy."
        )
        cpu["[O] brand"] = _run(["sysctl", "-n", "machdep.cpu.brand_string"])
        cpu["[P] features"] = _run(["sysctl", "-n", "machdep.cpu.features"], "[P]")
        cpu["[P] leaf7 features"] = _run(["sysctl", "-n", "machdep.cpu.leaf7_features"], "[P]")
        cpu["[P] arm64 FP features"] = _run(
            ["sysctl", "hw.optional.arm.FEAT_FP16", "hw.optional.AdvSIMD"], "[P]"
        )
    else:
        try:
            fn = ctypes.CDLL(None).gnu_get_libc_version
            fn.restype = ctypes.c_char_p
            libm["[O] gnu_get_libc_version"] = fn().decode()
        except (AttributeError, OSError) as exc:
            libm["[U] gnu_get_libc_version"] = f"unavailable: {type(exc).__name__}: {exc}"
        multiarch = cfg.get("MULTIARCH")
        libm["[P] libm.so.6 sha256"] = (
            _sha256_file(os.path.realpath(f"/lib/{multiarch}/libm.so.6"))
            if multiarch
            else "[U] unavailable: MULTIARCH not set; libm.so.6 path unknown"
        )
        try:
            with open("/proc/cpuinfo") as fh:
                lines = fh.read().splitlines()
            model = next((ln for ln in lines if ln.startswith("model name")), None)
            flags = next((ln for ln in lines if ln.startswith(("flags", "Features"))), None)
            cpu["[O] brand"] = (
                "[O] " + model.split(":", 1)[1].strip()
                if model
                else "[U] unavailable: no 'model name' line in /proc/cpuinfo"
            )
            cpu["[P] flags"] = (
                "[P] " + flags.split(":", 1)[1].strip()
                if flags
                else "[U] unavailable: no flags line in /proc/cpuinfo"
            )
        except OSError as exc:
            cpu["[U] /proc/cpuinfo"] = f"unavailable: {type(exc).__name__}: {exc}"
    libm["[U] variant dispatch"] = (
        "unavailable: glibc selects FMA/AVX2 variants of sin, cos and exp at load time from "
        "CPU features; the choice is not reported to the process (Linux). Not observable on "
        "macOS either."
    )
    cpu["[U] microcode / dispatch inside libm"] = "unavailable: not observable from the process"
    rec["libm"] = libm
    rec["cpu"] = cpu
    rec["floating_point"] = _fp_configuration()
    try:
        import numpy

        rec["numpy"] = {"[O] version": numpy.__version__}
    except ImportError as exc:
        rec["numpy"] = f"[U] unavailable: {exc}"
    rec["libm behaviour digest"] = _behaviour_digest()
    rec["limits"] = (
        "Recording these fields does not establish numerical reproducibility. [U] fields "
        "cannot be checked. The record supports no S2 pass/fail gate (DL-5's D-2 review is "
        "outside S2)."
    )
    return rec


def test_s2_environment_record_is_emitted():
    rec = build_record()
    text = json.dumps(rec, sort_keys=True, default=str)
    assert rec["libm behaviour digest"]["[O] results hashed"] == 7175
    assert rec["libm behaviour digest"]["[O] arguments"] == 6235
    warnings.warn(
        "S2-ENV-RECORD sha256=" + hashlib.sha256(text.encode()).hexdigest() + " " + text,
        EnvironmentRecord,
        stacklevel=1,
    )
