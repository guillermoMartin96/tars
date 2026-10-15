#!/usr/bin/env bash
# Run the complete Milestone 2 Proof suite (T8) and write evidence to proof/records/evidence/M2/.
# Usage: toolbox/scripts/run_m2_proof.sh [EVIDENCE_DIR]   (from the repository root; requires uv)
# The M2 suite includes every M1 gate (P10). It never writes proof/records/evidence/M1/.
# Exit code: 0 only if every step passes.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"
UV="${UV:-uv}"
EV="${1:-proof/records/evidence/M2}"
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
# The cross-platform record must come from the clean checkout (it records the tree state).
step "m2 cross-platform record (this platform)" "$UV" run python toolbox/validators/m2_cross_platform.py collect --out "$TMP/m2_final_states_record.json"
step "ruff check" "$UV" run ruff check .
step "ruff format --check" "$UV" run ruff format --check .
step "pytest" "$UV" run pytest -q
# M1 gates (P10), unchanged.
step "m1 determinism (cross-process)" "$UV" run python toolbox/validators/determinism.py
step "m1 cross-platform" sh -c "\"$UV\" run python toolbox/validators/cross_platform.py > \"$TMP/m1_cross_platform.json\""
step "m1_proof (non-GMAT)" "$UV" run python toolbox/validators/m1_proof.py --out "$TMP/m1_non_gmat.json"
step "gmat m1 compare" sh -c "\"$UV\" run python toolbox/scripts/gmat_m1.py compare > \"$TMP/gmat_m1_reference.json\""
# M2 gates.
for s in scenarios/m2_*.json; do
  step "m2 determinism $(basename "$s" .json)" "$UV" run python toolbox/validators/determinism.py --scenario "$s"
done
step "gmat m2 compare" sh -c "\"$UV\" run python toolbox/scripts/gmat_m2.py compare > \"$TMP/gmat_m2_reference.json\""
step "reference snapshot verify-baseline (DR-0021)" "$UV" run python toolbox/scripts/reference_snapshot.py verify-baseline toolbox/references/snapshot/m2/REFERENCE_SNAPSHOT.json.gz
step "m2_proof (O1-O9, contract, golden cross-platform)" sh -c "\"$UV\" run python toolbox/validators/m2_proof.py --out \"$TMP/m2_proof_report.json\" > \"$TMP/m2_proof_stdout.txt\""
for s in scenarios/m2_*.json; do
  b="$(basename "$s" .json)"
  step "run_mission $b" "$UV" run python toolbox/scripts/run_mission.py --scenario "$s" --out "$TMP/mission_$b"
done

echo "overall: $([ "$FAILED" -eq 0 ] && echo PASS || echo FAIL)" | tee -a "$LOG"
mkdir -p "$EV"
cp "$LOG" "$TMP"/*.json "$TMP"/*.txt "$EV"/
for d in "$TMP"/mission_*; do
  cp "$d/summary.json" "$EV/$(basename "$d")_summary.json"
done
exit "$FAILED"
