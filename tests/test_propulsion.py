"""Standalone propulsion model (M2 task T1; DR-0011, DR-0012, DR-0014; ADR-0007).

Reference-case values (R-4D-11 class, DR-0010) appear only here and in scenarios:
the model itself is configurable and holds no engine numbers.
"""

import math
from decimal import Decimal, localcontext
from itertools import pairwise

import numpy as np
import pytest
from scipy.integrate import quad, solve_ivp

from tars.astro.elements import circular_orbit_state, specific_energy
from tars.sim.constants import STANDARD_GRAVITY, WGS84
from tars.sim.integrators import RK4
from tars.sim.propulsion import (
    DIRECTION_LAWS,
    EVENT_TIME_RESOLUTION_S,
    BurnEndCause,
    BurnRejectedError,
    BurnRejection,
    EngineSpec,
    InsufficientPropellantPolicy,
    Prograde,
    PropulsionSpecError,
    Retrograde,
    SpacecraftSpec,
    TankSpec,
    plan_burn,
    rocket_equation_delta_v,
    thrust_acceleration,
)

# DR-0010 reference case (configurable parameters, not model constants).
REF_ENGINE = EngineSpec(thrust_n=490.0, isp_s=312.0)
REF_DRY_KG = 1000.0
REF_PROP_KG = 300.0
REF_IGNITION_S = 600.0
REF_DURATION_S = 77.3

BAD_NUMBERS = [0.0, -1.0, math.nan, math.inf, -math.inf]


def _ref_spacecraft() -> SpacecraftSpec:
    return SpacecraftSpec(
        dry_mass_kg=REF_DRY_KG, engine=REF_ENGINE, tank=TankSpec(propellant_kg=REF_PROP_KG)
    )


# ----------------------------------------------------------------------------- specs


def test_standard_gravity_is_the_exact_si_definition():
    # NIST CODATA: standard acceleration of gravity, 9.806 65 m/s^2 exactly (SCI-0009).
    assert STANDARD_GRAVITY == 9.80665


def test_engine_exhaust_velocity_and_mass_flow():
    # c = Isp g0; mdot = F / c (SCI-0008, SCI-0009). Hand values for 490 N / 312 s.
    assert REF_ENGINE.exhaust_velocity_mps == 312.0 * 9.80665
    assert REF_ENGINE.mass_flow_kgps == 490.0 / (312.0 * 9.80665)
    assert REF_ENGINE.mass_flow_kgps == pytest.approx(0.16014773857666, rel=1e-13, abs=0)


def test_engine_is_configurable_and_immutable():
    small = EngineSpec(thrust_n=22.0, isp_s=220.0)
    assert small.mass_flow_kgps == pytest.approx(22.0 / (220.0 * 9.80665), rel=1e-15, abs=0)
    with pytest.raises(AttributeError):
        small.thrust_n = 1.0  # type: ignore[misc]


@pytest.mark.parametrize("bad", BAD_NUMBERS)
def test_engine_rejects_non_positive_or_non_finite_parameters(bad):
    with pytest.raises(PropulsionSpecError):
        EngineSpec(thrust_n=bad, isp_s=312.0)
    with pytest.raises(PropulsionSpecError):
        EngineSpec(thrust_n=490.0, isp_s=bad)


@pytest.mark.parametrize("bad", [True, "490", None])
def test_engine_rejects_non_numeric_parameters(bad):
    with pytest.raises(PropulsionSpecError):
        EngineSpec(thrust_n=bad, isp_s=312.0)


def test_spacecraft_mass_properties():
    sc = _ref_spacecraft()
    assert sc.initial_mass_kg == 1300.0
    assert sc.tank.propellant_kg == 300.0


@pytest.mark.parametrize("bad", BAD_NUMBERS)
def test_spacecraft_rejects_invalid_dry_mass(bad):
    with pytest.raises(PropulsionSpecError):
        SpacecraftSpec(dry_mass_kg=bad, engine=REF_ENGINE, tank=TankSpec(propellant_kg=1.0))


@pytest.mark.parametrize("bad", [-1.0, -1e-300, math.nan, math.inf])
def test_tank_rejects_negative_or_non_finite_propellant(bad):
    with pytest.raises(PropulsionSpecError):
        TankSpec(propellant_kg=bad)


def test_empty_tank_is_a_valid_configuration():
    assert TankSpec(propellant_kg=0.0).propellant_kg == 0.0


