# AIES Path-Based Licensing

AI Engineering Standards (AIES) intentionally combines an openly licensed
engineering standard with an open-source executable platform. Each repository
path receives one applicable license according to the table below. This notice
implements [ADR-0014](adr/ADR-0014-Dual-License-Standards-and-Software.md),
accepted on 2026-08-03.

## License precedence

Apply these rules in order:

1. Third-party material retains the license and notice supplied with it.
2. A file-specific `SPDX-License-Identifier` or explicit license notice
   overrides the path default.
3. Otherwise, apply the path default below.

## Path defaults

| Path or material | License |
|---|---|
| Root Markdown documents (`/*.md`) | [CC BY-SA 4.0](LICENSES/CC-BY-SA-4.0.txt) |
| `Shared/`, `AEBOK/`, `AESQS/`, `AEOS/`, `AEAR/`, `AECT/`, `ECM/`, `adr/`, `docs/`, `research/`, `templates/`, and `diagrams/` | [CC BY-SA 4.0](LICENSES/CC-BY-SA-4.0.txt) |
| Narrative and data-first material under `examples/` | [CC BY-SA 4.0](LICENSES/CC-BY-SA-4.0.txt), unless an executable source file carries an Apache-2.0 notice |
| `platform/*.md`; platform assessment, calibration, competency, journey, profile, subject-profile, and task-mapping directories; and platform root YAML assessment data | [CC BY-SA 4.0](LICENSES/CC-BY-SA-4.0.txt) |
| Declarative conformance fixtures under `conformance/corpus/` and `conformance/*.md` | [CC BY-SA 4.0](LICENSES/CC-BY-SA-4.0.txt) |
| `platform/src/`, `platform/tests/`, `platform/scripts/`, `platform/contracts/`, `platform/examples/`, platform packaging/build configuration, and container/build files | [Apache License 2.0](LICENSES/Apache-2.0.txt) |
| Executable conformance engines and generators (`conformance/*.py`) | [Apache License 2.0](LICENSES/Apache-2.0.txt) |
| `.github/`, repository automation, and non-content repository configuration | [Apache License 2.0](LICENSES/Apache-2.0.txt) |
| `LICENSES/` | The corresponding unmodified license text or third-party notice |

The machine-checked boundary is implemented by
`platform/scripts/check_license_boundaries.py`. A mixed-purpose file must be
split or carry an explicit file-level license notice; ambiguity is a release
error.

## What the licenses permit

- **CC BY-SA 4.0** permits sharing and adaptation, including commercial use,
  subject to attribution and ShareAlike requirements.
- **Apache License 2.0** permits use, modification, and distribution of the
  executable software under its copyright, notice, and patent terms.

The complete official texts are:

- [Creative Commons Attribution-ShareAlike 4.0 International](LICENSES/CC-BY-SA-4.0.txt)
- [Apache License 2.0](LICENSES/Apache-2.0.txt)

## Contributions, trademarks, and warranties

Contributors retain copyright in their contributions and certify contribution
rights under the Developer Certificate of Origin described in
[CONTRIBUTING.md](CONTRIBUTING.md). Contributions are made under the license
applicable to the destination path.

These licenses do not grant rights to AIES names, logos, marks, certification
claims, or endorsements. The licenses provide the material without warranties;
read their complete terms before relying on them.
