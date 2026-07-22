# AIES in 5 Minutes

Experience the **entire workflow** — discover a deployment, run a named
qualification, auto-score it, get an authoritative outcome, and render a report —
**fully offline**, with no model, API key, or GPU. Everything below uses the
built-in `mock` runtime.

## The fastest path (one command)

```bash
git clone <repo-url> && cd aies/platform
pip install -e .
make demo            # or: bash scripts/demo.sh
```

`make demo` runs all seven stages end-to-end and prints a **PASS**. That's the
whole platform in one command. Read on to run it yourself, stage by stage.

## Step by step (understand each stage)

```bash
cd platform
pip install -e .                      # installs the `aies` command (Python >= 3.10)

aies doctor                           # 1. validate the environment; detect runtimes
aies discover                         # 2. register the mock deployments
aies registry list                    #    -> mock-mock-small, mock-mock-large
```

Now run a **declarative assessment** (the `coder` qualification: implementation,
tests, secure coding), auto-scored by a *different* deployment as judge:

```bash
aies qualify mock-mock-small \
    --assessment coder \
    --judge mock-mock-large \
    --repeats 5                        # 3. collect + auto-score + decide
```

> **Why these values.** The deployment id is `mock-mock-small` (not bare `mock`).
> The judge must differ from the candidate — never self-judge. `--repeats 5`
> gathers enough scored items to clear the RT2 — Moderate statistical minimum, so the result
> is *decisional* rather than INSUFFICIENT EVIDENCE.

The command prints the Canonical Assessment Result and the run id. Grab the run:

```bash
RUN=$(aies runs list --json | python -c "import sys,json; print(json.load(sys.stdin)[0]['run_id'])")

aies assessment result "$RUN"                 # 4. the authoritative outcome (PASS/FAIL/…)
aies capabilities "$RUN"                       # 5. per-area CL + autonomy, side by side
aies assessment result "$RUN" --format html --out result.html   # 6. presentation view
aies conform engine                            # 7. is the decision engine conformant?
```

You've now seen composition → evidence → decision → report → conformance.

## What just happened

- **The outcome is decided once, by the engine**, over the assessment's
  *mandatory* competencies — gate-first, no blended score. Every renderer (the
  table above, the HTML, a future dashboard) is a *view* of that one result.
- **Nothing here can masquerade as real qualification evidence** — the mock
  self-declares in provenance, and under-sampled runs are labelled NON-DECISIONAL.

## Next steps

- **A real model:** register a deployment (`aies discover` finds local runtimes,
  or hand-author one — see [platform/GUIDE.md §5](platform/GUIDE.md)), then
  `make integration-demo DEPLOYMENT=<id> JUDGE=<id>`.
- **Compose your own qualification:** [platform/ASSESSMENTS.md](platform/ASSESSMENTS.md).
- **Everything else:** [platform/REFERENCE.md](platform/REFERENCE.md) — the
  vocabulary, artifact schemas, and every command.
