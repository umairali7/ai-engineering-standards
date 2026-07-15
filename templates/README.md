# Templates

| | |
|---|---|
| **Document ID** | AIES-TPL-00 |
| **Status** | Review |
| **Audience** | Contributors & maintainers |

Authoring templates for AIES documents. Using these templates is how new documents stay consistent with the [Documentation Standards (AIES-STD-00)](../docs/standards/README.md) — metadata tables, RFC 2119 normative language, requirement IDs, and the Draft → Review → Approved → Deprecated lifecycle.

## Catalog

| Template | Use For | Governed By |
|----------|---------|-------------|
| [STANDARD_TEMPLATE.md](STANDARD_TEMPLATE.md) | New standard documents in any module (AEBOK, AESQS, AEOS, AEAR, AECT, Shared) | [Document Standard (AIES-STD-01)](../docs/standards/document-standard.md), [Metadata Standard (AIES-STD-02)](../docs/standards/metadata-standard.md), [CONTRIBUTING.md](../CONTRIBUTING.md) |
| [ADR_TEMPLATE.md](ADR_TEMPLATE.md) | Architecture Decision Records for normative or structural changes | [adr/README.md](../adr/README.md), [GOVERNANCE.md](../GOVERNANCE.md) |

## How to Use

1. Copy the template into the target directory with the correct name (see the ID scheme in the [Metadata Standard (AIES-STD-02)](../docs/standards/metadata-standard.md), the structure rules in the [Document Standard (AIES-STD-01)](../docs/standards/document-standard.md), and, for ADRs, the numbering rules in [adr/README.md](../adr/README.md)).
2. Fill every section; the inline `<!-- ... -->` comments explain what each section requires. Delete the comments before submitting.
3. Replace every `<angle-bracket>` placeholder. A submitted document containing unresolved placeholders is returned to Draft.
4. Submit via pull request per [CONTRIBUTING.md](../CONTRIBUTING.md).

Planned additions (alongside the module drafting phases in [ROADMAP.md](../ROADMAP.md)): assessment record template (AESQS), lab specification template (AECT), blueprint template (AEAR).

## Related Documents

- [Documentation Standards (AIES-STD-00)](../docs/standards/README.md)
- [Document Standard (AIES-STD-01)](../docs/standards/document-standard.md)
- [Metadata Standard (AIES-STD-02)](../docs/standards/metadata-standard.md)
- [Architecture Decision Records (AIES-ADR-00)](../adr/README.md)
- [CONTRIBUTING.md (AIES-GOV-02)](../CONTRIBUTING.md)
- [GOVERNANCE.md (AIES-GOV-01)](../GOVERNANCE.md)

## References

None.
