"""Maneuver commands and receipts (DR-0014; M2 task T3).

A ``BurnCommand`` is a request. It carries commanded intent only and never physical
state. ``Simulator.submit()`` validates it and schedules engine activity, returning an
immutable ``CommandReceipt``. Rejected commands change nothing. ``issuer`` is recorded
provenance with no authority: permission enforcement belongs to a future crew layer,
in front of ``submit()`` (DR-0014 section 6).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from tars.events.schema import COMMAND_ID_PATTERN, StrictVersion1
from tars.sim.propulsion import BurnPlan, BurnRejection

# Command IDs: 1-64 characters, ASCII alphanumerics and ``._:-``, starting with an
# alphanumeric. ``#`` is reserved for simulator-assigned burn IDs (``burn#000001``),
# so the two ID spaces can never collide.
_COMMAND_ID_RE = re.compile(COMMAND_ID_PATTERN)
_MAX_SCHEMA_ERRORS = 5


def safe_text(text: str, limit: int = 120) -> str:
    """Valid, bounded UTF-8 for machine-readable records (review REV-T3-04).

    Invalid code points such as lone surrogates are written as backslash escapes.
    """
    clean = text.encode("utf-8", "backslashreplace").decode("utf-8")
    return clean if len(clean) <= limit else clean[: limit - 3] + "..."


def _is_valid_utf8(text: str) -> bool:
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True


class BurnCommand(BaseModel):
    """Duration-based burn request, schema version 1 (DR-0014 1A, 2A, 3C).

    Strict: numbers must be real and finite (no bool, str or None), enums exact, no extra
    fields. The sign of ``duration_s`` is not a schema matter: a non-positive duration
    keeps its own approved rejection code, ``non_positive_duration``.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False, strict=True)

    schema_version: StrictVersion1 = 1
    type: Literal["BurnCommand"] = "BurnCommand"
    command_id: str = Field(pattern=COMMAND_ID_PATTERN)
    issuer: str = Field(min_length=1, max_length=64)
    ignition_t_s: float
    direction: Literal["prograde", "retrograde"]
    duration_s: float
    on_insufficient_propellant: Literal["reject", "burn_to_depletion"] = "reject"

    @field_validator("issuer")
    @classmethod
    def _issuer_is_valid_unicode(cls, value: str) -> str:
        # Defence in depth (REV-T3-04): pydantic currently rejects invalid Unicode in
        # length-constrained strings (string_unicode) but not in unconstrained ones.
        if not _is_valid_utf8(value):
            raise ValueError("issuer must be valid Unicode")
        return value


class CommandStatus(StrEnum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"


@dataclass(frozen=True)
class CommandReceipt:
    """Outcome of one submission, at simulation time (tick, t).

    Attributes:
        status: Accepted or rejected.
        command_id: The command's ID; None only if a malformed payload had no readable ID.
        issuer: Recorded provenance (no authority); None if unreadable.
        command: The validated command, verbatim commanded intent; None if schema-invalid.
        reason: Approved rejection code (DR-0014); None when accepted.
        detail: Human-readable explanation, derived from the structured fields.
        burn_id: Simulator-assigned, deterministic ID correlating engine events.
        plan: The exact executed plan (BurnPlan) when accepted.
        tick: Integer step counter when the command was submitted.
        t: Simulation time when the command was submitted [s].
        schema_errors: "field: error_type" entries for a schema-invalid payload.
    """

    status: CommandStatus
    command_id: str | None
    issuer: str | None
    command: BurnCommand | None
    reason: BurnRejection | None
    detail: str
    burn_id: str | None
    plan: BurnPlan | None
    tick: int
    t: float
    schema_errors: tuple[str, ...] = ()


def parse_command(payload: object) -> BurnCommand:
    """Validate a payload into a fresh, canonical BurnCommand (review REV-T3-02).

    Model instances, including subclasses and ``model_copy(update=...)`` results that
    skipped validation, are dumped and re-validated against the exact schema, so the
    result never aliases caller-owned objects.

    Raises:
        ValidationError: for any schema violation.
    """
    if isinstance(payload, BaseModel):
        payload = payload.model_dump(warnings=False)
    return BurnCommand.model_validate(payload)


def readable_field(payload: object, name: str) -> str | None:
    """A string field from a malformed payload, if it is safe to echo in a receipt:
    a valid command ID, or a valid-Unicode issuer of 1-64 characters."""
    if isinstance(payload, BaseModel):
        payload = payload.__dict__
    if not isinstance(payload, dict):
        return None
    value = payload.get(name)
    if not isinstance(value, str) or not _is_valid_utf8(value):
        return None
    if name == "command_id":
        return value if _COMMAND_ID_RE.fullmatch(value) else None
    return value if 0 < len(value) <= 64 else None


def schema_errors(err: ValidationError) -> tuple[str, ...]:
    """Bounded "field: error_type" entries; input values are never echoed (they may be
    huge, unprintable or invalid Unicode)."""
    entries = [
        safe_text(f"{'.'.join(str(p) for p in e['loc']) or '<payload>'}: {e['type']}", 80)
        for e in err.errors()[:_MAX_SCHEMA_ERRORS]
    ]
    more = err.error_count() - _MAX_SCHEMA_ERRORS
    return (*entries, f"+{more} more") if more > 0 else tuple(entries)
