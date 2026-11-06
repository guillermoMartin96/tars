"""S2 gate tests for the geodetic component (M3 T2 S2; proposal v11 §3.11 Part A).

Commit A holds only G-10 (X-P4: A-FP-1 at run time; a guard, exempt from red-first).
"""

from __future__ import annotations

# --- G-10, X-P4 (A-FP-1 at run time) [F-08] -------------------------------------------
#
# Every operand is built at run time from a string, so CPython cannot fold the
# expression at compile time (which would test the compiler's host, not this run).


def _h(s: str) -> float:
    return float.fromhex(s)


def test_g10_w1_round_to_nearest_excludes_toward_zero_and_down():
    # 1 + 3*2^-54 == 1 + 2^-52. False under round-toward-zero and round-down.
    assert _h("0x1p+0") + _h("0x3p-54") == _h("0x1.0000000000001p+0")


def test_g10_w2_round_to_nearest_excludes_up():
    # 1 + 2^-54 == 1. False under round-up.
    assert _h("0x1p+0") + _h("0x1p-54") == _h("0x1p+0")


def test_g10_w3_ties_to_even_excludes_ties_away():
    # 1 + 2^-53 == 1. False under ties-away.
    assert _h("0x1p+0") + _h("0x1p-53") == _h("0x1p+0")


def test_g10_w4_tie_to_even_upward():
    # (1 + 2^-52) + 2^-53 == 1 + 2^-51, tie to even.
    assert _h("0x1.0000000000001p+0") + _h("0x1p-53") == _h("0x1.0000000000002p+0")


def test_g10_w5_no_flush_to_zero():
    # 2^-1022 / 2 != 0. False under flush-to-zero.
    assert _h("0x1p-1022") / _h("0x1p+1") != _h("0x0p+0")


def test_g10_w6_no_denormals_are_zero():
    # 2^-1074 * 1.0 == 2^-1074 != 0. False under denormals-are-zero.
    tiny = _h("0x0.0000000000001p-1022")
    product = tiny * _h("0x1p+0")
    assert product == tiny
    assert product != _h("0x0p+0")


def test_g10_w7_subnormal_tie_to_even():
    # 2^-1074 / 2 == 0, the subnormal tie to even.
    assert _h("0x0.0000000000001p-1022") / _h("0x1p+1") == _h("0x0p+0")