# ------------------------------------------------------------------ thrust acceleration


def test_thrust_acceleration_is_thrust_over_current_mass_along_direction():
    # SCI-0010: a = F/m along u_hat; no mdot*v term.
    u = np.array([0.0, 0.6, 0.8])
    a = thrust_acceleration(REF_ENGINE, u, total_mass_kg=1287.5)
    np.testing.assert_array_equal(a, (490.0 / 1287.5) * u)
    assert not a.flags.writeable


@pytest.mark.parametrize("mass", [0.0, -5.0, math.nan, math.inf])
def test_thrust_acceleration_rejects_invalid_mass(mass):
    with pytest.raises(ValueError):
        thrust_acceleration(REF_ENGINE, np.array([1.0, 0.0, 0.0]), total_mass_kg=mass)


@pytest.mark.parametrize("u", [[2.0, 0.0, 0.0], [0.0, 0.0, 0.0], [math.nan, 0.0, 1.0], [1.0, 0.0]])
def test_thrust_acceleration_requires_a_unit_direction(u):
    with pytest.raises(ValueError):
        thrust_acceleration(REF_ENGINE, np.array(u), total_mass_kg=1300.0)


# ------------------------------------------------------------------- direction laws


def _orbit_state():
    return circular_orbit_state(
        radius=WGS84.equatorial_radius + 250_000.0,
        inclination=math.radians(51.6),
        raan=0.3,
        arg_latitude=1.1,
        mu=WGS84.mu,
    )


def test_prograde_is_the_unit_inertial_velocity():
    r, v = _orbit_state()
    u = Prograde().direction(0.0, r, v)
    assert np.linalg.norm(u) == pytest.approx(1.0, abs=1e-15)
    np.testing.assert_allclose(u, v / np.linalg.norm(v), rtol=0, atol=1e-16)
    # In the orbit plane: perpendicular to the orbit normal N = r x v (VNB, GMAT).
    n_hat = np.cross(r, v) / np.linalg.norm(np.cross(r, v))
    assert abs(float(u @ n_hat)) <= 1e-15


def test_retrograde_is_exactly_opposite_prograde():
    r, v = _orbit_state()
    np.testing.assert_array_equal(Retrograde().direction(0.0, r, v), -Prograde().direction(0, r, v))


def test_direction_laws_return_read_only_unaliased_arrays_and_accept_read_only_inputs():
    r, v = _orbit_state()
    r.flags.writeable = False
    v.flags.writeable = False
    for law in (Prograde(), Retrograde()):
        u = law.direction(0.0, r, v)
        assert not u.flags.writeable
        assert not np.shares_memory(u, v)


@pytest.mark.parametrize("v", [[0.0, 0.0, 0.0], [math.nan, 1.0, 0.0], [math.inf, 0.0, 0.0]])
def test_velocity_tracking_is_undefined_without_a_finite_nonzero_velocity(v):
    with pytest.raises(ValueError):
        Prograde().direction(0.0, np.array([7e6, 0.0, 0.0]), np.array(v))


def test_direction_registry_names_match_command_vocabulary():
    # DR-0014 command enum: direction in {"prograde", "retrograde"}.
    assert set(DIRECTION_LAWS) == {"prograde", "retrograde"}
    assert all(name == law.name for name, law in DIRECTION_LAWS.items())


class _InertialHold:
    """A future guidance mode, written outside the module (DR-0012 extensibility)."""

    name = "inertial_hold"

    def __init__(self, u):
        self.u = np.asarray(u, dtype=float)

    def direction(self, t, r, v):
        return self.u


def test_new_direction_laws_plug_in_without_changing_the_model():
    r, v = _orbit_state()
    law = _InertialHold([0.0, 0.0, 1.0])
    a = thrust_acceleration(REF_ENGINE, law.direction(0.0, r, v), total_mass_kg=1300.0)
    np.testing.assert_array_equal(a, [0.0, 0.0, 490.0 / 1300.0])


# -------------------------------------------------------------------------- burn plan


