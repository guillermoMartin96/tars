"""CI recording completeness check, v2 (recording-only; .github/recording/check_ci_records.py).

Modes (all read-only; they never change, re-run or repair a step and never judge test or gate
outcomes, which remain the existing steps' own results):

  records  --job check|gate --platform <matrix os> --root <records root> --out <CHECK.json>
      Every recorded step of this job (expected-steps.json) is checked: each own-process record
      against the complete S2 section/field contract for this platform (R-predicates), the step's
      process topology and exact root argv (T-predicates) and job-wide consistency (J-predicates).
  own      --job ... --platform ... --dir <records-mode S3REC_DIR> --check-json <CHECK.json>
           --out <OWN-CHECK.json>
      Run AFTER the records-mode process has exited: checks that process's own completed record
      (O-predicates). Its own record is checked offline from the uploaded artifact by the
      collection verifier, which imports check_job/check_own from this file by path.

Expectations come from expected-steps.json (literal pins, matrix, argv templates, platform rules)
and, in CI, from this job's own GITHUB_*/RUNNER_* environment. Recorded paths are compared as
strings with the recorded workspace; nothing is resolved on the checking host except, in CI, the
checkout files whose bytes are compared with the literal pins. Every problem names its predicate
id; exit status 1 on any problem. Platform rules whose status is not "adopted" never pass.
"""

import argparse
import hashlib
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HEX = re.compile(r"[0-9a-f]{64}")
PY_EXE = re.compile(r"python(3(\.\d+)?)?")
U_DIAG = re.compile(r"\[U\] unavailable: exit status -?\d+; stderr: .*; stdout: .*", re.S)
LABEL_P5 = "densities are UNVERIFIED ABOVE 1000 KM (P5)"
SECTIONS = {
    "build_config [P]",
    "cpu",
    "floating_point",
    "libm",
    "libm behaviour digest",
    "limits",
    "numpy",
    "os",
    "python",
    "record",
    "run",
}
RECORD_TITLE = "S2 DL-5 environment record (r2 section 7.1)"
BUILD_KEYS = {"CC", "CFLAGS", "OPT", "CONFIG_ARGS", "PY_CFLAGS_NODIST", "HOST_GNU_TYPE"}
FP_BOOL_KEYS = {
    "[O] round-to-nearest: 1 + 2^-54 == 1 and 1 + 3*2^-54 == 1 + 2^-52",
    "[O] ties to even: 1 + 2^-53 == 1 and (1 + 2^-52) + 2^-53 == 1 + 2^-51",
    "[O] gradual underflow: 2^-1022 / 2 > 0 and 2^-1074 * 1.0 == 2^-1074 > 0",
    "[O] subnormal tie to even: 2^-1074 / 2 == 0",
    "[O] no FMA contraction in Python a*b + c (an exact FMA would give 2^-60)",
}
FLOAT_INFO_KEYS = {"mant_dig", "max_exp", "min_exp", "rounds"}
STRUCTURAL_U_KEYS = {"[U] variant dispatch", "[U] microcode / dispatch inside libm"}
LAUNCH_EVENTS = {"subprocess.Popen", "os.posix_spawn", "os.spawn", "os.exec"}
FORK_EVENTS = {"os.fork", "os.forkpty", "pty.spawn"}
CI_KEYS = ("GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_JOB", "GITHUB_SHA")


def sha_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def is_hex(v):
    return isinstance(v, str) and HEX.fullmatch(v) is not None


def o_hex(v):
    return isinstance(v, str) and v.startswith("[O] ") and is_hex(v[4:])


def nonempty(v):
    return isinstance(v, str) and v.strip() != ""


def walk_u(o, path=()):
    """Yield every path whose key or string value starts with "[U]"."""
    if isinstance(o, dict):
        for k, v in o.items():
            p = (*path, str(k))
            if str(k).startswith("[U]"):
                yield p
            yield from walk_u(v, p)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk_u(v, (*path, i))
    elif isinstance(o, str) and o.startswith("[U]"):
        yield path


