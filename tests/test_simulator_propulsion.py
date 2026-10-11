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
    TIMING_DELTA_V_BUDGET_MPS,
    BurnEndCause,
    BurnRejectedError,
    BurnRejection,
    EngineSpec,
    EngineState,
    InsufficientPropellantPolicy,
    PropulsionSpecError,
    SpacecraftSpec,
    TankSpec,
    plan_burn,
    rocket_equation_delta_v,
    timing_delta_v_error_mps,
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
    assert abs(plan.burn_duration_s - 77.3) <= math.ulp(plan.cutoff_t_s)
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
    depletion = InsufficientPropellantPolicy.BURN_TO_DEPLETION
    with pytest.raises(BurnRejectedError) as err:
        plan_burn(ENGINE, PROP, 1e15, 0.1, dry_mass_kg=DRY)
    assert err.value.reason is BurnRejection.BURN_UNSCHEDULABLE
    with pytest.raises(BurnRejectedError) as err:
        plan_burn(ENGINE, 0.032, 1e15, 1.0, policy=depletion, dry_mass_kg=DRY)
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
    """N1 case under DR-0017: ignition ~1e9 s, tank = mdot * 0.1 s, exact-depletion
    command. The step-back residual (~1.5e-8 kg) is a negligible delta-v error for the
    1000 kg reference vehicle, which executes with propellant never negative; for a
    1e-10 kg dry mass the same residual is a large delta-v error and is rejected."""
    tank = ENGINE.mass_flow_kgps * 0.1
    duration = tank / ENGINE.mass_flow_kgps
    tiny = SpacecraftSpec(dry_mass_kg=1e-10, engine=ENGINE, tank=TankSpec(propellant_kg=tank))
    sim = Simulator(np.zeros(3), np.array([1.0, 0, 0]), _ZeroForce(), RK4(), 1.0e8, spacecraft=tiny)
    _run_until(sim, 9.0e8)
    with pytest.raises(BurnRejectedError) as err:
        sim.schedule_burn("prograde", ignition_t_s=1.0e9 + 50.0, duration_s=duration)
    assert err.value.reason is BurnRejection.BURN_UNSCHEDULABLE

    sc = SpacecraftSpec(dry_mass_kg=DRY, engine=ENGINE, tank=TankSpec(propellant_kg=tank))
    sim = Simulator(np.zeros(3), np.array([1.0, 0, 0]), _ZeroForce(), RK4(), 1.0e8, spacecraft=sc)
    _run_until(sim, 9.0e8)
    plan = sim.schedule_burn("prograde", ignition_t_s=1.0e9 + 50.0, duration_s=duration)
    assert plan.timing_delta_v_error_mps <= TIMING_DELTA_V_BUDGET_MPS
    while sim.t < 1.1e9:
        sim.step()
        assert sim.propulsion_snapshot().propellant_kg >= 0.0
    remaining = sim.propulsion_snapshot().propellant_kg
    assert abs(remaining - (tank - plan.propellant_used_kg)) <= 1e-12 * (DRY + tank)


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


# ------------------------------------------------- DR-0017 (B + D1a, approved 2026-10-10)


def _independent_timing_dv_error(engine, dry, prop, ignition, duration, policy):
    """Delta-v difference between the executed and intended intervals, from first
    principles in 40-digit arithmetic (not using production helpers)."""
    mdot = engine.thrust_n / (engine.isp_s * STANDARD_GRAVITY)
    t_dep = prop / mdot
    intended = duration if duration <= t_dep else t_dep
    cutoff = ignition + intended
    while cutoff - ignition > t_dep:  # D1a: never past depletion
        cutoff = math.nextafter(cutoff, -math.inf)
    executed = cutoff - ignition
    with localcontext() as ctx:
        ctx.prec = 40
        c = Decimal(engine.isp_s) * Decimal(STANDARD_GRAVITY)

        def mass(t):
            return Decimal(dry) + max(Decimal(prop) - Decimal(mdot) * Decimal(t), Decimal(0))

        return float(abs(c * (mass(executed) / mass(intended)).ln())), executed > 0


