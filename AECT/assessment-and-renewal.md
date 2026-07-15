# Assessment & Renewal

| | |
|---|---|
| **Document ID** | AIES-AECT-AR-01 |
| **Status** | Review |
| **Audience** | Educators & training providers · Assessors & qualification authorities |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

This document defines how AECT assessments are operated and how credentials are kept current: assessor qualifications, environment standardization for practical assessments, scoring and evidence verification, continuing education, the re-certification cycle, version currency, and appeals. It operationalizes the credential system of the [Certification Framework (AIES-AECT-CERT-01)](certification-framework.md) using the labs of [AIES-AECT-LAB-01](labs.md) and the scoring methodology of [AESQS](../AESQS/README.md).

---

## 1. Assessor Qualifications

An assessor is a person who scores practical assessments, verifies portfolios, or sits Fellow review panels. Assessment quality is bounded by assessor quality, so assessor standing is a certification requirement, not an administrative detail.

- [AIES-AECT-AR-01-R01] An assessor MUST hold a current AIES credential at the tier being assessed or higher: Practitioner labs are assessed by Practitioners or above, Professional labs and portfolios by Professionals or above, and Fellow panels by Fellows (subject to the bootstrap provision of [AIES-AECT-CERT-01-R04](certification-framework.md#2-certification-tiers)).
- [AIES-AECT-AR-01-R02] Assessors scoring an endorsement lab ([AIES-AECT-CERT-01 §3](certification-framework.md#3-role-specialization-endorsements)) MUST hold that endorsement or demonstrate equivalent role competency verified by the certification body.
- [AIES-AECT-AR-01-R03] Assessors MUST complete assessor calibration before their first scoring and periodic recalibration thereafter: scoring reference submissions against the gold-standard rubrics and remaining within the tolerance the certification body defines. Assessors whose scores drift outside tolerance MUST be recalibrated before scoring further candidates.
- [AIES-AECT-AR-01-R04] An assessor MUST NOT assess a candidate they have trained, mentored, managed, or have a personal or commercial relationship with; conflicts are declared before assignment and recorded.
- [AIES-AECT-AR-01-R05] Assessors are bound by the code of ethics ([AIES-AECT-CERT-01 §5](certification-framework.md#5-code-of-ethics-commitment)); verified assessor misconduct is grounds for revocation under [AIES-AECT-CERT-01 §6](certification-framework.md#6-revocation-and-suspension).

## 2. Environment Standardization

Practical assessment is only comparable if every candidate faces the same task under the same conditions ([AIES-AECT-LAB-01-R02](labs.md)).

- [AIES-AECT-AR-01-R06] Lab environments MUST be standardized per lab: identical fixtures, repository states, tooling classes, and AI-system capability envelopes for every candidate sitting the same lab version. Environments MUST be vendor-neutral — expressed as capability requirements (e.g., "a code-capable AI assistant operating at AL2"), never as named commercial products.
- [AIES-AECT-AR-01-R07] Environments MUST be reset to a known-good state between candidates, and candidate sessions MUST be isolated from one another and from any network resource that could expose gold-standard solutions.
- [AIES-AECT-AR-01-R08] The environment MUST record the candidate's session — actions taken, AI interactions, artifacts produced — as assessment evidence, and candidates MUST be informed of this recording. Session evidence is retained per the certification body's retention policy and at least until the appeal window (§6) closes.
- [AIES-AECT-AR-01-R09] Where equivalent capability cannot be guaranteed (e.g., a degraded AI system during a session), the session MUST be voided and rescheduled at no cost to the candidate rather than scored with a discount.

## 3. Scoring and Evidence Verification

- [AIES-AECT-AR-01-R10] Practical assessments MUST be scored using AESQS rubrics along the six evaluation dimensions EV1–EV6 ([AIES-SHARED-02 §8](../Shared/Taxonomy/README.md#8-evaluation-dimensions-ev1ev6)) against the lab's gold-standard rubric ([AIES-AECT-LAB-01](labs.md)). AECT MUST NOT define an alternative scoring methodology.
- [AIES-AECT-AR-01-R11] Scores MUST be reported per dimension, not only in aggregate; the pass standard is the tier's competency expectation ([AIES-AECT-CERT-01-R02](certification-framework.md#2-certification-tiers)), and a critical failure on EV3 (Safety & Security) or EV6 (Traceability) MUST fail the lab regardless of aggregate score.
- [AIES-AECT-AR-01-R12] **Double-scoring for high-stakes tiers.** Every Professional-tier lab, every endorsement lab, every portfolio review, and all Fellow evidence MUST be scored independently by two qualified assessors. Discrepancies beyond the calibration tolerance are resolved by a third senior assessor; the resolution and rationale are recorded. Practitioner labs MAY be single-scored, with an org-defined sample (RECOMMENDED at least 10%) double-scored for calibration monitoring.
- [AIES-AECT-AR-01-R13] **Portfolio verifiability** ([AIES-AECT-CERT-01 §2.4](certification-framework.md#24-portfolio-professional-and-fellow)). Each portfolio item MUST be verifiable: the candidate's individual contribution attested by a named referee with first-hand knowledge, dates and role stated, and provenance sufficient to distinguish the candidate's work from that of teammates or AI systems. Redaction of confidential content is permitted; redaction that prevents verification of the candidate's contribution disqualifies the item.
- [AIES-AECT-AR-01-R14] Candidates MUST receive a written result with per-dimension scores and, on failure, the failed criteria. Gold-standard solutions and rubric internals are not disclosed. Failed candidates MAY resit after a waiting period defined by the certification body, with a different lab variant where available.

## 4. Continuing Education

Renewal by continuing education (CE) keeps credential holders current between certification cycles. CE requirements per tier are set in [AIES-AECT-CERT-01 §4](certification-framework.md#4-validity-and-renewal) (Associate 20, Practitioner 30, Professional 45, Fellow 60 credits per cycle).

Credit categories:

| Category | Examples | Credits | Cap per cycle |
|----------|----------|---------|---------------|
| **Verified practice** | Documented AI-native delivery work in an AEOS role; staffing approval gates; serving as an accountable human | 1 per verified month | 50% of requirement |
| **AIES contribution** | Accepted changes to the AIES standard; serving as a qualified assessor; developing accepted lab or exam content | 5 per accepted contribution or assessment cycle | No cap |
| **Publications and teaching** | Published practice guidance, conference talks, delivering AECT-aligned training | 3 per item | 30% of requirement |
| **Formal learning** | Completing AECT learning-path modules ([AIES-AECT-LP-01](learning-paths.md)); refreshed labs | 1 per module; 5 per passed lab | No cap |

- [AIES-AECT-AR-01-R15] CE claims MUST be evidenced and verifiable; the certification body MUST audit a random sample of CE claims each cycle, and fabricated claims are an ethics breach under [AIES-AECT-CERT-01-R10](certification-framework.md#6-revocation-and-suspension).
- [AIES-AECT-AR-01-R16] Tier-specific renewal inclusions MUST be satisfied within the CE total: Practitioner renewal includes one refreshed lab, Professional renewal includes assessed practical activity (a lab or a verified gate-staffing/review engagement scored per §3), and Fellow renewal includes verified continued contribution ([AIES-AECT-CERT-01 §4](certification-framework.md#4-validity-and-renewal)).

## 5. Re-Certification and Version Currency

The re-certification cycle follows the validity periods of [AIES-AECT-CERT-01 §4](certification-framework.md#4-validity-and-renewal): three years for Associate, Practitioner, and Professional; five years for Fellow; endorsements sharing the expiry of the underlying credential; and a 12-month grace period after lapse.

- [AIES-AECT-AR-01-R17] Renewal MUST be completed before expiry via the tier's renewal mechanism (renewal exam or CE for Associate; CE with inclusions per R16 for other tiers). After the grace period, the full certification process for the tier applies again — there is no indefinite renewal-by-fee.
- [AIES-AECT-AR-01-R18] **Version currency.** Every credential MUST record the AIES standard version it was earned or last renewed against ([AIES-AECT-CERT-01-R01](certification-framework.md#1-purpose)), and the public register (AIES-AECT-CERT-01 §7) MUST display it. A credential is a claim about competency against that version, not against whatever version is current.
- [AIES-AECT-AR-01-R19] On a **minor** AIES version change, credentials remain current and re-anchor to the new version at their next renewal per [AIES-AECT-CERT-01-R08](certification-framework.md#4-validity-and-renewal). On a **major** AIES version change, holders MUST pass a **bridging assessment** — a focused delta exam (and, where the changes are practical, a delta lab) covering what changed — by the earlier of their next renewal or a transition deadline the certification body announces (minimum 18 months). Credentials not bridged by the deadline are marked *version-lapsed* on the register until bridged.
- [AIES-AECT-AR-01-R20] Bridging assessments MUST be scoped strictly to the delta between the versions and MUST NOT re-test unchanged material at full depth.

## 6. Appeals

- [AIES-AECT-AR-01-R21] Candidates MAY appeal any assessment result, CE audit finding, or version-lapse determination within 60 days of written notice. Appeals MUST be decided by assessors independent of the original decision, with access to the full session evidence (§2) and scoring record (§3), within 60 days of filing.
- [AIES-AECT-AR-01-R22] An upheld appeal MUST correct the record retroactively (including the public register) at no cost to the candidate; a rejected appeal MUST state its reasons in writing. Appeal outcomes feed assessor calibration (§1) where scoring error is found. Appeals against revocation follow the due process of [AIES-AECT-CERT-01-R11](certification-framework.md#6-revocation-and-suspension).

## Related Documents

- [Certification Framework (AIES-AECT-CERT-01)](certification-framework.md) — tiers, evidence requirements, validity, ethics, revocation
- [Labs (AIES-AECT-LAB-01)](labs.md) — the practical assessment content this document operates
- [Exam Blueprints (AIES-AECT-EB-01)](exam-blueprints.md) — knowledge exams and pass thresholds
- [Learning Paths (AIES-AECT-LP-01)](learning-paths.md) — preparation and CE-creditable modules
- [AESQS (AIES-AESQS-00)](../AESQS/README.md) — the scoring methodology and rubric definitions used in §3

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words