def test_burn_plan_for_completed_burn_has_exact_times_and_propellant():
    plan = plan_burn(REF_ENGINE, propellant_kg=REF_PROP_KG, ignition_t_s=600.0, duration_s=77.3)
    assert plan.ignition_t_s == 600.0
    assert plan.commanded_duration_s == 77.3
    assert plan.cutoff_t_s == 600.0 + 77.3
    # The plan describes the interval float64 event times represent (REV-T2-03).
    assert plan.burn_duration_s == plan.cutoff_t_s - plan.ignition_t_s
    assert abs(plan.burn_duration_s - 77.3) <= EVENT_TIME_RESOLUTION_S
    assert plan.end_cause is BurnEndCause.COMPLETED
    assert plan.propellant_used_kg == REF_ENGINE.mass_flow_kgps * plan.burn_duration_s
    assert plan.propellant_used_kg == pytest.approx(12.379420191975958, rel=1e-14, abs=0)


def test_insufficient_propellant_is_rejected_by_default():
    # DR-0014 3C: default policy is reject; no plan is produced.
    with pytest.raises(BurnRejectedError) as err:
        plan_burn(REF_ENGINE, propellant_kg=10.0, ignition_t_s=600.0, duration_s=77.3)
    assert err.value.reason is BurnRejection.INSUFFICIENT_PROPELLANT
    assert err.value.reason.value == "insufficient_propellant"


def test_burn_to_depletion_must_be_requested_and_ends_exactly_at_depletion():
    plan = plan_burn(
        REF_ENGINE,
        propellant_kg=10.0,
        ignition_t_s=600.0,
        duration_s=77.3,
        policy=InsufficientPropellantPolicy.BURN_TO_DEPLETION,
    )
    t_dep = 10.0 / REF_ENGINE.mass_flow_kgps
    assert plan.end_cause is BurnEndCause.PROPELLANT_DEPLETED
    assert plan.commanded_duration_s == 77.3
    assert plan.cutoff_t_s == 600.0 + t_dep
    assert plan.burn_duration_s == plan.cutoff_t_s - 600.0
    assert abs(plan.burn_duration_s - t_dep) <= EVENT_TIME_RESOLUTION_S
    assert plan.propellant_used_kg == 10.0  # exactly: propellant never goes negative


def test_burn_to_depletion_with_sufficient_propellant_completes_normally():
    plan = plan_burn(
        REF_ENGINE,
        propellant_kg=REF_PROP_KG,
        ignition_t_s=0.0,
        duration_s=77.3,
        policy=InsufficientPropellantPolicy.BURN_TO_DEPLETION,
    )
    assert plan.end_cause is BurnEndCause.COMPLETED
    assert plan.burn_duration_s == 77.3


def test_exactly_sufficient_propellant_is_accepted():
    duration = 12.0 / REF_ENGINE.mass_flow_kgps
    plan = plan_burn(REF_ENGINE, propellant_kg=12.0, ignition_t_s=0.0, duration_s=duration)
    assert plan.propellant_used_kg <= 12.0
    assert plan.propellant_used_kg == pytest.approx(12.0, rel=1e-15, abs=0)


def test_propellant_just_short_of_requirement_is_rejected():
    # Boundary: a burn needing 1 part in 1e9 more than is loaded must not be accepted.
    required = REF_ENGINE.mass_flow_kgps * REF_DURATION_S
    with pytest.raises(BurnRejectedError) as err:
        plan_burn(
            REF_ENGINE,
            propellant_kg=required * (1.0 - 1e-9),
            ignition_t_s=0.0,
            duration_s=REF_DURATION_S,
        )
    assert err.value.reason is BurnRejection.INSUFFICIENT_PROPELLANT


@pytest.mark.parametrize("policy", list(InsufficientPropellantPolicy))
def test_empty_tank_rejects_every_burn(policy):
    with pytest.raises(BurnRejectedError) as err:
        plan_burn(REF_ENGINE, propellant_kg=0.0, ignition_t_s=0.0, duration_s=1.0, policy=policy)
    assert err.value.reason is BurnRejection.NO_PROPELLANT


@pytest.mark.parametrize("duration", [0.0, -1.0])
def test_non_positive_duration_is_rejected(duration):
    with pytest.raises(BurnRejectedError) as err:
        plan_burn(REF_ENGINE, propellant_kg=1.0, ignition_t_s=0.0, duration_s=duration)
    assert err.value.reason is BurnRejection.NON_POSITIVE_DURATION


