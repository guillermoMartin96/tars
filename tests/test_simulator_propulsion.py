"""M2 task T2: propulsion inside the simulator (DR-0013, DR-0014, ADR-0007).

Covers the augmented state y = [r, v, m_prop, dv_sensed], the engine state machine,
exact RK4 step splitting at engine events, PropulsionSnapshot, scheduling
rejections, and M1 preservation.
"""

import math
from decimal import Decimal, localcontext
from itertools import pairwise

import numpy as np
import pytest
from scipy.integrate import solve_ivp

from tars.astro.elements import circular_orbit_state, rv_to_elements
from tars.sim.constants import STANDARD_GRAVITY, WGS84
from tars.sim.forces import PointMassGravity
from tars.sim.integrators import RK4
from tars.sim.propulsion import (
    EVENT_TIME_RESOLUTION_S,
    BurnEndCause,
    BurnRejectedError,
    BurnRejection,
    EngineSpec,
    EngineState,
    InsufficientPropellantPolicy,
    SpacecraftSpec,
    TankSpec,
    plan_burn,
    rocket_equation_delta_v,
)
from tars.sim.simulator import AscendingNodeDetector, Simulator

# DR-0010 reference case: configurable inputs, not model constants.
ENGINE = EngineSpec(thrust_n=490.0, isp_s=312.0)
DRY, PROP = 1000.0, 300.0
R0, V0 = circular_orbit_state(
    radius=WGS84.equatorial_radius + 250_000.0,
    inclination=math.radians(51.6),
    raan=0.0,
    arg_latitude=0.0,
    mu=WGS84.mu,
)


def _spacecraft(propellant=PROP):
    return SpacecraftSpec(dry_mass_kg=DRY, engine=ENGINE, tank=TankSpec(propellant_kg=propellant))


def _sim(dt=10.0, spacecraft="default", detectors=()):
    sc = _spacecraft() if spacecraft == "default" else spacecraft
    return Simulator(R0, V0, PointMassGravity(WGS84.mu), RK4(), dt, detectors, spacecraft=sc)


def _run_until(sim, t_end):
    while sim.t < t_end:
        sim.step()


def _state(sim):
    s = sim.snapshot()
    return np.concatenate([s.r, s.v])


# --------------------------------------------------------------------- M1 preservation


def test_without_spacecraft_the_m1_path_is_unchanged():
    """No spacecraft: identical to the M1 simulator, bit for bit (DR-0013 4A)."""
    m1 = Simulator(R0, V0, PointMassGravity(WGS84.mu), RK4(), 10.0)
    explicit_none = Simulator(R0, V0, PointMassGravity(WGS84.mu), RK4(), 10.0, spacecraft=None)
    for _ in range(600):
        m1.step()
        explicit_none.step()
    np.testing.assert_array_equal(_state(m1), _state(explicit_none))
    assert m1.propulsion_snapshot() is None


def test_spacecraft_without_burns_coasts_bit_identically_to_m1():
    """The augmented state must not perturb a coast: r, v identical to the 6-state path."""
    m1 = Simulator(R0, V0, PointMassGravity(WGS84.mu), RK4(), 10.0)
    sim = _sim()
    for _ in range(600):
        m1.step()
        sim.step()
    np.testing.assert_array_equal(_state(m1), _state(sim))
    p = sim.propulsion_snapshot()
    assert p.propellant_kg == PROP
    assert p.delta_v_sensed_mps == 0.0
    assert p.engine_state is EngineState.IDLE


@pytest.mark.parametrize("dt", [0.1, 7.0 / 3.0])
def test_coast_ticks_use_exactly_dt_for_any_step_size(dt):
    """Ticks without engine events must integrate h = dt exactly, like M1, not
    (k+1)*dt - k*dt, which differs from dt in the last bits for most dt."""
    m1 = Simulator(R0, V0, PointMassGravity(WGS84.mu), RK4(), dt)
    sim = _sim(dt=dt)
    for _ in range(300):
        m1.step()
        sim.step()
    np.testing.assert_array_equal(_state(m1), _state(sim))


# ------------------------------------------------------------------ state ownership


def test_public_api_cannot_set_physical_state():
    """Invariant 1: the only command entry point schedules engine activity."""
    sim = _sim()
    public = {name for name in dir(sim) if not name.startswith("_")}
    assert public == {
        "dt",
        "tick",
        "t",
        "snapshot",
        "step",
        "schedule_burn",
        "propulsion_snapshot",
        "engine_transitions",
    }
    for prop in ("dt", "tick", "t", "engine_transitions"):
        with pytest.raises(AttributeError):
            setattr(sim, prop, 0)


