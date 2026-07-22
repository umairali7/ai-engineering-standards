# Certification Framework

| | |
|---|---|
| **Document ID** | AIES-AECT-CERT-01 |
| **Status** | Review |
| **Audience** | Educators & training providers · Assessors & qualification authorities |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Purpose

This document defines the AIES credential system for human practitioners: the four certification tiers, role-specialization endorsements, prerequisites, the evidence required at each tier, validity and renewal, the code-of-ethics commitment, and the conditions for revocation.

The tiers map one-to-one onto the [competency levels CL1 — Foundation through CL4 — Expert (AIES-SHARED-02 — Taxonomy §6)](../Shared/Taxonomy/README.md#6-competency-levels-cl1cl4). A certificate is a portable, versioned, revocable statement that a person has demonstrated the corresponding competency level against a named version of the AIES standard.

[AIES-AECT-CERT-01-R01 — Certification Framework, requirement 01] AIES certificates MUST be issued to natural persons only and MUST record: holder identity, tier, endorsements (if any), the AIES standard version assessed against, issue date, and expiry date.

## 2. Certification Tiers

### 2.1 Tier Overview

| Credential | CL | Typical holder | Core claim |
|-----------|----|----------------|------------|
| **AIES Certified Associate** | CL1 | Engineers, analysts, and managers entering AI-native work | Understands AIES concepts, vocabulary, and taxonomy; applies practices with guidance |
| **AIES Certified Practitioner** | CL2 | Working engineers in AI-native delivery teams | Applies AI-native practices independently in standard situations |
| **AIES Certified Professional** | CL3 | Tech leads, senior engineers, reviewers, gate owners | Adapts practices to novel situations; reviews and coaches others; fit to staff approval gates |
| **AIES Certified Fellow** | CL4 | Principal engineers, heads of engineering, standards contributors | Sets practice at organizational scale; advances the discipline |

[AIES-AECT-CERT-01-R02 — Certification Framework, requirement 02] Each certification tier MUST correspond exactly to one competency level (Associate=CL1, Practitioner=CL2, Professional=CL3, Fellow=CL4), and the pass standard for each tier MUST be derived from the Competency Expectations sections of the [AEBOK Knowledge Areas](../AEBOK/README.md) at that level.

### 2.2 Prerequisites and Evidence Requirements

| Requirement | Associate (CL1) | Practitioner (CL2) | Professional (CL3) | Fellow (CL4) |
|-------------|-----------------|--------------------|--------------------|--------------|
| **Prerequisite credential** | None | Associate (or waiver, §2.3) | Practitioner | Professional |
| **Professional experience** | None | 1+ year software engineering | 2+ years in AI-native delivery | 5+ years, incl. 2+ at CL3 scope |
| **Knowledge exam** | Required | Required | Required | Not required |
| **Practical (lab) assessment** | — | Required: 2 labs | Required: 3 labs incl. one review/oversight lab | — |
| **Portfolio** | — | — | Required (§2.4) | Required, at organizational scale |
| **Peer contribution** | — | — | — | Required (§2.5) |
| **Panel review** | — | — | — | Required |
| **Code-of-ethics commitment (§5)** | Required | Required | Required | Required |

[AIES-AECT-CERT-01-R03 — Certification Framework, requirement 03] Practitioner and Professional certification MUST include practical assessment against the [labs catalog (AIES-AECT-LAB-01 — Labs)](labs.md), scored using [AESQS](../AESQS/README.md) rubrics along EV1–EV6, per the procedures in [Assessment & Renewal (AIES-AECT-AR-01 — Assessment and Renewal)](assessment-and-renewal.md).

[AIES-AECT-CERT-01-R04 — Certification Framework, requirement 04] Fellow certification MUST NOT be granted on examination alone; it requires portfolio evidence, verified peer contribution, and a review panel of at least three current Fellows (or, during the bootstrap period before Fellows exist, panelists appointed under [GOVERNANCE.md](../GOVERNANCE.md)).

### 2.3 Experience Waiver

Candidates with 3+ years of documented professional software engineering experience MAY sit the Practitioner exam without holding the Associate credential, provided they pass a foundation screening covering the Associate exam domains. The waiver applies to the *prerequisite credential* only; all Practitioner evidence requirements still apply.

### 2.4 Portfolio (Professional and Fellow)

A portfolio is a curated, verifiable body of the candidate's own work products in AI-native delivery. It MUST include, at minimum:

- Two artifacts showing **review of AI-produced work** (e.g., reviewed ART-06 source changes with recorded findings).
- One artifact showing **oversight or governance design** (e.g., an autonomy envelope, gate design, or agent definition ART-14).
- One artifact showing **evaluation or improvement** (e.g., a telemetry and evaluation report ART-12, or a post-incident review).

For Fellow, the portfolio MUST additionally demonstrate organizational-scale impact: an operating-model rollout, an organization-wide policy or standard, or a multi-team capability program. Portfolio items are redacted as needed; verifiability requirements are defined in [AIES-AECT-AR-01 — Assessment and Renewal §3](assessment-and-renewal.md).

### 2.5 Peer Contribution (Fellow)

Verified contribution to the discipline, satisfied by any one of: accepted contributions to the AIES standard itself (per [CONTRIBUTING.md](../CONTRIBUTING.md)); published practice guidance adopted beyond the candidate's own team; serving as a qualified assessor for 10+ practical assessments; or mentoring at least two candidates to Professional certification.

## 3. Role-Specialization Endorsements

An endorsement is an add-on to a Professional or Fellow credential attesting depth in one role of the [role model (AIES-SHARED-02 — Taxonomy §5)](../Shared/Taxonomy/README.md#5-ai-engineering-roles). Endorsements are written as, e.g., *AIES Certified Professional – Security Engineering*.

| Endorsement | Role ID(s) | Deep-dive KAs | Practical evidence focus |
|-------------|-----------|---------------|--------------------------|
| Business Analysis & Product | ROLE-02, ROLE-03 | KA-02, KA-04 | AI-assisted requirements and prioritization work with preserved human intent |
| Architecture | ROLE-05 | KA-03, KA-07, KA-10 | Architecture and ADRs for AI-operable systems |
| Software Engineering | ROLE-06 | KA-05, KA-06, KA-10 | AI-assisted implementation with review discipline and provenance |
| Quality Engineering | ROLE-07 | KA-06, KA-12 | Testing AI-produced code; evaluating non-deterministic components |
| Security Engineering | ROLE-08 | KA-07, KA-08 | Threat modeling and controls for AI-native delivery |
| DevOps & Release | ROLE-09 | KA-08, KA-06 | Pipelines as guardrails; gated deployment of AI-produced change |
| Site Reliability | ROLE-10 | KA-09, KA-12 | Operating AI-inclusive systems; agent activity observability |
| Knowledge & Context | ROLE-11, ROLE-12 | KA-10, KA-02 | Context asset (ART-13) curation and documentation pipelines |
| Oversight & Governance | ROLE-13, ROLE-14 | KA-11, KA-12 | Gate design, audit trails, risk-tier governance |

[AIES-AECT-CERT-01-R05 — Certification Framework, requirement 05] An endorsement MUST require (a) a current Professional or Fellow credential, (b) a role-specific exam section drawn from the endorsement's deep-dive KAs, and (c) one role-specific lab from [AIES-AECT-LAB-01 — Labs](labs.md) passed at CL3.

[AIES-AECT-CERT-01-R06 — Certification Framework, requirement 06] Endorsements MUST reference role IDs from the shared taxonomy; AECT MUST NOT create specialization categories outside the ROLE-01 … ROLE-14 model.

Note: the *Oversight & Governance* endorsement prepares humans to staff ROLE-13/ROLE-14 — roles the taxonomy requires to be human — and is therefore the RECOMMENDED credential expectation for staffing approval gates on RT3 — Significant through RT4 — Critical work.

## 4. Validity and Renewal

| Tier | Validity | Renewal mechanism |
|------|----------|-------------------|
| Associate | 3 years | Renewal exam **or** 20 continuing-education (CE) credits |
| Practitioner | 3 years | 30 CE credits, incl. 1 refreshed lab |
| Professional | 3 years | 45 CE credits, incl. assessed practical activity |
| Fellow | 5 years | 60 CE credits, incl. verified continued contribution |

Endorsements share the expiry date of the underlying credential and renew with it.

[AIES-AECT-CERT-01-R07 — Certification Framework, requirement 07] Every credential MUST carry an expiry date; credentials MUST NOT be issued as lifetime awards.

[AIES-AECT-CERT-01-R08 — Certification Framework, requirement 08] A renewed credential MUST be re-anchored to the AIES standard version current at renewal time, per the version-currency rules in [AIES-AECT-AR-01 — Assessment and Renewal §5](assessment-and-renewal.md).

Lapsed credentials enter a 12-month grace period during which renewal is still possible with a CE surcharge; after the grace period, the full certification process for the tier applies again. CE credit definitions are in [AIES-AECT-AR-01 — Assessment and Renewal §4](assessment-and-renewal.md).

## 5. Code-of-Ethics Commitment

Every candidate, at every tier, signs the AIES Code of Ethics as a condition of certification. Its obligations are:

1. **Human accountability.** Hold humans — beginning with yourself — accountable for engineering decisions; never present AI output as reviewed when it was not.
2. **Honest evidence.** Never fabricate, tamper with, or misrepresent evaluation evidence, test results, provenance records, or audit trails.
3. **Bounded autonomy.** Configure and operate AI systems only within declared autonomy levels and risk-tier limits; report circumvention when observed.
4. **Competence honesty.** Represent your certification tier, endorsements, and standard version accurately; do not undertake gated responsibilities beyond your demonstrated competency.
5. **Duty to escalate.** Escalate AI behavior that threatens safety, security, or legal compliance, even when doing so is commercially inconvenient.
6. **Confidentiality and integrity of the scheme.** Do not disclose exam content or lab gold-standard solutions; do not assist others in misrepresentation.

[AIES-AECT-CERT-01-R09 — Certification Framework, requirement 09] Certification MUST be conditional on a signed code-of-ethics commitment, and the commitment MUST be renewed at every renewal cycle.

## 6. Revocation and Suspension

[AIES-AECT-CERT-01-R10 — Certification Framework, requirement 10] The certification body MUST revoke a credential upon verified findings of: fraud in the certification process (including impersonation and evidence fabrication), material breach of the code of ethics, or disclosure of secure exam content.

[AIES-AECT-CERT-01-R11 — Certification Framework, requirement 11] Revocation and suspension decisions MUST follow a documented due process: written notice of the allegation, an opportunity for the holder to respond, decision by a body independent of the original assessors, and a right of appeal.

Suspension (temporary invalidation pending investigation) SHOULD be used where the allegation is credible but unresolved. Revoked credentials are removed from the public verification register (§7); a revoked holder MAY re-enter the scheme at the lowest tier after a minimum 24-month exclusion, at the certification body's discretion.

## 7. Credential Verification

Certificates are verifiable through a public register recording holder name (or consented pseudonymous ID), tier, endorsements, standard version, and status (current / expired / suspended / revoked). Employers SHOULD verify credentials against the register rather than accepting certificates at face value.

## Related Documents

- [Learning Paths (AIES-AECT-LP-01 — Learning Paths)](learning-paths.md) — how to prepare for each tier
- [Exam Blueprints (AIES-AECT-EB-01 — Exam Blueprints)](exam-blueprints.md) — what each tier's exam covers
- [Labs (AIES-AECT-LAB-01 — Labs)](labs.md) — practical assessment content
- [Assessment & Renewal (AIES-AECT-AR-01 — Assessment and Renewal)](assessment-and-renewal.md) — how assessments are run and credentials kept current
- [AESQS (AIES-AESQS-00 — Qualification Standard)](../AESQS/README.md) — scoring methodology and rubrics

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words
