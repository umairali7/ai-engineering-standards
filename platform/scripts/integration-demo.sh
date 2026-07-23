#!/usr/bin/env bash
# AIES end-to-end demo against a REAL deployment (opt-in; NOT run in default CI).
#
# Same golden path as scripts/demo.sh, but against a real model + judge you have
# registered. Requires a working runtime/endpoint (and possibly an API key via
# the runtime's env var). Because it needs infrastructure a contributor may not
# have, it is deliberately separate from `make demo` — nobody gets a degraded
# first-run experience.
#
#   make integration-demo DEPLOYMENT=local-qwen JUDGE=gpt-oss [ASSESSMENT=coder]
set -euo pipefail

DEPLOYMENT="${DEPLOYMENT:-}"
JUDGE="${JUDGE:-}"
ASSESSMENT="${ASSESSMENT:-coder}"

if [ -z "$DEPLOYMENT" ] || [ -z "$JUDGE" ]; then
  echo "error: set DEPLOYMENT and JUDGE to registered deployments." >&2
  echo "  make integration-demo DEPLOYMENT=local-qwen JUDGE=gpt-oss" >&2
  echo "  (list them with: aies deployment list)" >&2
  exit 2
fi
if [ "$DEPLOYMENT" = "$JUDGE" ]; then
  echo "error: DEPLOYMENT and JUDGE must differ (never self-judge)." >&2
  exit 2
fi

echo "== AIES integration demo (real deployment) =="
echo "candidate: $DEPLOYMENT   judge: $JUDGE   assessment: $ASSESSMENT"
echo

aies doctor
aies deployment list

RUN=$(aies qualify "$DEPLOYMENT" --assessment "$ASSESSMENT" --judge "$JUDGE" --json \
        | python -c 'import sys,json; print(json.load(sys.stdin)["run_id"])')
echo "run: $RUN"

aies assessment result "$RUN"
aies report "$RUN" --format html --write
echo
echo "== integration demo complete =="