def fill(t, ctx):
    return t.format(**ctx) if isinstance(t, str) else t


def plat(spec, platform):
    m = spec["matrix"][platform]
    return m, m["system"] + "-" + m["machine"]


def u_allowed(spec, rules_id, path):
    """Authority for a [U] path: S2 node structural key, or a platform rule that is adopted."""
    if path[-1] in STRUCTURAL_U_KEYS and len(path) == 2:
        return True, None
    if path == ("libm", "[U] libm binary") and rules_id.startswith("Darwin-"):
        return True, None
    for rid, r in spec["platform_rules"].items():
        if rules_id in r["applies"] and list(path) in r["paths"]:
            return r["status"] == "adopted", rid
    return False, None


def record_problems(rec, ctx, spec, platform, label, root):
    """R-predicates for one own-process record. ctx: workspace, runner_temp, sha, run ids."""
    p = []
    m, rid = plat(spec, platform)
    pins = spec["pins"]
    ws = ctx["workspace"]
    if rec.get("schema") != "s3-ci-envcap/1":
        p.append("R01 schema")
    pid, ppid = rec.get("pid"), rec.get("ppid")
    if not (type(pid) is int and type(ppid) is int and pid > 0 and ppid > 0 and pid != ppid):
        p.append("R02 pid/ppid")
    if rec.get("observer") != "sitecustomize-atexit":
        p.append("R03 observer")
    if rec.get("label") != label:
        p.append("R04 label")
    ev = rec.get("env_values") or {}
    if rec.get("subject_root") != ws or ev.get("S3REC_SUBJECT") != ws:
        p.append("R05 subject binding")
    if root and rec.get("cwd") != ws:
        p.append("R05 root cwd")
    s2 = rec.get("s2_env_record")
    s2 = s2 if isinstance(s2, dict) else {}
    body = s2.get("body")
    if "error" in s2 or not isinstance(body, dict):
        p.append("R06 S2 body missing or error")
        body = {}
    else:
        text = json.dumps(body, sort_keys=True, default=str)
        if hashlib.sha256(text.encode()).hexdigest() != s2.get("S2-ENV-RECORD body sha256"):
            p.append("R07 S2 body sha256")
    if (
        s2.get("module") != ws + "/" + pins["s2_module_path"]
        or s2.get("module_sha256") != pins["s2_module_sha256"]
    ):
        p.append("R08 S2 module identity")
    if set(body) != SECTIONS:
        missing, extra = sorted(SECTIONS - set(body)), sorted(set(body) - SECTIONS)
        p.append(f"R09 sections missing {missing} extra {extra}")
    if body.get("record") != RECORD_TITLE:
        p.append("R10 record title")
    run = body.get("run") if isinstance(body.get("run"), dict) else {}
    if run.get("[O] commit (git rev-parse HEAD)") != "[O] " + ctx["sha"]:
        p.append("R11 commit")
    lock = pins["uv_lock_sha256"]
    if (
        run.get("[O] uv.lock sha256") != "[O] " + lock
        or rec.get("subject_uv_lock_sha256_independent") != lock
    ):
        p.append("R12 uv.lock")
    bci = run.get("ci") if isinstance(run.get("ci"), dict) else {}
    rci = rec.get("ci") if isinstance(rec.get("ci"), dict) else {}
    keys = (*CI_KEYS, "RUNNER_OS", "RUNNER_ARCH", "GITHUB_REPOSITORY")
    if any(bci.get(k) != rci.get(k) for k in keys) or bci.get("GITHUB_ACTIONS") != "true":
        p.append("R13 body ci block")
    py = body.get("python") if isinstance(body.get("python"), dict) else {}
    exe_sha = rec.get("executable_sha256")
    vi = py.get("[O] version_info")
    if not (
        py.get("[O] implementation") == "cpython"
        and isinstance(vi, list)
        and vi[:2] == spec["python_minor"]
        and py.get("[O] sys.version") == rec.get("sys.version")
        and py.get("[O] sys.executable") == rec.get("sys.executable")
        and py.get("[O] executable realpath") == rec.get("executable_realpath")
        and is_hex(exe_sha)
        and py.get("[O] executable sha256") == "[O] " + str(exe_sha)
        and isinstance(py.get("[O] build"), list)
        and len(py["[O] build"]) == 2
        and all(nonempty(x) for x in py["[O] build"])
        and nonempty(py.get("[O] compiler"))
    ):
        p.append("R14 python/executable identity")
    shared = rec.get("Py_ENABLE_SHARED")
    blp, rlp = py.get("[P] libpython sha256"), rec.get("libpython_sha256")
    if shared:
        ok = o_hex(blp) and is_hex(rlp) and blp == "[O] " + rlp
    else:
        ok = blp == f"[O] not a shared build (Py_ENABLE_SHARED={shared!r})" and rlp == (
            "not a shared build"
        )
    if not ok or "Py_ENABLE_SHARED" not in rec:
        p.append("R15 libpython")
    bc = body.get("build_config [P]")
    if not (
        isinstance(bc, dict) and set(bc) == BUILD_KEYS and all(nonempty(v) for v in bc.values())
    ):
        p.append("R16 build_config")
    osr = body.get("os") if isinstance(body.get("os"), dict) else {}
    un = osr.get("[O] uname (node name redacted)")
    if not (
        nonempty(osr.get("[O] platform.platform()"))
        and isinstance(un, list)
        and len(un) == 6
        and un[0] == m["system"]
        and un[1] == "[redacted]"
        and un[4] == m["machine"]
        and all(nonempty(un[i]) for i in (2, 3, 5))
    ):
        p.append("R17 os/uname")
    libc = osr.get("[P] libc_ver (empty on macOS)")
    if m["system"] == "Darwin":
        sw = osr.get("[O] sw_vers")
        if not (isinstance(sw, str) and sw.startswith("[O] ") and "ProductVersion" in sw):
            p.append("R17 sw_vers")
        if libc != ["", ""]:
            p.append("R17 libc_ver")
    elif "[O] sw_vers" in osr or not (
        isinstance(libc, list) and len(libc) == 2 and libc[0] == "glibc" and nonempty(libc[1])
    ):
        p.append("R17 linux os fields")
    libm = body.get("libm") if isinstance(body.get("libm"), dict) else {}
    fl = "[P] find_library('m')"
    if m["system"] == "Darwin":
        want = {fl, "[U] libm binary", "[U] variant dispatch"}
        ok = set(libm) == want and nonempty(libm.get(fl))
    else:
        want = {fl, "[O] gnu_get_libc_version", "[P] libm.so.6 sha256", "[U] variant dispatch"}
        ok = (
            set(libm) == want
            and nonempty(libm.get(fl))
            and nonempty(libm.get("[O] gnu_get_libc_version"))
            and o_hex(libm.get("[P] libm.so.6 sha256"))
        )
    if not ok:
        p.append("R18 libm")
    cpu = body.get("cpu") if isinstance(body.get("cpu"), dict) else {}
    brand = cpu.get("[O] brand")
    ok = (
        cpu.get("[O] machine") == m["machine"]
        and isinstance(brand, str)
        and brand.startswith("[O] ")
        and nonempty(brand[4:])
        and "[U] microcode / dispatch inside libm" in cpu
    )
    if m["system"] == "Darwin":
        names = ("[P] features", "[P] leaf7 features", "[P] arm64 FP features")
        ok = ok and set(cpu) == {
            "[O] machine",
            "[O] brand",
            *names,
            "[U] microcode / dispatch inside libm",
        }
        for n in names:
            v = cpu.get(n)
            if isinstance(v, str) and v.startswith("[P] ") and nonempty(v[4:]):
                continue
            allowed, rule = u_allowed(spec, rid, ("cpu", n))
            if not (isinstance(v, str) and U_DIAG.fullmatch(v)):
                ok = False
            elif not allowed:
                p.append(
                    f"R19 cpu {n}: [U] not authorized" + (f" ({rule} not adopted)" if rule else "")
                )
    else:
        fv = cpu.get("[P] flags")
        ok = ok and set(cpu) == {
            "[O] machine",
            "[O] brand",
            "[P] flags",
            "[U] microcode / dispatch inside libm",
        }
        ok = ok and isinstance(fv, str) and fv.startswith("[P] ") and nonempty(fv[4:])
    if not ok:
        p.append("R19 cpu")
    fp = body.get("floating_point") if isinstance(body.get("floating_point"), dict) else {}
    fi = fp.get("[O] sys.float_info")
    if not (
        set(fp) == FP_BOOL_KEYS | {"[O] sys.float_info", "[O] float_repr_style"}
        and all(type(fp[k]) is bool for k in FP_BOOL_KEYS)
        and isinstance(fi, dict)
        and set(fi) == FLOAT_INFO_KEYS
        and all(type(v) is int for v in fi.values())
        and nonempty(fp.get("[O] float_repr_style"))
    ):
        p.append("R20 floating_point")
    npv = body.get("numpy")
    if not (
        rec.get("in_venv") is True and isinstance(npv, dict) and nonempty(npv.get("[O] version"))
    ):
        p.append("R21 numpy/venv")
    dg = body.get("libm behaviour digest")
    dg = dg if isinstance(dg, dict) else {}
    if [dg.get("[O] arguments"), dg.get("[O] results hashed")] != spec["libm_counts"] or not is_hex(
        dg.get("[O] sha256")
    ):
        p.append("R22 libm behaviour digest")
    if not nonempty(body.get("limits")):
        p.append("R23 limits")
    for path in walk_u(body):
        if path in (
            ("cpu", n) for n in ("[P] features", "[P] leaf7 features", "[P] arm64 FP features")
        ):
            continue  # decided under R19 (structural form + platform rule)
        if not u_allowed(spec, rid, path)[0]:
            p.append("R24 unexpected [U] at " + "/".join(map(str, path)))
    h = rec.get("harness") if isinstance(rec.get("harness"), dict) else {}
    if (
        h.get("envcap_sha256") != pins["envcap_sha256"]
        or h.get("loader_sha256") != pins["loader_sha256"]
        or h.get("envcap") != ws + "/.github/recording/envcap_ci.py"
    ):
        p.append("R26 harness identity")
    if any(rci.get(k) != ctx[k] for k in CI_KEYS) or rci.get("GITHUB_REPOSITORY") != ctx.get(
        "GITHUB_REPOSITORY"
    ):
        p.append("R27 run/job/attempt/sha")
    if rci.get("RUNNER_OS") != m["RUNNER_OS"] or rci.get("RUNNER_ARCH") != m["RUNNER_ARCH"]:
        p.append("R27 runner OS/arch vs matrix")
    if rci.get("GITHUB_WORKSPACE") != ws or rci.get("RUNNER_TEMP") != ctx["runner_temp"]:
        p.append("R27 workspace/temp")
    if rec.get("label_p5") != LABEL_P5:
        p.append("R28 P5 label")
    sp = rec.get("spawns")
    if not isinstance(sp, list):
        p.append("R29 spawn observation")
        sp = []
    cap = [s.get("argv") for s in sp if s.get("phase") == "capture"]
    pay = [s.get("argv") for s in sp if s.get("phase") == "payload"]
    probes = [["git", "-C", ws, "rev-parse", "HEAD"]]
    if m["system"] == "Darwin":
        probes += [
            ["sw_vers"],
            ["sysctl", "-n", "machdep.cpu.brand_string"],
            ["sysctl", "-n", "machdep.cpu.features"],
            ["sysctl", "-n", "machdep.cpu.leaf7_features"],
            ["sysctl", "hw.optional.arm.FEAT_FP16", "hw.optional.AdvSIMD"],
        ]
    if not all(x in cap for x in probes) or not (["uname", "-p"] in cap or ["uname", "-p"] in pay):
        p.append("R29 capture-phase probes")
    if rec.get("sys.executable") != ws + "/.venv/bin/python":
        p.append("R30 interpreter path")
    if not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", str(rec.get("utc"))):
        p.append("R31 utc")
    names = set(rec.get("env_names_present") or [])
    if not {"S3REC_DIR", "S3REC_SUBJECT", "S3REC_ENVCAP", "S3REC_LABEL"} <= names:
        p.append("R32 recording variables")
    return p