def test_scheduling_does_not_change_physical_state():
    sim = _sim()
    _run_until(sim, 100.0)
    before = (_state(sim), sim.propulsion_snapshot().propellant_kg)
    sim.schedule_burn("prograde", ignition_t_s=600.0, duration_s=77.3)
    with pytest.raises(BurnRejectedError):
        sim.schedule_burn("prograde", ignition_t_s=620.0, duration_s=5.0)
    np.testing.assert_array_equal(_state(sim), before[0])
    assert sim.propulsion_snapshot().propellant_kg == before[1]


def test_propulsion_snapshot_is_immutable():
    snap = _sim().propulsion_snapshot()
    with pytest.raises(AttributeError):
        snap.propellant_kg = 0.0  # type: ignore[misc]


def test_simulator_state_is_read_only_to_direction_laws_and_forces():
    """REV-004 pattern extended to the augmented state."""

    class _Mutating:
        name = "mutating"

        def acceleration(self, t, r, v):
            v += 1.0  # must raise: r, v are read-only views
            return np.zeros(3)

    sim = Simulator(R0, V0, _Mutating(), RK4(), 10.0, spacecraft=_spacecraft())
    with pytest.raises(ValueError):
        sim.step()


# ------------------------------------------------------------------- scheduling rules


def test_schedule_returns_the_exact_plan():
    sim = _sim()
    plan = sim.schedule_burn("prograde", ignition_t_s=605.5, duration_s=77.3)
    assert plan.ignition_t_s == 605.5
    assert plan.cutoff_t_s == 605.5 + 77.3
    assert plan.burn_duration_s == plan.cutoff_t_s - plan.ignition_t_s
    assert abs(plan.burn_duration_s - 77.3) <= EVENT_TIME_RESOLUTION_S
    assert plan.propellant_used_kg == ENGINE.mass_flow_kgps * plan.burn_duration_s
    p = sim.propulsion_snapshot()
    assert p.engine_state is EngineState.SCHEDULED
    assert p.pending_plans == (plan,)


@pytest.mark.parametrize(
    ("kwargs", "reason"),
    [
        ({"direction": "sideways"}, BurnRejection.SCHEMA_INVALID),
        ({"ignition_t_s": math.nan}, BurnRejection.SCHEMA_INVALID),
        ({"duration_s": 0.0}, BurnRejection.NON_POSITIVE_DURATION),
        ({"ignition_t_s": 50.0}, BurnRejection.IGNITION_IN_PAST),
        ({"duration_s": 3000.0}, BurnRejection.INSUFFICIENT_PROPELLANT),
    ],
)
def test_invalid_schedules_are_rejected_with_approved_codes(kwargs, reason):
    sim = _sim()
    _run_until(sim, 100.0)
    args = {"direction": "prograde", "ignition_t_s": 600.0, "duration_s": 10.0, **kwargs}
    with pytest.raises(BurnRejectedError) as err:
        sim.schedule_burn(**args)
    assert err.value.reason is reason
    assert sim.propulsion_snapshot().pending_plans == ()


def test_scheduling_without_propulsion_is_rejected():
    sim = Simulator(R0, V0, PointMassGravity(WGS84.mu), RK4(), 10.0)
    with pytest.raises(BurnRejectedError) as err:
        sim.schedule_burn("prograde", ignition_t_s=600.0, duration_s=10.0)
    assert err.value.reason is BurnRejection.NO_PROPULSION_CONFIGURED


def test_burns_execute_in_submission_order_without_overlap():
    """One engine. A new burn may not ignite before any scheduled burn's cutoff."""
    sim = _sim()
    sim.schedule_burn("prograde", ignition_t_s=600.0, duration_s=50.0)
    for ignition in (600.0, 620.0, 649.999, 100.0):
        with pytest.raises(BurnRejectedError) as err:
            sim.schedule_burn("prograde", ignition_t_s=ignition, duration_s=5.0)
        assert err.value.reason is BurnRejection.OVERLAPS_SCHEDULED_BURN
    sim.schedule_burn("retrograde", ignition_t_s=650.0, duration_s=5.0)  # back to back


def test_scheduling_into_the_active_burn_is_engine_busy():
    sim = _sim()
    sim.schedule_burn("prograde", ignition_t_s=600.0, duration_s=50.0)
    _run_until(sim, 620.0)
    assert sim.propulsion_snapshot().engine_state is EngineState.BURNING
    with pytest.raises(BurnRejectedError) as err:
        sim.schedule_burn("prograde", ignition_t_s=630.0, duration_s=5.0)
    assert err.value.reason is BurnRejection.ENGINE_BUSY


