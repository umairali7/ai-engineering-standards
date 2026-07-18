#!/usr/bin/env bash
# AIES COMPREHENSIVE DEMO — the whole platform end to end, fully offline.
#
# A narrated tour of everything AIES does, against the mock runtime: the three
# subjects it can assess (a model deployment, a repository, and the standard
# itself), instrument quality (calibration), the governance lifecycle (human
# grant + environment re-verification), decision-engine conformance, the Phase-2
# empirical harness, and the read-only API. No model, key, GPU, or network.
#
#   make demo-full     (or: bash scripts/demo-full.sh)
set -euo pipefail

WS="$(mktemp -d 2>/dev/null || echo "${TMPDIR:-/tmp}/aies-fulldemo-$$")"
export AIES_WORKSPACE="$WS"
CANDIDATE="mock-mock-small"
JUDGE="mock-mock-large"      # a DIFFERENT deployment — never self-judge
py() { python -c "import sys,json; $1"; }
hr() { echo; echo "==================================================================="; echo "$1"; echo "==================================================================="; }

hr "AIES COMPREHENSIVE DEMO  (offline, mock runtime)   ws=$WS"

hr "1. Setup — environment + deployment discovery"
aies doctor --json > /dev/null && echo "doctor: environment validated + fingerprinted"
aies discover > /dev/null && aies registry list

hr "2. The corpus is a set of calibrated MEASUREMENT INSTRUMENTS"
echo "Every scenario carries a ceiling anchor ('what a 4 does that a 3 doesn't'):"
aies suites validate | sed -n '1,8p'
aies suites calibrate | sed -n '1,12p'

hr "3. Declarative assessments (composition as data, ADR-0005)"
aies assessment list

hr "4. Qualify a deployment: compose -> collect -> auto-score -> DECIDE"
echo "Running the 'coder' assessment, auto-scored by a different mock as judge..."
RUN=$(aies qualify "$CANDIDATE" --assessment coder --judge "$JUDGE" --repeats 5 --json \
        | py 'print(json.load(sys.stdin)["run_id"])')
echo "run: $RUN"

hr "5. The Canonical Assessment Result (authoritative outcome + 3 layers)"
aies assessment result "$RUN" | sed -n '1,26p'

hr "6. Per-area capability profile (planner / coder / security ... side by side)"
aies capabilities "$RUN" || true

hr "7. Presentation-grade renders (views of the SAME result — no re-deciding)"
aies assessment result "$RUN" --format html --out "$WS/assessment.html" && echo "wrote $WS/assessment.html"
aies report "$RUN" --format html --write > /dev/null && echo "wrote evidence report (HTML)"

hr "8. The human grant lifecycle (the platform prepares evidence; a human grants)"
aies grant "$RUN" --decision grant \
    --authority "A. Architect (ROLE-13)" --second "P. Peer (ROLE-14)" > /dev/null \
    && echo "grant recorded" || echo "(grant step skipped)"
QUAL=$(aies qualification list --json 2>/dev/null | py 'r=json.load(sys.stdin); print(r[0]["record_id"] if r else "")' || true)
if [ -n "$QUAL" ]; then
  echo "Qualification Record: $QUAL"
  echo "Re-verify the environment (D7 — a fingerprint change would invalidate it):"
  aies verify "$QUAL" && echo "verify: environment unchanged, grant valid"
fi

hr "9. Decision-engine CONFORMANCE (the standard as a subject)"
echo "Does the reference engine reproduce AESQS decision semantics on the golden corpus?"
aies conform engine || true
echo
echo "-- and a FOREIGN engine (package-free reimplementation) self-verifies on the same corpus --"
aies conform engine --engine "python ../conformance/example_engine.py" 2>/dev/null | sed -n '1,4p' || echo "(foreign-engine step skipped)"

hr "10. Empirical calibration harness (Phase 2 — ready for a real-model panel)"
echo "Design-time calibration is done; EMPIRICAL calibration needs a model panel."
echo "Demonstrating the harness on a SYNTHETIC 3-ability panel (not real evidence):"
cat > "$WS/panel.json" <<JSON
{"panel":[{"model":"strong","ability":3},{"model":"mid","ability":2},{"model":"weak","ability":1}],
 "scores":{"SC-CA07-001":{"strong":[4,4,3],"mid":[3,3,2],"weak":[1,2,1]},
           "SC-CA05-001":{"strong":[4,4],"mid":[4,4],"weak":[4,3]}},
 "twins":{"SC-CA07-001":"SC-CA07-007"}}
JSON
aies suites empirical "$WS/panel.json"

hr "11. Repository conformance AUDIT (a different subject: the engineering practice)"
aies audit .. 2>/dev/null | sed -n '1,10p' || echo "(audit step skipped)"

hr "12. The platform reviews its OWN corpus (continuous QA — advisory, no single grade)"
aies corpus health 2>/dev/null | sed -n '1,18p' || echo "(corpus step skipped)"
echo
echo "-- and reviews a single scenario as a measurement instrument (structural + model critique) --"
aies corpus review SC-CA07-015 --reviewer "$JUDGE" 2>/dev/null | sed -n '1,14p' || echo "(review skipped)"

hr "DEMO COMPLETE"
echo "Subjects assessed:  a model deployment (qualify)  +  a repository (audit)  +  the standard (conform engine)"
echo "Also shown:  calibrated instruments, the human grant lifecycle, and the Phase-2 empirical harness."
echo "The same canonical result is served read-only over JSON:  aies serve --port 8722"
echo "workspace: $WS"
