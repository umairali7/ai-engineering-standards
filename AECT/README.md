# AECT — AI Engineering Certification & Training

| | |
|---|---|
| **Document ID** | AIES-AECT-00 |
| **Status** | Review |
| **Audience** | All readers |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Purpose

AECT answers the fifth question of the AIES standard: **How do engineers learn and become certified?**

It packages the knowledge defined in [AEBOK](../AEBOK/README.md) into structured learning paths, hands-on labs, examinations, and a vendor-neutral credential ladder for **human practitioners** of AI-native software engineering. AECT plays the role for AI Engineering that ISTQB certification plays for software testing: a portable, evidence-based statement that a person holds a defined level of competency (CL1–CL4) in the discipline.

AECT certifies **people**. The qualification of **AI systems** for scoped engineering work is the exclusive concern of [AESQS](../AESQS/README.md). The two share the same competency scale (CL1–CL4) and evaluation dimensions (EV1–EV6), because AIES holds humans and AI systems to a common evidentiary standard — but a certificate under AECT never authorizes an AI system, and an AESQS qualification never certifies a person.

Although the credential is for humans, the curriculum is centrally about working **with** AI: reviewing AI-produced artifacts, designing autonomy envelopes and oversight gates, governing agent activity, and evaluating non-deterministic components. A certified AI engineer is certified precisely in the discipline of directing and governing AI participation in the SDLC.

### 1.1 Scope

In scope:

- The AIES credential ladder and role-specialization endorsements ([Certification Framework](certification-framework.md)).
- Structured curricula mapping AEBOK Knowledge Areas to learner journeys ([Learning Paths](learning-paths.md)).
- Examination content outlines, item formats, and pass standards ([Exam Blueprints](exam-blueprints.md)).
- A catalog of standardized practical labs with gold-standard solutions and rubrics ([Labs](labs.md)).
- The operation of practical assessments, continuing education, and renewal ([Assessment & Renewal](assessment-and-renewal.md)).

Out of scope:

- The knowledge content itself → [AEBOK](../AEBOK/README.md) is the sole syllabus source.
- Scoring methodology and rubric definitions → [AESQS](../AESQS/README.md) owns assessment science.
- Qualification of AI systems → [AESQS](../AESQS/README.md).
- Vendor product training, model-specific techniques, prompt libraries → excluded by [project non-goals](../README.md#non-goals).

## 2. The Credential Ladder at a Glance

Certification tiers map one-to-one onto the [competency levels (CL1–CL4)](../Shared/Taxonomy/README.md#6-competency-levels-cl1cl4) of the shared taxonomy.

| Tier | Credential | CL | One-line meaning |
|------|-----------|----|------------------|
| 1 | **AIES Certified Associate** | CL1 | Understands the vocabulary, taxonomy, and core practices of AI-native engineering |
| 2 | **AIES Certified Practitioner** | CL2 | Applies AI-native practices independently in standard situations |
| 3 | **AIES Certified Professional** | CL3 | Adapts practice to novel situations; reviews, gates, and coaches others |
| 4 | **AIES Certified Fellow** | CL4 | Sets organizational practice; advances the discipline itself |

At the Professional tier and above, candidates MAY add **role-specialization endorsements** (e.g., *Professional – Security Engineering*, *Professional – Architecture*) mapped to the [role model](../Shared/Taxonomy/README.md#5-ai-engineering-roles) (ROLE-01 … ROLE-14). Details in the [Certification Framework (AIES-AECT-CERT-01)](certification-framework.md).

```
   Associate ──► Practitioner ──► Professional ──► Fellow
     (CL1)          (CL2)            (CL3)          (CL4)
      exam        exam + lab      exam + lab +    portfolio +
                  assessment       portfolio      contribution
                                 [+ endorsements]  + panel
```

## 3. Document Map

| Document | ID | Contents |
|----------|----|----------|
| [README](README.md) | AIES-AECT-00 | This overview |
| [Certification Framework](certification-framework.md) | AIES-AECT-CERT-01 | Tiers, endorsements, prerequisites, evidence requirements, validity, ethics, revocation |
| [Learning Paths](learning-paths.md) | AIES-AECT-LP-01 | Foundation path and role-based paths mapped to AEBOK KAs |
| [Exam Blueprints](exam-blueprints.md) | AIES-AECT-EB-01 | Per-tier exam domains, weightings, item formats, pass thresholds, sample items |
| [Labs](labs.md) | AIES-AECT-LAB-01 | Practical labs catalog (LAB-01 … LAB-10) with scenarios, solutions, rubrics |
| [Assessment & Renewal](assessment-and-renewal.md) | AIES-AECT-AR-01 | Practical assessment operations, continuing education, re-certification, version currency |

## 4. Relationship to Other Modules

```
        AEBOK ────────────► AECT ◄──────────── AESQS
   what to teach            │            how to assess
   (KAs = syllabus)         │            (rubrics, EV1–EV6,
                            │             scoring method)
        AEOS ───────────────┤
   practical content:       │
   workflows, gates,        ▼
   agent roles         credentialed
        AEAR ─────────► practitioners
   practical content:   (CL1–CL4 humans)
   reference
   architectures
```

- **AEBOK is the syllabus source.** Every exam domain, learning module, and lab objective traces to an AEBOK Knowledge Area; the Competency Expectations sections of the KAs are the authoritative statement of what each tier requires. AECT MUST NOT introduce knowledge content that does not exist in AEBOK.
- **AESQS is the assessment methodology.** Practical assessments and lab scoring use AESQS rubrics along EV1–EV6; AECT defines *what* is assessed and *when*, AESQS defines *how* capability evidence is scored.
- **AEOS and AEAR supply practical content.** Lab scenarios exercise AEOS operating-model constructs (autonomy envelopes, approval gates, agent role definitions, audit trails) and AEAR reference architectures, so certified engineers can operate real AI-native delivery systems, not just recite theory.

All AECT documents use the [Glossary (AIES-SHARED-01)](../Shared/Glossary/README.md) and [Taxonomy (AIES-SHARED-02)](../Shared/Taxonomy/README.md) without redefinition.

## 5. Normative Anchors

[AIES-AECT-00-R01] Every AECT curriculum element, exam domain, and lab objective MUST trace to at least one AEBOK Knowledge Area (KA-01 … KA-12).

[AIES-AECT-00-R02] Certification tiers MUST map one-to-one onto competency levels CL1–CL4 as defined in the shared taxonomy; AECT MUST NOT define an alternative proficiency scale.

[AIES-AECT-00-R03] AECT credentials MUST be issued to natural persons only. Authorization of AI systems for engineering work is governed exclusively by [AESQS](../AESQS/README.md).

[AIES-AECT-00-R04] All AECT content MUST remain vendor-neutral: no exam item, lab, or learning module may require knowledge of a specific commercial AI model, product, or provider.

## 6. Contents

```
AECT/
├── README.md                    ← this document (AIES-AECT-00)
├── certification-framework.md   ← credential system (AIES-AECT-CERT-01)
├── learning-paths.md            ← curricula (AIES-AECT-LP-01)
├── exam-blueprints.md           ← examinations (AIES-AECT-EB-01)
├── labs.md                      ← practical labs catalog (AIES-AECT-LAB-01)
└── assessment-and-renewal.md    ← assessment ops & renewal (AIES-AECT-AR-01)
```

## Related Documents

- [Certification Framework (AIES-AECT-CERT-01)](certification-framework.md)
- [Learning Paths (AIES-AECT-LP-01)](learning-paths.md)
- [Exam Blueprints (AIES-AECT-EB-01)](exam-blueprints.md)
- [Labs (AIES-AECT-LAB-01)](labs.md)
- [Assessment & Renewal (AIES-AECT-AR-01)](assessment-and-renewal.md)
- [AEBOK (AIES-AEBOK-00)](../AEBOK/README.md) — the sole syllabus source
- [AESQS (AIES-AESQS-00)](../AESQS/README.md) — assessment methodology and qualification of AI systems
- [Glossary (AIES-SHARED-01)](../Shared/Glossary/README.md) · [Taxonomy (AIES-SHARED-02)](../Shared/Taxonomy/README.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words
