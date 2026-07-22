# Runtimes — the Runtime Interface

| | |
|---|---|
| **Document ID** | AIES-PLAT-04 |
| **Status** | Draft |
| **Audience** | Engineers · Platform teams · Contributors & maintainers |

A **runtime adapter** is the only component that talks to a model. Everything
else in the platform — the engine, scoring, review, reporting — is
runtime-agnostic. This is the abstraction that lets `aies` qualify a model on
MLX today and the same model on a hosted API tomorrow without changing one line
of the engine (PLATFORM.md §8, design decision D9).

```
   Qualification Engine
          │
          ▼
   Runtime Interface        ← the four-operation contract below (frozen v1.0)
          │
   ┌──────┼─────────┬──────────┬──────────┬───────────┐
   ▼      ▼         ▼          ▼          ▼           ▼
 mock  openai-   ollama   lmstudio   llamacpp      mlx     + any out-of-tree
       compat                                              adapter (entry point)
```

## The interface (contract v1.0)

An adapter subclasses `aies.adapters.base.RuntimeAdapter` and implements four
required operations plus two optional discovery hooks:

| Operation | Required | Contract |
|-----------|----------|----------|
| `load(registry_entry)` | yes | attach the model named by the deployment; verify its checksum; fail loudly on mismatch |
| `generate(request) → response` | yes | run exactly one inference call; return raw text + usage; no retries the Test Runner did not order |
| `capabilities() → dict` | yes | declare modalities, tool/function calling, structured output, streaming, max context |
| `fingerprint() → dict` | yes | the runtime component of the environment fingerprint: id, version, device, settings |
| `probe_runtime() → dict` | optional | class method; is this runtime present? `{available, version, detail}` — best-effort, never raises. Powers `aies doctor` / `aies runtime list` |
| `discover_deployments() → list` | optional | class method; what does this runtime serve right now? Powers `aies discover` |

Class attributes: `adapter_id`, `adapter_version`, `contract_version` (target
the major of `ADAPTER_CONTRACT_VERSION`), and — for endpoint runtimes —
`RUNTIME_ENV` (the override env var) and `RUNTIME_DEFAULT` (the conventional
endpoint).

## Shipped adapters

| Runtime | id | Endpoint env var | Conventional default | Notes |
|---------|-----|------------------|----------------------|-------|
| Mock | `mock` | — | — | deterministic, offline; for trying the tool |
| Generic OpenAI-compatible | `openai-compat` | `AIES_OPENAI_BASE_URL` | *(none)* | any server/host speaking the chat-completions format |
| Ollama | `ollama` | `AIES_OLLAMA_BASE_URL` | `http://localhost:11434/v1` | |
| LM Studio | `lmstudio` | `AIES_LMSTUDIO_BASE_URL` | `http://localhost:1234/v1` | |
| llama.cpp (`llama-server`) | `llamacpp` | `AIES_LLAMACPP_BASE_URL` | `http://localhost:8080/v1` | |
| MLX / oMLX (`mlx_lm.server`) | `mlx` | `AIES_MLX_BASE_URL` | `http://localhost:8080/v1` | Apple Silicon |

The four named local runtimes all speak the OpenAI-compatible wire format, so
they share the HTTP logic of the generic adapter and differ only in their
conventional default endpoint and override env var — the runtime facts that
legitimately belong to an adapter (D9). A conventional default port is *not*
hard-coded configuration: it is the adapter's knowledge of its target, and it
is always overridable via the env var or a deployment manifest.

> llama.cpp and MLX both conventionally serve on `:8080`. If you run both, set
> `AIES_LLAMACPP_BASE_URL` / `AIES_MLX_BASE_URL` explicitly so `discover`
> attributes each served model to the right runtime.

## Inspecting runtimes

```
aies doctor                 # environment + which runtimes are up
aies runtime list           # every adapter, its contract version, availability
aies runtime inspect ollama # capabilities, endpoint env var, and models served now
aies discover               # register what the available runtimes serve
```

## Adding a runtime (out-of-tree, no core change)

Write an adapter against the contract, register it via an entry point, and it
appears in `aies runtime list` / `aies plugins` with no edit to the core engine —
the M3 exit criterion. A complete worked example is in
[examples/external_adapter/](examples/external_adapter/README.md):

```toml
# in your adapter package's pyproject.toml
[project.entry-points."aies.adapters"]
myruntime = "my_pkg:MyAdapter"
```

If your runtime already exposes an OpenAI-compatible endpoint, you often need no
new adapter at all — point the generic `openai-compat` adapter at it via
`AIES_OPENAI_BASE_URL` or a deployment's `runtime_config.base_url`. Write a
dedicated adapter when the runtime needs native discovery, a non-standard wire
format, or in-process loading.

## Related Documents

- [AIES-DOC-06 — Engineering Assessment Platform Specification](../docs/PLATFORM.md) — the plugin contract
- [AIES-PLAT-03 — Deployments — Qualify Deployments, Not Models](DEPLOYMENTS.md) — what an adapter serves
- [AIES-PLAT-01 — AIES Platform — Architecture & Run Guide](GUIDE.md) · [external adapter example](examples/external_adapter/README.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words
