# ADR-0017: Verified Run Portability and Comparison Cohorts

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 2026-07-23 |
| Deciders | Umair Ali (repository owner); Platform Module Editor |
| Scope | Cross-machine run transfer, workspace identity, and comparison discovery |

## Context

AIES runs are frequently produced on a different machine from the one used for
reporting and comparison. Manual archive extraction has produced
`runs/RUN/RUN/manifest.json` wrappers, disposable operating-system metadata,
and uncertainty about whether source evidence changed in transit. Comparison
also requires more than similar model names: task leaders are defensible only
when the assessment and Evidence Adapter protocols match.

## Decision

The platform provides a verified, non-overwriting run-import boundary:

1. `aies runs import DIRECTORY-OR-ZIP` accepts exactly one run manifest,
   validates its external identifier, bounds archive entry/file/total sizes,
   rejects absolute paths, traversal, drive paths, symlinks, duplicate
   case-folded paths, and unsupported path syntax, and excludes only declared
   disposable archive/cache metadata.
2. Every admitted file is inventoried by relative path, byte size, and SHA-256.
   A canonical package-tree digest binds the import plan and append-only
   receipt. The staged and final trees must match exactly.
3. An existing canonical run is never overwritten. An exact repeated import is
   idempotent; any missing, additional, or different file is a conflict.
4. A nested `RUN/RUN` source is normalized atomically. The original wrapper is
   retained under append-only `import-sources/`, while the verified inner
   package becomes canonical.
5. Import preserves admitted files byte-for-byte. It does not rescore,
   aggregate, validate claims, admit evidence, regenerate a qualification, or
   create authority. Presentation views may be regenerated later only through
   their existing renderer-owned commands.

The platform also exposes read-only cohort discovery. It groups aggregated
deployment runs by the same subject kind, risk tier, profile, suite versions,
task mapping, scoring semantics, rater protocol, repeat structure, and Evidence
Adapter profiles used by the ECM comparison gate. Cohorts larger than five are
expressed as connected two-to-five-run comparison batches with a stable anchor.

## Prohibited claims

- A valid package digest does not prove evidence truth, scoring quality, model
  quality, qualification, or safe deployment.
- Protocol compatibility does not prove run independence,
  representativeness, causal attribution, or a universal winner.
- Import receipts do not replace source provenance, environment fingerprints,
  retained rating records, or human qualification authority.
- Disposable archive metadata must never be counted as assessment evidence.

## Consequences

Cross-machine evidence becomes reproducible and inspectable without asking
users to hand-copy inner directories or risk overwriting a run. Existing
deployment-run layouts remain readable. The read-only API may expose import
receipts and compatible cohorts, but mutation remains CLI-only. Future signing,
remote object storage, organization portfolios, and composite-subject transfer
must build on this byte-bound receipt rather than weaken it.