@pytest.mark.parametrize(
    ("engine", "dry"),
    [
        (ENGINE, DRY),  # reference: a ~ 0.38 m/s^2
        (EngineSpec(thrust_n=1.0e5, isp_s=300.0), 1.0),  # extreme acceleration
        (EngineSpec(thrust_n=1.0, isp_s=3000.0), 1.0e4),  # extreme low acceleration
    ],
)
@pytest.mark.parametrize("ignition", [0.0, 605.5, 1.0e6, 3.3e7, 1.0e9, 7.7e10, 1.0e13, 1.0e15])
@pytest.mark.parametrize("policy", list(InsufficientPropellantPolicy))
def test_timing_delta_v_budget_classifies_like_an_independent_computation(
    engine, dry, ignition, policy
):
    """DR-0017 B: accept iff the projected timing-induced delta-v error <= 1e-7 m/s,
    across mission times and acceleration extremes, for both policies."""
    prop, duration = 50.0, 0.1
    if policy is InsufficientPropellantPolicy.BURN_TO_DEPLETION:
        duration = 2.0 * prop / engine.mass_flow_kgps  # forces a depletion cutoff
    expected_dv_err, representable = _independent_timing_dv_error(
        engine, dry, prop, ignition, duration, policy
    )
    accept = representable and expected_dv_err <= TIMING_DELTA_V_BUDGET_MPS
    if accept:
        plan = plan_burn(engine, prop, ignition, duration, policy=policy, dry_mass_kg=dry)
        assert plan.timing_delta_v_error_mps == pytest.approx(expected_dv_err, rel=1e-9, abs=1e-30)
    else:
        with pytest.raises(BurnRejectedError) as err:
            plan_burn(engine, prop, ignition, duration, policy=policy, dry_mass_kg=dry)
        assert err.value.reason is BurnRejection.BURN_UNSCHEDULABLE


def test_timing_budget_boundary_on_both_sides():
    """Reference engine: accepted at 1e9 s (error ~5e-8 m/s), rejected at 1e15 s."""
    ok = plan_burn(ENGINE, PROP, 1.0e9, 0.1, dry_mass_kg=DRY)
    assert 0.0 <= ok.timing_delta_v_error_mps <= TIMING_DELTA_V_BUDGET_MPS
    with pytest.raises(BurnRejectedError) as err:
        plan_burn(ENGINE, PROP, 1.0e15, 0.1, dry_mass_kg=DRY)
    assert err.value.reason is BurnRejection.BURN_UNSCHEDULABLE


def test_extreme_acceleration_is_rejected_where_the_reference_vehicle_is_accepted():
    """Same timing error, different physics: a 1e5 N engine on a 1 kg vehicle cannot
    tolerate the representation error that is negligible for the reference vehicle."""
    hot = EngineSpec(thrust_n=1.0e5, isp_s=300.0)
    ignition, duration = 1.0e7, 0.1  # reference error ~1.4e-10 m/s at this time
    plan_burn(ENGINE, PROP, ignition, duration, dry_mass_kg=DRY)  # accepted
    with pytest.raises(BurnRejectedError) as err:
        plan_burn(hot, 50.0, ignition, duration, dry_mass_kg=1.0)
    assert err.value.reason is BurnRejection.BURN_UNSCHEDULABLE


def test_depletion_residual_counts_toward_the_timing_budget():
    """D1a retains the residual; with a tiny dry mass that residual is a large share of
    the end mass, so the burn is rejected rather than silently mis-delivering delta-v."""
    tank = ENGINE.mass_flow_kgps * 0.1
    policy = InsufficientPropellantPolicy.BURN_TO_DEPLETION
    plan = plan_burn(ENGINE, tank, 1.0e9, 1.0, policy=policy, dry_mass_kg=DRY)
    assert plan.end_cause is BurnEndCause.PROPELLANT_DEPLETED
    assert plan.timing_delta_v_error_mps <= TIMING_DELTA_V_BUDGET_MPS
    with pytest.raises(BurnRejectedError) as err:
        plan_burn(ENGINE, tank, 1.0e9, 1.0, policy=policy, dry_mass_kg=1e-10)
    assert err.value.reason is BurnRejection.BURN_UNSCHEDULABLE


def test_schedule_burn_always_enforces_the_timing_budget():
    """The simulator passes the spacecraft's dry mass; no burn bypasses DR-0017."""
    hot = SpacecraftSpec(
        dry_mass_kg=1.0, engine=EngineSpec(thrust_n=1.0e5, isp_s=300.0), tank=TankSpec(50.0)
    )
    sim = Simulator(np.zeros(3), np.array([1.0, 0, 0]), _ZeroForce(), RK4(), 1.0e10, spacecraft=hot)
    _run_until(sim, 7.0e10)
    with pytest.raises(BurnRejectedError) as err:
        sim.schedule_burn("prograde", ignition_t_s=7.7e10, duration_s=0.1)
    assert err.value.reason is BurnRejection.BURN_UNSCHEDULABLE
    assert sim.propulsion_snapshot().pending_plans == ()