def test_ignition_before_earliest_allowed_time_is_rejected():
    with pytest.raises(BurnRejectedError) as err:
        plan_burn(
            REF_ENGINE, propellant_kg=1.0, ignition_t_s=99.0, duration_s=1.0, earliest_t_s=100.0
        )
    assert err.value.reason is BurnRejection.IGNITION_IN_PAST
    # Default earliest time is the simulation start, t = 0.
    with pytest.raises(BurnRejectedError):
        plan_burn(REF_ENGINE, propellant_kg=1.0, ignition_t_s=-1.0, duration_s=1.0)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("ignition_t_s", math.nan),
        ("ignition_t_s", math.inf),
        ("duration_s", math.nan),
        ("duration_s", math.inf),
        ("propellant_kg", math.nan),
        ("propellant_kg", -1.0),
    ],
)
def test_non_finite_or_invalid_burn_inputs_are_rejected(field, value):
    kwargs = {"propellant_kg": 1.0, "ignition_t_s": 0.0, "duration_s": 1.0, field: value}
    with pytest.raises(BurnRejectedError) as err:
        plan_burn(REF_ENGINE, **kwargs)
    assert err.value.reason is BurnRejection.SCHEMA_INVALID


def test_unknown_policy_is_rejected():
    with pytest.raises(BurnRejectedError) as err:
        plan_burn(
            REF_ENGINE, propellant_kg=1.0, ignition_t_s=0.0, duration_s=1.0, policy="sometimes"
        )
    assert err.value.reason is BurnRejection.SCHEMA_INVALID


# DR-0014 section 4 plus the 2026-10-10 amendment (burn_unschedulable). T3 must use
# exactly these stable codes; anything else is an unapproved vocabulary change.
APPROVED_REJECTION_CODES = frozenset(
    {
        "schema_invalid",
        "non_positive_duration",
        "ignition_in_past",
        "overlaps_scheduled_burn",
        "engine_busy",
        "no_propellant",
        "insufficient_propellant",
        "duplicate_command_id",
        "no_propulsion_configured",
        "burn_unschedulable",
    }
)


def test_rejection_codes_are_the_approved_dr0014_vocabulary():
    codes = {r.value for r in BurnRejection}
    assert codes <= APPROVED_REJECTION_CODES
    assert "invalid_input" not in codes
    assert {"schema_invalid", "burn_unschedulable"} <= codes


def test_propellant_used_at_time_is_piecewise_linear_and_bounded():
    plan = plan_burn(
        REF_ENGINE,
        propellant_kg=10.0,
        ignition_t_s=600.0,
        duration_s=77.3,
        policy=InsufficientPropellantPolicy.BURN_TO_DEPLETION,
    )
    mdot = REF_ENGINE.mass_flow_kgps
    assert plan.propellant_used_by(0.0) == 0.0
    assert plan.propellant_used_by(600.0) == 0.0
    assert plan.propellant_used_by(610.0) == pytest.approx(mdot * 10.0, rel=1e-13, abs=0)
    assert plan.propellant_used_by(plan.cutoff_t_s) == 10.0
    assert plan.propellant_used_by(1e9) == 10.0
    samples = np.linspace(0.0, 800.0, 4001)
    used = [plan.propellant_used_by(float(t)) for t in samples]
    assert all(0.0 <= u <= 10.0 for u in used)
    assert all(b >= a for a, b in pairwise(used))


def test_burn_plan_is_immutable():
    plan = plan_burn(REF_ENGINE, propellant_kg=1.0, ignition_t_s=0.0, duration_s=1.0)
    with pytest.raises(AttributeError):
        plan.duration_s = 2.0  # type: ignore[attr-defined]
    with pytest.raises(AttributeError):
        plan.cutoff_t_s = 2.0  # type: ignore[misc]


# ------------------------------------------------- analytic and independent references


def test_rocket_equation_known_values():
    c = REF_ENGINE.exhaust_velocity_mps
    assert rocket_equation_delta_v(c, 1300.0, 1300.0) == 0.0
    assert rocket_equation_delta_v(c, math.e, 1.0) == pytest.approx(c, rel=1e-15, abs=0)
    # Reference burn (VAL-0008): 12.379 kg from 1300 kg -> 29.2758 m/s.
    used = REF_ENGINE.mass_flow_kgps * REF_DURATION_S
    assert rocket_equation_delta_v(c, 1300.0, 1300.0 - used) == pytest.approx(
        29.275767297714708, rel=1e-13, abs=0
    )


