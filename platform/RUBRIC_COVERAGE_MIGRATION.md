# Legacy scenario rubric-coverage migration

| Field | Value |
|---|---|
| Governing decision | ADR-0007 — Scenario Rubric Applicability Metadata |
| Migration status | Complete |
| Review authority | Umair Ali (repository owner) |
| Completion date | 2026-07-22 |
| Legacy warnings resolved | 124 |
| Resolution | Added explicit EV anchors; no warning was suppressed and no dimension was bulk-declared non-applicable |

## Review disposition

Each previously uncovered dimension was reviewed against its competency rubric
and scenario task family. The migration adds an affirmative scoring anchor for
the missing dimension because the six canonical EV dimensions remain meaningful
for these engineering responses. Scoring thresholds, gates, evidence minima,
autonomy limits, and prior run artifacts are unchanged.

| Scenario | Previously uncovered dimensions | Disposition |
|---|---|---|
| SC-CA01-001 | EV2, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA01-002 | EV4, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA01-003 | EV4, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA01-004 | EV2, EV4, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA01-005 | EV2, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA01-006 | EV3, EV6 | Added scenario-family-specific rubric anchor(s) |
| SC-CA01-007 | EV4, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA01-008 | EV2, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA01-009 | EV4, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA01-010 | EV4, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA01-017 | EV2 | Added scenario-family-specific rubric anchor(s) |
| SC-CA01-018 | EV2, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA01-019 | EV2 | Added scenario-family-specific rubric anchor(s) |
| SC-CA02-001 | EV4, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA02-002 | EV5, EV6 | Added scenario-family-specific rubric anchor(s) |
| SC-CA02-003 | EV4, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA02-004 | EV2, EV4, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA02-005 | EV4, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA02-006 | EV5, EV6 | Added scenario-family-specific rubric anchor(s) |
| SC-CA02-007 | EV4, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA02-008 | EV1, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA02-009 | EV4, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA02-010 | EV2, EV4, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA03-001 | EV3, EV4 | Added scenario-family-specific rubric anchor(s) |
| SC-CA03-002 | EV3, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA03-003 | EV2, EV4 | Added scenario-family-specific rubric anchor(s) |
| SC-CA03-004 | EV2, EV4, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA03-005 | EV3, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA03-006 | EV3, EV4 | Added scenario-family-specific rubric anchor(s) |
| SC-CA03-007 | EV1, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA03-008 | EV2, EV4 | Added scenario-family-specific rubric anchor(s) |
| SC-CA03-009 | EV3, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA03-010 | EV2, EV4, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA04-001 | EV3, EV4 | Added scenario-family-specific rubric anchor(s) |
| SC-CA04-002 | EV5, EV6 | Added scenario-family-specific rubric anchor(s) |
| SC-CA04-003 | EV1, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA04-004 | EV2, EV4, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA04-005 | EV3, EV4 | Added scenario-family-specific rubric anchor(s) |
| SC-CA04-006 | EV3, EV6 | Added scenario-family-specific rubric anchor(s) |
| SC-CA04-007 | EV3, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA04-008 | EV5, EV6 | Added scenario-family-specific rubric anchor(s) |
| SC-CA04-009 | EV3, EV4 | Added scenario-family-specific rubric anchor(s) |
| SC-CA04-010 | EV2, EV4, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA05-001 | EV4, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA05-002 | EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA05-003 | EV4, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA05-004 | EV2, EV4, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA05-005 | EV3, EV4, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA05-006 | EV2, EV3, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA05-007 | EV3, EV4, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA05-008 | EV3, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA05-009 | EV3, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA05-010 | EV2, EV4, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA06-001 | EV3, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA06-002 | EV4, EV6 | Added scenario-family-specific rubric anchor(s) |
| SC-CA06-003 | EV4, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA06-004 | EV2, EV4, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA06-005 | EV3, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA06-006 | EV3, EV6 | Added scenario-family-specific rubric anchor(s) |
| SC-CA06-007 | EV4, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA06-008 | EV3, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA06-009 | EV5, EV6 | Added scenario-family-specific rubric anchor(s) |
| SC-CA06-010 | EV4, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA07-002 | EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA07-003 | EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA07-004 | EV2, EV4, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA07-005 | EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA07-006 | EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA07-008 | EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA07-010 | EV2, EV4, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA07-017 | EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA07-020 | EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA08-001 | EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA08-002 | EV4 | Added scenario-family-specific rubric anchor(s) |
| SC-CA08-003 | EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA08-004 | EV2, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA08-005 | EV3 | Added scenario-family-specific rubric anchor(s) |
| SC-CA08-006 | EV3 | Added scenario-family-specific rubric anchor(s) |
| SC-CA08-007 | EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA08-008 | EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA08-009 | EV2, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA08-010 | EV4 | Added scenario-family-specific rubric anchor(s) |
| SC-CA09-001 | EV3, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA09-002 | EV2, EV4 | Added scenario-family-specific rubric anchor(s) |
| SC-CA09-003 | EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA09-004 | EV2, EV4 | Added scenario-family-specific rubric anchor(s) |
| SC-CA09-005 | EV3 | Added scenario-family-specific rubric anchor(s) |
| SC-CA09-006 | EV2, EV4 | Added scenario-family-specific rubric anchor(s) |
| SC-CA09-007 | EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA09-008 | EV2, EV4 | Added scenario-family-specific rubric anchor(s) |
| SC-CA09-009 | EV2, EV4 | Added scenario-family-specific rubric anchor(s) |
| SC-CA09-010 | EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA10-001 | EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA10-002 | EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA10-003 | EV2, EV4 | Added scenario-family-specific rubric anchor(s) |
| SC-CA10-004 | EV2, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA10-005 | EV4 | Added scenario-family-specific rubric anchor(s) |
| SC-CA10-006 | EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA10-007 | EV3, EV4 | Added scenario-family-specific rubric anchor(s) |
| SC-CA10-008 | EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA10-009 | EV2, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA10-010 | EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA11-001 | EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA11-002 | EV3, EV4 | Added scenario-family-specific rubric anchor(s) |
| SC-CA11-003 | EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA11-004 | EV2, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA11-005 | EV3, EV4 | Added scenario-family-specific rubric anchor(s) |
| SC-CA11-006 | EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA11-007 | EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA11-008 | EV3, EV4 | Added scenario-family-specific rubric anchor(s) |
| SC-CA11-009 | EV2, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA11-010 | EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA12-001 | EV3 | Added scenario-family-specific rubric anchor(s) |
| SC-CA12-002 | EV4, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA12-003 | EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA12-004 | EV2, EV4 | Added scenario-family-specific rubric anchor(s) |
| SC-CA12-005 | EV3, EV4 | Added scenario-family-specific rubric anchor(s) |
| SC-CA12-006 | EV3, EV4 | Added scenario-family-specific rubric anchor(s) |
| SC-CA12-007 | EV3 | Added scenario-family-specific rubric anchor(s) |
| SC-CA12-008 | EV4, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA12-009 | EV2, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA12-010 | EV2, EV4 | Added scenario-family-specific rubric anchor(s) |
| SC-CA12-017 | EV2, EV5 | Added scenario-family-specific rubric anchor(s) |
| SC-CA12-019 | EV5 | Added scenario-family-specific rubric anchor(s) |

## Verification

The aies suites validate command reports zero warnings, zero undeclared
omissions, and zero validation errors after this migration. Future omissions
remain visible unless they are covered by an explicit rubric anchor or a
reviewed rubric_applicability declaration with a concrete rationale.
