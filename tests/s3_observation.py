"""S3 observation adapter (test-side; M3 T2 S3, proposal v4 section 8.3).

Every S3 density assertion compares observations, so an unexpected exception, a value where an
error was expected, or a wrong category becomes an ``AssertionError`` at the designated node,
never an escaping error (v4 section 10.1 kill criterion).

- ``observe(fn, arg)``: ``("value", <16 hex digits of the 64 bits>)`` when ``fn(arg)`` returns a
  ``float``; ``("raised", <category>)`` when it raises an exception carrying a string
  ``category`` (or, for dataset errors, ``reason``) attribute; ``("raised",
  "unexpected:<qualname>")`` for any other ``Exception``; ``("returned", <qualname>)`` when the
  result is not a ``float``.
- ``observe_parse(fn, raw)``: ``("accepted", <row count>)`` when ``fn(raw)`` returns;
  ``("raised", reason, rule)`` for an exception whose class is named ``DatasetIntegrityError``;
  ``("unexpected", <qualname>)`` for any other ``Exception`` (including ``UnicodeDecodeError``,
  ``ValueError``, ``IndexError`` and ``TypeError``).
- ``parse_token(token)``: binary64 hex tokens through ``float.fromhex``; the four non-finite
  tokens ``nan``, ``-nan``, ``inf``, ``-inf`` through ``float()``. No decimal re-parsing.

Equality is bitwise (``+0.0`` and ``-0.0`` differ). Stdlib only; imports no ``tars`` module.
"""

from __future__ import annotations

import struct

NONFINITE_TOKENS = ("nan", "-nan", "inf", "-inf")


def bits_hex(x: float) -> str:
    return f"{struct.unpack('<Q', struct.pack('<d', x))[0]:016x}"


def observe(fn, arg) -> tuple[str, str]:
    try:
        result = fn(arg)
    except Exception as exc:
        label = getattr(exc, "category", None)
        if not isinstance(label, str):
            label = getattr(exc, "reason", None)
        if isinstance(label, str):
            return ("raised", label)
        return ("raised", f"unexpected:{type(exc).__qualname__}")
    if type(result) is not float:
        return ("returned", type(result).__qualname__)
    return ("value", bits_hex(result))


def observe_parse(fn, raw: bytes) -> tuple:
    try:
        rows = fn(raw)
    except Exception as exc:
        if type(exc).__name__ == "DatasetIntegrityError":
            return ("raised", getattr(exc, "reason", None), getattr(exc, "rule", None))
        return ("unexpected", type(exc).__qualname__)
    return ("accepted", len(rows))


def parse_token(token: str) -> float:
    if token in NONFINITE_TOKENS:
        return float(token)
    return float.fromhex(token)


def token_of(x: float) -> str:
    """The listing token of a finite binary64 value (its exact hex form)."""
    return x.hex()