@pytest.mark.parametrize(("m0", "mf"), [(0.0, 1.0), (1.0, 0.0), (1.0, 2.0), (math.nan, 1.0)])
def test_rocket_equation_rejects_unphysical_masses(m0, mf):
    with pytest.raises(ValueError):
        rocket_equation_delta_v(300.0 * STANDARD_GRAVITY, m0, mf)


def test_integrated_thrust_acceleration_equals_rocket_equation_independent_quadrature():
    """O2 with an independent integrator: integral of F/m(t) dt by adaptive quadrature."""
    sc = _ref_spacecraft()
    plan = plan_burn(
        sc.engine, propellant_kg=sc.tank.propellant_kg, ignition_t_s=0.0, duration_s=77.3
    )
    m0 = sc.initial_mass_kg

    def accel(t):
        return float(
            np.linalg.norm(
                thrust_acceleration(sc.engine, [1.0, 0, 0], m0 - plan.propellant_used_by(t))
            )
        )

    # QUADPACK requires epsrel >= 50 eps when epsabs = 0; request 1e-13, assert 1e-12.
    sensed, _ = quad(accel, 0.0, plan.cutoff_t_s, epsabs=0.0, epsrel=1e-13)
    expected = rocket_equation_delta_v(
        sc.engine.exhaust_velocity_mps, m0, m0 - plan.propellant_used_kg
    )
    assert sensed == pytest.approx(expected, rel=1e-12, abs=0)


def _powered_free_space_rhs(sc, law):
    """y = [x, v, m_prop], no gravity: x' = v, v' = F/m u, m_prop' = -mdot."""

    def f(t, y):
        x, v, m_prop = y[:3], y[3:6], y[6]
        a = thrust_acceleration(sc.engine, law.direction(t, x, v), sc.dry_mass_kg + m_prop)
        return np.concatenate([v, a, [-sc.engine.mass_flow_kgps]])

    return f


def _rk4_to(f, y0, t_end, dt):
    """Project RK4 with the last step shortened to land exactly on t_end (cutoff)."""
    rk4, y, t = RK4(), y0.copy(), 0.0
    while t < t_end:
        h = min(dt, t_end - t)
        y = rk4.step(f, t, y, h)
        t += h
    return y


def _closed_form_free_space(sc, t):
    """O3 exact solution along u, in 40-digit decimal arithmetic: (dv, displacement).

    v = v0 + c ln(m0/m) u;  x = x0 + v0 t + c [t - (m/mdot) ln(m0/m)] u.
    High precision avoids the cancellation in t - (m/mdot) ln(m0/m), which costs
    about 1.5e-9 m in float64 for the reference burn.
    """
    with localcontext() as ctx:
        ctx.prec = 40
        c, mdot = Decimal(sc.engine.exhaust_velocity_mps), Decimal(sc.engine.mass_flow_kgps)
        m0, t = Decimal(sc.initial_mass_kg), Decimal(t)
        m = m0 - mdot * t
        ln = (m0 / m).ln()
        return c * ln, c * (t - (m / mdot) * ln)


def _free_space_run(sc, u, x0, v0, dt):
    """Project RK4 + model; errors of the thrust-induced parts vs the exact solution."""
    y = _rk4_to(
        _powered_free_space_rhs(sc, _InertialHold(u)),
        np.concatenate([x0, v0, [sc.tank.propellant_kg]]),
        REF_DURATION_S,
        dt,
    )
    dv, disp = _closed_form_free_space(sc, REF_DURATION_S)
    t = Decimal(REF_DURATION_S)
    with localcontext() as ctx:
        ctx.prec = 40
        v_err = [Decimal(y[3 + k]) - Decimal(v0[k]) - dv * Decimal(u[k]) for k in range(3)]
        x_err = [
            Decimal(y[k]) - Decimal(x0[k]) - Decimal(v0[k]) * t - disp * Decimal(u[k])
            for k in range(3)
        ]
    return math.hypot(*map(float, v_err)), math.hypot(*map(float, x_err)), float(dv), y


