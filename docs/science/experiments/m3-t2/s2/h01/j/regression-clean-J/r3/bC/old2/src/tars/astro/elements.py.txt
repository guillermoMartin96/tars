"""Conversion between Cartesian state and classical orbital elements.

References: Vallado (2013) §2.5 algorithms RV2COE/COE2RV; Curtis (2014) §4.4-4.6.

Singularities (see plan §2.4):
- Circular orbits (e ~ 0): argument of perigee and true anomaly are undefined. We
  set argp = 0 and nu = u, where u is the argument of latitude (angle from the
  ascending node to the position), which stays well defined.
- Equatorial orbits (i ~ 0 or pi): RAAN is undefined. We set raan = 0 and measure
  angles from the inertial x axis.
Angles are computed with atan2 to avoid acos quadrant ambiguity and precision loss.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from tars.sim.state import Vector

TWO_PI = 2.0 * math.pi
# Thresholds below which e or the node vector are treated as zero (singular cases).
ECC_TOL = 1e-11
NODE_TOL = 1e-11


@dataclass(frozen=True)
class ClassicalElements:
    """Classical (Keplerian) elements. Lengths in m, angles in radians in [0, 2pi).

    Attributes:
        a: Semi-major axis.
        e: Eccentricity.
        i: Inclination.
        raan: Right ascension of the ascending node.
        argp: Argument of perigee (0 for circular orbits).
        nu: True anomaly (equals ``u`` for circular orbits).
        u: Argument of latitude, argp + nu (from the x axis for equatorial orbits).
    """

    a: float
    e: float
    i: float
    raan: float
    argp: float
    nu: float
    u: float


def _wrap(angle: float) -> float:
    wrapped = math.fmod(angle, TWO_PI)
    return wrapped + TWO_PI if wrapped < 0.0 else wrapped


def _signed_angle(from_vec: Vector, to_vec: Vector, axis_hat: Vector) -> float:
    """Angle from ``from_vec`` to ``to_vec`` measured positively about ``axis_hat``."""
    sin_part = float(np.dot(np.cross(from_vec, to_vec), axis_hat))
    cos_part = float(np.dot(from_vec, to_vec))
    return _wrap(math.atan2(sin_part, cos_part))


def eccentricity_vector(r: Vector, v: Vector, mu: float) -> Vector:
    r_norm = float(np.linalg.norm(r))
    return ((float(np.dot(v, v)) - mu / r_norm) * r - float(np.dot(r, v)) * v) / mu


def specific_energy(r: Vector, v: Vector, mu: float) -> float:
    return 0.5 * float(np.dot(v, v)) - mu / float(np.linalg.norm(r))


def rv_to_elements(r: Vector, v: Vector, mu: float) -> ClassicalElements:
    r = np.asarray(r, dtype=np.float64)
    v = np.asarray(v, dtype=np.float64)
    h = np.cross(r, v)
    h_norm = float(np.linalg.norm(h))
    if h_norm == 0.0:
        raise ValueError("rectilinear trajectory: angular momentum is zero")
    h_hat = h / h_norm
    node = np.array([-h[1], h[0], 0.0])  # k x h
    node_norm = float(np.linalg.norm(node))
    e_vec = eccentricity_vector(r, v, mu)
    e = float(np.linalg.norm(e_vec))
    energy = specific_energy(r, v, mu)
    if energy == 0.0:
        raise ValueError("parabolic trajectory: semi-major axis undefined")
    a = -mu / (2.0 * energy)
    i = math.acos(max(-1.0, min(1.0, h[2] / h_norm)))

    equatorial = node_norm <= NODE_TOL * h_norm
    circular = e <= ECC_TOL
    x_hat = np.array([1.0, 0.0, 0.0])

    if equatorial:
        raan = 0.0
        node_hat = x_hat
    else:
        node_hat = node / node_norm
        raan = _wrap(math.atan2(node[1], node[0]))

    u = _signed_angle(node_hat, r, h_hat)
    if circular:
        argp = 0.0
        nu = u
    else:
        argp = _signed_angle(node_hat, e_vec, h_hat)
        nu = _signed_angle(e_vec, r, h_hat)

    return ClassicalElements(a=a, e=e, i=i, raan=raan, argp=argp, nu=nu, u=u)


def elements_to_rv(
    a: float, e: float, i: float, raan: float, argp: float, nu: float, mu: float
) -> tuple[Vector, Vector]:
    """Cartesian ECI (r, v) from classical elements (elliptical orbits, e < 1)."""
    if not 0.0 <= e < 1.0:
        raise ValueError("only elliptical orbits (0 <= e < 1) are supported")
    if a <= 0.0:
        raise ValueError("semi-major axis must be positive")
    p = a * (1.0 - e * e)
    cos_nu, sin_nu = math.cos(nu), math.sin(nu)
    r_pf = np.array([cos_nu, sin_nu, 0.0]) * (p / (1.0 + e * cos_nu))
    v_pf = np.array([-sin_nu, e + cos_nu, 0.0]) * math.sqrt(mu / p)

    cO, sO = math.cos(raan), math.sin(raan)
    ci, si = math.cos(i), math.sin(i)
    cw, sw = math.cos(argp), math.sin(argp)
    # Perifocal -> ECI rotation: R3(-raan) R1(-i) R3(-argp).
    rot = np.array(
        [
            [cO * cw - sO * sw * ci, -cO * sw - sO * cw * ci, sO * si],
            [sO * cw + cO * sw * ci, -sO * sw + cO * cw * ci, -cO * si],
            [sw * si, cw * si, ci],
        ]
    )
    return rot @ r_pf, rot @ v_pf


def circular_orbit_state(
    radius: float, inclination: float, raan: float, arg_latitude: float, mu: float
) -> tuple[Vector, Vector]:
    """State on a circular orbit; for e = 0 we use argp = 0 so nu = argument of latitude."""
    return elements_to_rv(radius, 0.0, inclination, raan, 0.0, arg_latitude, mu)


def keplerian_period(a: float, mu: float) -> float:
    """T = 2 pi sqrt(a^3 / mu) (Kepler's third law, two-body)."""
    if a <= 0.0:
        raise ValueError("period is defined only for bound (a > 0) orbits")
    return TWO_PI * math.sqrt(a**3 / mu)
