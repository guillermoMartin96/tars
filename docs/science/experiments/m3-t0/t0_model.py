"""M3 T0 spike reference model (research only; not project code; no Proof gate).

An independent, minimal coding of the physics approved for M3 (DR-0024, DR-0027 B-1,
DR-0028 J-ax-1), used by the T0 experiments to exercise reference configurations. It
does not import `tars` physics: only the M1/M2 scenario loaders and initial states are
taken from `src/` by the experiment scripts that need them.

Frame convention (DR-0028 J-ax-1; DR-0024 "Q4 coordinate conventions, revision 2"):
  * every vector here is in the M3 inertial frame I (SCI-0003);
  * the non-rotating Earth-axis-aligned model EA is the identity transformation of I;
    the J2 axis, the WGS 84 ellipsoid axis and the atmosphere rotation axis are +Z of I;
  * the air moves as the rigid velocity field v_air = omega_E Z x r (physics, not a frame
    derivative), so v_rel = v - omega_E Z x r.
The only departure from J-ax-1 in this module is `axis_fn`, an explicitly labelled
DIAGNOSTIC that evaluates J2 and the ellipsoid about a supplied unit vector. It exists only
to test DR-0025 Q-G2-1 option (b) against GMAT; it is not an M3 model.

Units: SI (m, s, kg, rad). The atmosphere table is kept in its file units (km) and
evaluated the way GMAT evaluates it unless `units="m"` is requested.
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

HERE = Path(__file__).resolve().parent

# ----------------------------------------------------------------- approved constants
# DR-0024 Resolution Q1-Q3, Q6, Q7 ([NGA] NGA.STND.0036 v1.0.0 Tables 3.1 and 5.1).
MU = 3.986004418e14  # m^3/s^2 (DR-0003; WGS 84)
A_WGS84 = 6378137.0  # m (equatorial radius; J2 reference radius, Q2)
INV_F_WGS84 = 298.257223563
F_WGS84 = 1.0 / INV_F_WGS84
E2_WGS84 = F_WGS84 * (2.0 - F_WGS84)
B_WGS84 = A_WGS84 * (1.0 - F_WGS84)
OMEGA_E = 7.292115e-5  # rad/s (Q7)
C20_EGM2008_TIDE_FREE = -0.484165143790815e-3  # NGA.STND.0036 Table 5.1
J2_FROM_C20 = -math.sqrt(5.0) * C20_EGM2008_TIDE_FREE  # the value a .cof file carries
J2_APPROVED_DECIMAL = 1.0826261739e-3  # the decimal written in DR-0024 Q1

# DR-0027 B-1: the GMAT R2026a table, pinned verbatim by this digest.
TABLE_SHA256 = "75762f679f82e089a4a6eadaa1251c797a2151aab5311b36b2ae96cffefda85e"
TABLE_COPY = HERE / "data" / "EarthExponentialAtmosphereData.txt"


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@dataclass(frozen=True)
class Band:
    base_km: float
    rho0: float  # kg/m^3
    scale_km: float


def load_table(path: Path = TABLE_COPY) -> tuple[Band, ...]:
    """Parse the exponential table after checking its pinned digest (DR-0027 B-1, B-3)."""
    digest = sha256(path)
    if digest != TABLE_SHA256:
        raise ValueError(f"atmosphere table digest {digest} != pinned {TABLE_SHA256}")
    bands = []
    for line in Path(path).read_text().splitlines():
        if line.strip():
            h, rho, s = (float(x) for x in line.split(","))
            bands.append(Band(h, rho, s))
    if [b.base_km for b in bands] != sorted({b.base_km for b in bands}):
        raise ValueError("band bases must be strictly increasing")
    return tuple(bands)


TABLE = load_table()
ONE_BAND_250 = tuple(b for b in TABLE if b.base_km == 250.0)  # DR-0024 Q5 one-band subset


class OutsideDomainError(ValueError):
    """Raised when a density is requested below the table's lower edge in 'raise' mode."""