def test_free_space_powered_motion_matches_closed_form():
    """O3: project RK4 + propulsion model vs the exact free-space solution.

    Velocity: v' = F/m(t) depends on time only, so RK4 reduces to Simpson's rule. Its
    error (h^5 a''''/2880, a'''' = 24 a (mdot/m)^4) is far below round-off, so the
    bound 1e-12 relative to dv is a round-off bound (measured 1.2e-14).
    Position: the local error depends on a''', a genuine 4th-order truncation error
    (measured 4.3e-9 m at dt = 10 s on 1130 m). No new tolerance is introduced; it
    is checked by convergence order, |p - 4| <= 0.5 (M1 policy, DR-0008).
    """
    sc = _ref_spacecraft()
    u = np.array([0.36, -0.48, 0.8])
    x0, v0 = np.array([1.0e6, -2.0e5, 3.0e4]), np.array([100.0, -50.0, 20.0])
    v_err, _, dv, y = _free_space_run(sc, u, x0, v0, 10.0)
    assert v_err <= 1e-12 * dv
    zero = np.zeros(3)
    x_errs = [_free_space_run(sc, u, zero, zero, dt)[1] for dt in (10.0, 5.0)]
    assert abs(math.log2(x_errs[0] / x_errs[1]) - 4.0) <= 0.5
    # Mass conservation: RK4 integrates the linear mass law exactly (round-off only).
    used = sc.engine.mass_flow_kgps * REF_DURATION_S
    assert y[6] == pytest.approx(sc.tank.propellant_kg - used, rel=1e-15, abs=0)
    assert sc.dry_mass_kg + y[6] == pytest.approx(sc.initial_mass_kg - used, rel=1e-15, abs=0)


def _powered_orbit_rhs(sc, law):
    def f(t, y):
        r, v, m_prop = y[:3], y[3:6], y[6]
        a = -WGS84.mu * r / np.linalg.norm(r) ** 3
        a = a + thrust_acceleration(sc.engine, law.direction(t, r, v), sc.dry_mass_kg + m_prop)
        return np.concatenate([v, a, [-sc.engine.mass_flow_kgps]])

    return f


def _independent_tracking_rhs(sc, sign):
    """Reference RHS written without any production propulsion code (REV-T1-05).

    Pointing is the instantaneous inertial velocity direction (sign +1 prograde,
    -1 retrograde); mass flow is F/(Isp g0) from the spec's raw inputs.
    """
    thrust, mdot = sc.engine.thrust_n, sc.engine.thrust_n / (sc.engine.isp_s * STANDARD_GRAVITY)

    def f(t, y):
        r, v, m_prop = y[:3], y[3:6], y[6]
        speed = math.sqrt(float(v @ v))
        a = -WGS84.mu * r / math.sqrt(float(r @ r)) ** 3
        a = a + (sign * thrust / (sc.dry_mass_kg + m_prop) / speed) * v
        return np.concatenate([v, a, [-mdot]])

    return f


@pytest.mark.parametrize(("law", "sign"), [(Prograde(), 1.0), (Retrograde(), -1.0)])
def test_powered_arc_converges_at_fourth_order_to_independent_reference(law, sign):
    """Production model + RK4 vs SciPy DOP853 on an independently written RHS.

    If the production law deviated from velocity tracking (e.g. held its first
    direction), RK4 would converge to a different trajectory and the error would stop
    shrinking. Convergence order |p - 4| <= 0.5 is the M1 policy (DR-0008); no new
    tolerance is introduced.
    """
    sc = _ref_spacecraft()
    r0, v0 = _orbit_state()
    y0 = np.concatenate([r0, v0, [sc.tank.propellant_kg]])
    ref = solve_ivp(
        _independent_tracking_rhs(sc, sign),
        (0.0, REF_DURATION_S),
        y0,
        method="DOP853",
        rtol=1e-13,
        atol=1e-9,
    )
    y_ref = ref.y[:, -1]
    f = _powered_orbit_rhs(sc, law)
    errs = [
        np.linalg.norm(_rk4_to(f, y0, REF_DURATION_S, dt)[:3] - y_ref[:3])
        for dt in (20.0, 10.0, 5.0)
    ]
    for coarse, fine in pairwise(errs):
        assert abs(math.log2(coarse / fine) - 4.0) <= 0.5


@pytest.mark.parametrize("law", [Prograde(), Retrograde()])
def test_direction_law_tracks_each_new_velocity(law):
    """One law instance must follow the velocity it is given at every call (REV-T1-05)."""
    sign = 1.0 if law.name == "prograde" else -1.0
    r = np.array([7.0e6, 0.0, 0.0])
    velocities = [
        np.array([0.0, 7.5e3, 0.0]),
        np.array([0.0, 4.0e3, 6.0e3]),
        np.array([-1.0e3, 0.0, 7.0e3]),
        np.array([0.0, 7.5e3, 0.0]),
    ]
    for v in velocities:
        np.testing.assert_allclose(
            law.direction(0.0, r, v), sign * v / np.linalg.norm(v), rtol=0, atol=1e-15
        )


