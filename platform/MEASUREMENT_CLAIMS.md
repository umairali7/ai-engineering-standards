# AIES Decision-Product Measurement Claims

Status: Draft, informational  
Machine-readable contract: `measurement-claims-v1.yaml`

This document states what AIES decision-product values estimate and, equally
important, what they do not establish. It does not change AESQS gates or grant
authority.

Every result is scoped to the exact subject, environment, instruments, task
mapping, scoring protocol, and run manifest recorded with the evidence.
Engineering Evaluation describes observed rubric performance. The Engineering
Capability Matrix (ECM) describes observed performance across directly mapped
engineering tasks and reports evidence confidence separately. Engineering Fit
turns those observations into bounded usage guidance. Comparison is valid only
over compatible evidence intersections. Formal Qualification is a separate,
human-governed conformity process.

Performance and evidence confidence must never be merged into one value. Exact
repeats may measure stability but do not increase distinct task breadth.
Unassessed tasks remain unknown. Controlled scenario results do not silently
become field-reliability claims, and no informational report grants autonomy,
qualification, certification, or production permission.

The YAML contract defines, for every product, the subject, target population,
sampling frame, unit of analysis, outcome, aggregation, uncertainty,
exclusions, intended decision, and prohibited interpretations. Renderers and
case studies should cite that versioned contract.