def test_later_burns_are_planned_against_propellant_left_by_earlier_ones():
    sim = _sim(spacecraft=_spacecraft(propellant=10.0))
    first = sim.schedule_burn("prograde", ignition_t_s=600.0, duration_s=40.0)
    remaining = 10.0 - first.propellant_used_kg
    with pytest.raises(BurnRejectedError) as err:
        sim.schedule_burn("prograde", ignition_t_s=700.0, duration_s=40.0)
    assert err.value.reason is BurnRejection.INSUFFICIENT_PROPELLANT
    second = sim.schedule_burn(
        "prograde",
        ignition_t_s=700.0,
        duration_s=40.0,
        policy=InsufficientPropellantPolicy.BURN_TO_DEPLETION,
    )
    assert second.end_cause is BurnEndCause.PROPELLANT_DEPLETED
    # Consumes what is left, up to the conservative-cutoff residual (review N5).
    bound = ENGINE.mass_flow_kgps * 2 * math.ulp(second.cutoff_t_s) + 2 * math.ulp(remaining)
    assert 0.0 <= remaining - second.propellant_used_kg <= bound


# ------------------------------------------------------ engine events and step splitting


def test_engine_transitions_are_recorded_at_exact_times_inside_ticks():
    sim = _sim()
    plan = sim.schedule_burn("prograde", ignition_t_s=605.5, duration_s=77.3)
    seen = []
    while sim.t < 700.0:
        sim.step()
        seen.extend(sim.engine_transitions)
    assert [(e.kind, e.t) for e in seen] == [
        ("ignition", 605.5),
        ("cutoff", plan.cutoff_t_s),
    ]
    assert seen[0].plan == plan and seen[1].plan == plan
    assert seen[0].propellant_kg == PROP
    assert sim.propulsion_snapshot().engine_state is EngineState.IDLE


def test_two_events_inside_one_tick():
    sim = _sim()
    sim.schedule_burn("prograde", ignition_t_s=601.0, duration_s=3.0)
    _run_until(sim, 600.0)
    sim.step()  # tick 600 -> 610 contains ignition and cutoff
    assert [(e.kind, e.t) for e in sim.engine_transitions] == [
        ("ignition", 601.0),
        ("cutoff", 604.0),
    ]
    used = PROP - sim.propulsion_snapshot().propellant_kg
    assert used == pytest.approx(ENGINE.mass_flow_kgps * 3.0, rel=1e-12, abs=0)


def test_events_on_tick_boundaries_and_back_to_back_burns():
    sim = _sim()
    sim.schedule_burn("prograde", ignition_t_s=600.0, duration_s=20.0)
    sim.schedule_burn("retrograde", ignition_t_s=620.0, duration_s=10.0)
    events = []
    while sim.t < 640.0:
        sim.step()
        events.extend((e.kind, e.t, e.plan.ignition_t_s) for e in sim.engine_transitions)
    assert events == [
        ("ignition", 600.0, 600.0),
        ("cutoff", 620.0, 600.0),
        ("ignition", 620.0, 620.0),
        ("cutoff", 630.0, 620.0),
    ]


def test_depletion_empties_the_tank_to_within_time_resolution_and_never_negative():
    sim = _sim(spacecraft=_spacecraft(propellant=5.0))
    plan = sim.schedule_burn(
        "prograde",
        ignition_t_s=603.7,
        duration_s=60.0,
        policy=InsufficientPropellantPolicy.BURN_TO_DEPLETION,
    )
    assert plan.end_cause is BurnEndCause.PROPELLANT_DEPLETED
    while sim.t < 700.0:
        sim.step()
        assert sim.propulsion_snapshot().propellant_kg >= 0.0
    p = sim.propulsion_snapshot()
    # The engine stops at the latest representable time not after depletion, so the
    # tank holds the plan's residual (<= mdot * 2 ulp(cutoff)), never a negative mass.
    bound = ENGINE.mass_flow_kgps * 2 * math.ulp(plan.cutoff_t_s) + 2 * math.ulp(5.0)
    assert 0.0 <= p.propellant_kg <= bound
    # Same O1 round-off bound as the other mass-law checks (1e-12 of initial mass).
    assert abs(p.propellant_kg - (5.0 - plan.propellant_used_kg)) <= 1e-12 * (DRY + 5.0)
    assert p.engine_state is EngineState.IDLE


def test_burn_scheduled_for_the_current_time_ignites_at_the_next_step():
    sim = _sim()
    _run_until(sim, 600.0)
    sim.schedule_burn("prograde", ignition_t_s=sim.t, duration_s=10.0)
    sim.step()
    assert [(e.kind, e.t) for e in sim.engine_transitions] == [
        ("ignition", 600.0),
        ("cutoff", 610.0),
    ]


# ------------------------------------------------------------------- physics oracles


def _burn_run(dt, ignition=605.5, duration=77.3, direction="prograde", t_end=700.0):
    sim = _sim(dt=dt)
    plan = sim.schedule_burn(direction, ignition_t_s=ignition, duration_s=duration)
    dv_at_ignition = None
    while sim.t < t_end:
        sim.step()
        for e in sim.engine_transitions:
            if e.kind == "ignition":
                dv_at_ignition = e.delta_v_sensed_mps
    return sim, plan, dv_at_ignition


