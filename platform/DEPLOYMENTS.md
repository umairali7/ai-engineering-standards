# Deployments — Evaluate Deployments, Not Bare Models

| | |
|---|---|
| **Document ID** | AIES-PLAT-03 |
| **Status** | Draft |
| **Audience** | Engineers · Platform teams · Assessors & qualification authorities |

The platform evaluates **deployments**, not bare models. The same deployment
identity is used when formal qualification is explicitly requested. This is
[D11 — Qualify deployments, not bare models](../docs/PLATFORM.md) in the
platform specification and one of the load-bearing ideas of the project.

## Why not "the model"?

A model's behavior is not a property of the weights alone. The same checkpoint
answers differently at a different quantization, under a different runtime, with
different generation settings, on different hardware. "How capable is
Qwen3.5?" is not answerable without deployment context. **"What did this
deployment demonstrate under this scope?"** is:

```
        deployment: local-qwen
              │
   ┌──────────┼───────────┬──────────────┐
   ▼          ▼           ▼              ▼
 runtime   quantization  endpoint      model
  MLX         Q6.5      localhost   Qwen3.5-122B-A10B
```

A deployment is the named tuple **model × runtime × config × endpoint**. It is
exactly the thing whose behavior the environment fingerprint captures—so
evaluating deployments is the
[D7 — Environment as provenance](../docs/PLATFORM.md) rule made into a
first-class object. Two ways of serving the same checkpoint are two deployments
with separate evidence and, if invoked, separate formal qualification records.

This is the Docker mental model: an image (the model artifact) is not a running
container (the deployment). You qualify what actually runs.

## The registry chain

```
Registry  ──►  Deployments  ──►  Assessment scope  ──►  Evidence products
(what's      (model×runtime    (how to compose     (ECM, fit, reports,
 available)   ×config×endpoint)  and weight)         comparison)
```

- **Registry** holds deployment manifests (YAML). Ids are stable and never reused.
- **`aies discover`** populates it by probing installed runtimes — you rarely
  hand-author one for a local runtime on its default port.
- **`aies evaluate <deployment> --judge <reviewer>`** runs the default
  non-blocking engineering pipeline. An explicitly requested formal
  qualification can later produce a human-recorded **Qualification Record**
  (`QUAL-YYYY-NNN`) tied to the exact deployment and environment.

## The deployment manifest

```yaml
id: local-qwen                 # the deployment name you qualify; never reused
runtime: mlx                   # resolves to an installed runtime adapter
model: Qwen3.5-122B-A10B       # server-side model name (data — vendor names OK)
quantization: q6_k
runtime_config:
  base_url: http://localhost:8080/v1
  model: Qwen3.5-122B-A10B
context_window: 262144
roles: [subject]               # optional, advisory: how you use this deployment
                               #   (subject and/or judge). NOT the Taxonomy's
                               #   ROLE-01…14; surfaces in `aies judge available`.
parameters_default:            # generation defaults for this deployment
  temperature: 0.6
  max_tokens: 32768
planning:                      # optional, declared estimate inputs
  estimated_input_tokens_per_item: 1800
  estimated_output_tokens_per_item: 900
  input_usd_per_million_tokens: 0.20
  output_usd_per_million_tokens: 0.80
  estimated_seconds_per_request: 12
provenance:
  source: local MLX server
  checksum: sha256:…           # binds the deployment to an exact artifact
  signature:                   # optional: AI supply-chain provenance (declared,
    method: openssf-model-signing   #   verified externally like the checksum)
    reference: oms://…              #   — OpenSSF Model Signing / Sigstore ref
    verified: true
  ai_bom:                      # optional: AI bill-of-materials reference
    format: cyclonedx-1.7      #   (CycloneDX / SPDX 3.0), or a plain path/URI string
    reference: ./sbom/local-qwen.cdx.json
```

`planning` is optional and informational. `aies evaluate --plan-only` uses it
to estimate each sequential phase before any endpoint call:

- Token-based cost requires all four token and per-million-price fields shown
  above. As an alternative, declare `usd_per_request`; do not declare both
  pricing methods.
- `estimated_seconds_per_request` is combined with the requested
  `--parallel N` as concurrency waves. It is an operator declaration, not an
  observed SLA.