def band_index(h_km: float, table: tuple[Band, ...] = TABLE) -> int:
    """GMAT's rule (ExponentialAtmosphere::FindBand): the first band i with h < base[i+1];
    the top band otherwise. An exact base height therefore belongs to the band above."""
    for i in range(len(table) - 1):
        if h_km < table[i + 1].base_km:
            return i
    return len(table) - 1


def density(
    h_m: float,
    table: tuple[Band, ...] = TABLE,
    below: str = "raise",
    units: str = "km",
) -> float:
    """Piecewise-exponential density at geodetic height h_m [m].

    below: behaviour for h below the lowest base: 'raise' (OutsideDomainError, GMAT's behaviour
           for h < 0 in R2026a is measured separately), or 'extrapolate' (lowest band's
           formula; a diagnostic used to measure what an RK4 stage would see).
    units: 'km' evaluates exactly as GMAT does (h converted to km, then the formula);
           'm' converts the table to metres once and compares in metres (DR-0024 §9).
    """
    if not math.isfinite(h_m):
        raise ValueError("non-finite height")
    lowest = table[0].base_km
    if units == "km":
        h = h_m / 1000.0
        if h < lowest and below == "raise":
            raise OutsideDomainError(f"h = {h_m} m below the table's lower edge")
        b = table[band_index(h, table)]
        return b.rho0 * math.exp(-(h - b.base_km) / b.scale_km)
    if units == "m":
        if h_m < lowest * 1000.0 and below == "raise":
            raise OutsideDomainError(f"h = {h_m} m below the table's lower edge")
        idx = len(table) - 1
        for i in range(len(table) - 1):
            if h_m < table[i + 1].base_km * 1000.0:
                idx = i
                break
        b = table[idx]
        return b.rho0 * math.exp(-(h_m - b.base_km * 1000.0) / (b.scale_km * 1000.0))
    raise ValueError(units)


# ------------------------------------------------------------------ geodetic height
def geodetic_to_cartesian(
    lat: float, lon: float, h: float, a: float = A_WGS84, e2: float = E2_WGS84
) -> np.ndarray:
    """Closed-form forward transformation (exact up to round-off), ellipsoid axis = +Z."""
    s, c = math.sin(lat), math.cos(lat)
    n = a / math.sqrt(1.0 - e2 * s * s)
    return np.array(
        [(n + h) * c * math.cos(lon), (n + h) * c * math.sin(lon), (n * (1.0 - e2) + h) * s]
    )


def geodetic_iterative(
    r: np.ndarray, a: float = A_WGS84, e2: float = E2_WGS84
) -> tuple[float, float]:
    """Fixed-point iteration on geodetic latitude, iterated to convergence (|dlat| <= 1e-15
    or 60 iterations), with the pole-safe height h = p cos(lat) + z sin(lat) - a sqrt(1 - e2
    sin^2 lat). Returns (lat, h)."""
    x, y, z = (float(c) for c in r)
    p = math.hypot(x, y)
    lat = math.atan2(z, p * (1.0 - e2))
    for _ in range(60):
        s = math.sin(lat)
        n = a / math.sqrt(1.0 - e2 * s * s)
        new = math.atan2(z + e2 * n * s, p)
        done = abs(new - lat) <= 1e-15
        lat = new
        if done:
            break
    s, c = math.sin(lat), math.cos(lat)
    return lat, p * c + z * s - a * math.sqrt(1.0 - e2 * s * s)


def geodetic_vermeille(
    r: np.ndarray, a: float = A_WGS84, e2: float = E2_WGS84
) -> tuple[float, float]:
    """Closed-form conversion of H. Vermeille, J. Geodesy 76 (2002) 451-454, valid outside
    the evolute (every point used here). Returns (lat, h)."""
    x, y, z = (float(c) for c in r)
    e4 = e2 * e2
    pp = (x * x + y * y) / (a * a)
    q = (1.0 - e2) / (a * a) * z * z
    rr = (pp + q - e4) / 6.0
    s = e4 * pp * q / (4.0 * rr**3)
    t = (1.0 + s + math.sqrt(s * (2.0 + s))) ** (1.0 / 3.0)
    u = rr * (1.0 + t + 1.0 / t)
    v = math.sqrt(u * u + e4 * q)
    w = e2 * (u + v - q) / (2.0 * v)
    k = math.sqrt(u + v + w * w) - w
    d = k * math.hypot(x, y) / (k + e2)
    lat = 2.0 * math.atan2(z, d + math.hypot(d, z))
    h = (k + e2 - 1.0) / k * math.hypot(d, z)
    return lat, h