def test_propellant_used_matches_the_mass_law():
    """O1: integrated propellant equals mdot * T to round-off (RK4 is exact for a
    linear law). Bound 1e-12 of the initial mass: measured 3.8e-15 (VAL-0008)."""
    sim, plan, _ = _burn_run(10.0)
    used = PROP - sim.propulsion_snapshot().propellant_kg
    assert abs(used - plan.propellant_used_kg) <= 1e-12 * (DRY + PROP)


def test_sensed_delta_v_matches_the_rocket_equation():
    """O2: integral of F/m over the burn equals c ln(m0/mf). Round-off bound 1e-12
    relative (measured 1.2e-14, VAL-0008)."""
    sim, plan, dv0 = _burn_run(10.0)
    sensed = sim.propulsion_snapshot().delta_v_sensed_mps - dv0
    m0 = DRY + PROP
    expected = rocket_equation_delta_v(
        ENGINE.exhaust_velocity_mps, m0, m0 - plan.propellant_used_kg
    )
    assert sensed == pytest.approx(expected, rel=1e-12, abs=0)


def _independent_reference(ignition, duration, sign, t_end):
    """DOP853 across the burn boundaries with a RHS sharing no production code."""
    mdot = ENGINE.thrust_n / (ENGINE.isp_s * STANDARD_GRAVITY)

    def rhs(on):
        def f(t, y):
            r, v, m = y[:3], y[3:6], y[6]
            a = -WGS84.mu * r / math.sqrt(float(r @ r)) ** 3
            if on:
                a = a + (sign * ENGINE.thrust_n / (DRY + m) / math.sqrt(float(v @ v))) * v
            return np.concatenate([v, a, [-mdot if on else 0.0]])

        return f

    y = np.concatenate([R0, V0, [PROP]])
    for a, b, on in ((0.0, ignition, False), (ignition, ignition + duration, True)):
        y = solve_ivp(rhs(on), (a, b), y, method="DOP853", rtol=1e-13, atol=1e-9).y[:, -1]
    return solve_ivp(
        rhs(False), (ignition + duration, t_end), y, method="DOP853", rtol=1e-13, atol=1e-9
    ).y[:, -1]


@pytest.mark.parametrize(("direction", "sign"), [("prograde", 1.0), ("retrograde", -1.0)])
def test_split_steps_keep_fourth_order_through_a_burn(direction, sign):
    """Ignition and cutoff both fall inside ticks for every dt used. Without exact
    step splitting the error would be ~1 m/s-level and not converge at order 4
    (VAL-0008: 168 km after 10 orbits). Order policy |p - 4| <= 0.5 (DR-0008)."""
    ignition, duration, t_end = 605.5, 77.3, 700.0
    ref = _independent_reference(ignition, duration, sign, t_end)
    errs = []
    for dt in (20.0, 10.0, 5.0):
        sim, _, _ = _burn_run(dt, ignition, duration, direction, t_end)
        errs.append(np.linalg.norm(sim.snapshot().r - ref[:3]))
    for coarse, fine in pairwise(errs):
        assert abs(math.log2(coarse / fine) - 4.0) <= 0.5


def test_prograde_raises_and_retrograde_lowers_the_orbit_in_plane():
    """O7: SMA sign follows direction; an in-plane burn leaves the orbit normal fixed.

    The plane is compared through the unit angular-momentum vector, which avoids
    RAAN wrapping at 0/2 pi; 1e-12 rad is a round-off bound.
    """
    a0 = rv_to_elements(R0, V0, WGS84.mu).a
    n0 = np.cross(R0, V0) / np.linalg.norm(np.cross(R0, V0))
    for direction, sign in (("prograde", 1.0), ("retrograde", -1.0)):
        sim, _, _ = _burn_run(10.0, direction=direction)
        s = sim.snapshot()
        assert sign * (rv_to_elements(s.r, s.v, WGS84.mu).a - a0) > 40_000.0  # ~50 km
        n1 = np.cross(s.r, s.v) / np.linalg.norm(np.cross(s.r, s.v))
        assert np.linalg.norm(np.cross(n0, n1)) <= 1e-12


def test_node_detection_still_works_with_propulsion():
    sim = _sim(detectors=[AscendingNodeDetector()])
    sim.schedule_burn("prograde", ignition_t_s=605.5, duration_s=77.3)
    crossings = []
    while sim.t < 6000.0:
        crossings.extend(sim.step())
    assert len(crossings) == 1


def test_propulsion_runs_are_deterministic():
    runs = []
    for _ in range(2):
        sim, _, _ = _burn_run(10.0, t_end=1200.0)
        p = sim.propulsion_snapshot()
        runs.append((_state(sim).tobytes(), p.propellant_kg, p.delta_v_sensed_mps))
    assert runs[0] == runs[1]


# ------------------------------------------------- review M2-T2-review-01 regressions


class _ZeroForce:
    name = "zero"

    def acceleration(self, t, r, v):
        return np.zeros(3)


