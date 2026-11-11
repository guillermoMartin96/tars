"""Earth exponential atmosphere: the pinned GMAT table and its density function (M3 T2 S3).

Densities are UNVERIFIED ABOVE 1000 KM (DR-0029 P5): above the top base the top band is
extrapolated, with no cutoff and no upper failure.

Dataset identity (DR-0027 B-1, option B1). The data file
``data/EarthExponentialAtmosphereData.txt`` beside this module is GMAT R2026a
``data/atmosphere/earth/EarthExponentialAtmosphereData.txt``, copied verbatim (git blob
``ec7f1e2023adba77711abf0c8c3c84577bbf49fc``; 661 bytes; 28 rows ``base_km, rho0_kg_m3, H_km``),
sha256 ``75762f679f82e089a4a6eadaa1251c797a2151aab5311b36b2ae96cffefda85e``. GMAT's provenance
statement cites Vallado, 5th ed., section 8.6. The table is 25 of 28 rows identical to the
author-published data file; it is not claimed to agree with any printed textbook table (B-5).
The disputed cells (the 0 km base altitude, the 900 km scale height, the 1000 km row, and the
printed-edition uncertainty) are documented in DR-0027 B-2 and ``docs/science/assumptions.md``;
no value is repaired or substituted (B-3).

Loading (owner decision D-S3-03 (a)). At import, exactly once, ``_load_checked`` reads the raw
bytes from ``Path(__file__).parent / "data" / ...``, compares their sha256 with the pinned literal
**before** any parsing, and only then parses and validates them; a missing, unreadable, altered
or invalid file makes the import fail closed with ``DatasetIntegrityError`` (``reason`` in
``missing``, ``unreadable``, ``digest_mismatch``, ``invalid_content``; ``rule`` V-1 ... V-9b only
for ``invalid_content``). There is no digest bypass. The parsed table is an immutable module
constant; evaluation does no I/O and touches no mutable state. Zip-imported distributions are
unsupported: the file cannot be read there, and the import fails closed with
``reason="unreadable"``.

Evaluation (r1 DQ-2 and DR-0029 P4, in this order): (1) a value whose type is not exactly the
built-in ``float`` raises ``UnsupportedHeightTypeError`` (category ``unsupported_type``; owner
decision D-S3-10 (a)); (2) a non-finite value raises ``DensityInputError`` (``nonfinite``);
(3) ``h_m < 0`` in metres, before any conversion, raises ``DensityInputError`` (``below_zero``;
-0.0 is in range); (4) ``h = h_m / 1000.0``; the band is the first ``i`` with
``h < base_km[i + 1]``, otherwise the top band (an exact base belongs to the band above);
``rho = rho0 * math.exp(-(h - base_km) / H_km)`` with exactly this grouping, in built-in ``float``
and ``math.exp``. Results between bases depend on the platform's ``exp`` (RQ-3).

The one-band 250 km subset (owner decision D-S3-09 (a1)): ``density_one_band_250`` evaluates the
table row whose base is exactly 250.0 km alone, derived once at import from the checked table
(never a literal or a second file), with the same input precedence and domain ``h_m >= 0``. Below
250 km it extrapolates that row below its base; it is a mathematical subset for analytic and
convergence cases and carries no accuracy claim. Selecting it from a scenario is later (T3) work.

Error classes: ``DensityInputError`` subclasses ``ValueError`` and ``UnsupportedHeightTypeError``
subclasses ``TypeError``; a caller's broad ``except ValueError`` would also catch density domain
errors (recorded for S4/T3). Every density error carries ``.category``.
"""

import hashlib
import math
from pathlib import Path
from typing import NamedTuple

__all__ = [
    "DATASET_SHA256",
    "DatasetIntegrityError",
    "DensityInputError",
    "Row",
    "UnsupportedHeightTypeError",
    "density",
    "density_one_band_250",
]

DATASET_SHA256 = "75762f679f82e089a4a6eadaa1251c797a2151aab5311b36b2ae96cffefda85e"
_DATA_PATH = Path(__file__).parent / "data" / "EarthExponentialAtmosphereData.txt"
_ROW_COUNT = 28
_SUBSET_BASE_KM = 250.0


class DatasetIntegrityError(Exception):
    """The pinned dataset could not be loaded; ``reason`` and (for invalid content) ``rule``."""

    def __init__(self, reason: str, rule: str | None = None) -> None:
        super().__init__(reason if rule is None else f"{reason} ({rule})")
        self.reason = reason
        self.rule = rule