def test_cutoff_events_distinguish_depletion_from_normal_cutoff():
    """DR-0017 safeguard 6: machine-readable end cause on every cutoff transition."""
    sim = _sim(spacecraft=_spacecraft(propellant=5.0))
    sim.schedule_burn("prograde", ignition_t_s=600.0, duration_s=10.0)
    sim.schedule_burn(
        "retrograde",
        ignition_t_s=620.0,
        duration_s=100.0,
        policy=InsufficientPropellantPolicy.BURN_TO_DEPLETION,
    )
    events = []
    while sim.t < 700.0:
        sim.step()
        events.extend(sim.engine_transitions)
    assert [(e.kind, e.end_cause) for e in events] == [
        ("ignition", None),
        ("cutoff", BurnEndCause.COMPLETED),
        ("ignition", None),
        ("cutoff", BurnEndCause.PROPELLANT_DEPLETED),
    ]


# --------------------------------- DR-0017 verification (M2-DR0017 review) F1, F2


def _decimal_log1p(u):
    """ln(1 + u) for Decimal u >= 0 at the working precision, exact also for tiny u
    (Decimal has no log1p; ln(1 + 1e-315) would round to ln(1) = 0)."""
    if u < Decimal("1e-20"):
        return u - u * u / 2 + u * u * u / 3  # next term ~u^4, negligible
    return (1 + u).ln()


def _exact_timing_dv_error(engine, dry, prop, intended, executed):
    """Exact delta-v the simulator integrates over the timing difference:
    integral of F/m dt = (F/mdot) ln(m_large/m_small), m(x) = dry + prop - mdot x with the
    simulator's float mdot, in 60-digit arithmetic (log1p series for tiny ratios)."""
    with localcontext() as ctx:
        ctx.prec = 60
        thrust, md = Decimal(engine.thrust_n), Decimal(engine.mass_flow_kgps)
        longer = max(Decimal(executed), Decimal(intended))
        small = Decimal(dry) + max(Decimal(prop) - md * longer, Decimal(0))
        dm = md * abs(Decimal(executed) - Decimal(intended))
        return thrust / md * _decimal_log1p(dm / small)


@pytest.mark.parametrize(
    ("intended", "executed"),
    [(10.0, 30.0), (30.0, 10.0), (0.0, 61.0), (61.0, 0.5), (50.3, (600.0 + 50.3) - 600.0)],
)
def test_timing_error_uses_the_smaller_end_mass_and_matches_exact_value(intended, executed):
    """F2: the error is the exact rocket-equation difference, so the end mass must be the
    one after the longer interval. Large interval differences make a wrong mass choice
    visible (|ln| changes at first order in dm/m)."""
    engine, dry, prop = ENGINE, 2.0, 10.0  # t_dep ~ 62.4 s; all intervals within it
    got = timing_delta_v_error_mps(engine, dry, prop, intended, executed)
    exact = _exact_timing_dv_error(engine, dry, prop, intended, executed)
    # a_max |dt| bound: exact <= got <= exact (1 + x), x = mdot |dt| / m_end, since
    # x / (1 + x) <= ln(1 + x) <= x. A larger (wrong) end mass falls below exact.
    with localcontext() as ctx:
        ctx.prec = 60
        md = Decimal(engine.mass_flow_kgps)
        m_end = Decimal(dry) + Decimal(prop) - md * Decimal(max(intended, executed))
        x = md * abs(Decimal(intended) - Decimal(executed)) / m_end
        assert Decimal(got) >= exact  # never an underestimate
        assert Decimal(got) <= exact * (1 + x) * (1 + Decimal("1e-12"))


