"""Deterministic, claim-bounded repository engineering analysis.

This is a companion to repository-practice maturity, not a replacement for it.
It observes retained source and structured tool artifacts without executing
repository code. Findings identify evidence and limitations; no perspective is
converted into an AESQS competency score or a correctness verdict.
"""

from __future__ import annotations

import ast
import datetime
import fnmatch
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import tomllib
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

import yaml

from . import evidence_events, subjects

SCHEMA = "aies-repository-analysis/v1"
ANALYZER_VERSION = "1.0.0"
SOURCE_EXTENSIONS = {
    ".py": "Python", ".pyi": "Python", ".js": "JavaScript",
    ".jsx": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript",
    ".go": "Go", ".rs": "Rust", ".java": "Java", ".kt": "Kotlin",
    ".cs": "C#", ".cpp": "C++", ".cc": "C++", ".c": "C",
    ".h": "C/C++ Header", ".hpp": "C++ Header", ".rb": "Ruby",
    ".php": "PHP", ".swift": "Swift", ".scala": "Scala",
    ".sh": "Shell", ".ps1": "PowerShell", ".sql": "SQL",
}
TEST_MARKERS = (
    "/tests/", "/test/", "test_", "_test.", ".test.", ".spec.",
)
MAX_HASH_BYTES = 256 * 1024 * 1024
MAX_FILE_HASH_BYTES = 16 * 1024 * 1024


class RepositoryAnalysisError(ValueError):
    pass


def _digest(value: object) -> str:
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _git(root: Path, *args: str) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), *args], capture_output=True, text=True,
            timeout=20, check=False)
    except Exception:
        return None
    return completed.stdout.strip() if completed.returncode == 0 else None


@lru_cache(maxsize=1)
def _git_version() -> str | None:
    try:
        completed = subprocess.run(
            ["git", "--version"], capture_output=True, text=True,
            timeout=10, check=False)
    except Exception:
        return None
    return completed.stdout.strip() if completed.returncode == 0 else None


def _is_test(path: str) -> bool:
    lowered = "/" + path.lower()
    return any(marker in lowered for marker in TEST_MARKERS)


def _source_files(ctx) -> list[str]:
    return [
        path for path in ctx.files
        if Path(path).suffix.lower() in SOURCE_EXTENSIONS
    ]


def _snapshot(ctx) -> dict:
    """Content-bind the analyzed scope while bounding pathological files."""
    digest = hashlib.sha256()
    hashed_bytes = 0
    hashed_files = 0
    excluded = []
    for relpath in ctx.files:
        path = ctx.root / relpath
        try:
            size = path.stat().st_size
        except OSError as exc:
            excluded.append({"path": relpath, "reason": exc.__class__.__name__})
            continue
        if size > MAX_FILE_HASH_BYTES:
            excluded.append({
                "path": relpath, "reason": "file-size-bound",
                "bytes": size, "limit": MAX_FILE_HASH_BYTES,
            })
            continue
        if hashed_bytes + size > MAX_HASH_BYTES:
            excluded.append({
                "path": relpath, "reason": "analysis-byte-budget",
                "bytes": size, "limit": MAX_HASH_BYTES,
            })
            continue
        try:
            content = path.read_bytes()
        except OSError as exc:
            excluded.append({"path": relpath, "reason": exc.__class__.__name__})
            continue
        digest.update(relpath.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(size).encode())
        digest.update(b"\0")
        digest.update(hashlib.sha256(content).digest())
        hashed_bytes += size
        hashed_files += 1
    return {
        "scope_digest": "sha256:" + digest.hexdigest(),
        "files_seen": len(ctx.files),
        "files_hashed": hashed_files,
        "bytes_hashed": hashed_bytes,
        "complete": not excluded,
        "excluded": excluded,
        "limits": {
            "max_total_bytes": MAX_HASH_BYTES,
            "max_file_bytes": MAX_FILE_HASH_BYTES,
        },
    }


def _language_inventory(ctx, source_files: list[str]) -> list[dict]:
    counts: dict[str, dict] = defaultdict(lambda: {"files": 0, "bytes": 0})
    for relpath in source_files:
        language = SOURCE_EXTENSIONS[Path(relpath).suffix.lower()]
        counts[language]["files"] += 1
        try:
            counts[language]["bytes"] += (ctx.root / relpath).stat().st_size
        except OSError:
            pass
    return [
        {"language": language, **values}
        for language, values in sorted(
            counts.items(), key=lambda item: (-item[1]["bytes"], item[0]))
    ]


def _build_systems(ctx) -> list[str]:
    markers = {
        "Python/PyPA": ("pyproject.toml", "setup.py", "setup.cfg"),
        "Node/npm": ("package.json",),
        "Go modules": ("go.mod",),
        "Cargo": ("cargo.toml",),
        "Maven": ("pom.xml",),
        "Gradle": ("build.gradle", "build.gradle.kts"),
        ".NET": ("*.sln", "*.csproj"),
        "Make": ("makefile",),
        "CMake": ("cmakelists.txt",),
    }
    return [
        name for name, patterns in markers.items()
        if ctx.has_glob(*patterns)
    ]


