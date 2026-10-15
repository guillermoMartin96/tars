#!/usr/bin/env bash
# Run the complete single-host Milestone 2 Proof suite (T8) and write evidence to
# proof/records/evidence/M2/ (or EVIDENCE_DIR).
# Usage: toolbox/scripts/run_m2_proof.sh [EVIDENCE_DIR]   (from the repository root; requires uv)
# - Includes every M1 gate (P10) and every M2 gate that one host can run. The DR-0023
#   three-platform final-state gate needs evidence from three platforms of one CI run; it is
#   the CI job `m2-cross-platform`, not part of this script. This script collects this
#   host's record and checks it against the pinned golden (inside the M2 Proof).
# - Refuses an evidence directory that is, or is inside, proof/records/evidence/M1/.
# - Exit code: 0 only if every step passes, every required artifact exists and the evidence
#   was published. The verdict is printed after publication.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd -P)"
cd "$REPO_ROOT"
UV="${UV:-uv}"
EV="${1:-proof/records/evidence/M2}"

# Resolve the destination without creating it, then guard it before anything is written.
resolve() { python3 -c 'import os, sys; print(os.path.realpath(sys.argv[1]))' "$1"; }
EV_ABS="$(resolve "$EV")" || { echo "cannot resolve evidence directory $EV" >&2; exit 2; }
M1_ABS="$(resolve proof/records/evidence/M1)"
case "$EV_ABS/" in
  "$M1_ABS"/*) echo "refusing to write into the M1 evidence directory: $EV_ABS" >&2; exit 2 ;;
esac
if [ "$EV_ABS" = "$REPO_ROOT" ]; then
  echo "refusing to write evidence into the repository root" >&2; exit 2
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Cleanliness is checked before any evidence is written (evidence files themselves are outputs).
# Only an evidence directory inside the repository is excluded; a git error counts as not clean.
SPEC=(.)
case "$EV_ABS/" in "$REPO_ROOT"/*) SPEC+=(":(exclude)${EV_ABS#"$REPO_ROOT"/}") ;; esac
if STATUS="$(git status --porcelain --untracked-files=normal -- "${SPEC[@]}")" && [ -z "$STATUS" ]; then
  CLEAN=yes
else
  CLEAN=no
fi
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

# Every artifact the record cites must exist before anything is published.
REQUIRED=(m2_final_states_record.json m1_cross_platform.json m1_non_gmat.json
  gmat_m1_reference.json gmat_m2_reference.json m2_proof_report.json m2_proof_stdout.txt)
for s in scenarios/m2_*.json; do REQUIRED+=("mission_$(basename "$s" .json)/summary.json"); done
for f in "${REQUIRED[@]}"; do
  if [ ! -s "$TMP/$f" ]; then
    echo "missing artifact: $f" | tee -a "$LOG"
    FAILED=1
  fi
done

# Publish. Previously published artifacts of the same names are removed first, so a
# file from an earlier run can never stand in for one this run did not produce.
publish() {
  mkdir -p "$EV" || return 1
  rm -f "$EV"/proof_run.log "$EV"/mission_*_summary.json || return 1
  for f in "${REQUIRED[@]}"; do
    case "$f" in
      mission_*/summary.json) rm -f "$EV/${f%/summary.json}_summary.json" || return 1 ;;
      *) rm -f "$EV/$f" || return 1 ;;
    esac
  done
  for f in "${REQUIRED[@]}"; do
    [ -e "$TMP/$f" ] || continue
    case "$f" in
      mission_*/summary.json) cp "$TMP/$f" "$EV/${f%/summary.json}_summary.json" || return 1 ;;
      *) cp "$TMP/$f" "$EV/$f" || return 1 ;;
    esac
  done
}
if ! publish; then
  echo "evidence publication to $EV failed" | tee -a "$LOG"
  FAILED=1
fi

VERDICT=$([ "$FAILED" -eq 0 ] && echo PASS || echo FAIL)
echo "overall: $VERDICT" >> "$LOG"
if ! cp "$LOG" "$EV/proof_run.log" 2>/dev/null; then
  echo "evidence publication to $EV failed (proof_run.log)"
  VERDICT=FAIL
  FAILED=1
fi
echo "overall: $VERDICT"
exit "$FAILED"
