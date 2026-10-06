"""Deterministic Proof validators (toolbox/validators/ wraps these as CLIs).

Validators compute metrics and compare them with versioned thresholds from
``proof/thresholds/``. A metric without an approved or provisional threshold is
reported but not gated; tolerances are never invented (playbook/testing.md).
"""