def _repository_descriptor(ctx, snapshot: dict, source_files: list[str]) -> dict:
    if ctx.is_git:
        revisions = (_git(
            ctx.root, "rev-parse", "HEAD", "HEAD^{tree}") or "").splitlines()
        commit = revisions[0] if revisions else None
        tree = revisions[1] if len(revisions) > 1 else None
        origin = _git(ctx.root, "config", "--get", "remote.origin.url")
        dirty_lines = (
            _git(ctx.root, "status", "--porcelain=v1") or "").splitlines()
        submodules = (_git(
            ctx.root, "submodule", "status", "--recursive") or "").splitlines()
    else:
        commit = tree = origin = None
        dirty_lines = []
        submodules = []
    identity_seed = origin or str(ctx.root)
    subject_id = (
        "repository:" + ctx.root.name + ":"
        + hashlib.sha256(identity_seed.encode()).hexdigest()[:12])
    relevant_configs = [
        path for path in ctx.files if (
            Path(path).name.lower() in {
                "pyproject.toml", "package.json", "go.mod", "cargo.toml",
                "pom.xml", "build.gradle", "build.gradle.kts",
                "tsconfig.json", "ruff.toml", "mypy.ini", ".eslintrc",
                ".pre-commit-config.yaml", "codecov.yml",
            }
            or path.startswith(".github/workflows/")
        )
    ]
    environment = {
        "os": platform.platform(),
        "python": platform.python_version(),
        "git": _git_version(),
        "analyzer": f"aies-repository-analysis/{ANALYZER_VERSION}",
    }
    descriptor = subjects.repository_descriptor(
        subject_id,
        display_name=ctx.root.name,
        commit=commit,
        tree=tree or snapshot["scope_digest"],
        environment_fingerprint=_digest(environment),
        extensions={
            "repository": {
                "commit": commit,
                "tree": tree,
                "origin_digest": _digest(origin) if origin else None,
                "working_tree_dirty": bool(dirty_lines),
                "dirty_path_count": len(dirty_lines),
                "submodules": submodules,
                "analysis_scope": {
                    "root": ".",
                    "files_seen": snapshot["files_seen"],
                    "files_hashed": snapshot["files_hashed"],
                    "scope_digest": snapshot["scope_digest"],
                    "complete": snapshot["complete"],
                    "exclusions": snapshot["excluded"],
                },
                "languages": _language_inventory(ctx, source_files),
                "build_systems": _build_systems(ctx),
                "relevant_configuration": sorted(relevant_configs),
                "dependency_state_digest": _dependency_state_digest(ctx),
                "environment": environment,
            },
        },
    )
    return descriptor


def _dependency_files(ctx) -> tuple[list[str], list[str]]:
    manifest_patterns = (
        "pyproject.toml", "requirements*.txt", "package.json", "go.mod",
        "cargo.toml", "pom.xml", "build.gradle*", "gemfile", "composer.json",
    )
    lock_patterns = (
        "poetry.lock", "uv.lock", "pdm.lock", "requirements*.lock",
        "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lock*",
        "cargo.lock", "go.sum", "gemfile.lock", "composer.lock",
    )
    manifests = [
        path for path in ctx.files
        if any(fnmatch.fnmatch(Path(path).name.lower(), pattern)
               for pattern in manifest_patterns)
    ]
    locks = [
        path for path in ctx.files
        if any(fnmatch.fnmatch(Path(path).name.lower(), pattern)
               for pattern in lock_patterns)
    ]
    return sorted(manifests), sorted(locks)


def _dependency_state_digest(ctx) -> str:
    manifests, locks = _dependency_files(ctx)
    return _digest([
        {"path": path, "content": ctx.read(path)}
        for path in manifests + locks
    ])


def _python_dependencies(path: str, text: str) -> list[dict]:
    dependencies = []
    if Path(path).name == "pyproject.toml":
        try:
            data = tomllib.loads(text)
        except (tomllib.TOMLDecodeError, ValueError):
            return []
        values = ((data.get("project") or {}).get("dependencies") or [])
        for value in values:
            dependencies.append({
                "name": re.split(
                    r"[<>=!~;\[]", value, maxsplit=1)[0].strip(),
                "declaration": value,
                "pinned": bool(re.search(r"===?[^,;\s]+", value)),
                "source": path,
            })
    elif Path(path).name.lower().startswith("requirements"):
        for line in text.splitlines():
            value = line.strip()
            if not value or value.startswith(("#", "-", "http:", "https:")):
                continue
            dependencies.append({
                "name": re.split(
                    r"[<>=!~;\[]", value, maxsplit=1)[0].strip(),
                "declaration": value,
                "pinned": bool(re.search(r"===?[^,;\s]+", value)),
                "source": path,
            })
    return dependencies


def _node_dependencies(path: str, text: str) -> list[dict]:
    if Path(path).name.lower() != "package.json":
        return []
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []
    output = []
    for group in ("dependencies", "devDependencies", "peerDependencies",
                  "optionalDependencies"):
        for name, version in (data.get(group) or {}).items():
            output.append({
                "name": name, "declaration": str(version),
                "pinned": bool(re.fullmatch(r"\d+\.\d+\.\d+(?:[-+].+)?",
                                            str(version))),
                "group": group, "source": path,
            })
    return output


