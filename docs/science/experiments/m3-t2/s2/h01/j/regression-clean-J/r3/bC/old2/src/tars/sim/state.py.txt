"""Immutable views of simulator-owned physical state (ADR-0002)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

Vector = NDArray[np.float64]


def frozen_vector(values: object, size: int = 3) -> Vector:
    """Return a read-only float64 copy of ``values`` with the given length."""
    arr = np.array(values, dtype=np.float64, copy=True)
    if arr.shape != (size,):
        raise ValueError(f"expected shape ({size},), got {arr.shape}")
    if not np.all(np.isfinite(arr)):
        raise ValueError("state contains non-finite values")
    arr.flags.writeable = False
    return arr


@dataclass(frozen=True)
class StateSnapshot:
    """Read-only spacecraft translational state in the ECI frame (SCI-0003).

    Attributes:
        tick: Integer step counter; simulation time is ``tick * dt``.
        t: Elapsed time since the scenario epoch [s].
        r: Position [m], read-only.
        v: Velocity [m/s], read-only.
    """

    tick: int
    t: float
    r: Vector
    v: Vector

    def __post_init__(self) -> None:
        object.__setattr__(self, "r", frozen_vector(self.r))
        object.__setattr__(self, "v", frozen_vector(self.v))
