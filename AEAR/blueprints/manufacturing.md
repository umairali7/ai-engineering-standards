# Blueprint: Manufacturing

| | |
|---|---|
| **Document ID** | AIES-AEAR-BP-MANUFACTURING |
| **Status** | Review |
| **Audience** | Architects · Platform teams · Engineering leadership |

Adaptation of the [Core Reference Architecture (AIES-AEAR-CORE-01 — Core Reference Architecture)](../core-reference-architecture.md) for discrete and process manufacturers. Assumes the [Enterprise Platform blueprint](enterprise-platform.md) as baseline and adds the constraints of the operational-technology (OT) estate: physical consequence, safety-instrumented systems, and plant floors that were never designed for cloud connectivity.

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Industry Context

Manufacturing software spans two worlds with different failure semantics: IT systems fail into data problems; OT systems fail into physical ones. The constraints that shape the architecture:

- **The OT/IT boundary** — industrial security frameworks (IEC 62443-style zone-and-conduit models, ISA-95-style level architectures) partition the estate into levels from enterprise IT down to sensors and actuators. Crossing levels downward is a controlled act. The AI engineering platform is an IT-side system, and everything in this blueprint follows from keeping it that way.
- **Functional safety regimes** — safety-instrumented systems (SIS), emergency shutdown logic, and machine-safety functions are engineered under functional-safety standards (IEC 61508/61511-style regimes) with safety integrity levels, mandated verification, and personal accountability for signatories. These regimes prescribe *who may change what, verified how* — an AI platform does not get to shortcut them.
- **Availability over confidentiality** — on the plant floor the classic security priority order inverts: an availability incident stops production and can create hazardous states. Any platform interaction with OT-adjacent systems must be incapable of degrading availability.
- **Legacy and vendor-locked control systems** — PLC programs, HMI configurations, and proprietary engineering-workstation formats dominate. Much of the estate cannot be meaningfully tested outside the vendor toolchain or a physical/virtual commissioning environment.
- **Connectivity constraints** — plants operate with limited, brokered, or no connectivity to enterprise networks; some regulated or high-security sites are fully air-gapped. The platform must function usefully under all three conditions.

## 2. Risk-Tier Profile

Typical defaults; per [AIES-AEAR-BP-00-R01 — Industry Blueprints, requirement 01](README.md), validate locally.