class _FailAfter:
    """Gravity that returns NaN for t in (t_fail, ...) while armed (REV-T2-01)."""

    name = "fail_after"

    def __init__(self, t_fail):
        self.t_fail, self.armed, self.gravity = t_fail, True, PointMassGravity(WGS84.mu)

    def acceleration(self, t, r, v):
        if self.armed and t > self.t_fail:
            return np.full(3, np.nan)
        return self.gravity.acceleration(t, r, v)


def test_a_failed_step_leaves_engine_schedule_and_state_unchanged():
    """REV-T2-01: a tick is atomic; a retry after a failure burns the planned amount."""
    force = _FailAfter(t_fail=2.0)
    sim = Simulator(R0, V0, force, RK4(), 10.0, spacecraft=_spacecraft())
    plan = sim.schedule_burn("prograde", ignition_t_s=1.0, duration_s=2.0)
    before = (_state(sim), sim.propulsion_snapshot())
    with pytest.raises(FloatingPointError):
        sim.step()
    assert sim.tick == 0
    np.testing.assert_array_equal(_state(sim), before[0])
    assert sim.propulsion_snapshot() == before[1]
    assert sim.engine_transitions == ()
    force.armed = False
    sim.step()
    assert [(e.kind, e.t) for e in sim.engine_transitions] == [("ignition", 1.0), ("cutoff", 3.0)]
    used = PROP - sim.propulsion_snapshot().propellant_kg
    assert abs(used - plan.propellant_used_kg) <= 1e-12 * (DRY + PROP)


@pytest.mark.parametrize(
    "ignition",
    [-math.inf, math.inf, math.nan, "-1", True, np.bool_(True), np.array(-1.0), None, 10**1000],
)
def test_malformed_ignition_is_schema_invalid_whatever_the_time_or_schedule(ignition):
    """REV-T2-02: schema validation precedes chronology and engine-conflict checks."""
    sim = _sim()
    _run_until(sim, 10.0)
    sim.schedule_burn("prograde", ignition_t_s=600.0, duration_s=50.0)
    with pytest.raises(BurnRejectedError) as err:
        sim.schedule_burn("prograde", ignition_t_s=ignition, duration_s=5.0)
    assert err.value.reason is BurnRejection.SCHEMA_INVALID


@pytest.mark.parametrize("duration", ["5", True, None, math.inf, 10**1000])
def test_malformed_duration_is_schema_invalid(duration):
    sim = _sim()
    with pytest.raises(BurnRejectedError) as err:
        sim.schedule_burn("prograde", ignition_t_s=600.0, duration_s=duration)
    assert err.value.reason is BurnRejection.SCHEMA_INVALID


def test_burn_whose_represented_interval_differs_materially_is_unschedulable():
    """REV-T2-03: at t ~ 1e15 s, float64 event times are 0.125 s apart; a 0.1 s burn
    cannot be represented and must be rejected, not silently stretched."""
    with pytest.raises(BurnRejectedError) as err:
        plan_burn(ENGINE, PROP, 1e15, 0.1)
    assert err.value.reason is BurnRejection.BURN_UNSCHEDULABLE
    with pytest.raises(BurnRejectedError) as err:
        plan_burn(ENGINE, 0.032, 1e15, 1.0, policy=InsufficientPropellantPolicy.BURN_TO_DEPLETION)
    assert err.value.reason is BurnRejection.BURN_UNSCHEDULABLE


@pytest.mark.parametrize(
    ("ignition", "duration", "propellant", "policy"),
    [
        (600.0, 77.3, PROP, InsufficientPropellantPolicy.REJECT),
        (605.5, 77.3, PROP, InsufficientPropellantPolicy.REJECT),
        (603.7, 60.0, 5.0, InsufficientPropellantPolicy.BURN_TO_DEPLETION),
    ],
)
def test_plan_describes_exactly_the_interval_that_is_integrated(
    ignition, duration, propellant, policy
):
    """REV-T2-03: plan duration = cutoff - ignition; consumption follows it, so the
    integrated propellant matches the plan to round-off and the floor only absorbs
    round-off."""
    plan = plan_burn(ENGINE, propellant, ignition, duration, policy=policy)
    assert plan.burn_duration_s == plan.cutoff_t_s - plan.ignition_t_s
    if plan.end_cause is BurnEndCause.COMPLETED:
        assert plan.propellant_used_kg == ENGINE.mass_flow_kgps * plan.burn_duration_s
    sim = _sim(spacecraft=_spacecraft(propellant=propellant))
    sim.schedule_burn("prograde", ignition_t_s=ignition, duration_s=duration, policy=policy)
    cutoffs = []
    while sim.t < ignition + duration + 20.0:
        sim.step()
        cutoffs.extend(e for e in sim.engine_transitions if e.kind == "cutoff")
    assert [e.t for e in cutoffs] == [plan.cutoff_t_s]
    used = propellant - sim.propulsion_snapshot().propellant_kg
    assert abs(used - plan.propellant_used_kg) <= 1e-12 * (DRY + propellant)


