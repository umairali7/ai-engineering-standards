# Versioning and Release Identity

AIES is one repository containing a governed standard and an executable
reference platform, but it is not one undifferentiated version number. A
release or report MUST identify the axis it means.

| Axis | Current identity | What changes it | What it does not claim |
|---|---|---|---|
| AIES standards corpus | `v0.4.0` | Governed content release under `GOVERNANCE.md` | That every document is Approved or empirically validated |
| Python platform distribution | `aies-platform 0.1.0` | Executable public development preview under semantic versioning | A stable 1.0 software release, qualification, standards approval, or measurement validity |
| Artifact schemas | Individually stamped in each artifact | A breaking or append-only contract change under `STABILITY.md` and `COMPATIBILITY.md` | Subject capability or evidence quality |
| Assessment/profile content | Version in each suite, assessment, profile, mapping, or instrument digest | A change to that governed measurement content | Compatibility with differently versioned evidence |
| Run evidence | Run ID, frozen suite/profile/instrument versions, and content digests | A new execution or imported evidence package | Transferability to another environment or subject |

Run `aies version` for the installed software's machine-readable inventory and
`aies --version` when only the platform package version is needed.
The complete artifact and consumer-view table is maintained in
[AIES-PLAT-05 — Platform Reference](../platform/REFERENCE.md#2-artifacts-and-their-versions).

The words `v1`, `v1.0`, or schema `1` in a contract name identify that
individual interface. This includes the historical “v1.0 Architecture Freeze”
in [STABILITY.md](../STABILITY.md). None of those labels means that the AIES
standards corpus has reached its pending v1.0 release or that the Python
platform has reached version 1.0.

The source repository is already public for development, testing, and external
review. That visibility is not the same event as a signed immutable platform
distribution or the separately governed v1.0 standards release.

## Local release bundle

From an isolated environment in `platform/`:

```text
python -m pip install build
python scripts/build_release_bundle.py --build
```

The command builds and validates exactly one wheel and source distribution,
checks package name/version/license metadata and the packaged Apache 2.0 text,
then emits `dist/SHA256SUMS` and `dist/release-manifest.json`. Set
`SOURCE_DATE_EPOCH` for a reproducible manifest timestamp and `AIES_REVISION`
when Git metadata is unavailable.

The manifest deliberately reports `signed: false` and
`provenance_attested: false`. Hashes prove byte identity; they do not prove
authorship, build provenance, safety, correctness, standards approval, or
measurement validity. The public release remains incomplete until CI-built
artifacts are signed/attested, independently verified, tested on clean
supported systems, and linked to release notes and the exact source revision.
