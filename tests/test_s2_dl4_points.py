"""G-17a (listing integrity) and G-17b (class X replay equality) — M3 T2 S2, proposal v11.

Component-free: this module never imports the geodetic component.

G-17a asserts, on every platform, from the frozen file's own text (RG-POL-2, RG-POL-3):
the sha256 recorded in the commit-A evidence (stop 10); the set sequence, contiguous
indices and per-set counts; the 24 S-AX boundary entries; the six DG-CUSP witness slots;
and every label recomputed by the test-side exact predicate (stop 15). It re-runs the
committed generator (RG-POL-6): the exact self-checks are asserted in every run; in the
generation environment every field must be equal (OT-9); elsewhere the structure and the
labels at identical coordinates must be equal (OT-10, OT-11) and class P coordinate
differences are reported, never asserted (OT-12). The regeneration report is emitted into
the pytest warnings summary.

G-17b (new gate, owner decision D-S2-7 (e) = (e-2), I-88) asserts that every one of the
8,853 class X entries of the re-run has the same x, y and z bits as the frozen file
(OT-13), in every environment.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
import warnings
from pathlib import Path

import pytest

from tests import s2_dl4_point_sets as gen
from tests.conftest import REPO_ROOT

LISTING = REPO_ROOT / "tests" / "s2_dl4_points.txt"
GENERATION_RECORD = (
    REPO_ROOT / "docs/science/experiments/m3-t2/s2/commit-a/listing-generation-record.json"
)


class ListingReport(UserWarning):
    """The G-17a / G-17b regeneration report (report-only; RG-POL-6)."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# Owner determination I-101 (pinned v11): "the generation environment" in §3.10 and the
# G-17a/G-17b replay rules means equality of exactly these recorded fields. The commit SHA
# and the CI-only run-record fields identify the run, not its environment: they remain
# mandatory wherever §3.16 requires them and are excluded from this equality. The
# executable's path identifies what is hashed; path equality is not compared. (The author
# chose these fields before I-101; I-101 approved that interpretation.)
ENVIRONMENT_BASIS = (
    "owner determination I-101: equality of sys.version, platform.platform(), "
    "platform.machine(), the uv.lock sha256 and the sha256 of the interpreter executable "
    "(real path resolved before hashing); commit SHA and CI-only run fields excluded"
)
# r83:83 (~/tars-evidence/I-83/review.md line 83), quoted; I-101 does not remove it.
LIMITATION = (
    "ENV fields with unobservable values do not certify a perfectly reproduced "
    "library/build environment; a controlled regeneration comparison must record that "
    "limitation rather than assume matching proxy fields prove identity. (r83:83)"
)


def environment_fields() -> dict[str, str]:
    """The recorded environment fields compared for RG-POL-5/6 (owner determination I-101).
    Equality selects the replay-policy case only; it does not prove library or build
    identity (r83:83)."""
    return {
        "sys.version": sys.version,
        "platform.platform()": platform.platform(),
        "platform.machine()": platform.machine(),
        "uv.lock sha256": _sha256(REPO_ROOT / "uv.lock"),
        "interpreter executable sha256": _sha256(Path(os.path.realpath(sys.executable))),
    }


def _bits3(e: gen.Entry) -> tuple[str, str, str]:
    return (e.x.hex(), e.y.hex(), e.z.hex())


def _same3(a: gen.Entry, b: gen.Entry) -> bool:
    return all(gen.same_bits(u, v) for u, v in ((a.x, b.x), (a.y, b.y), (a.z, b.z)))


@pytest.fixture(scope="module")
def record() -> dict:
    return json.loads(GENERATION_RECORD.read_text())


@pytest.fixture(scope="module")
def frozen() -> list[gen.Entry]:
    return gen.parse_listing(LISTING.read_text())