def test_prograde_raises_and_retrograde_lowers_orbital_energy():
    """O7 at model level: specific energy change has the sign of the direction law."""
    sc = _ref_spacecraft()
    r0, v0 = _orbit_state()
    y0 = np.concatenate([r0, v0, [sc.tank.propellant_kg]])
    e0 = specific_energy(r0, v0, WGS84.mu)
    for law, sign in ((Prograde(), 1.0), (Retrograde(), -1.0)):
        y = _rk4_to(_powered_orbit_rhs(sc, law), y0, REF_DURATION_S, 10.0)
        assert sign * (specific_energy(y[:3], y[3:6], WGS84.mu) - e0) > 0.0


# ----------------------------------------------- review M2-T1-review-01 regressions


@pytest.mark.parametrize("propellant", [0.1, 0.3, 1.0, 7.77, 12.0, 299.9])
@pytest.mark.parametrize("policy", list(InsufficientPropellantPolicy))
def test_burn_lasting_exactly_the_depletion_time_completes(propellant, policy):
    """REV-T1-03: sufficiency is decided in time; consumption is clamped at the boundary."""
    duration = propellant / REF_ENGINE.mass_flow_kgps
    plan = plan_burn(REF_ENGINE, propellant, 0.0, duration, policy=policy)
    assert plan.end_cause is BurnEndCause.COMPLETED
    assert plan.burn_duration_s == duration
    assert plan.propellant_used_kg <= propellant
    assert plan.propellant_used_kg == pytest.approx(propellant, rel=2.3e-16, abs=0)


@pytest.mark.parametrize("propellant", [0.1, 0.3, 1.0, 7.77, 12.0, 299.9])
def test_one_ulp_past_the_depletion_time_is_insufficient(propellant):
    t_dep = propellant / REF_ENGINE.mass_flow_kgps
    longer = math.nextafter(t_dep, math.inf)
    with pytest.raises(BurnRejectedError) as err:
        plan_burn(REF_ENGINE, propellant, 0.0, longer)
    assert err.value.reason is BurnRejection.INSUFFICIENT_PROPELLANT
    plan = plan_burn(
        REF_ENGINE, propellant, 0.0, longer, policy=InsufficientPropellantPolicy.BURN_TO_DEPLETION
    )
    assert plan.end_cause is BurnEndCause.PROPELLANT_DEPLETED
    assert plan.burn_duration_s == t_dep
    assert plan.propellant_used_kg == propellant
    shorter = plan_burn(REF_ENGINE, propellant, 0.0, math.nextafter(t_dep, 0.0))
    assert shorter.end_cause is BurnEndCause.COMPLETED
    assert shorter.propellant_used_kg <= propellant


def test_numpy_scalar_inputs_are_normalized_to_float64():
    """REV-T1-01: NumPy scalars give exactly the plan of the equivalent Python floats."""
    args = (np.float32(300.0), np.float32(600.0), np.float32(77.3))
    plan = plan_burn(REF_ENGINE, *args)
    expected = plan_burn(REF_ENGINE, *(float(x) for x in args))
    assert plan == expected
    for value in (
        plan.ignition_t_s,
        plan.commanded_duration_s,
        plan.burn_duration_s,
        plan.cutoff_t_s,
        plan.propellant_used_kg,
        plan.mass_flow_kgps,
    ):
        assert type(value) is float
    tiny = plan_burn(REF_ENGINE, np.float32(300), np.float32(600), np.float32(1e-5))
    assert tiny.cutoff_t_s > tiny.ignition_t_s
    assert tiny.propellant_used_by(tiny.cutoff_t_s) > 0.0
    spec = EngineSpec(thrust_n=np.float32(490.0), isp_s=np.int64(312))
    assert type(spec.thrust_n) is float and type(spec.isp_s) is float


