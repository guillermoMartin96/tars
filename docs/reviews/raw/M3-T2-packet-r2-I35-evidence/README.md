# I-35 verification evidence (research, NOT T2 evidence, NOT a gate)

This directory verifies the I-35 documentation corrections of Review 03's findings: R3-F1, the fingerprint field count, and R3-F2, the Newton denominator notation. It also covers the documentation-only `[U] unavailable` representation of the CPU fingerprint fields. **It regenerates no evidence.** It reads the committed outputs and manifests, and traces the I-33 draft Newton loop.

- **Host:** macOS x86_64, CPython 3.12.15, the locked environment at `d30e449`.
- **Run:**
  1. Copy `i35_checks.py.txt` to a scratch directory as `i35_checks.py`, with the I-33 `pog_lib.py.txt` beside it as `pog_lib.py`.
  2. `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I i35_checks.py <repo>`

| File | What it is |
|---|---|
| `i35_checks.py.txt` / `.out` | **R3-F1:** counts the fields by full JSON path and by leaf name, and lists the repeated names.<br>**R3-F2:** a replica of `_foot_point`'s Newton loop, operation for operation, checked equal to it. It traces the growth of a² + t and b² + t at (2³⁰,)³, (2¹³⁸,)³, (2¹³⁹,)³ and (2¹⁰²⁰,)³.<br>**Fingerprint:** the exit status and diagnostic of the CPU `sysctl` probes, extracted from Review 03's reviewer output; the original evidence manifests |
| `SHA256SUMS` | Checksums of every file above |
