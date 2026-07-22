# Troubleshooting

| | |
|---|---|
| **Document ID** | AIES-PLAT-06 |
| **Status** | Draft |
| **Audience** | Engineers · Platform teams · Assessors & qualification authorities |

Symptom → cause → fix for the things that actually go wrong when running `aies`
against real endpoints. Most failures are **endpoint or environment** issues,
not the platform. When a command fails, read the error: since the endpoint fixes
below landed, messages name the endpoint, the reason, and the next step.

First stop for any connectivity problem:

```
aies doctor                 # which runtimes are reachable
aies runtime <name>         # probe one runtime's endpoint
aies deployment inspect <id># the base_url and api_key_env a deployment uses
```

---

## Connectivity & TLS

### `error: timed out` / `no response from … within Ns`
The endpoint accepted nothing back in time.
- **Local server not running.** If `base_url` is `http://localhost:<port>/v1`,
  start the runtime that serves it (Ollama/vLLM/LM Studio/llama.cpp/MLX) and
  confirm: `curl -sS -m 10 http://localhost:<port>/v1/models`.
- **Wrong `base_url`.** It must be the API base that serves `/chat/completions`
  (usually ends in `/v1`), not a marketing host. Fix with
  `aies deployment update <file>`.
- **Genuinely slow model.** Raise the per-request timeout:
  `export AIES_REQUEST_TIMEOUT_S=600`.
- **Server refusing concurrency.** Lower `--parallel` (see below).

The pre-run liveness probe fails within ~30 s, so a dead endpoint no longer
makes you wait the full request timeout.

### `CERTIFICATE_VERIFY_FAILED — unable to get local issuer certificate`
Python has no usable CA bundle (common on fresh **python.org macOS** builds).
- Reinstall the platform so `certifi` is present: `pip install -e ".[test]"`
  (the adapter uses certifi's bundle automatically), **or**
- run the Python installer's `Install Certificates.command`, **or**
- point at a specific bundle (e.g. a corporate CA):
  `export SSL_CERT_FILE=/path/to/ca-bundle.pem`.

### `Connection refused`
Nothing is listening on that host/port — the server is down or on a different
port than the deployment records.

---

## Authentication

### HTTP `401` / `403` — unauthorized
- **The key is not set.** `export <THE_ENV_VAR>=<key>` (e.g. `ANTHROPIC_API_KEY`).
- **`api_key_env` holds the key itself.** It must be the **name** of an
  environment variable, not the secret. Manifest: `api_key_env: ANTHROPIC_API_KEY`;
  the secret lives in your shell. Fix with `aies deployment update <file>`.
- **Never commit a key.** If one lands in a file or the chat, **rotate it** in
  the provider console immediately.

### HTTP `404` — not found
`base_url` is wrong, or `runtime_config.model` is not a model the server serves.
Check `curl <base_url>/models`.

### HTTP `429` — rate limited
The provider is throttling. Lower `--parallel`, or slow the run down.

---

## Performance

### A run takes far too long
Almost always the **subject model**, not the platform.
- **Cap output length.** With no `max_tokens`, a model may generate very long
  answers. `export AIES_MAX_TOKENS=1024` (or set `parameters_default.max_tokens`
  in the deployment) — often the single biggest speedup.
- **Do less while exploring.** `--repeats 1` collects one answer per scenario
  (report labelled **NON-DECISIONAL**, which is correct for a spot-check). Raise
  repeats only for a decisional result (RT1 — Minimal/2/3/4 need ≥20/30/50/100 scored items
  per area).

### `--parallel N` doesn't speed things up
A single local GPU serves requests roughly one at a time, so extra workers just
queue on the model — parallelism helps hosted endpoints far more than a local
server. For local models, `max_tokens` and `--repeats` are the real levers.
`--parallel` applies to **both** phases (collection and judge scoring); each
prints how many workers it uses.

---

## The judge (`--judge`)

### The judge step failed after collection — do I re-run everything?
**No.** Responses are written as they are collected and are saved even when a
later step fails. Fix the judge issue, then score the **already-collected** run
without re-collecting:

```
aies review <run-id> --model-reviewer <judge-id> --parallel 8
aies qualify --resume <run-id>
```

### `WARNING: the model scored its own output (self-judging)`
`--judge self` (or a judge id equal to the subject) is biased. Use a different,
capable deployment — see [`examples/deployments/`](examples/deployments/README.md).

### The judge scored few/no responses (`unparseable` high)
The judge model isn't returning the required score JSON. Check its reliability
across runs with `aies judge list` (the **parse rate** column) and prefer a
stronger judge. Unparseable replies are skipped, never fabricated.

### How many judges do I have, and how have they done?
`aies judge available` (the pool you've registered with `roles: [judge]`),
`aies judge list` (track record), `aies judge history` (per run).

---

## Registry & deployments

### `model id '…' already registered` when re-adding
Ids are never reused by `add`. To change an existing deployment, don't re-add —
**update it in place**: `aies deployment update <file>`. To free an id entirely,
`aies deployment remove <id>` (hard delete) vs `aies deployment retire <id>`
(soft, keeps the id reserved for audit).

### `model '…' is served by multiple deployments`
The same model name maps to several deployments. Name the deployment id
directly, or pass `--runtime <name>` to disambiguate.

### `verify-artifact` says MISMATCH (or the signature won't verify)
`aies deployment verify-artifact <id> --artifact <path>` recomputes the file's
SHA-256 and compares it to the declared `provenance.checksum`. MISMATCH means the
local file is not the artifact the deployment was registered against — you have
the wrong file, or the manifest checksum is stale (fix with `aies deployment
update`). A declared **signature** shows `declared-not-checked` until you pass
`--pubkey` and `--signature`; `unverifiable` means the `cryptography` package
isn't installed (`pip install cryptography`, or verify with cosign/Sigstore
externally). `endpoint-served` checksums can't be checked against a local file.

### Importing external eval results (`aies import`) skipped items
`aies import` ingests only items with a `scenario_id` and **six integer 0–4 EV
scores**; anything else is skipped and counted (never fabricated). If everything
was skipped, your file isn't in the expected shape — see `aies import --help` or
[GUIDE §5.2](GUIDE.md). A single-metric benchmark can't be imported as a full
qualification; bring it as EV-shaped evidence or keep it as separate corroboration.

---

## Scoring & reports

### After `qualify` (no `--judge`) it says to edit a scoresheet
That is the **manual** path: open the run's `scoresheet.json`, set integer 0–4
scores per EV dimension and a rater, then `aies score <run>` and
`aies qualify --resume <run>`. (It is a file to edit, not a command to run.)

### I can't tell which response got which score
Read the whole run in one view: `aies transcript <run-id>` — per item the task,
the model's answer, and its scores/findings together.

### The report says NON-DECISIONAL
Fewer scored items than the risk-tier minimum. Increase `--repeats` (or combine
runs) until the area reaches its minimum; the gate is intentional.

---

## Related Documents

- [AIES-PLAT-01 — AIES Platform — Architecture & Run Guide](GUIDE.md) — setup and a start-to-finish run
- [AIES-PLAT-03 — Deployments — Qualify Deployments, Not Models](DEPLOYMENTS.md) · [AIES-PLAT-04 — Runtimes — the Runtime Interface](RUNTIMES.md)
- [AIES-DOC-06 — Engineering Assessment Platform Specification](../docs/PLATFORM.md)
- [Example deployments & judges](examples/deployments/README.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words
