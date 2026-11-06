"""S2 X-P3 and RP-9 listing by the log route (D-S2-6 (b'); report-only; RQ-3).

For every entry of the frozen listing ``tests/s2_dl4_points.txt`` it emits one census
record into the pytest warnings summary, which every CI job already prints:

    set,index,label,outcome,iterations,final_step_hex,h_hex,phi_hex,source

- a ``passes`` entry takes the DL-4 twin's record through the G-08 adapter (§3.10); the
  accepted (h, phi) bits are listed for X-P3, and a non-accepted pair is ``discarded``
  (E.3: never returned);
- an ``origin`` or ``evolute_region`` entry takes its label, with iterations, final step
  and outputs ``not_evaluated``; the twin is not called.

It does not import the component. On each platform, G-17 equates the component's
geometric outcome with the label and G-08 equates its numerical outcome and accepted bits
with the twin's, so once both are green there (and the twin has passed IN-2), this
component-free listing describes the component's outcomes and outputs. Cross-platform
differences are measured and reported only (RP-8, RP-9); no bound is borrowed.

The header carries the entry count and the sha256 of the body, so a truncated copy is
detectable (stop 18).
"""

from __future__ import annotations

import hashlib
import warnings
from collections import Counter

from tests import s2_dl4_point_sets as gen
from tests.conftest import REPO_ROOT
from tests.s2_dl4_geodetic_twin import twin_outcome

LISTING = REPO_ROOT / "tests" / "s2_dl4_points.txt"
NE = "not_evaluated"


class XP3Listing(UserWarning):
    """The S2 X-P3 / RP-9 census listing (report-only)."""


def census_lines() -> tuple[list[str], Counter]:
    lines = []
    outcomes: Counter = Counter()
    for e in gen.parse_listing(LISTING.read_text()):
        if e.label != "passes":
            row = (e.set, str(e.index), e.label, e.label, NE, NE, NE, NE, "listing label")
            outcomes[e.label] += 1
        else:
            res = twin_outcome(e.x, e.y, e.z)
            rec = res.record
            outcomes[res.outcome] += 1
            if rec is None:
                row = (e.set, str(e.index), e.label, res.outcome, "raised", "raised")
                row += ("discarded", "discarded", "twin record (G-08 adapter)")
            else:
                accepted = res.outcome == "accepted"
                row = (
                    e.set,
                    str(e.index),
                    e.label,
                    res.outcome,
                    str(rec.iterations),
                    rec.last_step.hex(),
                    rec.h.hex() if accepted else "discarded",
                    rec.phi.hex() if accepted else "discarded",
                    "twin record (G-08 adapter)",
                )
        lines.append(",".join(row))
    return lines, outcomes


def test_s2_xp3_rp9_listing_is_emitted():
    lines, outcomes = census_lines()
    assert len(lines) == gen.TOTAL_ENTRIES
    body = "\n".join(lines) + "\n"
    header = (
        f"S2-XP3-LISTING entries={len(lines)} "
        f"body_sha256={hashlib.sha256(body.encode()).hexdigest()} "
        f"outcomes={dict(sorted(outcomes.items()))}\n"
        "set,index,label,outcome,iterations,final_step_hex,h_hex,phi_hex,source\n"
    )
    warnings.warn(header + body + "S2-XP3-LISTING-END", XP3Listing, stacklevel=1)
