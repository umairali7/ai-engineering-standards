# Experimental Evidence Adapter Contract v1

Status: Experimental implementation contract, governed by accepted ADR-0015.

An adapter declares its source format and version, adapter profile and version,
accepted evidence modalities, privacy behavior, and deterministic duplicate
identity. Every conversion returns typed events plus a loss report containing
the source digest, counts seen/imported/skipped, reasons for every skip,
unrepresented fields, and any correlation gaps.

Adapters must not infer missing scores, silently change units, treat repeats or
reimports as new breadth, copy secrets, or elevate findings to correctness,
conformance, qualification, or authorization. Unknown remains unknown.

An adapter that knows why applicable evidence is absent may emit a typed
`collection-gap` event. Its condition is exactly one of `not-collected`,
`unavailable`, `tool-not-installed`, `redacted`, `failed-to-collect`, `stale`,
or `conflicting`, and its payload identifies the governed perspective cell and
a human-readable detail. A gap event is metadata about missing or compromised
collection; it is never direct evidence and can never fill a coverage cell.

Duplicate identity is the tuple `(source_digest, source_record_id,
adapter_profile)`. Major schema incompatibility is an error. Minor additions
must be preserved under `extensions` or disclosed as loss. An adapter fixture
must prove deterministic output, duplicate rejection, source hash binding,
malformed-input rejection, and no-claim inflation.

The shipped `aies-inspect-eval-log/v1` profile imports only explicit integer
AIES ratings from EV1 — Correctness through EV6 — Traceability and may inform
Engineering Evaluation and ECM products.
The shipped `aies-sarif-2.1.0/v1` profile preserves static-analysis findings as
informational repository observations and cannot establish an EV score,
maturity level, correctness, conformance, qualification, or authorization.
Both declare secrets prohibited and emit a source-bound loss report.

The shipped `aies-repository-conformance/v1` profile preserves verified,
asserted, and gap practice evidence for ML0 — Absent through ML4 — Optimizing
repository maturity only. The shipped
`aies-repository-analysis/v1` profile observes bounded source structure and
retained JUnit, coverage, SARIF, Ruff/ESLint JSON, CycloneDX/SPDX JSON,
dependency, policy, and configuration artifacts. Its perspective metrics,
confidence, findings, and remediation are informational; none are converted
into AIES evaluation-dimension scores, correctness, security, conformance,
qualification, or authorization.
