# Example: an out-of-tree runtime adapter

This directory shows that a runtime adapter can be written and shipped
**outside** the `aies` package, against the published contract, with no
change to the core engine (PLATFORM.md §8, M3 exit criterion).

## The contract (version 1.0)

A runtime adapter subclasses `aies.adapters.base.RuntimeAdapter` and
implements four required operations plus two optional ones:

| Operation | Required | Purpose |
|-----------|----------|---------|
| `load(registry_entry)` | yes | attach the model; verify checksum |
| `generate(request) -> response` | yes | one inference call, no unrequested retries |
| `capabilities() -> dict` | yes | declare modalities, tool/function calling, context |
| `fingerprint() -> dict` | yes | runtime component of the environment fingerprint |
| `probe_runtime() -> dict` | optional | detect the runtime for `aies doctor` |
| `discover_deployments() -> list` | optional | enumerate deployments for `aies discover` |

Set `adapter_id`, `adapter_version`, and `contract_version` (target the
major of `ADAPTER_CONTRACT_VERSION`).

## Registering it

In your external package's `pyproject.toml`:

```toml
[project.entry-points."aies.adapters"]
reverse = "aies_reverse_adapter:ReverseAdapter"
```

After `pip install`, with no edit to `aies` itself:

```
aies plugins                 # lists "reverse"
aies discover                # registers reverse-* deployments
aies qualify reverse-demo --profile research --rt 1
```

`aies_reverse_adapter.py` here is a complete, working example (it echoes
the prompt reversed — deliberately trivial so the example is about the
contract, not the model). The platform's own `mock` and `openai-compat`
adapters implement the same contract.