def geodetic_gmat_replica(
    r: np.ndarray, a: float = A_WGS84, f: float = F_WGS84
) -> tuple[float, float]:
    """DIAGNOSTIC replica of GMAT's AtmosphereModel::CalculateGeodetics (Vallado algorithm,
    stop when |dlat| <= 1e-7 rad; h = rxy / cos(lat) - N), read from the public GMAT source
    mirror (version not tied to R2026a; see the README). Not an M3 algorithm."""
    x, y, z = (float(c) for c in r)
    rxy = math.sqrt(x * x + y * y)
    lat = math.atan2(z, rxy)
    ecc2 = f * (2.0 - f)
    delta = 1.0
    while delta > 1.0e-7:
        old = lat
        s = math.sin(old)
        c_factor = a / math.sqrt(1.0 - ecc2 * s * s)
        lat = math.atan2(z + c_factor * ecc2 * s, rxy)
        delta = abs(lat - old)
    s = math.sin(lat)
    c_factor = a / math.sqrt(1.0 - ecc2 * s * s)
    return lat, rxy / math.cos(lat) - c_factor


def spherical_altitude(r: np.ndarray) -> float:
    """SCI-0006 reported altitude / v1-v2 impact quantity."""
    return float(np.linalg.norm(r)) - A_WGS84


HEIGHTS: dict[str, Callable[[np.ndarray], float]] = {
    "geodetic": lambda r: geodetic_iterative(r)[1],
    "geodetic_gmat_replica": lambda r: geodetic_gmat_replica(r)[1],
    "spherical": spherical_altitude,
}


# --------------------------------------------------------------------------- forces
@dataclass(frozen=True)
class Drag:
    cd: float
    area_m2: float
    table: tuple[Band, ...] = TABLE
    height: str = "geodetic"
    below: str = "raise"
    omega: float = OMEGA_E
    corotate: bool = True


@dataclass(frozen=True)
class Config:
    """A spike physics configuration. Everything off = point-mass gravity only."""

    j2: float = 0.0
    drag: Drag | None = None
    mu: float = MU
    re: float = A_WGS84
    # DIAGNOSTIC (Q-G2-1 option b): J2 / ellipsoid axis as a function of t; None = +Z.
    axis_fn: Callable[[float], np.ndarray] | None = None


def j2_accel(r: np.ndarray, j2: float, mu: float, re: float) -> np.ndarray:
    """DR-0024 §4.1, body axis = +Z:
    a = -(3/2) J2 mu R^2 / r^5 [x (1 - 5 z²/r²), y (1 - 5 z²/r²), z (3 - 5 z²/r²)]."""
    x, y, z = r
    rn2 = float(r @ r)
    rn = math.sqrt(rn2)
    k = -1.5 * j2 * mu * re * re / (rn2 * rn2 * rn)
    zz = 5.0 * z * z / rn2
    return k * np.array([x * (1.0 - zz), y * (1.0 - zz), z * (3.0 - zz)])


def frame_about(axis: np.ndarray) -> np.ndarray:
    """A rotation P with P @ axis = +Z (diagnostic use only)."""
    zhat = axis / np.linalg.norm(axis)
    helper = np.array([1.0, 0.0, 0.0])
    xhat = helper - (helper @ zhat) * zhat
    xhat /= np.linalg.norm(xhat)
    yhat = np.cross(zhat, xhat)
    return np.vstack([xhat, yhat, zhat])


def air_velocity(r: np.ndarray, omega: float) -> np.ndarray:
    """v_air = omega Z x r (DR-0024 Q7; DR-0028: a velocity field in I)."""
    return np.array([-omega * r[1], omega * r[0], 0.0])