def _dependencies(ctx) -> dict:
    manifests, locks = _dependency_files(ctx)
    dependencies = []
    parse_failures = []
    for path in manifests:
        text = ctx.read(path)
        before = len(dependencies)
        dependencies.extend(_python_dependencies(path, text))
        dependencies.extend(_node_dependencies(path, text))
        if (Path(path).name.lower() in {"pyproject.toml", "package.json"}
                and len(dependencies) == before):
            parse_failures.append(path)
    update_automation = ctx.matching("dependabot", "renovate")
    sbom = [
        path for path in ctx.files
        if any(token in path.lower() for token in ("sbom", "cyclonedx", ".spdx"))
    ]
    findings = []
    if not manifests:
        findings.append(_finding(
            "DEP-001", "high", "dependency", "No supported dependency manifest",
            [], "Dependency scope and reproducibility cannot be established."))
    if manifests and not locks:
        findings.append(_finding(
            "DEP-002", "medium", "dependency", "No supported lockfile",
            manifests, "Declared dependency resolution may change between runs."))
    unpinned = [item for item in dependencies if not item["pinned"]]
    if unpinned:
        findings.append(_finding(
            "DEP-003", "medium", "dependency",
            f"{len(unpinned)} direct declaration(s) are not exactly pinned",
            sorted({item["source"] for item in unpinned}),
            "This is a declaration signal; lockfiles may still pin resolution."))
    return {
        "status": "observed" if manifests else "not-observed",
        "metrics": {
            "manifests": len(manifests), "lockfiles": len(locks),
            "direct_dependencies_parsed": len(dependencies),
            "unpinned_direct_declarations": len(unpinned),
            "update_automation_files": len(update_automation),
            "sbom_files": len(sbom),
        },
        "evidence": {
            "manifests": manifests, "lockfiles": locks,
            "update_automation": update_automation, "sbom": sbom,
            "parse_failures": parse_failures,
        },
        "findings": findings,
        "confidence": _confidence(
            structured=len(manifests) + len(locks),
            heuristic=len(update_automation) + len(sbom),
            coverage=1.0 if not parse_failures else 0.7,
            limitations=[
                "Dependency declarations are inventoried; packages are not "
                "resolved, downloaded, or vulnerability-scanned.",
                "Cross-language dependency health is not normalized into a score.",
            ]),
    }


def _module_name(path: str) -> str:
    without = str(Path(path).with_suffix("")).replace("\\", "/")
    if without.endswith("/__init__"):
        without = without[:-9]
    for marker in ("/src/", "/lib/"):
        if marker in "/" + without:
            without = ("/" + without).split(marker, 1)[1]
            break
    return without.strip("/").replace("/", ".")


def _resolve_python_import(name: str, modules: set[str]) -> str | None:
    candidates = sorted(
        (module for module in modules
         if module == name or module.startswith(name + ".")
         or name.startswith(module + ".")),
        key=len)
    return candidates[0] if candidates else None


