"""DL-4 density twin: an independent, test-side transcription of the density sequence.

M3 T2 S3, proposal v4 section 8.2 (PC-7(S3); D-S3-14 (b)). It is the expectation source for the
S3 output-conformance gate (DL-4 for rho; r2 D-8: output conformance, not accuracy).

Transcribed from the governing text, never from the component:

- r1 DQ-2 (km route), in order: (1) if h_m is not finite, a distinct error; (2) guard in metres,
  before any conversion: h_m < 0 raises the typed domain error (-0.0 is not below);
  (3) h = h_m / 1000.0; (4) the band is the first i with h < base_km[i+1], else the top band
  (an exact base belongs to the band above); base_km, rho0 and H_km are the table's decimal
  strings parsed to binary64; (5) rho = rho0 * exp(-(h - base_km) / H_km), with exactly this
  grouping.
- DR-0029 P4 owner decision: fail closed below 0 m; guard in metres; -0.0 in range; non-finite
  distinct. P5: no cutoff and no upper failure; above 1000 km the top band is extrapolated and
  the result is UNVERIFIED ABOVE 1000 KM.
- Input types (owner decision D-S3-10 (a)): exactly built-in ``float``; anything else is
  ``unsupported_type``, checked before the non-finite check.
- The one-band 250 km subset (D-S3-09 (a1), v4 section 9.3): the table row whose base is
  exactly 250.0, evaluated alone, with the same precedence and the P4 guard (domain h_m >= 0,
  so it extrapolates that row below its base; a mathematical subset, no accuracy claim).

Its own data path and parser: it reads the protected T0 copy at L
(``docs/science/experiments/m3-t0/data/EarthExponentialAtmosphereData.txt``), checks the pinned
sha256 itself and parses with its own parser. Stdlib only; it imports no ``tars`` module in any
form (S3-T-17). Its path is resolved from this file (PB-1). It is the DL-4 limitation that a
faulty shared ``math.exp`` passes conformance (F5).
"""

from __future__ import annotations

import hashlib
import math
from pathlib import Path

PIN = "75762f679f82e089a4a6eadaa1251c797a2151aab5311b36b2ae96cffefda85e"
DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs/science/experiments/m3-t0/data/EarthExponentialAtmosphereData.txt"
)
SUBSET_BASE_KM = 250.0


class TwinDensityError(Exception):
    """A categorized twin outcome; ``category`` is compared through the observation adapter."""

    def __init__(self, category: str) -> None:
        super().__init__(category)
        self.category = category


class TwinDataError(Exception):
    """The twin's own data check failed (the twin cannot be used)."""


def read_rows(path: Path = DATA_PATH) -> tuple[tuple[float, float, float], ...]:
    """Read the bytes, check the pin on the raw bytes, then parse each line
    ``base_km, rho0, H_km`` with built-in ``float`` (correctly rounded)."""
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != PIN:
        raise TwinDataError("digest")
    rows = []
    for line in raw.decode("ascii").split("\n")[:-1]:
        base_text, rho0_text, scale_text = line.split(", ")
        rows.append((float(base_text), float(rho0_text), float(scale_text)))
    if len(rows) != 28:
        raise TwinDataError("rows")
    return tuple(rows)


TABLE = read_rows()


def subset_row(table=TABLE) -> tuple[float, float, float]:
    """The one row whose base is exactly 250.0 km, copied as is."""
    found = [row for row in table if row[0] == SUBSET_BASE_KM]
    if len(found) != 1:
        raise TwinDataError("subset")
    return found[0]


SUBSET = (subset_row(),)


def check_input(h_m) -> None:
    """Precedence: type, then non-finite, then the metre guard (P4)."""
    if type(h_m) is not float:
        raise TwinDensityError("unsupported_type")
    if not math.isfinite(h_m):
        raise TwinDensityError("nonfinite")
    if h_m < 0.0:
        raise TwinDensityError("below_zero")


def band_index(h: float, table=TABLE) -> int:
    """GMAT band rule: the first i with h < base_km[i+1]; otherwise the top band."""
    last = len(table) - 1
    i = 0
    while i < last:
        if h < table[i + 1][0]:
            return i
        i += 1
    return last


def evaluate(h_m: float, table=TABLE) -> float:
    """Steps 3-5 of DQ-2 on an already-checked input."""
    h = h_m / 1000.0
    i = band_index(h, table)
    base_km, rho0, scale_km = table[i]
    return rho0 * math.exp(-(h - base_km) / scale_km)


def density(h_m) -> float:
    """The full-table density twin (kg/m^3). UNVERIFIED ABOVE 1000 KM."""
    check_input(h_m)
    return evaluate(h_m, TABLE)


def density_one_band_250(h_m) -> float:
    """The (a1) subset twin: the 250 km row alone, domain h_m >= 0."""
    check_input(h_m)
    return evaluate(h_m, SUBSET)