def acceleration(cfg: Config, t: float, r: np.ndarray, v: np.ndarray, mass: float) -> np.ndarray:
    rn = float(np.linalg.norm(r))
    a = (-cfg.mu / rn**3) * r
    p = None if cfg.axis_fn is None else frame_about(cfg.axis_fn(t))
    if cfg.j2 != 0.0:
        a = a + (
            j2_accel(r, cfg.j2, cfg.mu, cfg.re)
            if p is None
            else p.T @ j2_accel(p @ r, cfg.j2, cfg.mu, cfg.re)
        )
    if cfg.drag is not None:
        d = cfg.drag
        rb = r if p is None else p @ r
        h = HEIGHTS[d.height](rb)
        rho = density(h, d.table, below=d.below)
        vrel = v - air_velocity(r, d.omega) if d.corotate else v
        a = a - (0.5 * rho * d.cd * d.area_m2 / mass) * math.sqrt(float(vrel @ vrel)) * vrel
    return a


# ------------------------------------------------------------------------ propagation
Thrust = Callable[[float, np.ndarray, np.ndarray, float], tuple[np.ndarray, float]]


def rhs(cfg: Config, thrust: Thrust | None = None):
    """y = [r, v, m]; thrust(t, r, v, m) -> (acceleration, dm/dt) or None."""

    def f(t: float, y: np.ndarray) -> np.ndarray:
        r, v, m = y[:3], y[3:6], y[6]
        a = acceleration(cfg, t, r, v, m)
        mdot = 0.0
        if thrust is not None:
            at, mdot = thrust(t, r, v, m)
            a = a + at
        return np.concatenate([v, a, [mdot]])

    return f


@dataclass
class Stage:
    t: float
    r: np.ndarray


def rk4_step(f, t: float, y: np.ndarray, dt: float, stages: list | None = None) -> np.ndarray:
    """Classical RK4 with the operation order of `tars.sim.integrators.RK4`."""
    half = 0.5 * dt
    k1 = f(t, y)
    y2 = y + half * k1
    k2 = f(t + half, y2)
    y3 = y + half * k2
    k3 = f(t + half, y3)
    y4 = y + dt * k3
    k4 = f(t + dt, y4)
    if stages is not None:
        stages.extend([Stage(t + half, y2[:3]), Stage(t + half, y3[:3]), Stage(t + dt, y4[:3])])
    return y + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


def dop853(f, y0: np.ndarray, t_end: float, t_eval=None, events=None, max_step=np.inf):
    sol = solve_ivp(
        f,
        (0.0, t_end),
        y0,
        method="DOP853",
        rtol=1e-13,
        atol=1e-9,
        t_eval=t_eval,
        events=events,
        max_step=max_step,
        dense_output=False,
    )
    if sol.status < 0:
        raise RuntimeError(sol.message)
    return sol


def sma(r: np.ndarray, v: np.ndarray, mu: float = MU) -> float:
    return 1.0 / (2.0 / float(np.linalg.norm(r)) - float(v @ v) / mu)


def raan(r: np.ndarray, v: np.ndarray) -> float:
    h = np.cross(r, v)
    return math.atan2(h[0], -h[1])


def circular_state(alt_m: float, inc_deg: float, mu: float = MU) -> tuple[np.ndarray, np.ndarray]:
    """Circular orbit at RAAN 0, argument of latitude 0 (the M1 construction)."""
    rn = A_WGS84 + alt_m
    vc = math.sqrt(mu / rn)
    i = math.radians(inc_deg)
    return np.array([rn, 0.0, 0.0]), np.array([0.0, vc * math.cos(i), vc * math.sin(i)])


def perigee_state(
    hp_m: float, ha_m: float, inc_deg: float, mu: float = MU
) -> tuple[np.ndarray, np.ndarray]:
    """Elliptic orbit at perigee (spherical altitudes), RAAN 0, argument of perigee 0."""
    rp, ra = A_WGS84 + hp_m, A_WGS84 + ha_m
    a = 0.5 * (rp + ra)
    vp = math.sqrt(mu * (2.0 / rp - 1.0 / a))
    i = math.radians(inc_deg)
    return np.array([rp, 0.0, 0.0]), np.array([0.0, vp * math.cos(i), vp * math.sin(i)])
