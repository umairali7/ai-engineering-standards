# Blueprint: Oil & Gas

| | |
|---|---|
| **Document ID** | AIES-AEAR-BP-OILGAS |
| **Status** | Review |
| **Audience** | Architects · Platform teams · Engineering leadership |

Adaptation of the [Core Reference Architecture (AIES-AEAR-CORE-01)](../core-reference-architecture.md) for upstream, midstream, and downstream oil and gas operators. Assumes the [Enterprise Platform blueprint](enterprise-platform.md) as baseline; the OT-boundary discipline of the [Manufacturing blueprint](manufacturing.md) applies wholesale to process-control environments and is not repeated here — this blueprint adds what is distinct to the sector.

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Industry Context

- **HSE criticality** — health, safety, and environment is the sector's governing discipline. Process-safety regimes (safety-case regulation, process safety management rules) and functional-safety standards govern safety-instrumented functions, emergency shutdown, and fire-and-gas systems; a software defect can contribute to loss of containment, with catastrophic human and environmental consequences and license-to-operate exposure.
- **Field operations with intermittent connectivity** — offshore platforms, remote wellsites, and pipeline stations operate over satellite or constrained links, with periods of full disconnection. Engineering support for field systems cannot assume the platform is reachable, and autonomy that depends on live oversight must degrade when oversight cannot be delivered.
- **Legacy SCADA adjacency** — decades-old SCADA, telemetry, and pipeline-control estates sit next to modern IT. Much of the engineering work is *adjacent* to these systems (historians, alarm management, leak-detection analytics) where the systems themselves cannot be changed safely by anyone but their maintainers.
- **Joint ventures and data segregation** — assets are commonly co-owned and co-operated under joint-venture (JV) agreements with strict data-sharing boundaries; seismic surveys, reservoir models, and production data are competitively and contractually sensitive per venture. Antitrust and license terms make cross-venture leakage a legal problem, not just a commercial one.
- **Trading and regulatory reporting adjacency** — commodity trading systems and environmental/regulatory reporting (emissions, flaring, production allocations) carry financial-market and regulator-facing accuracy obligations.

## 2. Risk-Tier Profile

Typical defaults; per [AIES-AEAR-BP-00-R01](README.md), validate locally against the operator's HSE risk assessment.

