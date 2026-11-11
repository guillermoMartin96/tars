# RR-15 (S3-T-15): author draft of the operation-by-operation source inspection

**Status: AUTHOR DRAFT.** It is not a review verdict and does not make RR-15 or any obligation MET. Only
the independent S3 implementation review completes RR-15 (v4 §10.1, §10.3, §20; PC-7 §11). This is a
review record: no pytest node, no red run, no JUnit, no import. Densities are UNVERIFIED ABOVE
1000 KM (P5).

**Subject.** `src/tars/sim/atmosphere.py` at committed BC `930e74f6c62719ad8aade6592493d1a1ba16c2a8`
(tree `1d2e9cab9b0f084ab0892d4e66d59b12bb84243d`), git blob `64b057b6…` (full id in `E-BLOB.json`).
The line numbers refer to that blob.

## A. v4 §6.1 / r1 DQ-2 / P4: `density(h_m)`

| # | Specified (v4 §6.1, D-S3-10 (a)) | Source at BC | Author observation |
|---|---|---|---|
| 1 | Type: exactly built-in `float`, else `unsupported_type`, checked first | l.183 `if type(h_m) is not float: raise UnsupportedHeightTypeError()`; `.category = "unsupported_type"` (l.90) | Matches. `type(...) is not float` rejects subclasses, `bool`, `int` and NumPy scalars |
| 2 | Non-finite → distinct error, before the domain check | l.185–186 `if not math.isfinite(h_m): raise DensityInputError("nonfinite")` | Matches the order |
| 3 | `h_m < 0` in metres, before conversion → `below_zero`; −0.0 in range | l.187–188 `if h_m < 0.0: raise DensityInputError("below_zero")` | Matches. `-0.0 < 0.0` is false, so −0.0 is in range |
| 4 | `h = h_m / 1000.0` | l.175 in `_evaluate` | Matches. It is a division, not a multiplication by 0.001 (cf. M-10) |
| 5 | Band: first `i` with `h < base_km[i+1]`, otherwise the top band; an exact base belongs to the band above | l.163–171 `_band_index`: a linear scan, strict `<`, returns `last` otherwise | Matches. Strict `<` puts an exact base in the band above |
| 6 | `ρ = ρ₀ · exp(−(h − base_km) / H_km)` with exactly this grouping | l.178 `return rho0 * math.exp(-(h - base_km) / scale_km)` | Matches. The operations are, in order: subtraction, unary negation, division, `math.exp`, multiplication. No other expression is used (cf. M-11, M-12, M-13) |
| 7 | Built-in `float` and `math.exp`; no NumPy; no `pow`/`**` | imports l.47–50: `hashlib`, `math`, `pathlib.Path`, `typing.NamedTuple`; the only transcendental call is `math.exp` | Matches (S3-T-06 also asserts this by AST) |
| 8 | No cutoff, no upper failure; ≥ 1000 km extrapolated | no branch on `h` other than the band scan | Matches |

## B. v4 §9.2 / §9.3 (a1): `density_one_band_250(h_m)`

| # | Specified | Source at BC | Author observation |
|---|---|---|---|
| 1 | Separate public callable with one parameter; `density` keeps one parameter | l.192 `def density_one_band_250(h_m: float)`; l.181 `def density(h_m: float)` | Matches |
| 2 | `_SUBSET = _derive_one_band_subset(_TABLE)`, computed once from the checked table; the unique row with `base == 250.0`, copied bitwise; no literal and no second file | l.160; l.151–156 `found = tuple(row for row in table if row[0] == _SUBSET_BASE_KM)`, which must be unique | Matches. `_SUBSET_BASE_KM = 250.0` (l.65) is the selection key, not a copy of the row's values (S3-T-14c scans for `7.248e-11` and `45.546` literals) |
| 3 | Precedence: type → non-finite → P4 `h_m < 0` → `below_zero` | l.194–199, the same three checks in the same order | Matches (a1). There is no `below_subset_base` category, which is correct for (a1) |
| 4 | Evaluation with the single row, DQ-2 grouping, `h = h_m / 1000.0` | l.200 `_evaluate(h_m, _SUBSET)`, the shared private evaluator | Matches. With one row, `_band_index` returns 0 (`last = 0`) |

## C. §5.3 checked loader (context for RR-15; gated elsewhere by S3-T-02/04)

- `_load_checked` reads raw bytes, maps `FileNotFoundError` → `missing` and `OSError` → `unreadable`,
  and compares the sha256 with `DATASET_SHA256` **before** `_parse_and_validate` (l.138–148).
- `_TABLE` is loaded once at import (l.159).
- There is no bypass.

## Limits of this draft

The author wrote both the component and this draft. The independent reviewer must perform the
inspection afresh. Equivalent mutant M-13 (`(base − h) / H`) is detectable only by this inspection:
row A6 records that the specified grouping `-(h - base_km) / scale_km` is present. This is not a
claim of libm accuracy.
