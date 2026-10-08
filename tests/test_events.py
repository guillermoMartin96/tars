import pytest
from pydantic import ValidationError

from tars.events import (
    OrbitCompleted,
    StateSampled,
    ValidationResult,
    parse_event,
    read_jsonl,
    to_jsonl,
)


def test_events_round_trip_through_jsonl():
    events = [
        StateSampled(tick=6, t=60.0, r=[1.0, 2.0, 3.0], v=[4.0, 5.0, 6.0], altitude_m=1.0),
        OrbitCompleted(tick=537, t=5370.0, orbit_number=1, crossing_t=5369.9),
        ValidationResult(
            tick=0,
            t=0.0,
            validator="x",
            passed=True,
            metrics={"m": 1.5},
            thresholds={"m": 2.0},
            threshold_status="provisional",
        ),
    ]
    text = to_jsonl(events)
    assert read_jsonl(text) == events
    assert text.count("\n") == 3


@pytest.mark.parametrize(
    "line",
    [
        '{"type": "Nope", "tick": 0, "t": 0}',
        '{"type": "StateSampled", "tick": 0, "t": 0, "r": [1, 2], "v": [1, 2, 3], "altitude_m": 0}',
        '{"type": "OrbitCompleted", "tick": -1, "t": 0, "orbit_number": 1, "crossing_t": 0}',
        '{"type": "OrbitCompleted", "tick": 1, "t": 0, "orbit_number": 1, "crossing_t": 0, "x": 1}',
        (
            '{"schema_version": 2, "type": "OrbitCompleted", "tick": 1, "t": 0,'
            ' "orbit_number": 1, "crossing_t": 0}'
        ),
    ],
)
def test_invalid_events_rejected(line):
    with pytest.raises(ValidationError):
        parse_event(line)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
@pytest.mark.parametrize("field", ["r", "v", "t", "altitude_m"])
def test_non_finite_telemetry_rejected(field, value):
    data = dict(tick=1, t=10.0, r=[1.0, 2.0, 3.0], v=[4.0, 5.0, 6.0], altitude_m=1.0)
    data[field] = [value, 0.0, 0.0] if field in ("r", "v") else value
    with pytest.raises(ValidationError):
        StateSampled(**data)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
@pytest.mark.parametrize("field", ["metrics", "thresholds"])
def test_non_finite_validation_event_numbers_rejected(field, value):
    data = dict(
        tick=0,
        t=0.0,
        validator="x",
        passed=False,
        metrics={"m": 1.0},
        thresholds={"m": 2.0},
        threshold_status="approved",
    )
    data[field] = {"m": value}
    with pytest.raises(ValidationError):
        ValidationResult(**data)