def python_target(s, rec):
    argv = s.get("argv") if isinstance(s.get("argv"), list) else None
    tgt = s.get("executable") or s.get("path") or (argv[0] if argv else None)
    if not isinstance(tgt, str):
        return False
    return tgt in (rec.get("sys.executable"), rec.get("executable_realpath")) or bool(
        PY_EXE.fullmatch(os.path.basename(tgt))
    )


def is_query(rec):
    argv, orig = rec.get("argv") or [], rec.get("orig_argv") or []
    payload = [s for s in (rec.get("spawns") or []) if s.get("phase") == "payload"]
    return argv[:1] == ["-c"] and "-c" in orig and not payload


def load_records(d, out):
    recs = {}
    for f in sorted(d.iterdir()):
        if f.name.endswith(".env.json"):
            try:
                r = json.loads(f.read_text())
            except (OSError, ValueError) as exc:
                out["problems"].append(f"T02 {f.name} unreadable: {exc}")
                continue
            if not isinstance(r, dict):
                out["problems"].append(f"T02 {f.name} is not a JSON object")
                continue
            if not all(type(r.get(k)) is int and r[k] > 0 for k in ("pid", "ppid")):
                out["problems"].append(f"R02 {f.name}: pid/ppid not positive integers")
                continue
            if f.name != f"{r.get('pid')}.env.json":
                out["problems"].append(f"R02 file name {f.name} vs pid {r.get('pid')}")
            if r.get("pid") in recs:
                out["problems"].append(f"T03 duplicate pid {r.get('pid')}")
            recs[r.get("pid")] = r
        else:
            out["problems"].append(f"T02 unexpected file {f.name}")
    return recs


