# syntax=docker/dockerfile:1
FROM python:3.12-slim

ARG AIES_REVISION=uncommitted
LABEL org.opencontainers.image.title="AIES Engineering Assessment Platform" \
      org.opencontainers.image.description="Vendor-neutral engineering evidence, ECM, fit, and repository assessment" \
      org.opencontainers.image.source="https://github.com/umairali7/ai-engineering-standards" \
      org.opencontainers.image.revision="${AIES_REVISION}"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore \
    AIES_WORKSPACE=/workspace/aies-workspace

WORKDIR /opt/aies
COPY platform /opt/aies/platform
COPY conformance /opt/aies/conformance

RUN python -m pip install --no-cache-dir /opt/aies/platform \
    && useradd --create-home --uid 10001 aies \
    && mkdir -p /workspace/aies-workspace \
    && chown -R aies:aies /workspace

USER 10001
WORKDIR /workspace

ENTRYPOINT ["aies"]
CMD ["help"]