def test_transition_arrays_cannot_be_made_writable():
    """REV-T2-04: retained event evidence is immutable."""
    sim = _sim()
    sim.schedule_burn("prograde", ignition_t_s=0.0, duration_s=5.0)
    sim.step()
    event = sim.engine_transitions[0]
    for arr in (event.r, event.v):
        with pytest.raises(ValueError):
            arr.flags.writeable = True
        with pytest.raises(ValueError):
            arr[0] = 999.0


def test_transition_states_in_free_space_match_the_closed_form():
    """REV-T2-05: event r, v are checked against exact free-space motion.

    Zero force, prograde burn: velocity direction is constant, so
    v = v0 + c ln(m0/m) u and x = x0 + v0 T + c [T - (m/mdot) ln(m0/m)] u after ignition.
    Coast before ignition is linear motion (exact under RK4). Ignition and cutoff
    share one tick here (601 s, 604 s) to exercise interior events.
    """
    v0 = np.array([30.0, 40.0, 0.0])
    u = v0 / 50.0
    sim = Simulator(np.zeros(3), v0, _ZeroForce(), RK4(), 10.0, spacecraft=_spacecraft())
    sim.schedule_burn("prograde", ignition_t_s=601.0, duration_s=3.0)
    _run_until(sim, 600.0)
    sim.step()
    ign, cut = sim.engine_transitions
    np.testing.assert_allclose(ign.r, v0 * 601.0, rtol=1e-15, atol=0)
    np.testing.assert_array_equal(ign.v, v0)
    mdot = ENGINE.mass_flow_kgps
    burn = cut.t - ign.t
    with localcontext() as ctx:  # 40 digits: the float64 closed form loses ~1e-9 m
        ctx.prec = 40
        c, md = Decimal(ENGINE.exhaust_velocity_mps), Decimal(mdot)
        m0, b = Decimal(DRY + PROP), Decimal(burn)
        m = m0 - md * b
        ln = (m0 / m).ln()
        dv, disp = c * ln, c * (b - (m / md) * ln)
        v_exact = [float(Decimal(v0[k]) + dv * Decimal(u[k])) for k in range(3)]
        r_exact = [float(Decimal(v0[k]) * Decimal(604) + disp * Decimal(u[k])) for k in range(3)]
    # Velocity: Simpson-exact to round-off. Position: one 3 s RK4 sub-step has a
    # truncation error ~1e-14 m; the bound is a few ulp of |r| (~2.4e4 m, ulp 3.6e-12).
    np.testing.assert_allclose(cut.v, v_exact, rtol=1e-14, atol=0)
    np.testing.assert_allclose(cut.r, r_exact, rtol=1e-14, atol=0)
    assert cut.propellant_kg == pytest.approx(PROP - mdot * burn, rel=1e-15, abs=0)


def test_transition_states_in_orbit_converge_to_independent_references():
    """REV-T2-05: interior ignition (605.5 s) vs exact Kepler; cutoff vs independent
    DOP853. Both converge at order 4 (|p - 4| <= 0.5, DR-0008), which a wrong or
    zeroed event state cannot satisfy."""
    from tars.astro import kepler

    r_k, _ = kepler.propagate(R0, V0, 605.5, WGS84.mu)
    ref = _independent_reference(605.5, 77.3, 1.0, 605.5 + 77.3)
    errs = {"ign_r": [], "cut_r": [], "cut_v": []}
    for dt in (20.0, 10.0, 5.0):
        sim = _sim(dt=dt)
        sim.schedule_burn("prograde", ignition_t_s=605.5, duration_s=77.3)
        events = {}
        while sim.t < 700.0:
            sim.step()
            events.update({e.kind: e for e in sim.engine_transitions})
        errs["ign_r"].append(np.linalg.norm(events["ignition"].r - r_k))
        errs["cut_r"].append(np.linalg.norm(events["cutoff"].r - ref[:3]))
        errs["cut_v"].append(np.linalg.norm(events["cutoff"].v - ref[3:6]))
    for series in errs.values():
        for coarse, fine in pairwise(series):
            assert abs(math.log2(coarse / fine) - 4.0) <= 0.5


def test_boundary_event_state_equals_the_tick_snapshot_and_records_stay_stable():
    sim = _sim()
    sim.schedule_burn("prograde", ignition_t_s=600.0, duration_s=20.0)
    _run_until(sim, 590.0)
    sim.step()  # ignition at the end of this tick, t = 600
    (ign,) = sim.engine_transitions
    snap = sim.snapshot()
    np.testing.assert_array_equal(ign.r, snap.r)
    np.testing.assert_array_equal(ign.v, snap.v)
    kept = (ign.r.copy(), ign.v.copy(), ign.propellant_kg)
    _run_until(sim, 700.0)
    np.testing.assert_array_equal(ign.r, kept[0])
    np.testing.assert_array_equal(ign.v, kept[1])
    assert ign.propellant_kg == kept[2]


