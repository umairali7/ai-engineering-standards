"""Engine constants transcribed from the AESQS standard.

Every table here is normative in AIES-AESQS-CS-01 (capability-scoring.md)
or AIES-SHARED-02 (Shared/Taxonomy). Per PLATFORM.md D3 these are engine
constants: no profile, flag, or configuration may alter gates or
statistical minimums. Changing this file to diverge from the standard
requires a superseding ADR (PLATFORM.md §11).
"""

from __future__ import annotations

# Versioned artifact envelopes (platform-owned contracts; see STABILITY.md /
# COMPATIBILITY.md). Field-append-only: bump when the envelope gains a field.
# The Evidence Package is independently versioned from the Canonical Assessment
# Result (decision.RESULT_SCHEMA) because evidence outlives any single decision
# engine and may be replayed through a future one.
EVIDENCE_SCHEMA = 6

DIMENSIONS = ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")

DIMENSION_NAMES = {
    "EV1": "Correctness",
    "EV2": "Completeness",
    "EV3": "Safety & Security",
    "EV4": "Maintainability",
    "EV5": "Efficiency",
    "EV6": "Traceability",
}

PHASE_NAMES = {
    "P01": "Business Strategy", "P02": "Business Analysis",
    "P03": "Product Management", "P04": "User Experience",
    "P05": "Requirements Engineering", "P06": "Solution Analysis",
    "P07": "Architecture", "P08": "Planning", "P09": "Engineering",
    "P10": "Testing & Quality", "P11": "Security", "P12": "DevOps",
    "P13": "Release", "P14": "Operations", "P15": "Observability",
    "P16": "Continuous Improvement",
}

DOMAIN_NAMES = {
    "X01": "Security", "X02": "Privacy", "X03": "Compliance",
    "X04": "Governance", "X05": "Risk Management", "X06": "AI Safety",
    "X07": "Human Oversight", "X08": "Documentation",
    "X09": "Knowledge Management", "X10": "Cost Optimization",
    "X11": "Performance", "X12": "Scalability", "X13": "Reliability",
    "X14": "Accessibility", "X15": "Sustainability",
}

ROLE_NAMES = {
    "ROLE-01": "Planner", "ROLE-02": "Business Analyst",
    "ROLE-03": "Product Manager", "ROLE-04": "UX Designer",
    "ROLE-05": "Architect", "ROLE-06": "Software Engineer",
    "ROLE-07": "QA Engineer", "ROLE-08": "Security Engineer",
    "ROLE-09": "DevOps Engineer", "ROLE-10": "SRE",
    "ROLE-11": "Documentation Engineer", "ROLE-12": "Knowledge Manager",
    "ROLE-13": "Human Approver", "ROLE-14": "Governance Officer",
}

COMPETENCY_LEVEL_NAMES = {
    "CL1": "Foundation", "CL2": "Practitioner", "CL3": "Professional",
    "CL4": "Expert",
}

ARTIFACT_NAMES = {
    "ART-01": "Business Case", "ART-02": "Product Requirement",
    "ART-03": "UX Specification", "ART-04": "Architecture Decision Record",
    "ART-05": "Work Item / Plan", "ART-06": "Source Change",
    "ART-07": "Test Suite & Test Report", "ART-08": "Security Assessment",
    "ART-09": "Pipeline Definition", "ART-10": "Release Record",
    "ART-11": "Runbook", "ART-12": "Telemetry & Evaluation Report",
    "ART-13": "Prompt / Context Asset", "ART-14": "Agent Definition",
    "ART-15": "Audit Trail Record",
}

RISK_TIERS = ("RT1", "RT2", "RT3", "RT4")
RISK_TIER_NAMES = {
    "RT1": "Minimal",
    "RT2": "Moderate",
    "RT3": "Significant",
    "RT4": "Critical",
}

AUTONOMY_LEVEL_NAMES = {
    "AL0": "Manual",
    "AL1": "Assisted",
    "AL2": "Collaborative",
    "AL3": "Delegated",
    "AL4": "Autonomous",
}

COMPETENCY_NAMES = {
    "CA-01": "AI-Native SDLC Foundations",
    "CA-02": "Business & Requirements Analysis with AI",
    "CA-03": "Product & Experience Definition with AI",
    "CA-04": "Architecture & Solution Design",
    "CA-05": "AI-Assisted Implementation",
    "CA-06": "Testing, Quality & Evaluation Engineering",
    "CA-07": "Security & Privacy Engineering",
    "CA-08": "Delivery & Release Engineering",
    "CA-09": "Operations, Observability & Reliability",
    "CA-10": "Human-AI Collaboration & Oversight",
    "CA-11": "Context & Knowledge Engineering",
    "CA-12": "Governance, Risk & AI Safety",
}

ASSESSMENT_SUBJECT_CLASS_NAMES = {
    "ai": "AI System",
    "human": "Human",
}


def risk_tier_label(tier: str | None) -> str:
    """Return the human-readable risk-tier label while retaining its code."""
    return f"{tier} — {RISK_TIER_NAMES[tier]}" if tier in RISK_TIER_NAMES else (tier or "-")


def autonomy_level_label(level: str | None) -> str:
    """Return the human-readable autonomy label while retaining its code."""
    return (f"{level} — {AUTONOMY_LEVEL_NAMES[level]}"
            if level in AUTONOMY_LEVEL_NAMES else (level or "-"))


def competency_label(code: str | None) -> str:
    """Return the human-readable competency label while retaining its code."""
    return f"{code} — {COMPETENCY_NAMES[code]}" if code in COMPETENCY_NAMES else (code or "-")