@pytest.fixture(scope="module")
def regenerated() -> gen.Generation:
    try:
        return gen.generate()
    except gen.SelfCheckError as exc:  # OT-6, OT-7: stop 15 in every run
        pytest.fail(f"stop 15: exact self-check failed in the re-run: {exc}")


@pytest.fixture(scope="module")
def in_generation_environment(record: dict) -> bool:
    return environment_fields() == record["environment"]


# --- G-17a: the frozen file -------------------------------------------------------------


def test_g17a_frozen_file_sha256_equals_commit_a_record(record):
    """RG-POL-2, OT-1: a mismatch is stop 10 (evidence edited after recording)."""
    assert _sha256(LISTING) == record["listing_sha256"], "stop 10"


def test_g17a_set_sequence_indices_and_counts(frozen):
    """RG-POL-3, OT-2: §3.10 set sequence, contiguous indices 0..n-1, per-set counts."""
    assert len(frozen) == gen.TOTAL_ENTRIES == 22665
    seen: list[str] = []
    for e in frozen:
        if not seen or seen[-1] != e.set:
            seen.append(e.set)
    assert tuple(seen) == gen.SET_ORDER
    for name in gen.SET_ORDER:
        indices = [e.index for e in frozen if e.set == name]
        assert indices == list(range(gen.SET_COUNTS[name])), name
    assert gen.SET_COUNTS["S-AX"] == 310


def test_g17a_s_ax_boundary_entries(frozen):
    """RG-POL-3, OT-3: S-AX indices 0-23 are nextDown(b_r), b_r, nextUp(b_r), each in the
    8 signed forms (sx outermost, sz innermost, + before -), by hex."""
    s_ax = [e for e in frozen if e.set == "S-AX"]
    expected = []
    for zhex in ("0x1.83fc4141c97cfp+22", "0x1.83fc4141c97d0p+22", "0x1.83fc4141c97d1p+22"):
        z0 = float.fromhex(zhex)
        for sx in (1.0, -1.0):
            for sy in (1.0, -1.0):
                for sz in (1.0, -1.0):
                    expected.append(((sx * 0.0).hex(), (sy * 0.0).hex(), (sz * z0).hex()))
    assert [_bits3(e) for e in s_ax[:24]] == expected


def test_g17a_dg_cusp_witness_slots(frozen):
    """RG-POL-3, OT-4: the six named witnesses at DG-CUSP indices 9, 6, 3, 51, 117, 7281."""
    cusp = [e for e in frozen if e.set == "DG-CUSP"]
    witnesses = {
        9: ("42697.67270722267", "0.0", "30.0"),
        6: ("42697.67270722267", "0.0", "1.0"),
        3: ("42697.67270722267", "0.0", "1e-3"),
        51: ("42701.94247445068", "0.0", "1.0"),
        7281: ("44832.55634253897", "0.0", "30.0"),
    }
    for idx, (x, y, z) in witnesses.items():
        assert _bits3(cusp[idx]) == (float(x).hex(), float(y).hex(), float(z).hex()), idx
    assert _bits3(cusp[117]) == ("0x1.b8a74054b25cap+15", "0x0.0p+0", "0x1.0624dd2f1a9fcp-10")


def test_g17a_labels_recomputed_from_the_file(frozen):
    """OT-5: every recorded label equals the test-side exact predicate on the file's hex."""
    bad = [(e.set, e.index) for e in frozen if gen.listing_label(e.x, e.y, e.z) != e.label]
    assert bad == [], f"stop 15: label disagreements {bad[:10]}"


# --- G-17a: the committed generator's re-run (RG-POL-6) ---------------------------------