def _strong_components(graph: dict[str, set[str]]) -> list[list[str]]:
    index = 0
    stack = []
    on_stack = set()
    indices = {}
    low = {}
    components = []

    def visit(node):
        nonlocal index
        indices[node] = low[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for target in graph.get(node, set()):
            if target not in indices:
                visit(target)
                low[node] = min(low[node], low[target])
            elif target in on_stack:
                low[node] = min(low[node], indices[target])
        if low[node] == indices[node]:
            component = []
            while True:
                value = stack.pop()
                on_stack.remove(value)
                component.append(value)
                if value == node:
                    break
            if len(component) > 1:
                components.append(sorted(component))

    for node in sorted(graph):
        if node not in indices:
            visit(node)
    return sorted(components)


def _architecture(ctx, source_files: list[str]) -> dict:
    python_files = [path for path in source_files if path.endswith((".py", ".pyi"))]
    modules = {_module_name(path): path for path in python_files}
    graph: dict[str, set[str]] = {module: set() for module in modules}
    parse_failures = []
    for module, path in modules.items():
        try:
            tree = ast.parse(ctx.read(path), filename=path)
        except SyntaxError:
            parse_failures.append(path)
            continue
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                target = _resolve_python_import(name, set(modules))
                if target and target != module:
                    graph[module].add(target)
    edges = sorted(
        [
            {"from": modules[source], "to": modules[target]}
            for source, targets in graph.items() for target in targets
        ],
        key=lambda item: (item["from"], item["to"]),
    )
    cycles = [
        [modules[module] for module in component]
        for component in _strong_components(graph)
    ]
    coupling = sorted([
        {"artifact": modules[module], "outgoing_internal_dependencies": len(targets)}
        for module, targets in graph.items() if len(targets) >= 8
    ], key=lambda item: (-item["outgoing_internal_dependencies"], item["artifact"]))
    adrs = [
        path for path in ctx.files
        if ("adr/" in path.lower() or "decisions/" in path.lower())
        and path.lower().endswith(".md")
    ]
    adr_refs = []
    source_set = set(source_files)
    for adr in adrs:
        referenced = sorted({
            token for token in re.findall(r"`([^`]+\.[A-Za-z0-9]+)`", ctx.read(adr))
            if token.replace("\\", "/") in source_set
        })
        adr_refs.append({"adr": adr, "source_references": referenced})
    layers, layer_violations, layer_error = _declared_layers(ctx, edges)
    findings = []
    for index, cycle in enumerate(cycles, start=1):
        findings.append(_finding(
            f"ARCH-CYCLE-{index:03d}", "medium", "architecture",
            "Internal dependency cycle observed", cycle,
            "Cycle is structural evidence; architectural harm depends on intent."))
    for index, violation in enumerate(layer_violations, start=1):
        findings.append(_finding(
            f"ARCH-LAYER-{index:03d}", "high", "architecture",
            f"Declared layer boundary violation: {violation['from_layer']} "
            f"to {violation['to_layer']}",
            [violation["from"], violation["to"]],
            "Violation is evaluated only against repository-declared layer policy."))
    for item in coupling[:20]:
        findings.append(_finding(
            f"ARCH-COUPLING-{len(findings)+1:03d}", "low", "architecture",
            f"High internal fan-out ({item['outgoing_internal_dependencies']})",
            [item["artifact"]],
            "Fan-out is a review signal, not proof of poor architecture."))
    return {
        "status": "observed" if source_files else "not-observed",
        "metrics": {
            "source_artifacts": len(source_files),
            "python_modules_parsed": len(python_files) - len(parse_failures),
            "internal_dependency_edges": len(edges),
            "dependency_cycles": len(cycles),
            "declared_layers": len(layers),
            "layer_violations": len(layer_violations),
            "architecture_decision_records": len(adrs),
            "adrs_with_source_references": sum(
                bool(item["source_references"]) for item in adr_refs),
        },
        "evidence": {
            "topology_edges": edges[:500],
            "cycles": cycles,
            "high_fan_out": coupling,
            "architecture_decisions": adr_refs,
            "declared_layers": layers,
            "layer_policy_error": layer_error,
            "parse_failures": parse_failures,
        },
        "findings": findings,
        "confidence": _confidence(
            structured=len(layers) + len(adrs),
            heuristic=len(python_files),
            coverage=(0 if not source_files else
                      (len(python_files) - len(parse_failures))
                      / max(1, len(source_files))),
            limitations=[
                "Import topology is currently language-aware for Python; other "
                "languages remain inventoried but not graph-parsed.",
                "Cycles and fan-out are review signals, not quality verdicts.",
                "Layer violations require repository-declared policy.",
            ]),
    }


def _declared_layers(ctx, edges: list[dict]) -> tuple[list[dict], list[dict], str | None]:
    config_path = next((
        path for path in ctx.files
        if Path(path).name == "aies-repository-analysis.yaml"), None)
    if not config_path:
        return [], [], None
    try:
        data = yaml.safe_load(ctx.read(config_path)) or {}
        raw_layers = data.get("layers") or {}
        layers = [
            {"name": name, "include": value.get("include") or [],
             "may_depend_on": value.get("may_depend_on") or []}
            for name, value in raw_layers.items()
        ]
    except Exception as exc:
        return [], [], f"{config_path}: {exc.__class__.__name__}"

    def layer_for(path):
        return next((
            layer["name"] for layer in layers
            if any(fnmatch.fnmatch(path, pattern)
                   for pattern in layer["include"])), None)

    allowed = {layer["name"]: set(layer["may_depend_on"]) | {layer["name"]}
               for layer in layers}
    violations = []
    for edge in edges:
        source = layer_for(edge["from"])
        target = layer_for(edge["to"])
        if source and target and target not in allowed.get(source, {source}):
            violations.append({
                **edge, "from_layer": source, "to_layer": target})
    return layers, violations, None


def _function_complexity(tree: ast.AST, path: str) -> list[dict]:
    rows = []
    branch_nodes = (
        ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With,
        ast.AsyncWith, ast.BoolOp, ast.IfExp, ast.Match,
    )
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        complexity = 1 + sum(
            isinstance(child, branch_nodes) for child in ast.walk(node))
        length = max(1, (getattr(node, "end_lineno", node.lineno) - node.lineno + 1))
        rows.append({
            "artifact": path, "function": node.name, "line": node.lineno,
            "complexity_signal": complexity, "lines": length,
        })
    return rows


def _code_quality(ctx, source_files: list[str]) -> dict:
    total_lines = 0
    test_lines = 0
    parse_failures = []
    complex_functions = []
    large_files = []
    todo_locations = []
    duplicate_index: dict[str, list[dict]] = defaultdict(list)
    python_functions = python_docstrings = 0
    for path in source_files:
        text = ctx.read(path)
        lines = text.splitlines()
        total_lines += len(lines)
        if _is_test(path):
            test_lines += len(lines)
        if len(lines) > 700:
            large_files.append({"artifact": path, "lines": len(lines)})
        for number, line in enumerate(lines, start=1):
            if re.search(r"\b(TODO|FIXME|HACK)\b", line, re.IGNORECASE):
                todo_locations.append({"artifact": path, "line": number})
        normalized = [
            re.sub(r"\s+", " ", line.strip()) for line in lines
            if line.strip() and not line.lstrip().startswith(("#", "//", "*"))
        ]
        for index in range(max(0, len(normalized) - 7)):
            block = "\n".join(normalized[index:index + 8])
            if len(block) >= 160:
                duplicate_index[hashlib.sha256(block.encode()).hexdigest()].append(
                    {"artifact": path, "normalized_line": index + 1})
        if path.endswith((".py", ".pyi")):
            try:
                tree = ast.parse(text, filename=path)
            except SyntaxError:
                parse_failures.append(path)
                continue
            functions = [
                node for node in ast.walk(tree)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
            python_functions += len(functions)
            python_docstrings += sum(bool(ast.get_docstring(node)) for node in functions)
            complex_functions.extend(_function_complexity(tree, path))
    complex_functions = [
        row for row in complex_functions
        if row["complexity_signal"] > 15 or row["lines"] > 100
    ]
    duplicates = [
        occurrences for occurrences in duplicate_index.values()
        if len({item["artifact"] for item in occurrences}) > 1
    ][:50]
    lint_configs = ctx.matching(
        "ruff.toml", ".flake8", "eslint", "pylintrc", "biome.json",
        "golangci", "clippy")
    type_configs = ctx.matching(
        "mypy.ini", "pyrightconfig", "tsconfig.json", "strict")
    findings = []
    for index, item in enumerate(complex_functions[:50], start=1):
        findings.append(_finding(
            f"QUALITY-COMPLEX-{index:03d}", "medium", "code-quality",
            f"Complex or long function: {item['function']}",
            [f"{item['artifact']}:{item['line']}"],
            f"Signal complexity={item['complexity_signal']}, lines={item['lines']}; "
            "review intent before refactoring."))
    for index, item in enumerate(large_files[:30], start=1):
        findings.append(_finding(
            f"QUALITY-SIZE-{index:03d}", "low", "code-quality",
            f"Large source artifact ({item['lines']} lines)",
            [item["artifact"]], "Size is a review signal, not a defect."))
    if duplicates:
        findings.append(_finding(
            "QUALITY-DUPLICATION-001", "low", "code-quality",
            f"{len(duplicates)} repeated normalized block(s) across files",
            sorted({item["artifact"] for group in duplicates for item in group}),
            "Lexical duplication requires semantic review before consolidation."))
    return {
        "status": "observed" if source_files else "not-observed",
        "metrics": {
            "source_files": len(source_files), "source_lines": total_lines,
            "test_lines": test_lines,
            "test_to_source_line_percent": round(
                test_lines / max(1, total_lines) * 100, 1),
            "python_parse_failures": len(parse_failures),
            "complex_or_long_functions": len(complex_functions),
            "large_source_files": len(large_files),
            "duplicate_block_groups": len(duplicates),
            "todo_fixme_markers": len(todo_locations),
            "python_documented_function_percent": (
                round(python_docstrings / python_functions * 100, 1)
                if python_functions else None),
            "lint_configuration_files": len(lint_configs),
            "type_check_configuration_files": len(type_configs),
        },
        "evidence": {
            "lint_configuration": lint_configs,
            "type_check_configuration": type_configs,
            "parse_failures": parse_failures,
            "complex_or_long_functions": complex_functions[:100],
            "large_source_files": large_files,
            "duplicate_blocks": duplicates,
            "todo_fixme_locations": todo_locations[:100],
        },
        "findings": findings,
        "confidence": _confidence(
            structured=len(lint_configs) + len(type_configs),
            heuristic=len(source_files),
            coverage=(len(source_files) - len(parse_failures))
            / max(1, len(source_files)),
            limitations=[
                "Complexity and duplication are bounded static signals; native "
                "linter, type-checker, and duplication reports are not executed.",
                "No cross-language maintainability score is produced.",
                "Dead-code and trend claims require language-native historical evidence.",
            ]),
    }


def _coverage_artifacts(ctx) -> tuple[list[dict], list[str]]:
    values = []
    failures = []
    for path in ctx.files:
        name = Path(path).name.lower()
        if name == "coverage.json":
            try:
                data = json.loads(ctx.read(path))
                percent = ((data.get("totals") or {}).get("percent_covered"))
                values.append({"artifact": path, "line_percent": percent,
                               "format": "coverage.py-json"})
            except (json.JSONDecodeError, ValueError):
                failures.append(path)
        elif name in {"coverage.xml", "cobertura.xml"}:
            try:
                root = ET.fromstring(ctx.read(path))
                rate = root.attrib.get("line-rate")
                values.append({
                    "artifact": path,
                    "line_percent": round(float(rate) * 100, 2) if rate else None,
                    "format": "cobertura-xml",
                })
            except (ET.ParseError, ValueError):
                failures.append(path)
    return values, failures


def _test_results(ctx) -> tuple[list[dict], list[str]]:
    results = []
    failures = []
    for path in ctx.files:
        name = Path(path).name.lower()
        if not (name.startswith(("junit", "test-results", "test_result"))
                and name.endswith(".xml")):
            continue
        try:
            root = ET.fromstring(ctx.read(path))
            suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
            results.append({
                "artifact": path,
                "tests": sum(int(s.attrib.get("tests", 0)) for s in suites),
                "failures": sum(int(s.attrib.get("failures", 0)) for s in suites),
                "errors": sum(int(s.attrib.get("errors", 0)) for s in suites),
                "skipped": sum(int(s.attrib.get("skipped", 0)) for s in suites),
            })
        except (ET.ParseError, ValueError):
            failures.append(path)
    return results, failures


def _correctness(ctx, source_files: list[str]) -> dict:
    tests = [path for path in source_files if _is_test(path)]
    coverage, coverage_failures = _coverage_artifacts(ctx)
    test_results, result_failures = _test_results(ctx)
    ci = [
        path for path in ctx.files
        if path.startswith(".github/workflows/")
        or Path(path).name.lower() in {
            ".gitlab-ci.yml", "azure-pipelines.yml", "jenkinsfile"}]
    mutation = [
        path for path in ctx.files
        if any(token in path.lower() for token in (
            "mutmut", "cosmic-ray", "stryker", "pitest", "mutation"))]
    property_tests = [
        path for path in tests
        if any(token in ctx.read(path).lower() for token in (
            "hypothesis", "fast-check", "proptest", "quickcheck"))]
    contract_tests = [
        path for path in tests
        if "contract" in path.lower() or "pact" in ctx.read(path).lower()]
    failures = sum(item["failures"] + item["errors"] for item in test_results)
    tests_reported = sum(item["tests"] for item in test_results)
    coverage_values = [
        item["line_percent"] for item in coverage
        if isinstance(item.get("line_percent"), (int, float))]
    findings = []
    if not tests:
        findings.append(_finding(
            "CORRECTNESS-001", "high", "correctness",
            "No test source was detected", [],
            "Absence of retained tests leaves intended behavior unobserved."))
    if tests and not test_results:
        findings.append(_finding(
            "CORRECTNESS-002", "medium", "correctness",
            "Tests exist but no structured execution result was retained",
            tests[:20],
            "Test presence is not execution evidence."))
    if failures:
        findings.append(_finding(
            "CORRECTNESS-003", "high", "correctness",
            f"Retained test results contain {failures} failure/error(s)",
            [item["artifact"] for item in test_results if
             item["failures"] or item["errors"]],
            "Failure evidence is reported directly and is not averaged away."))
    if tests and not coverage:
        findings.append(_finding(
            "CORRECTNESS-004", "medium", "correctness",
            "No supported structured coverage artifact was retained",
            tests[:20],
            "Untested behavior cannot be estimated from test-file count."))
    return {
        "status": "observed" if tests or test_results else "not-observed",
        "metrics": {
            "test_source_files": len(tests),
            "ci_configuration_files": len(ci),
            "structured_test_result_artifacts": len(test_results),
            "tests_reported": tests_reported,
            "test_failures_or_errors": failures,
            "retained_test_pass_percent": (
                round((tests_reported - failures) / tests_reported * 100, 1)
                if tests_reported else None),
            "coverage_artifacts": len(coverage),
            "retained_line_coverage_percent": (
                max(coverage_values) if coverage_values else None),
            "mutation_evidence_files": len(mutation),
            "property_test_files": len(property_tests),
            "contract_test_files": len(contract_tests),
        },
        "evidence": {
            "test_sources": tests[:500], "ci_configuration": ci,
            "test_results": test_results, "coverage": coverage,
            "mutation": mutation, "property_tests": property_tests,
            "contract_tests": contract_tests,
            "parse_failures": coverage_failures + result_failures,
        },
        "findings": findings,
        "confidence": _confidence(
            structured=len(test_results) + len(coverage) + len(mutation),
            heuristic=len(tests) + len(ci),
            coverage=(1.0 if test_results else 0.4 if tests else 0.0),
            limitations=[
                "Repository code and tests are not executed by this read-only analysis.",
                "Passing retained tests demonstrate only the exercised behavior; "
                "they do not prove repository correctness.",
                "Coverage, mutation, property, and contract evidence is absent "
                "unless a supported artifact or explicit source signal is retained.",
            ]),
    }


def _sarif_summary(ctx) -> tuple[list[dict], list[str]]:
    summaries = []
    failures = []
    for path in ctx.files:
        if not path.lower().endswith((".sarif", ".sarif.json")):
            continue
        try:
            data = json.loads(ctx.read(path))
            if data.get("version") != "2.1.0":
                failures.append(path)
                continue
            counter = Counter()
            tools = []
            for run in data.get("runs") or []:
                driver = ((run.get("tool") or {}).get("driver") or {})
                tools.append({
                    "name": driver.get("name"),
                    "version": driver.get("semanticVersion")
                    or driver.get("version"),
                })
                counter.update(
                    result.get("level", "warning")
                    for result in run.get("results") or [])
            summaries.append({
                "artifact": path, "tools": tools,
                "findings": sum(counter.values()),
                "levels": dict(sorted(counter.items())),
            })
        except (json.JSONDecodeError, ValueError):
            failures.append(path)
    return summaries, failures


def _security(ctx) -> dict:
    sarif, parse_failures = _sarif_summary(ctx)
    scanners = ctx.matching(
        "codeql", "semgrep", "gitleaks", "trufflehog", "detect-secrets",
        "snyk", "trivy", "dependabot")
    policies = ctx.matching("security.md", "security-policy")
    secrets_files = [
        path for path in ctx.files
        if Path(path).name.lower() in {".env", ".npmrc", ".pypirc"}
        and (not ctx.is_git or path in ctx.tracked)
    ]
    total_findings = sum(item["findings"] for item in sarif)
    errors = sum(item["levels"].get("error", 0) for item in sarif)
    findings = []
    if secrets_files:
        findings.append(_finding(
            "SECURITY-001", "critical", "security",
            "Sensitive configuration filename is retained in analyzed scope",
            secrets_files,
            "Filename evidence is not proof of a secret; inspect and remove or "
            "replace with a documented example."))
    if not scanners and not sarif:
        findings.append(_finding(
            "SECURITY-002", "medium", "security",
            "No supported security scanner configuration or SARIF evidence",
            [], "Scanner absence is an evidence gap, not proof of vulnerability."))
    if errors:
        findings.append(_finding(
            "SECURITY-003", "high", "security",
            f"Retained SARIF contains {errors} error-level finding(s)",
            [item["artifact"] for item in sarif
             if item["levels"].get("error", 0)],
            "Tool findings require triage; severity is preserved, not remapped."))
    return {
        "status": "observed" if scanners or sarif or policies else "not-observed",
        "metrics": {
            "scanner_configuration_signals": len(scanners),
            "security_policy_files": len(policies),
            "sarif_artifacts": len(sarif),
            "sarif_findings": total_findings,
            "sarif_error_findings": errors,
            "sensitive_configuration_filenames": len(secrets_files),
        },
        "evidence": {
            "scanner_configuration": scanners,
            "policies": policies,
            "sarif": sarif,
            "sensitive_configuration_filenames": secrets_files,
            "parse_failures": parse_failures,
        },
        "findings": findings,
        "confidence": _confidence(
            structured=len(sarif), heuristic=len(scanners) + len(policies),
            coverage=1.0 if sarif else 0.4 if scanners else 0.0,
            limitations=[
                "This analysis does not search file contents for secrets, "
                "execute SAST, or resolve vulnerabilities.",
                "SARIF findings retain tool semantics and do not prove "
                "exploitability, correctness, or conformance.",
                "An empty successful scan narrows only that tool's declared scope.",
            ]),
    }


def _finding(
    finding_id: str,
    severity: str,
    perspective: str,
    title: str,
    artifacts: list[str],
    interpretation: str,
) -> dict:
    return {
        "id": finding_id,
        "severity": severity,
        "perspective": perspective,
        "title": title,
        "artifacts": artifacts,
        "interpretation": interpretation,
    }


def _confidence(
    *,
    structured: int,
    heuristic: int,
    coverage: float,
    limitations: list[str],
) -> dict:
    coverage = max(0.0, min(1.0, coverage))
    if structured >= 2 and coverage >= 0.8:
        level = "high"
    elif structured or heuristic:
        level = "medium" if coverage >= 0.5 else "low"
    else:
        level = "not-established"
    return {
        "level": level,
        "coverage_percent": round(coverage * 100, 1),
        "structured_sources": structured,
        "heuristic_sources": heuristic,
        "limitations": limitations,
        "interpretation": (
            "Confidence describes evidence coverage for this perspective; "
            "it is not confidence that the repository is correct or good."),
    }


def _remediation(
    findings: list[dict],
    repo_argument: str,
) -> list[dict]:
    priority = {"critical": 1, "high": 2, "medium": 3, "low": 4}
    actions = {
        "architecture": (
            "Review the identified topology against intended boundaries; "
            "declare enforceable layers and add an architecture fitness test.",
            "Declared boundaries pass their repository-native architecture check."),
        "code-quality": (
            "Confirm the signal with language-native lint/type/complexity tools "
            "and refactor only behavior-preserving, tested candidates.",
            "Native quality checks pass and affected behavior remains covered."),
        "correctness": (
            "Retain reproducible test, coverage, and where appropriate mutation "
            "or property/contract-test results for the changed scope.",
            "Structured results show the intended suite ran with no unresolved failures."),
        "security": (
            "Triage retained findings, enable a scoped security scanner, and "
            "retain its versioned SARIF result.",
            "Findings have documented disposition and a repeat scan is retained."),
        "dependency": (
            "Declare and lock dependencies, enable update review, and retain an "
            "SBOM plus scoped vulnerability evidence.",
            "Manifest, lockfile, update policy, SBOM, and scan evidence are retained."),
    }
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for finding in findings:
        family = re.sub(r"-\d{3}$", "", finding["id"])
        grouped[
            (finding["severity"], finding["perspective"], family)
        ].append(finding)
    output = []
    for (severity, perspective, family), members in sorted(
            grouped.items(), key=lambda item: (
                priority.get(item[0][0], 9), item[0][1], item[0][2])):
        finding = members[0]
        action, acceptance = actions[finding["perspective"]]
        output.append({
            "id": "REM-" + family,
            "priority": priority.get(severity, 9),
            "severity": severity,
            "perspective": perspective,
            "impact": (
                finding["title"] if len(members) == 1
                else f"{len(members)} related findings: {finding['title']}"),
            "finding_ids": [item["id"] for item in members],
            "evidence_refs": sorted({
                artifact for item in members for artifact in item["artifacts"]
            }),
            "recommendation": action,
            "acceptance_signal": acceptance,
            "owner_authority": (
                "Repository owner assigns and accepts the change; AIES does not."),
            "dependencies": [],
            "reassessment_trigger": (
                "Material source, dependency, configuration, tool, or evidence change."),
            "reassessment_command": f"aies audit {repo_argument}",
        })
    return output


def analyze(ctx, audit_results: list[dict] | None = None) -> dict:
    """Analyze one already-scanned repository without executing its code."""
    started = datetime.datetime.now(datetime.timezone.utc)
    source_files = _source_files(ctx)
    snapshot = _snapshot(ctx)
    descriptor = _repository_descriptor(ctx, snapshot, source_files)
    perspectives = {
        "architecture": _architecture(ctx, source_files),
        "code_quality": _code_quality(ctx, source_files),
        "correctness_assurance": _correctness(ctx, source_files),
        "security": _security(ctx),
        "dependencies": _dependencies(ctx),
    }
    findings = [
        finding for perspective in perspectives.values()
        for finding in perspective["findings"]
    ]
    if audit_results:
        for check in audit_results:
            if check["state"] != "gap":
                continue
            findings.append(_finding(
                "PRACTICE-" + check["id"].upper(), "medium",
                "security" if check["area"] == "CA-07" else "code-quality",
                check["title"], [check.get("evidence")] if check.get("evidence") else [],
                "Repository-practice gap from the separate conformance layer."))
    recommendations = _remediation(findings, f'"{ctx.root}"')
    events = []
    for name, perspective in perspectives.items():
        payload = {
            "perspective": name,
            "status": perspective["status"],
            "metrics": perspective["metrics"],
            "finding_ids": [item["id"] for item in perspective["findings"]],
            "confidence": perspective["confidence"],
        }
        events.append(evidence_events.build(
            event_type="observation",
            subject_id=descriptor["id"],
            instrument_id=f"repository-{name}/v1",
            modality="repository-static-analysis",
            source="aies-repository-analysis",
            source_record_id=f"{snapshot['scope_digest']}:{name}",
            source_digest=snapshot["scope_digest"],
            adapter_profile="aies-repository-analysis/v1",
            observed_at=started.isoformat(),
            classification=descriptor["privacy"],
            payload=payload,
        ))
    replay = evidence_events.replay(events)
    finished = datetime.datetime.now(datetime.timezone.utc)
    return {
        "kind": "repository-engineering-analysis",
        "schema": SCHEMA,
        "analyzer": {
            "id": "aies-repository-analysis",
            "version": ANALYZER_VERSION,
            "execution": "read-only-static-and-retained-artifact-analysis",
        },
        "subject": descriptor,
        "snapshot": snapshot,
        "perspectives": perspectives,
        "findings": sorted(findings, key=lambda item: (
            {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(
                item["severity"], 9),
            item["perspective"], item["id"])),
        "remediation_plan": recommendations,
        "events": events,
        "event_replay": replay,
        "timing": {
            "started_at": started.isoformat(),
            "completed_at": finished.isoformat(),
            "elapsed_seconds": round((finished - started).total_seconds(), 3),
        },
        "claim_boundary": (
            "This analysis reports deterministic source and retained-tool "
            "evidence. It does not execute code, prove correctness or security, "
            "assign an AESQS competency score, or make a conformance decision."),
    }


def render_markdown(analysis: dict) -> str:
    lines = [
        "## Repository Engineering Analysis",
        "",
        "> **INFORMATIONAL — STATIC AND RETAINED-ARTIFACT EVIDENCE ONLY.**",
        "",
        f"Subject: `{analysis['subject']['id']}` · snapshot "
        f"`{analysis['snapshot']['scope_digest']}`",
        "",
        "| Perspective | Status | Evidence confidence | Key observations | Findings |",
        "|---|---|---|---:|---:|",
    ]
    for name, perspective in analysis["perspectives"].items():
        metrics = perspective["metrics"]
        observations = sum(
            value for value in metrics.values()
            if isinstance(value, int))
        label = name.replace("_", " ").title()
        confidence = perspective["confidence"]
        lines.append(
            f"| {label} | {perspective['status']} | "
            f"{confidence['level']} ({confidence['coverage_percent']:.0f}%) | "
            f"{observations} | {len(perspective['findings'])} |")
    lines += ["", "### Evidence-linked findings", ""]
    if not analysis["findings"]:
        lines.append(
            "No bounded analyzer finding was emitted. This is not proof that "
            "the repository has no defects.")
    for finding in analysis["findings"]:
        artifacts = ", ".join(
            f"`{path}`" for path in finding["artifacts"]) or "no retained artifact"
        lines.append(
            f"- **{finding['severity'].upper()} · {finding['perspective']} · "
            f"{finding['id']}** — {finding['title']}. Evidence: {artifacts}. "
            f"{finding['interpretation']}")
    lines += ["", "### Evidence-linked remediation plan", ""]
    for item in analysis["remediation_plan"]:
        lines.append(
            f"{item['priority']}. **{item['id']} — {item['impact']}**  \n"
            f"   Action: {item['recommendation']}  \n"
            f"   Acceptance: {item['acceptance_signal']}  \n"
            f"   Reassess: `{item['reassessment_command']}`")
    lines += ["", "### Analysis limitations", ""]
    limitations = sorted({
        limitation
        for perspective in analysis["perspectives"].values()
        for limitation in perspective["confidence"]["limitations"]
    })
    lines.extend(f"- {limitation}" for limitation in limitations)
    lines += ["", analysis["claim_boundary"]]
    return "\n".join(lines)