@pytest.mark.parametrize(
    ("engine", "ignition", "duration"),
    [
        (REF_ENGINE, 1e16, 1.0),  # cutoff rounds back onto ignition
        (EngineSpec(thrust_n=1e-308, isp_s=312.0), 1e308, 1e308),  # t_dep and cutoff overflow
    ],
)
def test_unrepresentable_cutoff_is_rejected(engine, ignition, duration):
    """REV-T1-01: a plan must have a finite cutoff strictly after ignition (DR-0013)."""
    with pytest.raises(BurnRejectedError) as err:
        plan_burn(engine, 300.0, ignition, duration)
    assert err.value.reason is BurnRejection.BURN_UNSCHEDULABLE


def test_depletion_time_that_underflows_the_clock_is_rejected():
    with pytest.raises(BurnRejectedError) as err:
        plan_burn(
            REF_ENGINE,
            5e-324,
            600.0,
            10.0,
            policy=InsufficientPropellantPolicy.BURN_TO_DEPLETION,
        )
    assert err.value.reason is BurnRejection.BURN_UNSCHEDULABLE


@pytest.mark.parametrize(
    ("thrust", "isp"),
    [(490.0, 1e308), (1e308, 1e-308), (5e-324, 312.0)],  # c overflows; mdot inf; mdot underflows
)
def test_engine_rejects_specs_with_invalid_derived_quantities(thrust, isp):
    """REV-T1-02: exhaust velocity and mass flow must be finite and positive."""
    with pytest.raises(PropulsionSpecError):
        EngineSpec(thrust_n=thrust, isp_s=isp)


def test_spacecraft_rejects_overflowing_total_mass():
    with pytest.raises(PropulsionSpecError):
        SpacecraftSpec(dry_mass_kg=1e308, engine=REF_ENGINE, tank=TankSpec(propellant_kg=1e308))


def _ln_ratio_reference(m0, mf):
    with localcontext() as ctx:
        ctx.prec = 50
        return float((Decimal(m0) / Decimal(mf)).ln())


@pytest.mark.parametrize(
    ("m0", "mf"),
    [
        (1.0, math.nextafter(1.0, 0.0)),
        (1300.0, math.nextafter(1300.0, 0.0)),
        (1300.0, 1287.620579808024),
        (1300.0, 1000.0),
        (1e300, 1e-300),
        (1e308, 1e-308),
    ],
)
def test_rocket_equation_is_accurate_from_tiny_to_extreme_mass_ratios(m0, mf):
    """REV-T1-04: within a few ulp of a 50-digit reference, never overflowing."""
    c = 3000.0
    expected = c * _ln_ratio_reference(m0, mf)
    assert rocket_equation_delta_v(c, m0, mf) == pytest.approx(expected, rel=4.5e-16, abs=0)


@pytest.mark.parametrize("mass", [True, "1300", None])
def test_thrust_acceleration_rejects_non_numeric_mass(mass):
    """REV-T1-06: same scalar validation as the specs; ValueError, never TypeError."""
    with pytest.raises(ValueError):
        thrust_acceleration(REF_ENGINE, np.array([1.0, 0.0, 0.0]), total_mass_kg=mass)


def test_thrust_acceleration_rejects_an_overflowing_result():
    with pytest.raises(ValueError):
        thrust_acceleration(EngineSpec(1e308, 312.0), np.array([1.0, 0.0, 0.0]), 1e-10)


@pytest.mark.parametrize("v", [[1.0, 0.0], [1.0, 0.0, 0.0, 0.0], [[1.0, 0.0, 0.0]]])
def test_velocity_tracking_requires_a_three_vector(v):
    with pytest.raises(ValueError):
        Prograde().direction(0.0, np.array([7e6, 0.0, 0.0]), np.array(v))


@pytest.mark.parametrize("scale", [1e200, 1e-200, 1e-310])
def test_velocity_tracking_is_scale_invariant(scale):
    v = scale * np.array([0.0, 0.6, 0.8])
    for law, sign in ((Prograde(), 1.0), (Retrograde(), -1.0)):
        np.testing.assert_allclose(
            law.direction(0.0, np.zeros(3), v), sign * np.array([0.0, 0.6, 0.8]), atol=1e-15
        )


def test_positive_burn_with_underflowing_consumption_is_rejected():
    """Reviewer re-verification N1: a planned burn must consume a positive mass."""
    with pytest.raises(BurnRejectedError) as err:
        plan_burn(EngineSpec(thrust_n=1e-308, isp_s=312.0), 300.0, 0.0, 1e-100)
    assert err.value.reason is BurnRejection.BURN_UNSCHEDULABLE