def check_step(d, step, ctx, spec, platform, job):
    out = {
        "dir": d.name,
        "problems": [],
        "roots": [],
        "incidental": [],
        "children": [],
        "other_launches": [],
    }
    if not d.is_dir():
        out["problems"].append("T01 step directory missing")
        return out, {}
    recs = load_records(d, out)
    label = f"ci {ctx['GITHUB_JOB']} {platform} {d.name}"
    roots = {pid for pid, r in recs.items() if r.get("ppid") not in recs}
    queries = {pid for pid in roots if is_query(recs[pid])}
    for pid, r in recs.items():
        if pid in queries:
            out["incidental"].append(
                {
                    "pid": pid,
                    "orig_argv": r.get("orig_argv"),
                    "record_problems_not_required_Q1": record_problems(
                        r, ctx, spec, platform, label, False
                    ),
                }
            )
            continue
        for prob in record_problems(r, ctx, spec, platform, label, pid in roots):
            out["problems"].append(f"{pid}: {prob}")
    used = set()
    for pid, r in recs.items():
        for s in r.get("spawns") or []:
            if s.get("phase") != "payload":
                continue
            ev = s.get("event")
            if ev in FORK_EVENTS:
                out["problems"].append(f"T04 {pid}: {ev} cannot be matched to a record")
            elif ev == "os.system":
                if "python" in str(s.get("command")):
                    out["problems"].append(f"T04 {pid}: python launched through a shell")
                else:
                    out["other_launches"].append([pid, s.get("command")])
            elif ev in LAUNCH_EVENTS and python_target(s, r):
                argv = s.get("argv")
                if ev == "os.exec" or "-S" in (argv or [])[1:2]:
                    out["problems"].append(f"T04 {pid}: unrecordable python launch {ev} {argv}")
                    continue
                m = [
                    c
                    for c, x in recs.items()
                    if x.get("ppid") == pid and x.get("orig_argv") == argv and c not in used
                ]
                if len(m) != 1:
                    out["problems"].append(f"T04 {pid}: launch {argv} has {len(m)} child records")
                else:
                    used.add(m[0])
                    out["children"].append(
                        {
                            "parent": pid,
                            "child": m[0],
                            "argv": argv,
                            "node": s.get("parent_test_node"),
                        }
                    )
            elif ev in LAUNCH_EVENTS:
                out["other_launches"].append([pid, s.get("argv") or s.get("path")])
    for pid, r in recs.items():
        if pid not in roots and pid not in used:
            out["problems"].append(
                f"T05 record {pid} (ppid {r.get('ppid')}) has no recorded launch"
            )
    want = [[fill(a, ctx) for a in t] for t in step["roots"]]
    got = [recs[pid].get("argv") for pid in sorted(roots - queries)]
    for pid in sorted(roots - queries):
        out["roots"].append({"pid": pid, "argv": recs[pid].get("argv")})
    if sorted(map(json.dumps, got)) != sorted(map(json.dumps, want)):
        out["problems"].append(f"T06 roots {got} != expected {want}")
    if "junit" in step:
        j = d.parent / step["junit"]
        try:
            suites = ET.parse(j).getroot()
            cases = list(suites.iter("testcase"))
            out["junit"] = {"sha256": sha_file(j), "testcases": len(cases)}
            if not cases:
                out["problems"].append("T07 JUnit has no test cases")
        except (OSError, ET.ParseError) as exc:
            out["problems"].append(f"T07 JUnit missing or unreadable: {type(exc).__name__}")
    return out, recs


