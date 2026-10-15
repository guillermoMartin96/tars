from pathlib import Path

base = Path("docs/reviews/raw/M2-DR0017-codex-reverify-scratch")
s = (
    (base / "search.py")
    .read_text()
    .replace("c = Decimal(e.exhaust_velocity_mps)", "c = Decimal(e.thrust_n) / md")
)
Path("review_scratch/search.py").write_text(s)
s = (
    (base / "ordinary.py")
    .read_text()
    .replace("Decimal(e.exhaust_velocity_mps)", "(Decimal(e.thrust_n) / md)")
)
Path("review_scratch/ordinary.py").write_text(s)
s = (base / "reproductions.py").read_text()
start = s.index('p = s.schedule_burn("prograde", 1e9, 0.1)')
end = s.index("# Archived pre-T2")
s = (
    s[:start]
    + """try:
    s.schedule_burn("prograde", 1e9, 0.1)
except BurnRejectedError as err:
    assert err.reason == BurnRejection.BURN_UNSCHEDULABLE
    print("N1 rejected", err)
else:
    raise AssertionError("N1 accepted")
"""
    + s[end:]
)
Path("review_scratch/reproductions.py").write_text(s)
