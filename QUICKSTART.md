# See AIES Work in 60 Seconds

Run the real Engineering Evaluation pipeline fully offline: collect responses,
score them in optimized batches, generate the Engineering Capability Matrix
(ECM), derive Engineering Fit, and open the linked report bundle.

```powershell
cd platform
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
aies demo --open
```

macOS or Linux:

```bash
cd platform
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
aies demo --open
```

Do not use `--break-system-packages`. If you already use an isolated
application manager, `pipx install ./platform` or `uv tool install ./platform`
is an optional source-checkout alternative.

This works in PowerShell, Bash, and Zsh. It needs Python 3.10 or newer, but no
model server, GPU, API key, Make, Bash script, or human review. The mock subject
and reviewer are deterministic; the product path and artifacts are the same
ones used for a real deployment.

The final screen links to an Executive Summary and shows the exact command for
creating an anonymized, derived-view-only sharing bundle.

## Try a real deployment

Create a safe workspace and discover supported local runtimes:

```powershell
aies init
$env:AIES_WORKSPACE = (Resolve-Path aies-workspace)
aies support
aies starter list
aies discover
aies deployment list
```

On Bash or Zsh, set the same variable with:

```bash
export AIES_WORKSPACE="$(pwd)/aies-workspace"
```

If discovery cannot find an OpenAI-compatible endpoint, generate a non-secret
starter manifest:

```powershell
aies init aies-workspace --starter-manifest
# edit model and base_url; put the API key in AIES_OPENAI_API_KEY, never YAML
aies deployment add aies-workspace/deployment.example.yaml
```

Plan before spending time or tokens:

```powershell
aies evaluate SUBJECT --judge REVIEWER --plan-only --parallel 4
```

The plan shows distinct scenario calls, optimized judge calls, concurrency,
known cost/duration estimates, and limitations. It schedules no exact repeats.
When the scope looks right:

```powershell
aies evaluate SUBJECT --judge REVIEWER --parallel 4
aies snapshot latest
aies open latest
aies open latest --export-redacted
```

Automated scores complete the informational Engineering Evaluation, ECM,
diagnostics, fit guidance, and reports. Human evaluation is an optional,
separately visible assurance input. Formal Qualification is a different,
explicit human-governed workflow and is never forced into ordinary assessment.

`aies snapshot latest` is the fastest terminal view: it keeps observed
performance, distinct-scenario evidence confidence, unassessed tasks, and the
informational engineering interpretation in separate columns. Use
`--observed-only` for a shorter table; the coverage line still records hidden
tasks as unknown rather than zero.

## Choose the next path

- Understand every command and parameter: [CLI Reference](platform/CLI_REFERENCE.md)
- Check executable versus planned subjects: `aies support`
- Choose a bounded workflow by decision: `aies starter show understand-deployment`
- Register real endpoints: [Platform Guide](platform/GUIDE.md)
- Compare compatible runs: `aies compare RUN_A RUN_B`
- Analyze repository practice: `aies audit .`
- Import Inspect evidence: `aies bridge inspect-import RUN FILE`
- Import SARIF findings: `aies bridge sarif-import FILE`
- Learn what every metric claims: [Measurement Claims](platform/MEASUREMENT_CLAIMS.md)
- Enter formal governance intentionally: [AESQS](AESQS/README.md)

If a command fails, AIES preserves completed work where possible. Use
[Troubleshooting](platform/TROUBLESHOOTING.md) for endpoint, TLS,
authentication, quota, performance, scoring, and resume guidance.
