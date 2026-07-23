# Example deployment manifests

A **deployment** is what AIES qualifies: `model × runtime × config × endpoint`
(design decision D11). A **judge** is just a deployment you pass to
`aies qualify --judge`. Nothing about a deployment marks it as a judge — the
subject and the judge are drawn from the same registry, and any deployment can
play either role.

## The three ways to run a judge

| File | Where the judge runs | The only thing that changes |
|---|---|---|
| [`judge-cloud-frontier.yaml`](judge-cloud-frontier.yaml) | A hosted frontier model (OpenAI, DeepSeek, Together, …) | `base_url` = provider URL + an API key env var |
| [`judge-local.yaml`](judge-local.yaml) | A second model on **this** machine | `base_url` = `http://localhost:<port>/v1` |
| [`judge-remote-machine.yaml`](judge-remote-machine.yaml) | A model on **another** machine on your network | `base_url` = `http://<that-ip>:<port>/v1` |

"Cloud vs local vs another machine" is entirely the `base_url`. The engine calls
an endpoint; it never knows or cares where that endpoint lives.

## Ready-made frontier judges

Drop-in manifests for common hosted frontier models, already tagged
`roles: [judge]` (so they appear in `aies judge available`). Add the ones you
have keys for and pass the id to `--judge`.

| File | Model | Endpoint |
|---|---|---|
| [`claude-opus-4-8-native.yaml`](claude-opus-4-8-native.yaml) | `claude-opus-4-8` | `https://api.anthropic.com/v1` |
| [`claude-sonnet-5-native.yaml`](claude-sonnet-5-native.yaml) | `claude-sonnet-5` | `https://api.anthropic.com/v1` |
| [`claude-fable-5-native.yaml`](claude-fable-5-native.yaml) | `claude-fable-5` | `https://api.anthropic.com/v1` |
| [`gpt-5-6-sol-native.yaml`](gpt-5-6-sol-native.yaml) | `gpt-5.6-sol` | `https://api.openai.com/v1` |
| [`gpt-5-6-terra-native.yaml`](gpt-5-6-terra-native.yaml) | `gpt-5.6-terra` | `https://api.openai.com/v1` |
| [`gpt-5-6-luna-native.yaml`](gpt-5-6-luna-native.yaml) | `gpt-5.6-luna` | `https://api.openai.com/v1` |

> **Anthropic wire format.** The Claude manifests target Anthropic's
> **OpenAI-compatibility** base (`https://api.anthropic.com/v1`), which the
> built-in `openai-compat` adapter can drive. Anthropic's *native* Messages API
> is a different wire format — to use that directly you'd write a dedicated
> adapter (D9), not the generic `openai-compat` one. Set `ANTHROPIC_API_KEY`
> (Claude) or `OPENAI_API_KEY` (GPT) before use. `context_window` values in these
> files are unverified claims recorded until discovery probes the endpoint.

## Register and use

```bash
# 1. register the judge once (id must be unique and is never reused)
aies deployment add examples/deployments/judge-cloud-frontier.yaml

# 2. (cloud only) provide the key named in the manifest
export OPENAI_API_KEY=sk-...

# 3. qualify a subject and let the judge score it — both phases run
#    concurrently at --parallel N (collection AND judge scoring)
aies qualify local-qwen --rt 2 --judge judge-cloud-frontier --parallel 8
```

The three judge modes at a glance:

- `--judge self` — the subject scores its own output. Cheapest; prints a
  self-judging **WARNING** (expect inflation). Fine for a smoke test.
- `--judge <a different deployment>` — recommended. A stronger, independent
  model grades the subject.
- omit `--judge` — collect responses only, then score by hand
  (`aies score`) or read them with `aies transcript <run>`.

## What the judge's scores mean

`qualify --judge` records the judge's scores as **model-kind ratings** and
stamps the report **JUDGE-PRODUCED** — fast, automated *evidence*. It is **not**
a grant and does **not** by itself establish that the judge is trustworthy. The
formal **calibration gate** (a judge must agree with human anchor scores before
its ratings are admitted) lives in the `aies review` flow. A revocable grant is
always a separate, human act: `aies grant <run> …`.

## Earmarking a judge (`roles: [judge]`)

Each manifest here carries `roles: [judge]` — an **advisory** tag saying "I keep
this deployment around to use as a judge." It changes nothing about how the
deployment runs (any deployment can still be qualified, and any can be passed to
`--judge` whether tagged or not); it only lets you see your judge **pool**:

```bash
aies judge available     # counts + lists every deployment tagged roles:[judge],
                         #   each annotated with its track record or "never used"
```

`roles` accepts `subject` and/or `judge`. It is unrelated to the organizational
roles (ROLE-01…14) in the Shared Taxonomy — these are deployment usage tags.

## Notes

- **Wire format.** The built-in `openai-compat` adapter speaks the OpenAI
  chat/completions format, which most hosted providers and local runtimes
  (vLLM, Ollama, LM Studio, llama.cpp, MLX, TGI) expose. A native API with a
  different shape needs its own out-of-tree adapter — see
  [`../external_adapter/`](../external_adapter/) (design decision D9: vendor code
  lives only in adapters).
- **Keys.** Name the key's env var with `runtime_config.api_key_env`; the value
  never goes in the manifest. LAN servers usually need none.
- **Planning.** To make `aies evaluate --plan-only` estimate rather than report
  unknown cost/ETA, add the optional validated `planning` declarations
  documented in [`DEPLOYMENTS.md`](../../DEPLOYMENTS.md). Keep provider prices
  and measured endpoint speed current; they are operator assumptions, not
  guarantees.
- **`checksum: sha256:endpoint-served`** is the convention for a remotely served
  artifact — the server owns artifact verification, and the deployment's
  identity is pinned by its environment fingerprint (D7).
