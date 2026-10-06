import math

import numpy as np
import pytest

from tars.sim.integrators import RK4


def _integrate(step, f, y0, t_end, n):
    dt = t_end / n
    y = np.array(y0, dtype=float)
    for k in range(n):
        y = step(f, k * dt, y, dt)
    return y


def _euler_step(f, t, y, dt):
    """Negative control only (ADR-0004): explicit Euler, first order."""
    return y + dt * f(t, y)


def _oscillator(t, y):
    return np.array([y[1], -y[0]])


def _observed_order(step, f, y0, t_end, exact, n_values):
    errors = [np.linalg.norm(_integrate(step, f, y0, t_end, n) - exact) for n in n_values]
    slope = np.polyfit(np.log([t_end / n for n in n_values]), np.log(errors), 1)[0]
    return slope, errors


def test_rk4_is_fourth_order_on_harmonic_oscillator():
    exact = np.array([math.cos(10.0), -math.sin(10.0)])
    order, _ = _observed_order(
        RK4().step, _oscillator, [1.0, 0.0], 10.0, exact, [50, 100, 200, 400]
    )
    assert order == pytest.approx(4.0, abs=0.1)


def test_rk4_is_fourth_order_on_exponential_growth():
    exact = np.array([math.exp(2.0)])
    order, _ = _observed_order(RK4().step, lambda t, y: y, [1.0], 2.0, exact, [20, 40, 80, 160])
    assert order == pytest.approx(4.0, abs=0.1)


def test_rk4_handles_explicit_time_dependence():
    # y' = 3 t^2  ->  y = t^3; RK4 is exact for polynomials of degree <= 3 in t (Simpson).
    y = _integrate(RK4().step, lambda t, y: np.array([3 * t * t]), [0.0], 2.0, 7)
    assert y[0] == pytest.approx(8.0, rel=1e-14)


def test_euler_negative_control_is_first_order():
    exact = np.array([math.cos(10.0), -math.sin(10.0)])
    order, _ = _observed_order(
        _euler_step, _oscillator, [1.0, 0.0], 10.0, exact, [2000, 4000, 8000]
    )
    assert order == pytest.approx(1.0, abs=0.1)