| Task type | Typical tier | Rationale | Default max AL |
|-----------|-------------|-----------|----------------|
| Corporate IT, docs, test scaffolding, analytics prototypes | RT1–RT2 | Standard blast radius | AL3–AL4 |
| Production-data and historian pipelines | RT3 | Allocation, royalty, and reporting accuracy | AL2 |
| Leak-detection, alarm-management, and pipeline-monitoring analytics | RT3–RT4 | Degradation masks hazardous conditions | AL2 → AL1 |
| SCADA-adjacent integration code (telemetry ingestion, control-room displays) | RT4 | Operator situational awareness; OT adjacency | AL1 |
| **Safety-instrumented functions, ESD, fire-and-gas logic** | **RT4, non-negotiable** | Safety-critical ([Taxonomy §4](../../Shared/Taxonomy/README.md#4-risk-tiers-rt1rt4)); functional-safety regime owns the change discipline | AL1, no risk-acceptance path |
| Emissions/regulatory reporting and production allocation | RT4 | Misstatement to a regulator or JV partner | AL1 |
| Trading-system order and position logic | RT4 | Financial transactions ([AIES-AEAR-CORE-01-R29]) | AL1 |

[AIES-AEAR-BP-OILGAS-R01] Engineering tasks on safety-instrumented functions, emergency-shutdown, or fire-and-gas systems MUST be classified RT4 and capped at AL1, with no risk-acceptance relaxation (mirroring [AIES-AEAR-BP-MANUFACTURING-R01]); AI participation is limited to analysis and suggestion feeding qualified functional-safety personnel.

[AIES-AEAR-BP-OILGAS-R02] Tasks on systems whose degradation would reduce detection of hazardous conditions (leak detection, gas detection analytics, alarm management) MUST be tiered RT4 even though they do not actuate anything, because their failure mode is silent.

## 3. Architecture Deltas from the Core

| Plane | Oil & gas delta |
|-------|-----------------|
| Interaction | Approval consoles show asset operational state (producing, turnaround, shut-in) and permit-to-work linkage for changes touching site systems |
| Orchestration | Field-site tasks carry a **connectivity class**; workflows requiring AL3 checkpoints or live oversight MUST NOT be scheduled onto assets in degraded-connectivity states — autonomy falls to the level the available oversight supports ([AIES-AEAR-BP-OILGAS-R03], applying core principle 6) |
| Model | Hybrid topology: corporate estates use gateway-routed external or internal serving; offshore/remote sites needing local assistance run site-local model deployments under air-gapped rules ([AIES-AEAR-CORE-01-R51]), with queued sync of telemetry and audit records on reconnection |
| Context & Knowledge | Knowledge stores are **JV-partitioned**: seismic, reservoir, and production data carry venture tags, and retrieval enforces venture entitlement exactly as tenant isolation ([AIES-AEAR-CORE-01-R49] applied per JV) ([AIES-AEAR-BP-OILGAS-R04]). Safety-case and HAZOP records are retrieval-restricted to authorized safety tasks |
| Execution | No sandbox reachability into process-control networks (per Manufacturing [AIES-AEAR-BP-MANUFACTURING-R03]); SCADA-adjacent changes verify against replayed historian data and simulators, never live telemetry paths |
| Guardrail | See §4 |
| Observability | ART-15 records for site-affecting changes reference the permit-to-work and MoC identifiers; audit sync from disconnected sites is integrity-verified on arrival |
| Governance | Agent entitlements are asset- and venture-scoped; JV audit rights extend to platform evidence for jointly owned assets |

## 4. Domain-Specific Guardrails

- **Safety-system write lock** — agent-produced artifacts cannot reach SIS, ESD, or fire-and-gas toolchains through any platform pathway; the designation list is owned by ROLE-14 with HSE-authority sign-off.
- **JV segregation filter** — retrieval and context assembly deny cross-venture data mixing; a single task cannot hold context tagged to two ventures unless both entitlements are explicit and logged.
- **Detection-integrity gate** — changes to leak/gas-detection or alarm logic require attached evidence that detection sensitivity is non-degraded (replay-based regression) before the RT4 gate opens.
- **Connectivity-aware envelope reduction** — loss of oversight connectivity to a site automatically reduces in-flight autonomy on that site's tasks (AL3 → AL2 → hold), never continues unobserved ([AIES-AEAR-CORE-01-R59]).
- **Regulatory-figure control** — emissions, flaring, and allocation figures in agent-produced reports require a human gate by the accountable reporting role.
- **Turnaround freeze** — orchestration holds non-essential changes for assets in turnaround, startup, or emergency-response states.

## 5. Example Use Cases

| Use case | Phases | Typical RT | Typical AL |
|----------|--------|-----------|------------|
| Documentation reconstruction of a legacy SCADA telemetry protocol (read-only) | P15, X08 | RT1 | AL4 with spot audit |
| Test generation for a production-allocation service | P10 | RT2 | AL3 |
| Historian-to-analytics pipeline refactor | P09 | RT3 | AL2 |
| Alarm-rationalization analysis support | P06, P15 | RT3 | AL2 (analysis only) |
| Leak-detection threshold logic change | P09 | RT4 | AL1 with detection-integrity evidence |
| ESD logic modification support | P09 | RT4 | AL1 only — suggestion to functional-safety engineer |
| Emissions-reporting field-mapping change | P09 | RT4 | AL1 with reporting-role gate |

---

## Related Documents

- [AIES-AEAR-BP-00 — Blueprint Catalog](README.md) · [AIES-AEAR-BP-MANUFACTURING — Manufacturing](manufacturing.md) · [AIES-AEAR-BP-ENTERPRISE — Enterprise Platform](enterprise-platform.md) · [AIES-AEAR-CORE-01 — Core Reference Architecture](../core-reference-architecture.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words