def test_g17a_rerun_exact_self_checks_structure_labels_and_report(
    frozen, regenerated, in_generation_environment, record
):
    """OT-6/7 (exact self-checks, via the fixture), OT-9 (generation environment: every
    field equal), OT-10 (structure), OT-11 (labels at identical coordinates); OT-12 class P
    coordinate differences in another environment are reported, never asserted."""
    re_entries = regenerated.entries
    assert [(e.set, e.index) for e in re_entries] == [(e.set, e.index) for e in frozen]
    class_p_diffs, class_x_diffs, label_diffs = [], [], []
    for f, r in zip(frozen, re_entries, strict=True):
        same = _same3(f, r)
        if same and f.label != r.label:
            label_diffs.append((f.set, f.index, f.label, r.label))
        if not same:
            row = (f.set, f.index, _bits3(f), _bits3(r), f.label, r.label)
            (class_x_diffs if gen.is_class_x(f.set, f.index) else class_p_diffs).append(row)
    slot_fail = [s.index for s in regenerated.slot_checks if not s.equal]
    env = "generation" if in_generation_environment else "other"
    report = {
        "check": "G-17a regeneration report (RG-POL-6)",
        "environment_kind": env,
        "environment": environment_fields(),
        "generation_record_environment": record["environment"],
        "environment_basis": ENVIRONMENT_BASIS,
        "limitation": LIMITATION,
        "entries_compared": len(re_entries),
        "class_P_coordinate_differences": len(class_p_diffs),
        "class_X_coordinate_differences": len(class_x_diffs),
        "label_differences_at_identical_coordinates": len(label_diffs),
        "witness_slot_comparison_failures": slot_fail,
        "differing_entries": [
            {
                "set": s,
                "index": i,
                "class": "X" if gen.is_class_x(s, i) else "P",
                "frozen_hex": list(fh),
                "regenerated_hex": list(rh),
                "frozen_label": fl,
                "regenerated_label": rl,
            }
            for s, i, fh, rh, fl, rl in class_x_diffs + class_p_diffs
        ],
    }
    warnings.warn(
        "S2-G17A-REPORT " + json.dumps(report, sort_keys=True), ListingReport, stacklevel=1
    )
    assert label_diffs == [], f"stop 15 (OT-11): {label_diffs[:5]}"
    if in_generation_environment:
        assert class_p_diffs == [] and class_x_diffs == [] and slot_fail == [], (
            "stop 15 (OT-9): same-environment replay is not byte-identical"
        )
        assert gen.format_listing(re_entries).encode() == LISTING.read_bytes(), (
            "stop 15 (OT-9): same-environment replay bytes differ"
        )


# --- G-17b: class X replay equality (OT-13; owner decision D-S2-7 (e-2), I-88) -----------


def test_g17b_class_x_replay_equality(frozen, regenerated, in_generation_environment):
    """Every class X entry (8,853) of the committed generator's re-run has the same x, y
    and z bits as the frozen file at the same (set, index), signed zeros distinguished.
    A difference is stop 15, in every environment."""
    compared = 0
    diffs = []
    for f, r in zip(frozen, regenerated.entries, strict=True):
        if not gen.is_class_x(f.set, f.index):
            continue
        compared += 1
        if (f.set, f.index) != (r.set, r.index) or not _same3(f, r):
            diffs.append(
                {
                    "set": f.set,
                    "index": f.index,
                    "frozen_hex": list(_bits3(f)),
                    "regenerated_hex": list(_bits3(r)),
                    "frozen_label": f.label,
                    "regenerated_label": r.label,
                }
            )
    warnings.warn(
        "S2-G17B-RECORD "
        + json.dumps(
            {
                "check": "G-17b class X replay equality (OB-33)",
                "environment_kind": "generation" if in_generation_environment else "other",
                "environment": environment_fields(),
                "environment_basis": ENVIRONMENT_BASIS,
                "limitation": LIMITATION,
                "class_X_entries_compared": compared,
                "differences": diffs,
            },
            sort_keys=True,
        ),
        ListingReport,
        stacklevel=1,
    )
    assert compared == gen.CLASS_X_COUNT == 8853
    assert diffs == [], f"stop 15 (G-17b, OT-13): {len(diffs)} class X differences"