@pytest.mark.parametrize(
    ("thrust", "c", "dry", "prop", "intended", "executed"),
    [
        # F1 cancellation (reviewer): huge tank, small dry mass, end mass ill-conditioned
        (3e-7, 3e-7, 3.0, 1e16, 9999999999999998.0, 9999999999999996.0),
        # F1 underflow (reviewer): subnormal masses, mdot * dt underflows
        (1e-280, 1e20, 1e-310, 1e-310, 1e-11, 1.0000000000000004e-11),
        # cancellation where an unslackened end mass underestimates by ~38 % (found by
        # seeded search; the slack in the end-mass lower bound is required)
        (
            0.0012764678484075565,
            0.0008405601224338024 * STANDARD_GRAVITY,
            0.32186917193715897,
            7.460733292860184e16,
            4.81793673421924e17,
            4.817936734219239e17,
        ),
        # dt underflow with ordinary vehicle (error is genuinely negligible)
        (490.0, 312.0 * 9.80665, DRY, PROP, 5e-324, 1e-323),
    ],
)
def test_timing_error_is_never_underestimated_at_arithmetic_extremes(
    thrust, c, dry, prop, intended, executed
):
    engine = EngineSpec(thrust_n=thrust, isp_s=c / STANDARD_GRAVITY)
    got = timing_delta_v_error_mps(engine, dry, prop, intended, executed)
    exact = _exact_timing_dv_error(engine, dry, prop, intended, executed)
    assert not math.isnan(got)
    assert Decimal(got) >= exact * (1 - Decimal("1e-15"))


def test_reviewer_over_budget_configurations_are_rejected_by_the_simulator():
    """F1: both reviewer reproductions were accepted by schedule_burn; one executed."""
    cases = [
        (EngineSpec(3e-7, 3e-7 / STANDARD_GRAVITY), 3.0, 1e16, 3.0, 9999999999999998.0),
        (EngineSpec(1e-280, 1e20 / STANDARD_GRAVITY), 1e-310, 1e-310, 1e-10, 1e-11),
    ]
    for engine, dry, prop, ignition, duration in cases:
        sc = SpacecraftSpec(dry_mass_kg=dry, engine=engine, tank=TankSpec(propellant_kg=prop))
        sim = Simulator(np.zeros(3), np.array([1.0, 0, 0]), _ZeroForce(), RK4(), 1.0, spacecraft=sc)
        with pytest.raises(BurnRejectedError) as err:
            sim.schedule_burn("prograde", ignition_t_s=ignition, duration_s=duration)
        assert err.value.reason is BurnRejection.BURN_UNSCHEDULABLE


APPROVED_TIMING_BUDGET_MPS = 1e-7  # DR-0017 resolution, 2026-10-10


def test_timing_budget_is_the_approved_value():
    assert TIMING_DELTA_V_BUDGET_MPS == APPROVED_TIMING_BUDGET_MPS


def test_classification_is_tight_around_the_budget():
    """F2: scan representation errors for a high-acceleration vehicle; many cases fall
    within a factor of 2 of the 1e-7 m/s budget. Accept iff the exact error is within
    budget, allowing only the conservative evaluation margin (1e-9 relative)."""
    engine, dry, prop = EngineSpec(thrust_n=2.0e3, isp_s=300.0), 10.0, 50.0
    near = 0
    n = 4000
    for k in range(n):
        ignition = 10.0 ** (7.5 + k / n)  # ulp(t) ~ 4e-9 .. 1.5e-8 s
        duration = 0.1 + k * (0.4 / n)
        cutoff = ignition + duration
        executed = cutoff - ignition
        exact = float(_exact_timing_dv_error(engine, dry, prop, duration, executed))
        if 0.5 * APPROVED_TIMING_BUDGET_MPS <= exact <= 2.0 * APPROVED_TIMING_BUDGET_MPS:
            near += 1
        try:
            plan_burn(engine, prop, ignition, duration, dry_mass_kg=dry)
            accepted = True
        except BurnRejectedError as err:
            assert err.reason is BurnRejection.BURN_UNSCHEDULABLE
            accepted = False
        if exact > APPROVED_TIMING_BUDGET_MPS:
            assert not accepted, (ignition, duration, exact)
        elif exact <= APPROVED_TIMING_BUDGET_MPS * (1 - 1e-9):
            assert accepted, (ignition, duration, exact)
    assert near >= 1000  # measured ~1870 of 4000 within a factor of 2 of the budget
    # Includes cases within 1 % on both sides (measured 16 just over, 19 just under).


