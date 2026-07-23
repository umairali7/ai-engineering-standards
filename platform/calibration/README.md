# Scenario Design-Review Records

This directory stores attributable human decisions about AIES assessment
instruments. It does not store real-subject-panel results and cannot establish
empirical calibration.

`design-review-ledger.json` is the canonical append-only decision history. Each
event identifies a named accountable human and binds its disposition to exact
scenario IDs and canonical content hashes. A matching accepted decision makes
`design_reviewed` effective at load time without rewriting packed scenario
source. Any content change breaks the hash binding and automatically reopens the
instrument.

A tranche record means the named human accepted every exact item listed in that
event. It must disclose AI assistance and must not imply separate manual review
actions that did not occur. Automated structural or semantic preflight may
inform the human, but cannot create an accepted event on its own.

Empirical calibration remains a different workflow requiring a preregistered
real-subject panel, observed discrimination and repeatability, documented
limitations, and a subsequent human promotion decision. A design-review event
therefore always records `empirical_calibration: false`.
