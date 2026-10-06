#!/usr/bin/env bash
# Run the complete Milestone 1 Proof suite and write evidence to proof/records/evidence/M1/.
# Usage: toolbox/scripts/run_m1_proof.sh   (from the repository root; requires uv)
# Exit code: 0 only if every step passes.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"
UV="${UV:-uv}"
EV="proof/records/evidence/M1"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Cleanliness is checked before any evidence is written (evidence files themselves are outputs).
CLEAN=$([ -z "$(git status --porcelain --untracked-files=normal -- . ":(exclude)$EV")" ] && echo yes || echo no)
FAILED=0
LOG="$TMP/proof_run.log"

step() {
  local name="$1"; shift
  echo "== $name: $*" | tee -a "$LOG"
  "$@" >>"$LOG" 2>&1
  local code=$?
  echo "   exit=$code" | tee -a "$LOG"
  [ "$code" -eq 0 ] || FAILED=1
}

{
  echo "revision: $(git rev-parse HEAD)"
  echo "branch: $(git rev-parse --abbrev-ref HEAD)"
  echo "date_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "working_tree_clean_excluding_evidence: $CLEAN"
} | tee "$LOG"

step "uv sync --locked" "$UV" sync --locked
step "ruff check" "$UV" run ruff check .
step "ruff format --check" "$UV" run ruff format --check .
step "pytest" "$UV" run pytest -q
step "determinism (cross-process)" "$UV" run python toolbox/validators/determinism.py
step "cross-platform" sh -c "\"$UV\" run python toolbox/validators/cross_platform.py > \"$TMP/cross_platform.json\""
step "m1_proof (non-GMAT)" "$UV" run python toolbox/validators/m1_proof.py --out "$TMP/m1_non_gmat.json"
step "gmat compare" sh -c "\"$UV\" run python toolbox/scripts/gmat_m1.py compare > \"$TMP/gmat_reference.json\""
step "run_mission" "$UV" run python toolbox/scripts/run_mission.py --scenario scenarios/m1_leo_250km.json --out "$TMP/mission"

echo "overall: $([ "$FAILED" -eq 0 ] && echo PASS || echo FAIL)" | tee -a "$LOG"
mkdir -p "$EV"
cp "$LOG" "$TMP"/*.json "$EV"/
cp "$TMP/mission/summary.json" "$EV/mission_summary.json"
exit "$FAILED"
