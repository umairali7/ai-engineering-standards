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
# Keep stdout as a reviewable transcript while stderr shows the originating
# command's live tasks, dynamic worker activity, elapsed time, throughput, and
# ETA. The durable run directory is the source of identity, not parsed prose.
aies qualify "$CANDIDATE" --assessment coder --judge "$JUDGE" \
    > "$WS/qualification-transcript.md"
RUN=$(basename "$(ls -d "$WS"/runs/run-* | sort | tail -n1)")
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

hr "6. Engineering Capability Matrix — what was observed, and what is still unknown"
cat "$WS/runs/$RUN/engineering-capability-matrix.json" | py '
d=json.load(sys.stdin)
print("  mapping:", d["mapping"]["kind"], "v"+d["mapping"]["version"], "("+d["mapping"]["status"]+")")
for t in d["tasks"]:
    perf="not assessed" if t["observed_performance"] is None else "{:.0f}% observed".format(t["observed_performance"]/4*100)
    print("  {} {:<28} {:<16} {}".format(t["task_id"], t["task"], perf, t["status"]))
'
echo "Pending mapping review remains visible; the demo never upgrades observed evidence into demonstrated capability."

hr "7. Per-area qualification profile (formal evidence, kept separate from ECM)"
aies capabilities "$RUN"

hr "8. Qualification-bounded Deployment Guidance"
cat "$WS/runs/$RUN/deployment-guidance.json" | py '
d=json.load(sys.stdin); counts={}
for t in d["tasks"]: counts[t["guidance"]]=counts.get(t["guidance"],0)+1
print("  qualification record:", d["qualification_record"] or "not supplied")
[print(" ", k, v) for k,v in sorted(counts.items())]
'
echo "No human Qualification Record was supplied, so guidance correctly emits no Use recommendation."

hr "9. Protocol-compatible ECM comparison (same evidence fixture, no invented winner)"
aies compare "$RUN" "$RUN" --ecm --json | py '
d=json.load(sys.stdin)
print("  global protocol compatible:", d["compatible"])
print("  comparable demonstrated task rows:", sum(1 for t in d["tasks"] if t["comparable"]))
print("  winners emitted:", sum(1 for t in d["tasks"] if t["winner"]))
'

hr "10. Linked audience-specific decision products"
cat "$WS/runs/$RUN/report-bundle.json" | py '
d=json.load(sys.stdin)
print("  bundle schema:", d["report_bundle_schema"])
[print("  {:<24} {}".format(name,file)) for name,file in d["artifacts"].items() if name.endswith("_html") or name=="html"]
'
echo
sed -n '1,34p' "$WS/runs/$RUN/executive-summary.md"

hr "11. Presentation-grade renders (views of the SAME evidence — no hidden inference)"
HTML_EXIT=0
aies assessment result "$RUN" --format html --out "$WS/assessment.html" || HTML_EXIT=$?
if { [ "$HTML_EXIT" -eq 0 ] || [ "$HTML_EXIT" -eq 1 ]; } && [ -s "$WS/assessment.html" ]; then
  echo "wrote $WS/assessment.html (formal gate exit $HTML_EXIT contained)"
else
  echo "assessment HTML render failed with exit $HTML_EXIT" >&2
  exit "${HTML_EXIT:-2}"
fi
aies report "$RUN" --format html --write > /dev/null && echo "refreshed the complete linked report bundle"

hr "12. Formal grant boundary (expected refusal on automated-only evidence)"
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

hr "13. Decision-engine CONFORMANCE (the standard as a subject)"
echo "Does the reference engine reproduce AESQS decision semantics on the golden corpus?"
aies conform engine
echo
echo "-- and a FOREIGN engine (package-free reimplementation) self-verifies on the same corpus --"
aies conform engine --engine "python ../conformance/example_engine.py" | sed -n '1,4p'

hr "14. Empirical calibration harness (ready for a real-subject panel)"
echo "Design-time calibration is done; EMPIRICAL calibration needs a model panel."
echo "Demonstrating the harness on a SYNTHETIC 3-ability panel (not real evidence):"
cat > "$WS/panel.json" <<JSON
{"panel":[{"model":"strong","ability":3},{"model":"mid","ability":2},{"model":"weak","ability":1}],
 "scores":{"SC-CA07-001":{"strong":[4,4,3],"mid":[3,3,2],"weak":[1,2,1]},
           "SC-CA05-001":{"strong":[4,4],"mid":[4,4],"weak":[4,3]}},
 "twins":{"SC-CA07-001":"SC-CA07-007"}}
JSON
aies suites empirical "$WS/panel.json"

hr "15. Repository conformance AUDIT (a different subject: the engineering practice)"
aies audit .. | sed -n '1,10p'

hr "16. The platform reviews its OWN corpus (continuous QA — advisory, no single grade)"
aies corpus health | sed -n '1,18p'
echo
echo "-- and reviews a single scenario as a measurement instrument (structural + model critique) --"
aies corpus review SC-CA07-015 --reviewer "$JUDGE" | sed -n '1,14p'

hr "DEMO COMPLETE"
echo "Subjects assessed:  a model deployment (qualify)  +  a repository (audit)  +  the standard (conform engine)"
echo "Also shown:  live task/ETA progress, ECM strengths/gaps, bounded guidance, compatible comparison,"
echo "             the linked Executive Summary bundle, qualification boundary, and empirical harness."
echo "The same canonical result is served read-only over JSON:  aies serve --port 8722"
echo "workspace: $WS"