def check_job(root, job, platform, ctx, spec):
    """All steps of one job; ctx keys: workspace runner_temp sha GITHUB_* (and os)."""
    ctx = dict(ctx, os=platform)
    steps, allrecs = [], {}
    probs = []
    if ctx.get("GITHUB_JOB") != spec["job_ids"][job]:
        probs.append(f"J06 GITHUB_JOB {ctx.get('GITHUB_JOB')} is not the {job} job")
    for step in spec["jobs"][job]:
        res, recs = check_step(Path(root) / step["dir"], step, ctx, spec, platform, job)
        steps.append(res)
        allrecs.update({(step["dir"], k): v for k, v in recs.items()})
    present = {x.name for x in Path(root).iterdir()} if Path(root).is_dir() else set()
    allowed = (
        {s["dir"] for s in spec["jobs"][job]}
        | set(spec["checker_dirs"])
        | {"junit", "CHECK.json", "OWN-CHECK.json"}
    )
    if present - allowed:
        probs.append(f"J01 unexpected entries {sorted(present - allowed)}")
    ident = {
        json.dumps(
            [
                r.get("executable_realpath"),
                r.get("executable_sha256"),
                r.get("libpython_sha256"),
                r.get("sys.version"),
                ((r.get("s2_env_record") or {}).get("body") or {}).get("build_config [P]"),
            ],
            sort_keys=True,
        )
        for r in allrecs.values()
    }
    if len(ident) > 1:
        probs.append(f"J02 {len(ident)} different interpreter identities in one job")
    return {"job": job, "platform": platform, "problems": probs, "steps": steps}