def test_timing_error_is_never_underestimated_for_ill_conditioned_end_masses():
    """F1 property: over seeded random huge-tank / small-dry-mass configurations near
    depletion, the conservative estimate is never below the exact error."""
    import random

    rng = random.Random(7)
    checked = 0
    while checked < 1500:
        prop, dry = 10 ** rng.uniform(10, 17), 10 ** rng.uniform(-1, 2)
        engine = EngineSpec(10 ** rng.uniform(-8, 2), 10 ** rng.uniform(-9, 3))
        t_dep = prop / engine.mass_flow_kgps
        intended = t_dep * (1 - 10 ** rng.uniform(-17, -14))
        executed = math.nextafter(intended, 0.0)
        if not (0.0 < executed <= t_dep and intended <= t_dep):
            continue
        exact = _exact_timing_dv_error(engine, dry, prop, intended, executed)
        got = timing_delta_v_error_mps(engine, dry, prop, intended, executed)
        assert Decimal(got) >= exact * (1 - Decimal("1e-15")), (engine, dry, prop, intended)
        checked += 1


def test_subnormal_log_argument_cannot_admit_an_over_budget_burn():
    """Re-verification N1: Isp ~1e307 s makes (F/m)dt/c subnormal; its relative rounding
    once let a 1.0000000005e-7 m/s burn pass as 9.99999998e-8. Upper bound a*dt applies."""
    engine = EngineSpec(thrust_n=8.38860800614743, isp_s=1.0197162129779283e307)
    sc = SpacecraftSpec(dry_mass_kg=1.0, engine=engine, tank=TankSpec(propellant_kg=1.0))
    executed = (1.0e9 + 0.1) - 1.0e9
    exact = _exact_timing_dv_error(engine, 1.0, 1.0, 0.1, executed)
    assert exact > Decimal(APPROVED_TIMING_BUDGET_MPS)
    got = timing_delta_v_error_mps(engine, 1.0, 1.0, 0.1, executed)
    assert Decimal(got) >= exact
    sim = Simulator(np.zeros(3), np.array([1.0, 0, 0]), _ZeroForce(), RK4(), 1.0e8, spacecraft=sc)
    _run_until(sim, 9.0e8)
    with pytest.raises(BurnRejectedError) as err:
        sim.schedule_burn("prograde", ignition_t_s=1.0e9, duration_s=0.1)
    assert err.value.reason is BurnRejection.BURN_UNSCHEDULABLE


def test_timing_error_bound_is_never_an_underestimate_across_the_float_range():
    """Adversarial property (seeded): spec-valid engines and masses over the full float
    range, representation pairs at random mission times (both orderings) and near-
    depletion pairs. The bound must never be below the exact integral of F/m. A
    90 000-case run of this generator (3 seeds) found none; 3 000 run here."""
    import random

    rng = random.Random(2026)
    checked = 0
    while checked < 3000:
        try:
            engine = EngineSpec(10 ** rng.uniform(-300, 300), 10 ** rng.uniform(-300, 307))
            dry, prop = 10 ** rng.uniform(-310, 300), 10 ** rng.uniform(-310, 300)
        except (PropulsionSpecError, OverflowError):
            continue
        t_dep = prop / engine.mass_flow_kgps
        if not (math.isfinite(dry + prop) and math.isfinite(t_dep) and t_dep > 0.0):
            continue
        kind = rng.choice(["repr", "depl", "swap"])
        if kind == "depl":
            intended = t_dep * (1 - 10 ** rng.uniform(-17, -1))
            executed = math.nextafter(intended, rng.choice([0.0, math.inf]))
        else:
            t, d = 10 ** rng.uniform(-5, 18), t_dep * rng.uniform(1e-6, 1.0)
            intended, executed = d, (t + d) - t
            if kind == "swap":
                intended, executed = executed, intended
        if not (0 < executed <= t_dep and 0 < intended <= t_dep) or executed == intended:
            continue
        got = timing_delta_v_error_mps(engine, dry, prop, intended, executed)
        exact = _exact_timing_dv_error(engine, dry, prop, intended, executed)
        assert math.isinf(got) or Decimal(got) >= exact, (engine, dry, prop, intended, executed)
        checked += 1


def test_reference_vehicle_is_never_rejected_at_ordinary_mission_times():
    """The conservative bound must not reject physically reasonable burns: the DR-0010
    vehicle up to 1e9 s (~32 years) for durations 0.01..900 s (measured max 2.5e-8 m/s)."""
    import random

    rng = random.Random(1)
    for _ in range(5000):
        t, d = 10 ** rng.uniform(0, 9), rng.uniform(0.01, 900.0)
        plan = plan_burn(ENGINE, PROP, t, d, dry_mass_kg=DRY)
        assert plan.timing_delta_v_error_mps <= APPROVED_TIMING_BUDGET_MPS
