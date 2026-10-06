"""Orbit metrics: two-body invariants and comparison with reference trajectories."""

from __future__ import annotations

from collections.abc import Callable, Sequence

import numpy as np

from tars.astro import kepler
from tars.astro.elements import eccentricity_vector, keplerian_period, specific_energy
from tars.sim.state import StateSnapshot, Vector

ReferenceFn = Callable[[float], tuple[Vector, Vector]]


def invariant_metrics(samples: Sequence[StateSnapshot], mu: float) -> dict[str, float]:
    """Drift of quantities that are exactly conserved in two-body motion.

    Any drift is numerical error (or a modelling bug), never physics, under SCI-0001/0004.
    """
    if len(samples) < 2:
        raise ValueError("need at least two samples")
    r0, v0 = samples[0].r, samples[0].v
    e0 = specific_energy(r0, v0, mu)
    h0 = np.cross(r0, v0)
    ecc0 = eccentricity_vector(r0, v0, mu)
    a0 = -mu / (2.0 * e0)
    energy_drift = h_drift = ecc_drift = sma_drift = 0.0
    for s in samples[1:]:
        e = specific_energy(s.r, s.v, mu)
        energy_drift = max(energy_drift, abs((e - e0) / e0))
        h_drift = max(h_drift, float(np.linalg.norm(np.cross(s.r, s.v) - h0) / np.linalg.norm(h0)))
        ecc_drift = max(ecc_drift, float(np.linalg.norm(eccentricity_vector(s.r, s.v, mu) - ecc0)))
        sma_drift = max(sma_drift, abs(-mu / (2.0 * e) - a0))
    return {
        "energy_rel_drift_max": energy_drift,
        "angular_momentum_rel_drift_max": h_drift,
        "eccentricity_vector_drift_max": ecc_drift,
        "sma_drift_max_m": sma_drift,
    }


def kepler_reference(initial: StateSnapshot, mu: float) -> ReferenceFn:
    def ref(t: float) -> tuple[Vector, Vector]:
        return kepler.propagate(initial.r, initial.v, t - initial.t, mu)

    return ref


def trajectory_error_metrics(
    samples: Sequence[StateSnapshot], reference: ReferenceFn
) -> dict[str, float]:
    pos_err = []
    vel_err = []
    for s in samples:
        r_ref, v_ref = reference(s.t)
        pos_err.append(float(np.linalg.norm(s.r - r_ref)))
        vel_err.append(float(np.linalg.norm(s.v - v_ref)))
    return {
        "position_error_max_m": max(pos_err),
        "position_error_final_m": pos_err[-1],
        "velocity_error_max_mps": max(vel_err),
        "velocity_error_final_mps": vel_err[-1],
    }


def period_metrics(
    crossing_times: Sequence[float], initial: StateSnapshot, mu: float
) -> dict[str, float]:
    """Compare ascending-node crossing times with the analytic Keplerian period.

    For two-body motion the nodal period equals the Keplerian period T = 2pi sqrt(a^3/mu).
    The M1 initial state lies on the ascending node, so crossing k should occur at k*T.
    """
    if not crossing_times:
        raise ValueError("no node crossings recorded")
    # The k*T comparison is valid only if the run starts on the ascending node (REV-011).
    if not (
        abs(float(initial.r[2])) <= 1e-9 * float(np.linalg.norm(initial.r)) and initial.v[2] > 0.0
    ):
        raise ValueError("period_metrics requires the initial state on the ascending node")
    a = -mu / (2.0 * specific_energy(initial.r, initial.v, mu))
    period = keplerian_period(a, mu)
    times = np.asarray(crossing_times) - initial.t
    k = np.arange(1, len(times) + 1)
    intervals = np.diff(np.concatenate([[0.0], times]))
    return {
        "analytic_period_s": period,
        "measured_mean_period_s": float(times[-1] / len(times)),
        "period_error_max_s": float(np.max(np.abs(intervals - period))),
        "node_crossing_time_error_max_s": float(np.max(np.abs(times - k * period))),
        "orbits_measured": float(len(times)),
    }