def check_own(d, job, platform, ctx, spec, check_json, kind="records"):
    """O-predicates for the single record of a checker process (kind: records|own)."""
    ctx = dict(ctx, os=platform, job=job, platform=platform)
    out = {"dir": str(d), "problems": []}
    d = Path(d)
    if not d.is_dir():
        out["problems"].append("O01 checker record directory missing")
        return out
    recs = load_records(d, out)
    out["problems"] = ["O01 " + x for x in out["problems"]]
    if len(recs) != 1:
        out["problems"].append(f"O01 {len(recs)} records (expected exactly 1)")
    want = [fill(a, ctx) for a in spec["checker_argv"][kind]]
    for r in recs.values():
        label = f"ci {ctx['GITHUB_JOB']} {platform} {d.name}"
        out["problems"] += [
            "O02 " + x for x in record_problems(r, ctx, spec, platform, label, True)
        ]
        if r.get("ppid") in recs or r.get("argv") != want:
            out["problems"].append(f"O03 argv {r.get('argv')} != {want}")
        if (r.get("sys.flags") or {}).get("isolated") != 1:
            out["problems"].append("O04 not isolated (-I)")
        if any(s.get("phase") == "payload" for s in r.get("spawns") or []):
            out["problems"].append("O05 checker launched a process")
    try:
        cj = json.loads(Path(check_json).read_text())
        out["check_json"] = {"sha256": sha_file(check_json), "ok": cj.get("ok")}
        if (cj.get("job"), cj.get("platform"), cj.get("mode")) != (job, platform, kind) or cj.get(
            "ctx", {}
        ).get("GITHUB_SHA") != ctx["GITHUB_SHA"]:
            out["problems"].append("O06 CHECK.json binding")
    except (OSError, ValueError) as exc:
        out["problems"].append(f"O06 CHECK.json missing or unreadable: {type(exc).__name__}")
    return out


