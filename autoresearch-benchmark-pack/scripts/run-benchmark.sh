#!/usr/bin/env bash
set -euo pipefail

# Runnable benchmark driver for initial Tier-A tasks.
#
# Usage:
#   ./scripts/run-benchmark.sh <task-id> <candidate-command> [skill-variant] [run-tag]
#
# Example:
#   ./scripts/run-benchmark.sh basename-subset /usr/bin/basename strict test01

TASK_ID="${1:-}"
CANDIDATE_CMD="${2:-}"
SKILL_VARIANT="${3:-unknown}"
RUN_TAG="${4:-manual}"

if [[ -z "$TASK_ID" || -z "$CANDIDATE_CMD" ]]; then
  echo "Usage: $0 <task-id> <candidate-command> [skill-variant] [run-tag]"
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RESULTS_DIR="$ROOT_DIR/results"
RUNS_DIR="$RESULTS_DIR/runs"
mkdir -p "$RUNS_DIR"

TS="$(date +%Y%m%dT%H%M%S)"
RUN_DIR="$RUNS_DIR/${TS}-${TASK_ID}-${RUN_TAG}"
mkdir -p "$RUN_DIR"

# Seed run directory with required artifact templates.
TEMPLATE_DIR="$ROOT_DIR/templates/run-artifacts"
for f in intake-form.md taint-register.yaml spec-index.yaml test-index.yaml traceability-matrix.yaml compliance-report.md; do
  if [[ -f "$TEMPLATE_DIR/$f" ]]; then
    cp "$TEMPLATE_DIR/$f" "$RUN_DIR/$f"
  else
    touch "$RUN_DIR/$f"
  fi
done

python3 "$ROOT_DIR/scripts/eval_task.py" \
  --task "$TASK_ID" \
  --candidate "$CANDIDATE_CMD" \
  > "$RUN_DIR/test-report.json"

python3 "$ROOT_DIR/scripts/check_artifacts.py" \
  --run-dir "$RUN_DIR" \
  > "$RUN_DIR/checklist-report.json"

python3 "$ROOT_DIR/scripts/score-run.py" \
  --test-report "$RUN_DIR/test-report.json" \
  --checklist-report "$RUN_DIR/checklist-report.json" \
  > "$RUN_DIR/score-report.json"

TOTAL_SCORE="$(python3 - <<'PY' "$RUN_DIR/score-report.json"
import json,sys
p=json.load(open(sys.argv[1]))
print(p.get('total_score',0.0))
PY
)"
STATUS="$(python3 - <<'PY' "$RUN_DIR/score-report.json"
import json,sys
p=json.load(open(sys.argv[1]))
print(p.get('status','unknown'))
PY
)"

mkdir -p "$RESULTS_DIR"
if [[ ! -f "$RESULTS_DIR/results.tsv" ]]; then
  printf "iter\tcommit\ttask_id\tskill_variant\tscore\tdelta\tstatus\tdescription\n" > "$RESULTS_DIR/results.tsv"
fi

ITER="$(($(wc -l < "$RESULTS_DIR/results.tsv")))"
COMMIT="$(git rev-parse --short HEAD 2>/dev/null || echo nocommit)"
DESC="candidate=${CANDIDATE_CMD} run_dir=$(basename "$RUN_DIR")"
printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
  "$ITER" "$COMMIT" "$TASK_ID" "$SKILL_VARIANT" "$TOTAL_SCORE" "0.0000" "$STATUS" "$DESC" \
  >> "$RESULTS_DIR/results.tsv"

cat > "$RUN_DIR/iteration-report.md" <<EOF
# Iteration Report

- run_tag: $RUN_TAG
- iteration: $ITER
- task_id: $TASK_ID
- skill_variant: $SKILL_VARIANT
- candidate_command: $CANDIDATE_CMD
- score: $TOTAL_SCORE
- status: $STATUS
- run_dir: $RUN_DIR

See JSON artifacts in this directory.
EOF

echo "Run complete."
echo "  run_dir: $RUN_DIR"
echo "  score:   $TOTAL_SCORE"
echo "  status:  $STATUS"
echo "  ledger:  $RESULTS_DIR/results.tsv"