# ------------------------------------- re-verification (M2-T2-review-01 addendum) N1-N3


@pytest.mark.parametrize("ignition", [0.0, 1.0, 605.5, 1.0e6, 1.0e9])
@pytest.mark.parametrize("policy", list(InsufficientPropellantPolicy))
def test_executed_interval_never_exceeds_the_depletion_time(ignition, policy):
    """N1: sufficiency must hold for the represented interval that is integrated.
    At the exact depletion boundary the cutoff is the latest representable time
    not after depletion, so consumption never exceeds the loaded propellant."""
    tank = ENGINE.mass_flow_kgps * 0.1
    t_dep = tank / ENGINE.mass_flow_kgps
    plan = plan_burn(ENGINE, tank, ignition, t_dep, policy=policy)
    assert plan.burn_duration_s <= t_dep
    assert ENGINE.mass_flow_kgps * plan.burn_duration_s <= tank
    assert plan.propellant_used_kg <= tank


def test_boundary_burn_at_large_time_executes_without_negative_mass():
    """N1 reviewer case: ignition 1e9 s, tank = mdot * 0.1 s, tiny dry mass."""
    tank = ENGINE.mass_flow_kgps * 0.1
    sc = SpacecraftSpec(dry_mass_kg=1e-10, engine=ENGINE, tank=TankSpec(propellant_kg=tank))
    sim = Simulator(
        np.zeros(3), np.array([1.0, 0.0, 0.0]), _ZeroForce(), RK4(), 1.0e8, spacecraft=sc
    )
    _run_until(sim, 9.0e8)
    plan = sim.schedule_burn(
        "prograde", ignition_t_s=1.0e9 + 50.0, duration_s=tank / ENGINE.mass_flow_kgps
    )
    while sim.t < 1.1e9:
        sim.step()
        assert sim.propulsion_snapshot().propellant_kg >= 0.0
    # The cutoff is the latest representable time not after depletion, so a tiny
    # residual (here ~1.5e-8 kg) may remain; it equals the plan's remainder.
    remaining = sim.propulsion_snapshot().propellant_kg
    assert abs(remaining - (tank - plan.propellant_used_kg)) <= 1e-12 * (1e-10 + tank)


@pytest.mark.parametrize("field", ["ignition_t_s", "duration_s"])
def test_integers_beyond_the_repr_limit_are_schema_invalid(field):
    """N2: building the rejection message must not itself raise."""
    sim = _sim()
    args = {"direction": "prograde", "ignition_t_s": 600.0, "duration_s": 10.0, field: 10**10000}
    with pytest.raises(BurnRejectedError) as err:
        sim.schedule_burn(**args)
    assert err.value.reason is BurnRejection.SCHEMA_INVALID
    with pytest.raises(BurnRejectedError) as err:
        plan_burn(ENGINE, 10**10000, 0.0, 1.0)
    assert err.value.reason is BurnRejection.SCHEMA_INVALID


def test_invalid_policy_is_schema_invalid_before_chronology():
    sim = _sim()
    _run_until(sim, 100.0)
    with pytest.raises(BurnRejectedError) as err:
        sim.schedule_burn("prograde", ignition_t_s=50.0, duration_s=10.0, policy="sometimes")
    assert err.value.reason is BurnRejection.SCHEMA_INVALID


def test_back_to_back_prograde_then_retrograde_transitions_match_free_space():
    """N3: every transition state, across two burns sharing an instant (604 s) and in
    both directions, against the exact free-space solution in 40-digit arithmetic."""
    v0 = np.array([3000.0, 4000.0, 0.0])
    u = v0 / 5000.0
    sim = Simulator(np.zeros(3), v0, _ZeroForce(), RK4(), 10.0, spacecraft=_spacecraft())
    sim.schedule_burn("prograde", ignition_t_s=601.0, duration_s=3.0)
    sim.schedule_burn("retrograde", ignition_t_s=604.0, duration_s=5.0)
    events = []
    while sim.t < 620.0:
        sim.step()
        events.extend(sim.engine_transitions)
    assert [(e.kind, e.t, e.direction) for e in events] == [
        ("ignition", 601.0, "prograde"),
        ("cutoff", 604.0, "prograde"),
        ("ignition", 604.0, "retrograde"),
        ("cutoff", 609.0, "retrograde"),
    ]
    with localcontext() as ctx:
        ctx.prec = 40
        c, md = Decimal(ENGINE.exhaust_velocity_mps), Decimal(ENGINE.mass_flow_kgps)
        speed, pos, mass, t = Decimal(5000), Decimal(0), Decimal(DRY + PROP), Decimal(0)
        expected = []
        for start, length, sign in ((601, 3, 1), (604, 5, -1)):
            pos += speed * (Decimal(start) - t)  # coast
            expected.append((pos, speed))
            m_end = mass - md * Decimal(length)
            ln = (mass / m_end).ln()
            pos += speed * Decimal(length) + sign * c * (Decimal(length) - (m_end / md) * ln)
            speed += sign * c * ln
            mass, t = m_end, Decimal(start + length)
            expected.append((pos, speed))
    for event, (s_exact, v_exact) in zip(events, expected, strict=True):
        np.testing.assert_allclose(event.r, float(s_exact) * u, rtol=1e-14, atol=1e-9)
        np.testing.assert_allclose(event.v, float(v_exact) * u, rtol=1e-14, atol=1e-12)