def ci_ctx():
    e = os.environ
    ctx = {k: e.get(k) for k in (*CI_KEYS, "GITHUB_REPOSITORY", "RUNNER_OS", "RUNNER_ARCH")}
    ctx.update(
        workspace=e.get("GITHUB_WORKSPACE"),
        runner_temp=e.get("RUNNER_TEMP"),
        sha=e.get("GITHUB_SHA"),
    )
    return ctx


def checkout_pins(spec):
    pins, p = spec["pins"], []
    for rel, key in (
        (pins["s2_module_path"], "s2_module_sha256"),
        ("uv.lock", "uv_lock_sha256"),
        (".github/recording/envcap_ci.py", "envcap_sha256"),
        (".github/recording/sitecustomize.py", "loader_sha256"),
    ):
        if sha_file(ROOT / rel) != pins[key]:
            p.append(f"J03 checkout {rel} differs from pin")
    if (
        sorted(x.relative_to(ROOT).as_posix() for x in ROOT.glob("scenarios/m2_*.json"))
        != spec["m2_scenarios"]
    ):
        p.append("J04 scenarios/m2_*.json differs from the listed scenarios")
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("records", "own"))
    ap.add_argument("--job", required=True, choices=("check", "gate"))
    ap.add_argument("--platform", required=True)
    ap.add_argument("--root")
    ap.add_argument("--dir")
    ap.add_argument("--check-json")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    spec = json.loads((HERE / "expected-steps.json").read_text())
    ctx = ci_ctx()
    missing = [k for k in ("workspace", "runner_temp", *CI_KEYS) if not ctx.get(k)]
    m = spec["matrix"].get(a.platform, {})
    host = (
        []
        if (ctx.get("RUNNER_OS"), ctx.get("RUNNER_ARCH"))
        == (m.get("RUNNER_OS"), m.get("RUNNER_ARCH"))
        else ["J05 this runner differs from the matrix"]
    )
    if a.mode == "records":
        res = check_job(a.root, a.job, a.platform, ctx, spec)
        res["problems"] = (
            [f"J00 missing {missing}"] * bool(missing)
            + host
            + checkout_pins(spec)
            + res["problems"]
        )
    else:
        res = check_own(a.dir, a.job, a.platform, ctx, spec, a.check_json)
        res["problems"] = [f"J00 missing {missing}"] * bool(missing) + host + res["problems"]
    res.update(
        schema="s3-ci-record-check/2",
        mode=a.mode,
        ctx=ctx,
        job=a.job,
        platform=a.platform,
        spec_sha256=sha_file(HERE / "expected-steps.json"),
    )
    allp = res["problems"] + [x for s in res.get("steps", []) for x in s["problems"]]
    res["ok"] = not allp
    Path(a.out).write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"ok": res["ok"], "problems": allp}))
    sys.exit(0 if res["ok"] else 1)


if __name__ == "__main__":
    main()
