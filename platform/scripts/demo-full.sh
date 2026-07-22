#!/usr/bin/env bash
# AIES COMPREHENSIVE DEMO — the whole platform end to end, fully offline.
#
# A narrated tour of everything AIES does, against the mock runtime: the three
# subjects it can assess (a model deployment, a repository, and the standard
# itself), instrument quality (calibration), a complete automated Engineering
# Evaluation, the formal qualification/grant boundary, decision-engine
# conformance, the Phase-2 empirical harness, and the read-only API. No model,
# key, GPU, or network.
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

hr "4. Assess a deployment: compose -> collect -> automated Engineering Evaluation"
echo "Running the 'coder' assessment once per distinct instrument, auto-scored by a different mock judge..."
RUN=$(aies qualify "$CANDIDATE" --assessment coder --judge "$JUDGE" --json \
        | py 'print(json.load(sys.stdin)["run_id"])')
echo "run: $RUN"

# The mock judge is deliberately not trusted by default.  This fixture is
# synthetic and exists only to exercise the bootstrap-calibration admission
# path in offline CI; no real-model evidence or grant is implied.
cat > "$WS/mock-judge-calibration.json" <<'JSON'
{"model":[{"EV1":4,"EV2":4,"EV3":4,"EV4":4,"EV5":4,"EV6":4}],
 "human_anchor":[{"EV1":4,"EV2":4,"EV3":4,"EV4":4,"EV5":4,"EV6":4}]}
JSON
aies review "$RUN" --reviewer "model:$JUDGE" \
    --calibration "$WS/mock-judge-calibration.json" > /dev/null
echo "mock judge admitted through a synthetic bootstrap-calibration fixture (offline CI only)"

hr "5. Engineering Evaluation COMPLETE; Formal Qualification remains separate"
echo "Automated coverage is enough to complete the informational Engineering Evaluation:"
cat "$WS/runs/$RUN/engineering-evaluation.json" | py 'd=json.load(sys.stdin); print("  status:", d["status"].upper()); print("  human evaluation:", "reviewed" if d["human_evaluation"]["status"] == "reviewed" else "not reviewed (optional)"); [print(" ", a, v["status"].upper(), "by", v.get("completed_by") or "mixed") for a,v in d["areas"].items()]'
echo
echo "The Canonical Assessment Result answers the stricter formal-qualification question."
RESULT_EXIT=0
aies assessment result "$RUN" > "$WS/assessment-result.md" || RESULT_EXIT=$?
if [ "$RESULT_EXIT" -ne 0 ] && [ "$RESULT_EXIT" -ne 1 ]; then
  echo "unexpected assessment-result exit: $RESULT_EXIT" >&2
  exit "$RESULT_EXIT"
fi
sed -n '1,26p' "$WS/assessment-result.md"
echo "formal result exit $RESULT_EXIT is expected and contained by the demo"

hr "6. Per-area capability profile (planner / coder / security ... side by side)"
aies capabilities "$RUN"

hr "7. Presentation-grade renders (views of the SAME result — no re-deciding)"
HTML_EXIT=0
aies assessment result "$RUN" --format html --out "$WS/assessment.html" || HTML_EXIT=$?
if { [ "$HTML_EXIT" -eq 0 ] || [ "$HTML_EXIT" -eq 1 ]; } && [ -s "$WS/assessment.html" ]; then
  echo "wrote $WS/assessment.html (formal gate exit $HTML_EXIT contained)"
else
  echo "assessment HTML render failed with exit $HTML_EXIT" >&2
  exit "${HTML_EXIT:-2}"
fi
aies report "$RUN" --format html --write > /dev/null && echo "wrote evidence report (HTML)"

hr "8. Formal grant boundary (expected refusal on automated-only evidence)"
if aies grant "$RUN" --decision grant \
    --authority "A. Architect (ROLE-13)" --second "P. Peer (ROLE-14)" \
    > "$WS/unexpected-grant.txt" 2> "$WS/grant-refusal.txt"; then
  echo "ERROR: automated-only evidence unexpectedly produced a grant" >&2
  exit 1
else
  if ! grep -q "cannot grant on NON-DECISIONAL evidence" "$WS/grant-refusal.txt"; then
    echo "grant command failed for an unexpected reason:" >&2
    cat "$WS/grant-refusal.txt" >&2
    exit 1
  fi
  echo "grant correctly refused for non-decisional evidence; Engineering Evaluation remains complete and usable"
  grep -m1 "cannot grant on NON-DECISIONAL evidence" "$WS/grant-refusal.txt"
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
echo "Also shown:  calibrated instruments, the qualification boundary, and the Phase-2 empirical harness."
echo "The same canonical result is served read-only over JSON:  aies serve --port 8722"
echo "workspace: $WS"
