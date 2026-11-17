"""Recording-only bootstrap, backend-binding harness b1. Inert unless S3REC_DIR is set.

Lineage (byte sources inspected and kept in this packet):
  - preflight v3.1  S3-review-recording-preflight-v1/harness/rec/sitecustomize.py
                    sha256 68f4538d…e049
  - r5 harness-v5   S3-IMPL-REVIEW-E-4298dd3-r5/harness-v5/rec/sitecustomize.py
                    sha256 066000c4…2e39
    (= v3.1 + "parent_test_node" in each spawn observation; kept unchanged here)
b1 adds, and changes nothing else:
  (a) at start-up, two clock samples (time.time_ns / time.monotonic_ns) held in memory only;
  (b) at exit, AFTER the unchanged ENV capture, an OPTIONAL backend-binding capture: only when
      S3REC_BINDCAP names a file, it is loaded BY PATH and writes <S3REC_DIR>/<pid>.binding.json.
      Any exception is written to <S3REC_DIR>/<pid>.binding-error.txt. Never alters exit status,
      never writes to stdout/stderr.
  (c) sys.dont_write_bytecode stays True for the whole at-exit block (ENV and binding capture).

Unchanged from v3.1/v5: ONE append-only audit hook for child-process launch events (never raises,
blocks or writes; records no environment contents) and ONE atexit handler. Start-up imports only
os, sys, atexit, time. No import of tars/tests/backend/numpy, no sys.path change, profiler, tracer,
warning filter, FP or stdio change, and no subprocess/platform patching. Processes ending via
os._exit, exec, or a fatal signal leave no record (exposed by parent spawns and record counts).
"""

import os

if os.environ.get("S3REC_DIR"):
    import atexit
    import sys
    import time

    _s3rec_start = {"time_ns": time.time_ns(), "monotonic_ns": time.monotonic_ns()}
    _S3REC_EVENTS = frozenset(
        {
            "subprocess.Popen",
            "os.system",
            "os.posix_spawn",
            "os.spawn",
            "os.exec",
            "os.fork",
            "os.forkpty",
            "pty.spawn",
        }
    )
    _s3rec_spawns = []
    _s3rec_phase = ["payload"]

    def _s3rec_text(x):
        if isinstance(x, (bytes, bytearray)):
            return os.fsdecode(bytes(x))
        return x if isinstance(x, str) else repr(x)

    def _s3rec_audit(event, args):
        if event not in _S3REC_EVENTS:
            return
        try:
            item = {
                "event": event,
                "phase": _s3rec_phase[0],
                "n": len(_s3rec_spawns),
                "t_monotonic_ns": time.monotonic_ns(),
                "pid": os.getpid(),
                "parent_test_node": os.environ.get("PYTEST_CURRENT_TEST"),
            }
            if event == "subprocess.Popen":
                exe, argv, cwd, env = args
                item.update(
                    executable=None if exe is None else _s3rec_text(exe),
                    argv=[_s3rec_text(a) for a in argv]
                    if isinstance(argv, (list, tuple))
                    else _s3rec_text(argv),
                    cwd=None if cwd is None else _s3rec_text(cwd),
                    env_overridden=env is not None,
                )
            elif event in ("os.posix_spawn", "os.exec", "os.spawn"):
                item.update(
                    path=_s3rec_text(args[0]),
                    argv=[_s3rec_text(a) for a in args[1]] if len(args) > 1 else None,
                    env_overridden=len(args) > 2 and args[2] is not None,
                )
            elif event == "os.system":
                item.update(command=_s3rec_text(args[0]))
            _s3rec_spawns.append(item)
        except BaseException:
            pass

    sys.addaudithook(_s3rec_audit)

    def _s3rec_load(name, path):
        import importlib.util

        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def _s3rec_err(path, exc):
        try:
            with open(path, "x", encoding="utf-8") as fh:
                fh.write(f"{type(exc).__qualname__}: {exc}\n")
        except BaseException:
            pass

    def _s3rec_capture():
        d = os.environ["S3REC_DIR"]
        pid = os.getpid()
        _s3rec_phase[0] = "capture"
        _dwb = sys.dont_write_bytecode
        sys.dont_write_bytecode = True
        loader = os.path.realpath(__file__)
        env_path = os.path.join(d, f"{pid}.env.json")
        try:
            try:
                mod = _s3rec_load("_s3rec_envcap", os.environ["S3REC_ENVCAP"])
                mod.capture(
                    env_path,
                    os.environ["S3REC_SUBJECT"],
                    os.environ.get("S3REC_LABEL", ""),
                    "sitecustomize-atexit",
                    spawns=_s3rec_spawns,
                    loader=loader,
                )
            except BaseException as exc:  # never alters exit status
                _s3rec_err(os.path.join(d, f"{pid}.error.txt"), exc)
            bc = os.environ.get("S3REC_BINDCAP")
            if bc:
                try:
                    bmod = _s3rec_load("_s3rec_bindcap", bc)
                    bmod.capture(
                        os.path.join(d, f"{pid}.binding.json"),
                        env_path=env_path,
                        spawns=_s3rec_spawns,
                        start=_s3rec_start,
                        loader=loader,
                    )
                except BaseException as exc:  # never alters exit status
                    _s3rec_err(os.path.join(d, f"{pid}.binding-error.txt"), exc)
        finally:
            sys.dont_write_bytecode = _dwb

    atexit.register(_s3rec_capture)