| Task type | Typical tier | Rationale | Default max AL |
|-----------|-------------|-----------|----------------|
| Enterprise IT applications (ERP-adjacent, analytics dashboards), docs, tests | RT1 — Minimal through RT2 — Moderate | Standard IT blast radius | AL3 — Delegated through AL4 — Autonomous |
| Manufacturing execution system (MES) features behind review | RT2 — Moderate–RT3 — Significant | Production-scheduling errors are costly but recoverable | AL3 — Delegated → AL2 — Collaborative |
| Historian, quality-data, and traceability pipelines | RT3 — Significant | Regulatory and recall evidence integrity | AL2 — Collaborative |
| SCADA/HMI configuration and supervisory-control changes | RT3 — Significant through RT4 — Critical | Direct operator-facing control surface | AL2 — Collaborative → AL1 — Assisted |
| PLC/controller logic in non-safety functions | RT4 — Critical | Physical actuation; commissioning-verified change discipline | AL1 — Assisted |
| **Safety-instrumented systems, ESD logic, machine-safety functions** | **RT4 — Critical, non-negotiable** | Safety-critical per [Taxonomy §4](../../Shared/Taxonomy/README.md#4-risk-tiers-rt1rt4); governed by functional-safety law and standards | AL1 — Assisted, no risk-acceptance path |

[AIES-AEAR-BP-MANUFACTURING-R01] Engineering tasks on safety-instrumented systems, emergency-shutdown logic, or machine-safety functions MUST be classified RT4 — Critical and capped at AL1 — Assisted. Unlike other RT4 — Critical defaults, this cap MUST NOT be relaxed by documented risk acceptance: the applicable functional-safety regime, not the organization, owns the change discipline. AI participation is limited to suggestion and analysis feeding a qualified human safety engineer.

[AIES-AEAR-BP-MANUFACTURING-R02] Any task whose deployment target sits at or below the supervisory-control level of the OT reference hierarchy MUST be classified RT4 — Critical by default; reclassification downward requires a documented risk acceptance naming the accountable plant authority.

## 3. Architecture Deltas from the Core

### 3.1 Topology

Hybrid is the norm: the platform's planes deploy on the enterprise IT side; high-security or regulated sites run the air-gapped topology of [AIES-AEAR-CORE-01 — Core Reference Architecture §13.3](../core-reference-architecture.md#13-deployment-topologies) with internally hosted model serving inside the site boundary. For air-gapped sites, model, knowledge, and policy updates travel by controlled transfer and are treated as supply-chain risk surfaces per the core.

[AIES-AEAR-BP-MANUFACTURING-R03] No plane of the platform may be deployed inside an OT zone, and no Execution Plane sandbox may hold network reachability into OT networks; where OT artifacts (controller programs, HMI configurations) are worked on, they are exported into the IT-side platform through the established OT/IT conduit and re-imported through the same controlled channel.

### 3.2 Plane-Level Deltas

| Plane | Manufacturing delta |
|-------|---------------------|
| Interaction | Approval consoles present the **plant and line context** of a change (site, production state, scheduled downtime window) so approvers judge physical, not just logical, blast radius. Engineering-workstation integration is read-oriented |
| Orchestration | Workflow engine encodes **management-of-change (MoC)** procedures: OT-affecting workflows embed the plant's MoC approval chain as human gates, and RT4 — Critical deployment steps bind to scheduled maintenance windows |
| Model | Air-gapped sites front internal model deployments only; the gateway's degraded-mode rules ([AIES-AEAR-CORE-01-R51 — Core Reference Architecture, requirement 51]) apply. Latency classes account for sites reached over constrained links |
| Context & Knowledge | Knowledge stores ingest OT documentation (P&IDs, control narratives, alarm rationalization records) as first-class context — with classification tags distinguishing safety-related content, which is retrieval-restricted ([AIES-AEAR-BP-MANUFACTURING-R04]). Site-local knowledge replicas serve air-gapped plants |
| Execution | Verification of control-logic changes uses **virtual commissioning** environments (plant simulation, controller emulation) staged in the Execution Plane; passing simulation is a gate prerequisite, never a substitute for the plant's own commissioning tests |
| Guardrail | See §4. Egress control enforces the OT boundary as a structural rule, not a policy exception |
| Observability | ART-15 records for OT-affecting changes capture the MoC reference and commissioning evidence. Evaluation pipelines score AI suggestions on control-logic tasks against simulation outcomes before any qualification claim |
| Governance | Agent Definitions authorized for OT-artifact analysis form a separate, smaller registry subset with plant-authority sign-off; entitlements never include OT write paths |

## 4. Domain-Specific Guardrails

- **OT egress prohibition** — the egress gateway holds no routes into OT zones; this is verified by network architecture review, and any attempted resolution of OT-zone addresses from a sandbox is an alarmed event.
- **Safety-content retrieval shield** — SIS logic, safety requirement specifications, and interlock rationale enter context only for tasks explicitly authorized on safety analysis, and never into tasks that produce deployable artifacts.
- **Controller-artifact write lock** — agent-produced controller logic, HMI configuration, or alarm-threshold changes are staged artifacts only; the action filter denies any pathway that would transfer them toward OT without the MoC gate chain completing.
- **Maintenance-window binding** — production-affecting deployment actions are denied outside the plant's scheduled window for the affected line.
- **Simulation-first rule** — RT3 — Significant and above changes to control-adjacent code require virtual-commissioning evidence attached before the approval gate opens.
- **Site-freeze awareness** — orchestration holds changes for sites in startup, shutdown, or abnormal-situation states as signaled by the plant's operational calendar.

## 5. Example Use Cases

| Use case | Phases | Typical RT | Typical AL |
|----------|--------|-----------|------------|
| Documentation reconstruction for legacy PLC programs (read-only analysis) | P15, X08 | RT1 — Minimal | AL4 — Autonomous with spot audit |
| Test generation for MES order-scheduling logic | P10 | RT2 — Moderate | AL3 — Delegated |
| Historian data-pipeline refactor | P09 | RT3 — Significant | AL2 — Collaborative |
| Alarm-rationalization analysis support for engineers | P06, P15 | RT3 — Significant | AL2 — Collaborative (analysis only) |
| HMI screen logic change for a packaging line | P09 | RT4 — Critical | AL1 — Assisted, MoC-gated |
| SIS logic modification support | P09 | RT4 — Critical | AL1 — Assisted only — suggestion to qualified safety engineer ([AIES-AEAR-BP-MANUFACTURING-R01]) |
| Virtual-commissioning scenario authoring | P10 | RT2 — Moderate | AL3 — Delegated |

---

## Related Documents

- [AIES-AEAR-BP-00 — AEAR Blueprint Catalog](README.md) · [AIES-AEAR-BP-ENTERPRIS — Industry BlueprintE — Enterprise Platform](enterprise-platform.md) · [AIES-AEAR-CORE-01 — Core Reference Architecture — Enterprise AI Engineering Platform](../core-reference-architecture.md) · [AIES-AEAR-XC-01 — Cross-Cutting Concerns in Platform Architecture](../cross-cutting-concerns.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words
- IEC 62443 — Security for industrial automation and control systems
- ISA-95 — Enterprise-control system integration (International Society of Automation)
- IEC 61508 — Functional safety of electrical/electronic/programmable electronic safety-related systems
- IEC 61511 — Functional safety — Safety instrumented systems for the process industry sector