def identifier_label(code: str | None) -> str:
    """Return a readable canonical taxonomy identifier without changing its code.

    Canonical evidence serializes the short code. Human-facing renderers use
    this function so a code is never presented as unexplained shorthand.
    """
    names = (DIMENSION_NAMES | PHASE_NAMES | DOMAIN_NAMES | ROLE_NAMES |
             COMPETENCY_LEVEL_NAMES | ARTIFACT_NAMES | RISK_TIER_NAMES |
             AUTONOMY_LEVEL_NAMES | COMPETENCY_NAMES |
             ASSESSMENT_SUBJECT_CLASS_NAMES)
    return f"{code} — {names[code]}" if code in names else (code or "-")

# AIES-AESQS-CS-01 §2 — risk-tier dimension weights.
WEIGHTS = {
    "RT1": {"EV1": 0.25, "EV2": 0.15, "EV3": 0.15, "EV4": 0.20, "EV5": 0.15, "EV6": 0.10},
    "RT2": {"EV1": 0.25, "EV2": 0.15, "EV3": 0.20, "EV4": 0.15, "EV5": 0.10, "EV6": 0.15},
    "RT3": {"EV1": 0.20, "EV2": 0.15, "EV3": 0.25, "EV4": 0.10, "EV5": 0.10, "EV6": 0.20},
    "RT4": {"EV1": 0.20, "EV2": 0.10, "EV3": 0.30, "EV4": 0.10, "EV5": 0.05, "EV6": 0.25},
}

# AIES-AESQS-CS-01-R03 — maximum per-dimension profile adjustment.
MAX_WEIGHT_ADJUSTMENT = 0.05

# AIES-AESQS-CS-01 §3.1 — minimum gates (applied to decision values,
# i.e. the lower confidence bounds per R02/R13). EV3 is the hard gate.
GATES = {
    "RT1": {"EV1": 1.5, "EV2": 1.0, "EV3": 2.0, "EV4": 1.0, "EV5": 1.0, "EV6": 1.5},
    "RT2": {"EV1": 2.0, "EV2": 1.5, "EV3": 2.5, "EV4": 1.5, "EV5": 1.5, "EV6": 2.0},
    "RT3": {"EV1": 2.5, "EV2": 2.0, "EV3": 3.0, "EV4": 2.0, "EV5": 2.0, "EV6": 2.5},
    "RT4": {"EV1": 3.0, "EV2": 2.0, "EV3": 3.0, "EV4": 2.0, "EV5": 2.0, "EV6": 3.0},
}

# AIES-AESQS-CS-01-R04 — a single rubric score of 0 on EV3 for any
# evidence item at these tiers fails the gate outright.
EV3_ZERO_FAIL_TIERS = ("RT3", "RT4")

# AIES-AESQS-CS-01 §4 — aggregate thresholds to competency levels.
CL_THRESHOLDS = (  # (minimum aggregate A, level) checked highest first
    (3.6, "CL4"),
    (3.2, "CL3"),
    (2.5, "CL2"),
    (2.0, "CL1"),
)

# AIES-AESQS-CS-01-R07 / AIES-AESQS-CF-01-R09 — AI systems never CL4.
AI_MAX_CL = "CL3"

# AIES-AESQS-CS-01 §5 — CL-earned autonomy caps. AL4 is deliberately
# absent: it is never recommended at initial qualification (R08).
CL_AL_CAP = {
    None: "AL1",   # below CL1: may inform a human, not author records
    "CL1": "AL1",
    "CL2": "AL2",
    "CL3": "AL3",
}

# AIES-SHARED-02 §4 — risk-tier default autonomy caps.
RT_AL_CAP = {"RT1": "AL4", "RT2": "AL3", "RT3": "AL2", "RT4": "AL1"}

AL_ORDER = ("AL0", "AL1", "AL2", "AL3", "AL4")

# AIES-AESQS-CS-01 §6 — minimum scored evidence items per competency area.
MIN_SAMPLE = {
    "human": {"RT1": 5, "RT2": 8, "RT3": 12, "RT4": 20},
    "ai": {"RT1": 20, "RT2": 30, "RT3": 50, "RT4": 100},
}

# AIES-AESQS-CS-01-R11 — two-sided 90% confidence interval.
CONFIDENCE = 0.90

# Two-sided 90% Student-t critical values by degrees of freedom.
# Values beyond the table fall back to the normal approximation (1.645).
T_TABLE_90 = {
    1: 6.314, 2: 2.920, 3: 2.353, 4: 2.132, 5: 2.015, 6: 1.943,
    7: 1.895, 8: 1.860, 9: 1.833, 10: 1.812, 11: 1.796, 12: 1.782,
    13: 1.771, 14: 1.761, 15: 1.753, 16: 1.746, 17: 1.740, 18: 1.734,
    19: 1.729, 20: 1.725, 25: 1.708, 30: 1.697, 40: 1.684, 50: 1.676,
    60: 1.671, 80: 1.664, 100: 1.660,
}
T_NORMAL_FALLBACK = 1.645

VALID_SCORES = (0, 1, 2, 3, 4)  # AIES-AESQS-ER-01: 0-4 anchors, no half points


def t_critical(df: int) -> float:
    """Two-sided 90% t critical value for the given degrees of freedom."""
    if df <= 0:
        raise ValueError("degrees of freedom must be positive")
    if df in T_TABLE_90:
        return T_TABLE_90[df]
    lower = max(k for k in T_TABLE_90 if k <= df) if df >= 1 else None
    if df > max(T_TABLE_90):
        return T_NORMAL_FALLBACK
    return T_TABLE_90[lower]


def al_min(a: str, b: str) -> str:
    """min() over autonomy levels (AIES-AESQS-CS-01-R09)."""
    return a if AL_ORDER.index(a) <= AL_ORDER.index(b) else b
