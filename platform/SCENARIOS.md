# Authoring Competency Scenarios

| | |
|---|---|
| **Document ID** | AIES-PLAT-07 |
| **Status** | Draft |
| **Audience** | Contributors · Suite maintainers · Assessors |

How to add a **scenario** to a competency suite so it strengthens qualification
rather than padding it. A scenario is one prompt the subject answers; the
answer is scored on EV1–EV6. Suites live under
`platform/competencies/CA-NN-*/scenarios/` and are checked by
`aies suites validate` (run in CI).

## 1. File and schema

One scenario per YAML file, named `SC-CANN-0KK.yaml` (continue the numbering
after the highest existing id in the area). Required and recommended fields:

```yaml
id: SC-CA05-017              # SC-<AREA><NN>-<KK>; must match the filename
area: CA-05                  # the competency area (CA-01…CA-12)
family: constrained-code-change   # a short scenario-family label
risk_tier: RT2              # RT1 | RT2 | RT3 | RT4 — the task's blast radius
prompt: |                    # multi-line, concrete, with real constraints
  <the task the subject must respond to>
expected_qualities:          # 5–7 bullets a strong answer exhibits
  - ...
rubric:                      # ONE list item per dimension: what earns credit
  EV1: [ ... ]  # Correctness
  EV2: [ ... ]  # Completeness
  EV3: [ ... ]  # Safety & Security   (the hard gate)
  EV4: [ ... ]  # Maintainability
  EV5: [ ... ]  # Efficiency
  EV6: [ ... ]  # Traceability
weight: 1.1                  # 1.0–1.3; higher for harder / higher-stakes items
failure_conditions:          # 2–3 concrete failures, each tagged to a dimension
  - invents an API and presents it as ready to run   # -> EV1
  - omits authorization checks                        # -> EV3
repeats_min: 3               # 2–3; repeats measure variance, not padding
```

`id`, `area`, `risk_tier`, `prompt`, `expected_qualities`, and `rubric` are
**required** (the validator errors without them). `family`, `weight`,
`failure_conditions`, and `repeats_min` are strongly recommended. An optional
`calibration:` block records why the scenario exists and how well it measures —
see [CALIBRATION.md](CALIBRATION.md), which treats each scenario as a
*measurement instrument*.
[SC-CA05-011](competencies/CA-05-ai-assisted-implementation/scenarios/SC-CA05-011.yaml)
is a good worked example;
[SC-CA07-001](competencies/CA-07-security-privacy-engineering/scenarios/SC-CA07-001.yaml)
shows a calibrated one.

## 2. The quality bar (this is the point)

A scenario earns its place only if it **discriminates a strong answer from a
weak one**. Aim for:

- **Realistic and multi-constraint.** A concrete situation with genuine tension —
  competing requirements, missing context, sensitive data, ambiguity, dual-use,
  or concerns that cross into other areas.
- **Distinct.** Materially different from every other scenario in the area. Do
  not rephrase an existing prompt — that produces the *repetition* the suites
  exist to avoid.
- **Judgment-forcing.** The best answer often states assumptions, asks for the
  right context, refuses to fabricate, or escalates scope — not just "produces
  output."
- **Refuse/escalate coverage.** Each area's RT3/RT4 set MUST include at least one
  scenario whose *correct* outcome is to **refuse or escalate**
  ([AIES-AESQS-QP-01-R08](../AESQS/qualification-process.md)).

## 3. Choosing a risk tier

Risk tier is the **blast radius of the task**, not the difficulty of the prompt
(see [Taxonomy §4](../Shared/Taxonomy/README.md#4-risk-tiers-rt1rt4)):

| Tier | Use when the task's failure… |
|------|------------------------------|
| RT1 | is trivial/local and easily reversed |
| RT2 | affects a limited scope, recoverable with effort |
| RT3 | is significant — customer-facing, data-integrity, or hard to reverse |
| RT4 | is critical/irreversible — safety, security, legal, regulated data |

Most decisional volume is RT2, so weight new scenarios toward **distinct RT2**
cases, then RT3, with RT4 reserved for genuinely critical/irreversible tasks.

## 4. Writing rubrics and failure conditions

- Each **rubric** item says *what earns credit* on that dimension for this
  specific task — concrete enough that two reviewers would agree. Avoid generic
  restatements of the dimension name.
- **EV3 (Safety & Security)** is the hard gate; make its criterion sharp.
- Each **failure_condition** is a concrete wrong move, tagged `# -> EVn` to the
  dimension it should cost. These double as anti-gaming traps — include the
  tempting-but-wrong shortcut (a partial-compliance or false-authorization trap).
- A rubric may target a subset of dimensions; the validator only **warns** on
  uncovered dimensions. Full EV1–EV6 coverage is preferred for new scenarios.

## 5. Safety when authoring

- No real secrets, credentials, or personal data in prompts.
- No operational attack instructions. Dual-use security topics stay at the
  **authorization-boundary** level — the correct answer is to require
  authorization evidence, not to perform the exploit (see CA-07).

## 6. Validate before you commit

```
cd platform
aies suites validate          # schemas, IDs, dimensions, risk tiers, counts
pytest tests/                 # conformance tests
```

`suites validate` MUST report **0 errors**. Warnings (e.g. partial rubric
coverage) are acceptable but prefer to resolve them on new scenarios. A content
change bumps the suite version, so results are only comparable across identical
suite versions ([PLATFORM.md §9](../docs/PLATFORM.md)).

## Related Documents

- [Guide (AIES-PLAT-01)](GUIDE.md) · [Journeys (AIES-PLAT-05)](JOURNEYS.md)
- [Competency Framework (AIES-AESQS-CF-01)](../AESQS/competency-framework.md)
- [Qualification Process (AIES-AESQS-QP-01)](../AESQS/qualification-process.md) — sampling & refuse/escalate rules
- [Taxonomy (AIES-SHARED-02)](../Shared/Taxonomy/README.md) — risk tiers & EV dimensions

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words
