# Deployments — Qualify Deployments, Not Models

| | |
|---|---|
| **Document ID** | AIES-PLAT-03 |
| **Status** | Draft |
| **Audience** | Engineers · Platform teams · Assessors & qualification authorities |

The platform qualifies **deployments**, not bare models. This is design
decision **D11** in the [platform specification](../docs/PLATFORM.md), and it
is one of the load-bearing ideas of the whole project.

## Why not "the model"?

A model's behavior is not a property of the weights alone. The same checkpoint
answers differently at a different quantization, under a different runtime, with
different generation settings, on different hardware. "Is Qwen3.5 qualified as
an RT2 engineer?" is not answerable. **"Is *this deployment* qualified?"** is:

```
        deployment: local-qwen
              │
   ┌──────────┼───────────┬──────────────┐
   ▼          ▼           ▼              ▼
 runtime   quantization  endpoint      model
  MLX         Q6.5      localhost   Qwen3.5-122B-A10B
```

A deployment is the named tuple **model × runtime × config × endpoint**. It is
exactly the thing whose behavior the environment fingerprint captures — so
qualifying deployments is the [environment-as-provenance rule (D7)](../docs/PLATFORM.md)
made into a first-class object. Two ways of serving the same checkpoint are two
deployments and two separate qualification subjects, each with its own record.

This is the Docker mental model: an image (the model artifact) is not a running
container (the deployment). You qualify what actually runs.

## The registry chain

```
Registry  ──►  Deployments  ──►  Profiles  ──►  Qualifications
(what's      (model×runtime    (how to weigh   (the QUAL-… manifest:
 available)   ×config×endpoint)  the evaluation) a human-recorded grant)
```

- **Registry** holds deployment manifests (YAML). Ids are stable and never reused.
- **`aies discover`** populates it by probing installed runtimes — you rarely
  hand-author one for a local runtime on its default port.
- **`aies qualify <deployment> --profile <p>`** runs the pipeline; the human
  grant produces a **Qualification Record** (`QUAL-YYYY-NNN`) — the audit
  manifest that ties a scoped grant to the exact deployment and environment.

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
parameters_default:            # generation defaults for this deployment
  temperature: 0.6
  max_tokens: 32768
provenance:
  source: local MLX server
  checksum: sha256:…           # binds the deployment to an exact artifact
```

```
aies discover                       # auto-register what your runtimes serve
aies deployment list                # what is registered
aies deployment inspect local-qwen  # the full manifest
aies deployment add ./local-qwen.yaml
aies deployment retire local-qwen   # ids are retired, never deleted/reused
```

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

## Related Documents

- [Platform Specification (AIES-DOC-06) §5.1, D7, D11](../docs/PLATFORM.md)
- [Guide (AIES-PLAT-01)](GUIDE.md) — setup and a start-to-finish run
- [Profiles (AIES-PLAT-02)](PROFILES.md)
- [Revision & Revocation (AIES-AESQS-RR-01)](../AESQS/revision-and-revocation.md) — re-qualification triggers

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words