- Candidate requests are estimated one per distinct scenario. Judge requests
  use the configured batch size; token estimates remain per scored item.
- Missing declarations stay `unknown`. Retries, batch fallback, queueing,
  provider overhead, and variable output length can increase actual cost or
  duration.

The deterministic mock deployments declare zero request cost and a nominal
local duration so the offline planning path is demonstrable without suggesting
prices for real providers.

`signature` and `ai_bom` are **optional** and **declarative** — the platform
records them as provenance and surfaces them in `aies deployment inspect` and in
the durable evidence (run manifest → evidence package → Qualification Record),
so an audit trail is complete against the AI supply-chain standards
([CROSSWALK §3b](../docs/CROSSWALK.md)). Cryptographic verification is delegated
to the signer/registry, exactly as artifact `checksum` verification is.

```
aies discover                        # auto-register what your runtimes serve
aies deployment list                 # what is registered
aies deployment inspect local-qwen   # the full manifest
aies deployment add ./local-qwen.yaml    # register a NEW deployment
aies deployment update ./local-qwen.yaml # edit an EXISTING one in place (same id)
aies deployment retire local-qwen    # soft-mark; id stays reserved for audit
aies deployment remove local-qwen    # hard-delete; frees the id to reuse
aies deployment verify-artifact local-qwen --artifact ./model.safetensors
                                     # recompute SHA-256 vs the declared checksum
                                     #   (+ --pubkey/--signature to verify a signature)
```

`add` only registers new ids (it refuses an id that already exists). To fix a
manifest — a wrong endpoint, an `api_key_env` typo, changed generation defaults,
or adding `roles: [judge]` — use `update`, which overwrites the entry in place
and keeps the id. `update` warns when a field that defines the deployment's
behavioral identity (runtime, model, quantization, `runtime_config`) changed,
because prior qualifications for that id may no longer describe what now runs —
the environment fingerprint (D7) will flag it on `aies qualification verify`.
`remove` deletes an entry outright (freeing the id); `retire` is the softer,
audit-preserving path that keeps the id reserved.

When a bare model name maps to several deployments (e.g. the same model on MLX
*and* Ollama), the platform requires the deployment id or a `--runtime` filter —
it never guesses which one you meant.

## The Qualification Record is the audit manifest

Every human grant writes a `QUAL-YYYY-NNN` record binding, in one file:

```
qualification: QUAL-2026-001
subject:   deployment · model · runtime · checksum
scope:     profile · risk tier · per-area competency levels · AL envelopes
evidence:  run id · suite versions · environment fingerprint
humans:    authority (ROLE-13) · second (ROLE-14)
status:    active | conditional | denied | invalidated | revoked | superseded
```

`aies qualification history` lists these; `aies qualification verify QUAL-…`
re-checks the environment fingerprint and **invalidates** the grant if the
deployment's model, quantization, runtime, or host changed (D7). The record is
the durable, queryable audit trail — everything else references it.

## Judges are deployments too

A **judge** — the model that scores a run under `aies qualify --judge` — is not
a special kind of object. It is an ordinary deployment in this same registry,
and the subject and the judge are drawn from the same pool. Because a deployment
is `model × runtime × config × endpoint`, running the judge in the cloud, on
this machine, or on another machine on your network is **only a difference of
`base_url`** — the engine calls an endpoint and never learns where it lives.

Copy-paste manifests for all three are in
[`examples/deployments/`](examples/deployments/README.md). Register one with
`aies deployment add <file>` and pass it as `--judge <its-id>`. Prefer a
different, capable deployment over `--judge self` (a model grading its own
output is biased and warned against).

## Related Documents

- [AIES-DOC-06 — Engineering Assessment Platform Specification](../docs/PLATFORM.md)
- [AIES-PLAT-01 — AIES Platform — Architecture & Run Guide](GUIDE.md) — setup and a start-to-finish run
- [AIES-PLAT-02 — Qualification Profiles](PROFILES.md)
- [Revision & Revocation (AIES-AESQS-RR-01 — Revision and Revocation)](../AESQS/revision-and-revocation.md) — re-qualification triggers

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words