class DensityInputError(ValueError):
    """A height outside the supported domain; ``category`` is ``nonfinite`` or ``below_zero``."""

    def __init__(self, category: str) -> None:
        super().__init__(category)
        self.category = category


class UnsupportedHeightTypeError(TypeError):
    """The height is not exactly the built-in ``float``; ``category`` is ``unsupported_type``."""

    def __init__(self) -> None:
        super().__init__("unsupported_type")
        self.category = "unsupported_type"


class Row(NamedTuple):
    """One table row: base altitude (km), base density (kg/m^3), scale height (km)."""

    base_km: float
    rho0: float
    scale_km: float


def _invalid(rule: str) -> DatasetIntegrityError:
    return DatasetIntegrityError("invalid_content", rule)


def _parse_and_validate(raw: bytes) -> tuple[Row, ...]:
    """Parse the whole file and apply V-1 ... V-9b in order; stop at the first failure."""
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError:
        raise _invalid("V-1") from None
    if not text.endswith("\n") or "\r" in text:
        raise _invalid("V-2")
    lines = text[:-1].split("\n")
    if "" in lines:
        raise _invalid("V-2")
    if len(lines) != _ROW_COUNT:
        raise _invalid("V-3")
    fields = [line.split(", ") for line in lines]
    if any(len(tokens) != 3 for tokens in fields):
        raise _invalid("V-4")
    try:
        values = [tuple(float(token) for token in tokens) for tokens in fields]
    except ValueError:
        raise _invalid("V-5") from None
    if not all(math.isfinite(v) for row in values for v in row):
        raise _invalid("V-6")
    if values[0][0] != 0.0:
        raise _invalid("V-7")
    if any(values[i + 1][0] <= values[i][0] for i in range(len(values) - 1)):
        raise _invalid("V-8")
    if not all(row[1] > 0.0 for row in values):
        raise _invalid("V-9a")
    if not all(row[2] > 0.0 for row in values):
        raise _invalid("V-9b")
    return tuple(Row(*row) for row in values)


def _load_checked(path: Path) -> tuple[Row, ...]:
    """Read the raw bytes, check the pinned digest, and only then parse and validate."""
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        raise DatasetIntegrityError("missing") from None
    except OSError:
        raise DatasetIntegrityError("unreadable") from None
    if hashlib.sha256(raw).hexdigest() != DATASET_SHA256:
        raise DatasetIntegrityError("digest_mismatch")
    return _parse_and_validate(raw)


def _derive_one_band_subset(table: tuple[Row, ...]) -> tuple[Row, ...]:
    """The one row whose base is exactly 250.0 km, copied as is."""
    found = tuple(row for row in table if row[0] == _SUBSET_BASE_KM)
    if len(found) != 1:
        raise LookupError("the 250 km base row is not unique")
    return found


_TABLE = _load_checked(_DATA_PATH)
_SUBSET = _derive_one_band_subset(_TABLE)


def _band_index(h: float, table: tuple[Row, ...]) -> int:
    """GMAT band rule: the first i with h < base_km[i+1]; otherwise the top band."""
    last = len(table) - 1
    i = 0
    while i < last:
        if h < table[i + 1][0]:
            return i
        i += 1
    return last


def _evaluate(h_m: float, table: tuple[Row, ...]) -> float:
    h = h_m / 1000.0
    i = _band_index(h, table)
    base_km, rho0, scale_km = table[i]
    return rho0 * math.exp(-(h - base_km) / scale_km)


def density(h_m: float) -> float:
    """Density (kg/m^3) at geodetic height ``h_m`` (metres). UNVERIFIED ABOVE 1000 KM."""
    if type(h_m) is not float:
        raise UnsupportedHeightTypeError()
    if not math.isfinite(h_m):
        raise DensityInputError("nonfinite")
    if h_m < 0.0:
        raise DensityInputError("below_zero")
    return _evaluate(h_m, _TABLE)


def density_one_band_250(h_m: float) -> float:
    """Density (kg/m^3) from the 250 km row alone, domain ``h_m >= 0`` (D-S3-09 (a1))."""
    if type(h_m) is not float:
        raise UnsupportedHeightTypeError()
    if not math.isfinite(h_m):
        raise DensityInputError("nonfinite")
    if h_m < 0.0:
        raise DensityInputError("below_zero")
    return _evaluate(h_m, _SUBSET)
