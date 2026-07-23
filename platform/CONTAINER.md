# AIES Container Guide

| | |
|---|---|
| **Document ID** | AIES-PLAT-12 |
| **Status** | Draft |
| **Audience** | Engineers · Platform teams · CI maintainers |

The container provides a reproducible, non-root execution environment for the
offline demo, repository assessment, decision-engine conformance, and supported
networked assessment commands. It does not embed credentials or a model.

## Build

Use the repository root as the build context:

```bash
docker build \
  --file platform/Dockerfile \
  --build-arg AIES_REVISION="$(git rev-parse HEAD)" \
  --tag aies:local .
```

The Python base image supports normal `linux/amd64` and `linux/arm64`
builds. For a multi-architecture artifact:

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --file platform/Dockerfile \
  --build-arg AIES_REVISION="$(git rev-parse HEAD)" \
  --tag YOUR_REGISTRY/aies:VERSION \
  --push .
```

Pin the base-image digest and retain the OCI revision label for a published
release. A local unpinned build is development evidence, not release
provenance.

## Try the complete offline product

```bash
docker run --rm \
  --volume aies-workspace:/workspace/aies-workspace \
  aies:local demo --workspace /workspace/aies-workspace
```

No API key or network access is required after the image is built.

## Audit a repository

The source mount can remain read-only. A second mount retains generated CI
evidence:

```bash
mkdir -p aies-ci
docker run --rm \
  --volume "$PWD:/target:ro" \
  --volume "$PWD/aies-ci:/evidence" \
  aies:local ci audit /target --rt 2 --out /evidence
```

This is advisory by default. Add `--enforce` only when repository owners have
explicitly adopted the selected risk-tier policy.

## Verify decision semantics

```bash
docker run --rm aies:local \
  conform engine --corpus /opt/aies/conformance/corpus
```

## Run a networked assessment

Pass only the environment variable named by the deployment manifest and mount
the manifest/workspace deliberately:

```bash
docker run --rm \
  --network bridge \
  --env AIES_PROVIDER_KEY \
  --volume "$PWD/aies-workspace:/workspace/aies-workspace" \
  aies:local evaluate SUBJECT --judge REVIEWER --plan-only
```

Then remove `--plan-only` only after reviewing the call plan. Never bake keys,
`.env` files, raw run evidence, or host credentials into the image. Localhost
inside the container is the container itself; reach a host-served model through
the host gateway appropriate to the operating system.

## Ownership and cleanup

The image runs as non-root UID `10001`. Named volumes preserve evidence between
containers. Inspect and export required evidence before deleting a volume:

```bash
docker volume rm aies-workspace
```

Deletion is irreversible. Repository source mounted read-only is never changed
by `audit` or `ci audit`.
