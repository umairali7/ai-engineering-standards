# Shared Standards

| | |
|---|---|
| **Document ID** | AIES-SHARED-00 |
| **Status** | Review |
| **Audience** | All readers |

The Shared Standards hold the **canonical vocabulary** of AIES: the terms and classification systems that AEBOK, AESQS, AEOS, AEAR, and AECT all build on, defined once so the modules never redefine the same concept differently. Documentation conventions — metadata tables, identifiers, normative language, lifecycle, diagrams — are defined in the [Documentation Standards (AIES-STD-00)](../docs/standards/README.md).

## Contents

| Document | Purpose |
|----------|---------|
| [Glossary (AIES-SHARED-01)](Glossary/README.md) | Canonical definitions of every term used across AIES |
| [Taxonomy (AIES-SHARED-02)](Taxonomy/README.md) | Canonical classification systems: SDLC phases, autonomy levels, risk tiers, roles, competency levels, artifact types |

## Relationship to Modules

```
                 ┌────────────────────────────┐
                 │      Shared Standards      │
                 │    Glossary · Taxonomy     │
                 └─────────────┬──────────────┘
        ┌──────────┬───────────┼───────────┬──────────┐
        ▼          ▼           ▼           ▼          ▼
     AEBOK      AESQS        AEOS        AEAR       AECT
   (knowledge) (qualify)   (operate)  (architect) (certify)
```

A change to a shared definition is a **breaking change** for every module and MUST be handled through an ADR (see [adr/](../adr/README.md)).

## Related Documents

- [Glossary (AIES-SHARED-01)](Glossary/README.md)
- [Taxonomy (AIES-SHARED-02)](Taxonomy/README.md)
- [Documentation Standards (AIES-STD-00)](../docs/standards/README.md)
- [GOVERNANCE.md (AIES-GOV-01)](../GOVERNANCE.md)
- [Architecture Decision Records (AIES-ADR-00)](../adr/README.md)

## References

None.
