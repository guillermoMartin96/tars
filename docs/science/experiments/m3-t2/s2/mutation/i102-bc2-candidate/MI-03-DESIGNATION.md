# MI-03: designated killer versus actual killer (I-102 step 4)

"MI-03" is the campaign script's identifier. v11 has no identifier for this row.

## v11's mutant and designated killer (verbatim)

v11 §3.12, "Interface and error mutants" table (P:2257):

> | Precedence swap, non-finite after evolute | G-06 (inf, 0, 0) |

## Exact transformation applied by the campaign (`scripts/mutate.py`, MI-03; unchanged from I-101)

Edit 1 removes these three lines (`src/tars/sim/geodesy.py` lines 148–150 at BC):

```
    # Step 2: non_finite.
    if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
        raise GeodeticDomainError("non_finite")
```

Edit 2 inserts the same check directly after the evolute check (after lines 155–156):

```
    if _in_evolute_region(x, y, z):
        raise GeodeticDomainError("evolute_region")
    if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
        raise GeodeticDomainError("non_finite")
```

The campaign designates the whole parametrized test `test_g06_section_3_8_order_table`, which has 8 nodes.

## What actually kills it

In the I-101 campaign at BC, 1 of the 8 nodes failed: `test_g06_section_3_8_order_table[r0-non_finite]`, the row `((math.nan, 0.0, 0.0), "non_finite")`.

The assertion is in `_raises_reason`, in `tests/test_s2_geodetic.py`:

```
    except BaseException as exc:  # any other exception is a failure of this node
        raise AssertionError(f"{r!r}: expected {reason}, got {type(exc).__name__}: {exc}") from exc
```

Recorded message: `AssertionError: (nan, 0.0, 0.0): expected non_finite, got ValueError: cannot convert NaN to integer ratio`.

The node `[r1-non_finite]` is the row `((math.inf, 0.0, 0.0), "non_finite")`, which is v11's designated killer. It **passed** against the mutant.

## Why the designated row cannot kill it

- `_in_evolute_region` begins with the exact pre-filter `if abs(x) >= _PREFILTER or abs(y) >= _PREFILTER or abs(z) >= _PREFILTER: return False` (§3.7.5).
- For any input with an infinite component, `abs(inf) >= 65536.0` is True. The guard therefore returns False before any `Fraction` is built.
- The relocated non-finite check then raises `non_finite`, which is the same outcome as the unmutated component.
- So **no input with an infinite component can distinguish the mutant**. This includes (inf, 0, 0).
- The mutant is observable only for a NaN component whose other components are all finite with |·| < 2^16. For those inputs, `abs(nan) >= 65536.0` is False, `Fraction(nan)` raises `ValueError` outside E.1, and the raw exception escapes. (nan, 0, 0) is one such input.

## Is (nan, 0, 0) "another designated assertion within the same approved G-06 test row"?

**No.**
- v11 lists (nan, 0, 0) → `non_finite` and (inf, 0, 0) → `non_finite, not overflow` as **separate rows** of the §3.8 order table (P:1497–1499).
- v11's MI-03 designation names the (inf, 0, 0) row specifically.
- The (nan, 0, 0) row is in the same approved G-06 test, but it is not the designated row.
- Counting it would substitute a killer. That is a designation correction, and it needs an owner decision.

## Proposed change (owner decision requested; not applied)

1. In v11 §3.12, "Interface and error mutants", change the killer for "Precedence swap, non-finite after evolute" from "G-06 (inf, 0, 0)" to "G-06 (nan, 0, 0)". This is the existing §3.8/G-06 row and needs no test or production change. Reason: the §3.7.5 pre-filter makes (inf, 0, 0) unable to distinguish the mutant, as shown above. This is the same class of defect as F-07, where the designated kill was impossible.
2. Narrow the campaign's MI-03 node list from the whole parametrized test to the single node `tests/test_s2_geodetic.py::test_g06_section_3_8_order_table[r0-non_finite]`. The existing counting rule then applies to it: the node must fail, and only by assertion.
3. Record this in D and in the review handoff as an owner-approved designation correction.

The alternative of keeping (inf, 0, 0) as the designated killer would leave MI-03 UNKILLED (stop 8). No test can change that, because the mutant is unobservable at every input with an infinite component.

## Corrected campaign (I-102, `campaign/`)

The result is unchanged: `[r0-non_finite]` (nan, 0, 0) FAILS by the same assertion, and `[r1-non_finite]` (inf, 0, 0) PASSES. The other 6 nodes pass.
