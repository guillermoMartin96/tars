import numpy as np
import pytest

from tars.sim.state import StateSnapshot


def test_snapshot_is_immutable_and_copies_input():
    r = np.array([1.0, 2.0, 3.0])
    snap = StateSnapshot(tick=0, t=0.0, r=r, v=[0.0, 0.0, 0.0])
    r[0] = 99.0
    assert snap.r[0] == 1.0
    with pytest.raises(ValueError):
        snap.r[0] = 5.0
    with pytest.raises(AttributeError):
        snap.r = np.zeros(3)  # type: ignore[misc]


@pytest.mark.parametrize("bad", [[1.0, 2.0], [np.nan, 0.0, 0.0], [np.inf, 0.0, 0.0]])
def test_snapshot_rejects_invalid_vectors(bad):
    with pytest.raises(ValueError):
        StateSnapshot(tick=0, t=0.0, r=bad, v=[0.0, 0.0, 0.0])
