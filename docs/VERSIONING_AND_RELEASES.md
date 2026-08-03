# Versioning and Release Identity

AIES is one repository containing a governed standard and an executable
reference platform, but it is not one undifferentiated version number. A
release or report MUST identify the axis it means.

| Axis | Current identity | What changes it | What it does not claim |
|---|---|---|---|
| AIES standards corpus | `v0.4.0` | Governed content release under `GOVERNANCE.md` | That every document is Approved or empirically validated |
| Python platform distribution | `aies-platform 0.1.0` | Executable software release under semantic versioning | Qualification, standards approval, or measurement validity |
| Artifact schemas | Individually stamped in each artifact | A breaking or append-only contract change under `STABILITY.md` and `COMPATIBILITY.md` | Subject capability or evidence quality |
| Assessment/profile content | Version in each suite, assessment, profile, mapping, or instrument digest | A change to that governed measurement content | Compatibility with differently versioned evidence |
| Run evidence | Run ID, frozen suite/profile/instrument versions, and content digests | A new execution or imported evidence package | Transferability to another environment or subject |

Run `aies version` for the installed software's machine-readable inventory and
`aies --version` when only the platform package version is needed.

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