@pytest.mark.parametrize(("direction", "sign"), [("prograde", 1.0), ("retrograde", -1.0)])
def test_orbital_transition_states_converge_in_both_directions(direction, sign):
    """N3: ignition r, v vs exact Kepler and cutoff r, v vs independent DOP853,
    order 4 +/- 0.5 (DR-0008), for prograde and retrograde."""
    from tars.astro import kepler

    r_k, v_k = kepler.propagate(R0, V0, 605.5, WGS84.mu)
    ref = _independent_reference(605.5, 77.3, sign, 605.5 + 77.3)
    errs = {k: [] for k in ("ign_r", "ign_v", "cut_r", "cut_v")}
    for dt in (20.0, 10.0, 5.0):
        sim = _sim(dt=dt)
        sim.schedule_burn(direction, ignition_t_s=605.5, duration_s=77.3)
        ev = {}
        while sim.t < 700.0:
            sim.step()
            ev.update({e.kind: e for e in sim.engine_transitions})
        errs["ign_r"].append(np.linalg.norm(ev["ignition"].r - r_k))
        errs["ign_v"].append(np.linalg.norm(ev["ignition"].v - v_k))
        errs["cut_r"].append(np.linalg.norm(ev["cutoff"].r - ref[:3]))
        errs["cut_v"].append(np.linalg.norm(ev["cutoff"].v - ref[3:6]))
    for series in errs.values():
        for coarse, fine in pairwise(series):
            assert abs(math.log2(coarse / fine) - 4.0) <= 0.5


# ----------------------------------- second re-verification (M2-T2-review-01) N2, N4, N5


def test_depletion_with_tiny_dry_mass_never_evaluates_negative_mass():
    """N4: RK4 stages near depletion can carry -1e-17 kg of propellant round-off; the
    dynamics must use the physical (non-negative) propellant so the step succeeds."""
    tank = ENGINE.mass_flow_kgps * 1.0
    sc = SpacecraftSpec(dry_mass_kg=1e-20, engine=ENGINE, tank=TankSpec(propellant_kg=tank))
    sim = Simulator(np.zeros(3), np.array([1.0, 0.0, 0.0]), _ZeroForce(), RK4(), 0.1, spacecraft=sc)
    sim.schedule_burn("prograde", ignition_t_s=0.0, duration_s=1.0)
    while sim.t < 2.0:
        sim.step()
        assert sim.propulsion_snapshot().propellant_kg >= 0.0
    assert sim.propulsion_snapshot().engine_state is EngineState.IDLE


def test_conservative_depletion_cutoff_keeps_its_residual():
    """N5: when the cutoff steps back before depletion, consumption follows the
    executed interval for burn_to_depletion too, and the residual is retained."""
    tank = ENGINE.mass_flow_kgps * 0.1
    plan = plan_burn(
        ENGINE, tank, 1.0e9, 1.0, policy=InsufficientPropellantPolicy.BURN_TO_DEPLETION
    )
    assert plan.end_cause is BurnEndCause.PROPELLANT_DEPLETED
    assert plan.burn_duration_s < tank / ENGINE.mass_flow_kgps
    assert plan.propellant_used_kg == ENGINE.mass_flow_kgps * plan.burn_duration_s
    residual = tank - plan.propellant_used_kg
    assert residual > 0.0

    sc = SpacecraftSpec(dry_mass_kg=DRY, engine=ENGINE, tank=TankSpec(propellant_kg=tank))
    sim = Simulator(
        np.zeros(3), np.array([1.0, 0.0, 0.0]), _ZeroForce(), RK4(), 1.0e8, spacecraft=sc
    )
    _run_until(sim, 9.0e8)
    sim.schedule_burn(
        "prograde",
        ignition_t_s=1.0e9,
        duration_s=1.0,
        policy=InsufficientPropellantPolicy.BURN_TO_DEPLETION,
    )
    _run_until(sim, 1.1e9)
    assert sim.propulsion_snapshot().propellant_kg == pytest.approx(residual, rel=1e-6, abs=0)


def test_huge_integer_policy_is_schema_invalid_in_plan_burn():
    with pytest.raises(BurnRejectedError) as err:
        plan_burn(ENGINE, PROP, 0.0, 1.0, policy=10**10000)
    assert err.value.reason is BurnRejection.SCHEMA_INVALID
