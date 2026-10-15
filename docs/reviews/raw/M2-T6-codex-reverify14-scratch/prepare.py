# ruff: noqa
from pathlib import Path

root = Path("docs/reviews/raw/M2-T6-codex-reverify13-scratch")
for name in ["anchor_phase", "anchor_acceptance"]:
    s = (root / (name + ".py")).read_text()
    # Original probes must now terminate at the new rejecting boundary.
    Path("review_scratch/" + name + ".py").write_text(
        "# ruff: noqa\nimport runpy\ntry:\n    runpy.run_path("
        + repr(str(root / (name + ".py")))
        + ', run_name="__main__")\nexcept RuntimeError as e:\n    assert "anchor tick positions disagree" in str(e)\n    print("EXPECTED REJECTION", e)\nelse:\n    raise AssertionError("reference was not rejected")\n'
    )
Path("review_scratch/disable_tick.py").write_text(
    '# ruff: noqa\nimport inspect\nfrom tars.validation import m2\ns=inspect.getsource(m2.dop853_reference)\ns=s.replace("if not within(np.linalg.norm(tick_r - dense[:3].T, axis=1), tol):", "if False:")\nexec(s, m2.__dict__)\n'
)
for name in [
    "artifact_sweep",
    "row_sweep",
    "simulator_sweep",
    "translation_probe",
    "overflow_velocity_probe",
    "extrema_acceptance_probe",
    "reference_phase_probe",
    "correlated_probe",
]:
    Path("review_scratch/" + name + ".py").write_text((root / (name + ".py")).read_text())
