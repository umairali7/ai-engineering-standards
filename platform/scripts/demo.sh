#!/usr/bin/env bash
# AIES end-to-end demo — the whole platform, fully offline, in one script.
#
# Executable documentation (STABILITY/onboarding): a contributor with nothing
# installed but `aies` can watch the complete workflow run against the mock
# runtime — discover a deployment, compose a named qualification from an
# assessment, collect + auto-score evidence with a mock judge, let the frozen
# decision engine decide the outcome, and render the Canonical Assessment
# Result. No GPU, no API key, no network.
#
# For a run against a REAL deployment, see `make integration-demo`.
set -euo pipefail

WS="$(mktemp -d 2>/dev/null || echo "${TMPDIR:-/tmp}/aies-demo-$$")"
export AIES_WORKSPACE="$WS"
CANDIDATE="mock-mock-small"
JUDGE="mock-mock-large"          # a DIFFERENT deployment — never self-judge
ASSESSMENT="coder"

echo "== AIES demo (offline, mock runtime) =="
echo "workspace: $WS"
echo

echo "-- 1. environment + discovery --"
aies doctor --json > /dev/null && echo "doctor: ok"
aies discover > /dev/null && echo "discover: registered mock deployments"

echo
echo "-- 2. the named qualification (declarative) --"
aies assessment list

echo
echo "-- 3. compose + collect + auto-score + decide --"
RUN=$(aies qualify "$CANDIDATE" --assessment "$ASSESSMENT" --judge "$JUDGE" \
        --repeats 5 --json | python -c 'import sys,json; print(json.load(sys.stdin)["run_id"])')
echo "run: $RUN"

echo
echo "-- 4. the Canonical Assessment Result (authoritative outcome) --"
aies assessment result "$RUN"

echo
echo "-- 5. presentation-grade renders (views of the same result) --"
aies assessment result "$RUN" --format html --out "$WS/assessment.html" && echo "wrote $WS/assessment.html"
aies report "$RUN" --format html --write > /dev/null && echo "wrote evidence report (HTML)"

echo
echo "== demo complete: $WS =="
