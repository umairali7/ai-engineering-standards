# Example deployment manifests

A **deployment** is the named `model × runtime × config × endpoint` tuple that
AIES evaluates. This is [D11 — Qualify deployments, not bare models](../../../docs/PLATFORM.md):
the same weights served with another runtime, quantization, configuration, or
endpoint are a different subject with different evidence.

The files here are editable examples, not verified claims about a model,
provider, context window, endpoint, or artifact. Inspect every value before
registration. A manifest stores only the *name* of a credential environment
variable; never put an API key in YAML.

## Fastest setup

From `platform/`, first let AIES look for reachable supported local runtimes:

```bash
aies doctor
aies discover
aies deployment list
aies deployment inspect DEPLOYMENT_ID
```

If discovery does not find the endpoint, choose one of two safe paths.

### Generate a manifest

This writes a valid starter without a credential and prints the exact
workspace and registration commands for the current shell:

```bash
aies init aies-workspace --starter deployment --deployment-id local-coder --model served-model-id --endpoint http://127.0.0.1:1234/v1 --api-key-env AIES_OPENAI_API_KEY --role subject
```

Use `aies init --guided` for prompts instead. The generated
`deployment.example.yaml` is deliberately separate from the registry so it can
be reviewed before `aies deployment add` mutates the workspace.

### Adapt an example

Copy the nearest template, verify its `id`, `model`, `base_url`,
`context_window`, role, and provenance, then register it:

```bash
aies deployment add examples/deployments/local-qwen3-coder-next-8b.yaml
aies deployment inspect local-qwen3-coder-next-8bit
```

`add` is new-ID only. Use `aies deployment update FILE` after intentionally
changing an existing deployment, `retire ID` to preserve its audit identity,
or `remove ID` only when that identity can safely be discarded.

## Local OpenAI-compatible examples

These examples default to `http://localhost:8000/v1`. They work only when the
declared model is actually served there through the OpenAI chat-completions
wire format. The role is advisory: `subject` appears as an evaluation target;
`judge` appears in `aies judge available`. It does not technically prevent the
deployment being used in the other position.

| File | Registry ID | Intended role |
|---|---|---|
| [`local-gemma-4-12B-it-8bit.yaml`](local-gemma-4-12B-it-8bit.yaml) | `local-gemma-4-12b-it-8bit` | Subject |
| [`local-gemma-4-26b-a4b-it-8bit.yaml`](local-gemma-4-26b-a4b-it-8bit.yaml) | `local-gemma-4-26b-a4b-it-8bit` | Subject |
| [`local-ornith-oq8.yaml`](local-ornith-oq8.yaml) | `local-ornith-oq8` | Subject |
| [`local-qwen3-coder-next-6bit.yaml`](local-qwen3-coder-next-6bit.yaml) | `local-qwen3-coder-next-6bit` | Subject |
| [`local-qwen3-coder-next-8b.yaml`](local-qwen3-coder-next-8b.yaml) | `local-qwen3-coder-next-8bit` | Subject |
| [`local-qwen3.6-27B-oQ8-fp16-mtp.yaml`](local-qwen3.6-27B-oQ8-fp16-mtp.yaml) | `local-qwen36-27b-oq8-fp16-mtp` | Subject |
| [`local-qwen3.6-35B-A3B-oQ8-fp16.yaml`](local-qwen3.6-35B-A3B-oQ8-fp16.yaml) | `local-qwen3.6-35b-a3b-oq8-fp16-mtp` | Subject |
| [`local-Qwopus3.6-35B-A3B-v1-oQ8-mtp.yaml`](local-Qwopus3.6-35B-A3B-v1-oQ8-mtp.yaml) | `local-qwopus3.6-35b-a3b-v1-oq8-mtp` | Subject |
| [`local-gpt-oss-120b-mlx-8Bit.yaml`](local-gpt-oss-120b-mlx-8Bit.yaml) | `local-gpt-oss-120b-mlx-8bit` | Judge |
| [`local-Qwen3-5-122B-A10B-LM-MLX-Q6-5.yaml`](local-Qwen3-5-122B-A10B-LM-MLX-Q6-5.yaml) | `local-qwen3.5-122b-a10b-lm-mlx-q6.5` | Judge |
| [`local-qwen35-122b-6bit.yaml`](local-qwen35-122b-6bit.yaml) | `qwen3.5-122b-6bit` | Judge |

