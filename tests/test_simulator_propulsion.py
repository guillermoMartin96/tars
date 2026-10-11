"""M2 task T2: propulsion inside the simulator (DR-0013, DR-0014, ADR-0007).

Covers the augmented state y = [r, v, m_prop, dv_sensed], the engine state machine,
exact RK4 step splitting at engine events, PropulsionSnapshot, scheduling
rejections, and M1 preservation.
"""

import math
from itertools import pairwise

import numpy as np
import pytest
from scipy.integrate import solve_ivp

from tars.astro.elements import circular_orbit_state, rv_to_elements
from tars.sim.constants import STANDARD_GRAVITY, WGS84
from tars.sim.forces import PointMassGravity
from tars.sim.integrators import RK4
from tars.sim.propulsion import (
    BurnEndCause,
    BurnRejectedError,
    BurnRejection,
    EngineSpec,
    EngineState,
    InsufficientPropellantPolicy,
    SpacecraftSpec,
    TankSpec,
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
    assert plan.propellant_used_kg == ENGINE.mass_flow_kgps * 77.3
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
    assert second.propellant_used_kg == remaining
    assert second.end_cause is BurnEndCause.PROPELLANT_DEPLETED


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


def test_depletion_ends_with_an_exactly_empty_tank_and_never_negative():
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
    assert p.propellant_kg == 0.0
    assert p.total_mass_kg == DRY
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
