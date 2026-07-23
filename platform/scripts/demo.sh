#!/usr/bin/env bash
# AIES end-to-end engineering evaluation demo — fully offline.
set -euo pipefail

WS="$(mktemp -d 2>/dev/null || echo "${TMPDIR:-/tmp}/aies-demo-$$")"
export AIES_WORKSPACE="$WS"
CANDIDATE="mock-mock-small"
JUDGE="mock-mock-large"          # a different deployment — never self-judge
ASSESSMENT="coder"

echo "== AIES engineering evaluation demo (offline, mock runtime) =="
echo "workspace: $WS"
echo

echo "-- 1. environment + discovery --"
aies doctor --json > /dev/null && echo "doctor: ok"
aies discover > /dev/null && echo "discover: registered mock deployments"

echo
echo "-- 2. named engineering assessments (declarative composition) --"
aies assessment list

echo
echo "-- 3. compose + collect + auto-score + analyze --"
RUN=$(aies qualify "$CANDIDATE" --assessment "$ASSESSMENT" --judge "$JUDGE" \
        --parallel 8 --json | python -c 'import sys,json; print(json.load(sys.stdin)["run_id"])')
echo "run: $RUN"

echo
echo "-- 4. Engineering Assessment Result (human evaluation optional) --"
aies assessment result "$RUN"

echo
echo "-- 5. Engineering Capability Matrix (task strengths and gaps) --"
aies capabilities "$RUN" --ecm

echo
echo "-- 6. evidence-derived Engineering Fit Guidance --"
aies guidance "$RUN"

echo
echo "-- 7. presentation-grade renders --"
aies assessment result "$RUN" --format html --out "$WS/assessment.html"
echo "wrote $WS/assessment.html"
aies report "$RUN" --format html --write > /dev/null
echo "wrote Engineering Evaluation Report (HTML)"

echo
echo "-- 8. decision-engine conformance --"
aies conform engine

echo
echo "== demo complete: $WS =="
echo "Human evaluation was optional and did not block collection, scoring, analysis, assessment, or reporting."
echo "Formal qualification is available separately with --formal-qualification."