The intended role documents this example set; it is not a claim that model
size makes a reviewer trustworthy. Reviewer identity, protocol, parse rate,
calibration, and agreement evidence remain visible in AIES outputs.

## Hosted and remote reviewer patterns

| File | Where it runs | Configuration difference |
|---|---|---|
| [`judge-cloud-frontier.yaml`](judge-cloud-frontier.yaml) | Hosted provider | Provider `base_url` plus `api_key_env` |
| [`judge-local.yaml`](judge-local.yaml) | This machine | Loopback `base_url` |
| [`judge-remote-machine.yaml`](judge-remote-machine.yaml) | Another machine on the network | Reachable LAN `base_url` |

Ready-made hosted reviewer manifests are also provided for the model IDs named
in the following files. Provider availability, names, prices, and context
limits can change; verify them with the provider before use.

| File | Credential variable |
|---|---|
| [`claude-opus-4-8-native.yaml`](claude-opus-4-8-native.yaml) | `ANTHROPIC_API_KEY` |
| [`claude-sonnet-5-native.yaml`](claude-sonnet-5-native.yaml) | `ANTHROPIC_API_KEY` |
| [`claude-fable-5-native.yaml`](claude-fable-5-native.yaml) | `ANTHROPIC_API_KEY` |
| [`gpt-5-6-sol-native.yaml`](gpt-5-6-sol-native.yaml) | `OPENAI_API_KEY` |
| [`gpt-5-6-terra-native.yaml`](gpt-5-6-terra-native.yaml) | `OPENAI_API_KEY` |
| [`gpt-5-6-luna-native.yaml`](gpt-5-6-luna-native.yaml) | `OPENAI_API_KEY` |

The Claude examples use Anthropic's OpenAI-compatibility endpoint, not its
native Messages wire format. A native API with a different shape needs a
dedicated runtime adapter.

## Plan, evaluate, and inspect

Register a separate reviewer where possible, then inspect the call plan before
executing it:

```bash
aies deployment list
aies judge available
aies evaluate SUBJECT_ID --judge REVIEWER_ID --plan-only --parallel 4
aies evaluate SUBJECT_ID --judge REVIEWER_ID --parallel 4
aies snapshot latest
aies open latest
```

`--judge self` is available for a smoke test and emits a self-review warning.
Omitting `--judge` collects responses for later automated or optional human
review. Automated ratings complete the informational Engineering Evaluation;
they do not create a qualification grant or deployment authority.

## Manifest guidance

- **Wire format:** the built-in `openai-compat` adapter speaks the OpenAI
  chat-completions format exposed by many local and hosted runtimes.
- **Secrets:** use `runtime_config.api_key_env`; never store the value in the
  manifest. A local endpoint may not need a credential.
- **Planning:** optional `planning` declarations let `--plan-only` estimate
  cost and duration. Missing values remain unknown rather than invented.
- **Identity:** `sha256:endpoint-served` means artifact verification belongs to
  the server; the run still records the deployment and environment identity.
- **Reviewers:** prefer a different deployment from the subject. A role tag is
  organization, not reviewer qualification or calibration evidence.

See [AIES-PLAT-03 — Deployments](../../DEPLOYMENTS.md) for every field and
lifecycle command, [AIES-PLAT-01 — Architecture & Run Guide](../../GUIDE.md)
for an end-to-end run, and the
[out-of-tree adapter example](../external_adapter/README.md) for another wire
format.
