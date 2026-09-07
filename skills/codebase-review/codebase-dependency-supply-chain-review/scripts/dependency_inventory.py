#!/usr/bin/env python3
"""Read-only dependency inventory helper for supply-chain reviews."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None


SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".cache",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "target",
    ".gradle",
    ".idea",
}

VENDORED_DIR_NAMES = {
    "vendor",
    "vendors",
    "third_party",
    "third-party",
    "3rdparty",
    "external",
    "extern",
    "deps",
    "dependencies",
}

GENERATED_DIR_NAMES = {
    "generated",
    "gen",
    "openapi",
    "swagger",
    "grpc",
    "proto",
    "protobuf",
}

MANIFEST_NAMES = {
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "setup.py",
    "setup.cfg",
    "Pipfile",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "settings.gradle",
    "settings.gradle.kts",
    "composer.json",
    "Gemfile",
    "Package.swift",
    "pubspec.yaml",
    "packages.config",
    "Directory.Packages.props",
}

LOCKFILE_NAMES = {
    "package-lock.json",
    "npm-shrinkwrap.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "bun.lock",
    "bun.lockb",
    "uv.lock",
    "poetry.lock",
    "Pipfile.lock",
    "requirements.lock",
    "requirements.txt.lock",
    "Cargo.lock",
    "go.sum",
    "Gemfile.lock",
    "composer.lock",
    "packages.lock.json",
    "gradle.lockfile",
    "Package.resolved",
    "pubspec.lock",
}

REGISTRY_CONFIG_NAMES = {
    ".npmrc",
    ".yarnrc",
    ".yarnrc.yml",
    ".pypirc",
    "pip.conf",
    "pip.ini",
    "nuget.config",
    "NuGet.config",
    "settings.xml",
    "gradle.properties",
    "composer.json",
}

CI_FILE_PATTERNS = (
    ".github/workflows/",
    ".gitlab-ci.yml",
    "azure-pipelines.yml",
    "Jenkinsfile",
    "bitbucket-pipelines.yml",
    ".circleci/config.yml",
)

INSTALL_COMMAND_RE = re.compile(
    r"\b("
    r"npm\s+(ci|install)|yarn\s+install|pnpm\s+install|bun\s+install|"
    r"pip\s+install|python\s+-m\s+pip\s+install|uv\s+sync|uv\s+pip\s+install|"
    r"poetry\s+install|pipenv\s+sync|bundle\s+install|composer\s+install|"
    r"cargo\s+(fetch|build|test)|go\s+mod\s+download|mvn\s+.*(install|test|dependency)|"
    r"gradle\s+.*(build|test|dependencies)|dotnet\s+restore"
    r")\b",
    re.IGNORECASE,
)

DOWNLOAD_COMMAND_RE = re.compile(r"\b(curl|wget)\b[^\n]*(https?://[^\s\"')|]+)", re.IGNORECASE)
URL_RE = re.compile(r"https?://[^\s\"')]+")
ACTION_RE = re.compile(r"uses:\s*([A-Za-z0-9_.\-/]+@[^\s#]+)")
DOCKER_FROM_RE = re.compile(r"^\s*FROM\s+(?:--platform=\S+\s+)?([^\s]+)", re.IGNORECASE)
YAML_IMAGE_RE = re.compile(r"^\s*image:\s*['\"]?([^'\"\s]+)")


@dataclass
class Dependency:
    name: str
    spec: str = ""
    scope: str = "dependencies"
    source: str = ""
    pinned: str = "unknown"


@dataclass
class Manifest:
    path: str
    ecosystem: str
    package_manager: str
    dependencies: list[Dependency] = field(default_factory=list)
    install_scripts: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def rel(path: Path, root: Path) -> str:
    return str(path.relative_to(root))


def read_text(path: Path, limit: int = 2_000_000) -> str:
    try:
        data = path.read_bytes()
    except OSError:
        return ""
    if len(data) > limit:
        data = data[:limit]
    return data.decode("utf-8", errors="replace")


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def load_toml(path: Path) -> dict[str, Any]:
    if tomllib is None:
        return {}
    try:
        with path.open("rb") as handle:
            data = tomllib.load(handle)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def version_pin_status(spec: str, ecosystem: str = "") -> str:
    value = (spec or "").strip()
    if not value:
        return "unknown"
    lower = value.lower()
    if any(marker in lower for marker in ("git+", "github:", "gitlab:", "http://", "https://")):
        if re.search(r"[@#][0-9a-f]{12,40}\b", lower):
            return "pinned"
        return "mutable-source"
    if (
        lower in {"*", "latest", "x"}
        or "*" in lower
        or re.search(r"(^|[.\-\s])x($|[.\-\s])", lower)
    ):
        return "unpinned"
    if lower.startswith(("^", "~", ">", "<", ">=", "<=", "~=", "!=")) or "," in lower:
        return "unpinned"
    if ecosystem == "python" and "==" in lower:
        return "pinned"
    if lower.startswith("="):
        return "pinned"
    if re.match(r"^\d+(?:\.\d+){0,3}(?:[-+][0-9a-zA-Z_.-]+)?$", value):
        return "pinned"
    if re.match(r"^v?\d+(?:\.\d+){1,3}$", value):
        return "pinned"
    return "unknown"


def add_deps_from_mapping(
    deps: list[Dependency],
    mapping: Any,
    scope: str,
    source: str,
    ecosystem: str,
) -> None:
    if not isinstance(mapping, dict):
        return
    for name, spec in sorted(mapping.items()):
        if isinstance(spec, dict):
            spec_text = json.dumps(spec, sort_keys=True)
        else:
            spec_text = str(spec)
        deps.append(
            Dependency(
                name=str(name),
                spec=spec_text,
                scope=scope,
                source=source,
                pinned=version_pin_status(spec_text, ecosystem),
            )
        )


def parse_package_json(path: Path, root: Path) -> Manifest:
    data = load_json(path)
    manifest = Manifest(rel(path, root), "node", "npm/yarn/pnpm/bun")
    for scope in (
        "dependencies",
        "devDependencies",
        "optionalDependencies",
        "peerDependencies",
        "bundledDependencies",
        "bundleDependencies",
    ):
        value = data.get(scope)
        if isinstance(value, list):
            for name in value:
                manifest.dependencies.append(
                    Dependency(str(name), "(bundled)", scope, manifest.path, "unknown")
                )
        else:
            add_deps_from_mapping(manifest.dependencies, value, scope, manifest.path, "node")
    scripts = data.get("scripts")
    if isinstance(scripts, dict):
        for name, command in sorted(scripts.items()):
            if re.search(r"(preinstall|install|postinstall|prepare|prepublish|prepack|postpack)", name):
                manifest.install_scripts.append(f"{name}: {command}")
    return manifest


def parse_requirements(path: Path, root: Path) -> Manifest:
    manifest = Manifest(rel(path, root), "python", "pip")
    for line in read_text(path).splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith(("-", "--")):
            continue
        name_part = re.split(r"\s*(==|===|~=|>=|<=|>|<|!=)\s*", stripped, maxsplit=1)
        if len(name_part) >= 3:
            name = name_part[0].strip()
            spec = "".join(name_part[1:]).strip()
        else:
            name = re.split(r"[;\[]", stripped, maxsplit=1)[0].strip()
            spec = ""
        manifest.dependencies.append(
            Dependency(name, spec, "requirements", manifest.path, version_pin_status(spec, "python"))
        )
    return manifest


def parse_pyproject(path: Path, root: Path) -> Manifest:
    data = load_toml(path)
    manifest = Manifest(rel(path, root), "python", "pyproject")
    project = data.get("project", {}) if isinstance(data.get("project"), dict) else {}
    for dep in project.get("dependencies", []) if isinstance(project.get("dependencies"), list) else []:
        add_python_dep_string(manifest, dep, "project.dependencies")
    optional = project.get("optional-dependencies", {})
    if isinstance(optional, dict):
        for group, deps in sorted(optional.items()):
            if isinstance(deps, list):
                for dep in deps:
                    add_python_dep_string(manifest, dep, f"project.optional-dependencies.{group}")
    poetry = data.get("tool", {}).get("poetry", {}) if isinstance(data.get("tool"), dict) else {}
    if isinstance(poetry, dict):
        add_deps_from_mapping(
            manifest.dependencies,
            poetry.get("dependencies", {}),
            "tool.poetry.dependencies",
            manifest.path,
            "python",
        )
        add_deps_from_mapping(
            manifest.dependencies,
            poetry.get("dev-dependencies", {}),
            "tool.poetry.dev-dependencies",
            manifest.path,
            "python",
        )
        groups = poetry.get("group", {})
        if isinstance(groups, dict):
            for group, value in sorted(groups.items()):
                deps = value.get("dependencies", {}) if isinstance(value, dict) else {}
                add_deps_from_mapping(
                    manifest.dependencies,
                    deps,
                    f"tool.poetry.group.{group}.dependencies",
                    manifest.path,
                    "python",
                )
    build_system = data.get("build-system", {})
    if isinstance(build_system, dict):
        for dep in build_system.get("requires", []) if isinstance(build_system.get("requires"), list) else []:
            add_python_dep_string(manifest, dep, "build-system.requires")
    return manifest


def add_python_dep_string(manifest: Manifest, dep: Any, scope: str) -> None:
    text = str(dep)
    match = re.match(r"\s*([A-Za-z0-9_.-]+)\s*(.*)", text)
    name = match.group(1) if match else text
    spec = match.group(2).strip() if match else ""
    manifest.dependencies.append(
        Dependency(name, spec, scope, manifest.path, version_pin_status(spec, "python"))
    )


def parse_cargo_toml(path: Path, root: Path) -> Manifest:
    data = load_toml(path)
    manifest = Manifest(rel(path, root), "rust", "cargo")
    for scope in ("dependencies", "dev-dependencies", "build-dependencies"):
        add_deps_from_mapping(manifest.dependencies, data.get(scope, {}), scope, manifest.path, "rust")
    target = data.get("target", {})
    if isinstance(target, dict):
        for target_name, target_data in target.items():
            if isinstance(target_data, dict):
                for scope in ("dependencies", "dev-dependencies", "build-dependencies"):
                    add_deps_from_mapping(
                        manifest.dependencies,
                        target_data.get(scope, {}),
                        f"target.{target_name}.{scope}",
                        manifest.path,
                        "rust",
                    )
    return manifest


def parse_go_mod(path: Path, root: Path) -> Manifest:
    manifest = Manifest(rel(path, root), "go", "go modules")
    text = read_text(path)
    in_require = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("require ("):
            in_require = True
            continue
        if in_require and stripped == ")":
            in_require = False
            continue
        if stripped.startswith("require "):
            parts = stripped.split()
            if len(parts) >= 3:
                manifest.dependencies.append(
                    Dependency(parts[1], parts[2], "require", manifest.path, "pinned")
                )
        elif in_require and stripped and not stripped.startswith("//"):
            parts = stripped.split()
            if len(parts) >= 2:
                scope = "require indirect" if "indirect" in stripped else "require"
                manifest.dependencies.append(Dependency(parts[0], parts[1], scope, manifest.path, "pinned"))
    return manifest


def parse_composer_json(path: Path, root: Path) -> Manifest:
    data = load_json(path)
    manifest = Manifest(rel(path, root), "php", "composer")
    add_deps_from_mapping(manifest.dependencies, data.get("require", {}), "require", manifest.path, "php")
    add_deps_from_mapping(manifest.dependencies, data.get("require-dev", {}), "require-dev", manifest.path, "php")
    scripts = data.get("scripts", {})
    if isinstance(scripts, dict):
        for name, value in sorted(scripts.items()):
            if name in {"pre-install-cmd", "post-install-cmd", "pre-update-cmd", "post-update-cmd"}:
                manifest.install_scripts.append(f"{name}: {value}")
    return manifest


def parse_gemfile(path: Path, root: Path) -> Manifest:
    manifest = Manifest(rel(path, root), "ruby", "bundler")
    for line in read_text(path).splitlines():
        match = re.search(r"^\s*gem\s+['\"]([^'\"]+)['\"]\s*(?:,\s*['\"]([^'\"]+)['\"])?", line)
        if match:
            spec = match.group(2) or ""
            manifest.dependencies.append(
                Dependency(match.group(1), spec, "gem", manifest.path, version_pin_status(spec, "ruby"))
            )
    return manifest


def parse_pom(path: Path, root: Path) -> Manifest:
    manifest = Manifest(rel(path, root), "java", "maven")
    try:
        tree = ET.parse(path)
    except Exception:
        return manifest
    root_el = tree.getroot()
    for dep in root_el.findall(".//{*}dependency"):
        group = dep.findtext("{*}groupId") or ""
        artifact = dep.findtext("{*}artifactId") or ""
        version = dep.findtext("{*}version") or ""
        scope = dep.findtext("{*}scope") or "compile"
        if artifact:
            name = f"{group}:{artifact}" if group else artifact
            manifest.dependencies.append(
                Dependency(name, version, scope, manifest.path, version_pin_status(version, "java"))
            )
    for plugin in root_el.findall(".//{*}plugin"):
        group = plugin.findtext("{*}groupId") or ""
        artifact = plugin.findtext("{*}artifactId") or ""
        version = plugin.findtext("{*}version") or ""
        if artifact:
            name = f"{group}:{artifact}" if group else artifact
            manifest.dependencies.append(
                Dependency(name, version, "build-plugin", manifest.path, version_pin_status(version, "java"))
            )
    return manifest


def parse_csproj(path: Path, root: Path) -> Manifest:
    manifest = Manifest(rel(path, root), ".net", "dotnet")
    try:
        tree = ET.parse(path)
    except Exception:
        return manifest
    for ref in tree.findall(".//{*}PackageReference"):
        name = ref.attrib.get("Include") or ref.attrib.get("Update") or ""
        version = ref.attrib.get("Version") or ref.findtext("{*}Version") or ""
        if name:
            manifest.dependencies.append(
                Dependency(name, version, "PackageReference", manifest.path, version_pin_status(version, "dotnet"))
            )
    return manifest


def parse_generic_manifest(path: Path, root: Path) -> Manifest:
    name = path.name
    if name == "package.json":
        return parse_package_json(path, root)
    if name == "pyproject.toml":
        return parse_pyproject(path, root)
    if name.startswith("requirements") and path.suffix == ".txt":
        return parse_requirements(path, root)
    if name == "Cargo.toml":
        return parse_cargo_toml(path, root)
    if name == "go.mod":
        return parse_go_mod(path, root)
    if name == "composer.json":
        return parse_composer_json(path, root)
    if name == "Gemfile":
        return parse_gemfile(path, root)
    if name == "pom.xml":
        return parse_pom(path, root)
    if path.suffix == ".csproj" or name in {"packages.config", "Directory.Packages.props"}:
        return parse_csproj(path, root)
    if name in {"build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts"}:
        return Manifest(rel(path, root), "java", "gradle", notes=["Gradle dependencies are not parsed by this helper."])
    if name in {"setup.py", "setup.cfg", "Pipfile"}:
        return Manifest(rel(path, root), "python", name, notes=["Dependency counts are not parsed by this helper."])
    return Manifest(rel(path, root), "unknown", name)


def is_manifest(path: Path) -> bool:
    if path.name in MANIFEST_NAMES:
        return True
    if path.name.startswith("requirements") and path.suffix in {".txt", ".in"}:
        return True
    if path.suffix == ".csproj":
        return True
    if path.name.endswith(".gemspec"):
        return True
    return False


def is_lockfile(path: Path) -> bool:
    if path.name in LOCKFILE_NAMES:
        return True
    if path.name.endswith(".lock"):
        return True
    return False


def is_ci_file(path: Path, root: Path) -> bool:
    r = rel(path, root)
    if r.startswith(".github/workflows/") and path.suffix in {".yml", ".yaml"}:
        return True
    return r in CI_FILE_PATTERNS


def is_docker_file(path: Path) -> bool:
    name = path.name
    return name == "Dockerfile" or name.startswith("Dockerfile.") or name in {
        "docker-compose.yml",
        "docker-compose.yaml",
        "compose.yml",
        "compose.yaml",
    }


def discover_files(root: Path) -> tuple[list[Path], list[Path], list[Path], list[Path], list[Path], list[Path], list[Path]]:
    manifests: list[Path] = []
    lockfiles: list[Path] = []
    ci_files: list[Path] = []
    docker_files: list[Path] = []
    registry_configs: list[Path] = []
    vendored_dirs: list[Path] = []
    generated_dirs: list[Path] = []

    for current, dirs, files in os.walk(root):
        current_path = Path(current)
        kept_dirs = []
        for dirname in dirs:
            lower = dirname.lower()
            full = current_path / dirname
            if lower in VENDORED_DIR_NAMES or lower in GENERATED_DIR_NAMES:
                if lower in VENDORED_DIR_NAMES:
                    vendored_dirs.append(full)
                if lower in GENERATED_DIR_NAMES:
                    generated_dirs.append(full)
            if dirname in SKIP_DIRS or lower in VENDORED_DIR_NAMES:
                continue
            kept_dirs.append(dirname)
        dirs[:] = kept_dirs

        for filename in files:
            path = current_path / filename
            if is_manifest(path):
                manifests.append(path)
            if is_lockfile(path):
                lockfiles.append(path)
            if is_ci_file(path, root):
                ci_files.append(path)
            if is_docker_file(path):
                docker_files.append(path)
            if filename in REGISTRY_CONFIG_NAMES or filename.endswith(".npmrc"):
                registry_configs.append(path)
    return manifests, lockfiles, ci_files, docker_files, registry_configs, vendored_dirs, generated_dirs


def lockfile_count(path: Path) -> str:
    name = path.name
    if name in {"package-lock.json", "npm-shrinkwrap.json"}:
        data = load_json(path)
        packages = data.get("packages")
        if isinstance(packages, dict):
            return str(max(len(packages) - 1, 0))
        deps = data.get("dependencies")
        if isinstance(deps, dict):
            return str(len(deps))
    if name == "composer.lock":
        data = load_json(path)
        count = 0
        for key in ("packages", "packages-dev"):
            if isinstance(data.get(key), list):
                count += len(data[key])
        return str(count)
    if name == "Pipfile.lock":
        data = load_json(path)
        count = 0
        for key in ("default", "develop"):
            if isinstance(data.get(key), dict):
                count += len(data[key])
        return str(count)
    if name == "go.sum":
        modules = set()
        for line in read_text(path).splitlines():
            parts = line.split()
            if len(parts) >= 2:
                modules.add((parts[0], parts[1].replace("/go.mod", "")))
        return str(len(modules))
    if name == "Cargo.lock":
        return str(sum(1 for line in read_text(path).splitlines() if line.strip() == "[[package]]"))
    return "unknown"


def extract_ci_commands(paths: list[Path], root: Path) -> tuple[list[str], list[str]]:
    commands: list[str] = []
    actions: list[str] = []
    for path in paths:
        r = rel(path, root)
        for line in read_text(path).splitlines():
            if INSTALL_COMMAND_RE.search(line):
                commands.append(f"{r}: {line.strip()}")
            action = ACTION_RE.search(line)
            if action:
                actions.append(f"{r}: {action.group(1)}")
    return commands, actions


def extract_images(paths: list[Path], root: Path) -> list[str]:
    images: list[str] = []
    for path in paths:
        r = rel(path, root)
        for line in read_text(path).splitlines():
            from_match = DOCKER_FROM_RE.search(line)
            image_match = YAML_IMAGE_RE.search(line)
            if from_match:
                images.append(f"{r}: FROM {from_match.group(1)}")
            elif image_match:
                images.append(f"{r}: image {image_match.group(1)}")
    return images


def extract_download_commands(paths: list[Path], root: Path) -> list[str]:
    downloads: list[str] = []
    for path in paths:
        r = rel(path, root)
        for line in read_text(path).splitlines():
            if DOWNLOAD_COMMAND_RE.search(line):
                downloads.append(f"{r}: {line.strip()}")
    return downloads


def extract_registry_urls(paths: list[Path], root: Path) -> list[str]:
    urls: list[str] = []
    for path in paths:
        text = read_text(path)
        for match in URL_RE.finditer(text):
            url = match.group(0)
            if any(token in url.lower() for token in ("registry", "npm", "pypi", "nuget", "maven", "rubygems", "packagist", "crates")):
                urls.append(f"{rel(path, root)}: {url}")
    return sorted(set(urls))


def ecosystem_from_lockfile(path: Path) -> str:
    name = path.name
    if name in {"package-lock.json", "npm-shrinkwrap.json", "yarn.lock", "pnpm-lock.yaml", "bun.lock", "bun.lockb"}:
        return "node"
    if name in {"uv.lock", "poetry.lock", "Pipfile.lock", "requirements.lock", "requirements.txt.lock"}:
        return "python"
    if name == "Cargo.lock":
        return "rust"
    if name == "go.sum":
        return "go"
    if name == "Gemfile.lock":
        return "ruby"
    if name == "composer.lock":
        return "php"
    if name in {"packages.lock.json", "Package.resolved"}:
        return "dotnet/swift"
    if name == "gradle.lockfile":
        return "java"
    return "unknown"


def summarize(root: Path) -> dict[str, Any]:
    manifests_paths, lockfile_paths, ci_files, docker_files, registry_configs, vendored_dirs, generated_dirs = discover_files(root)
    manifests = [parse_generic_manifest(path, root) for path in sorted(manifests_paths)]
    ecosystems = Counter(m.ecosystem for m in manifests)
    package_managers = Counter(m.package_manager for m in manifests)

    dep_counts = defaultdict(int)
    pinned_counts = Counter()
    direct_deps: list[Dependency] = []
    install_scripts: list[str] = []
    duplicate_names = Counter()

    for manifest in manifests:
        dep_counts[manifest.path] = len(manifest.dependencies)
        for dep in manifest.dependencies:
            direct_deps.append(dep)
            pinned_counts[dep.pinned] += 1
            duplicate_names[(dep.name, dep.scope)] += 1
        for script in manifest.install_scripts:
            install_scripts.append(f"{manifest.path}: {script}")

    duplicates = [
        f"{name} ({scope}) appears {count} times"
        for (name, scope), count in sorted(duplicate_names.items())
        if count > 1
    ]

    ci_commands, actions = extract_ci_commands(sorted(ci_files), root)
    images = extract_images(sorted(docker_files), root)
    download_commands = extract_download_commands(sorted(ci_files + docker_files), root)
    registry_urls = extract_registry_urls(sorted(registry_configs), root)

    return {
        "root": str(root),
        "ecosystems": dict(sorted(ecosystems.items())),
        "package_managers": dict(sorted(package_managers.items())),
        "manifests": [
            {
                "path": m.path,
                "ecosystem": m.ecosystem,
                "package_manager": m.package_manager,
                "dependency_count": len(m.dependencies),
                "notes": m.notes,
            }
            for m in manifests
        ],
        "lockfiles": [
            {
                "path": rel(path, root),
                "ecosystem_hint": ecosystem_from_lockfile(path),
                "resolved_dependency_count_hint": lockfile_count(path),
            }
            for path in sorted(lockfile_paths)
        ],
        "dependency_counts_by_manifest": dict(sorted(dep_counts.items())),
        "pinned_status_counts": dict(sorted(pinned_counts.items())),
        "dependency_examples": [
            {
                "name": dep.name,
                "spec": dep.spec,
                "scope": dep.scope,
                "source": dep.source,
                "pin_status": dep.pinned,
            }
            for dep in direct_deps[:50]
        ],
        "install_scripts": install_scripts,
        "duplicate_dependency_hints": duplicates[:50],
        "ci_dependency_commands": ci_commands,
        "github_actions": actions,
        "docker_images": images,
        "download_command_hints": download_commands,
        "registry_config_files": [rel(path, root) for path in sorted(registry_configs)],
        "registry_urls": registry_urls,
        "vendored_directories": [rel(path, root) for path in sorted(vendored_dirs)],
        "generated_directories": [rel(path, root) for path in sorted(generated_dirs)],
        "ci_files": [rel(path, root) for path in sorted(ci_files)],
        "docker_files": [rel(path, root) for path in sorted(docker_files)],
    }


def print_report(data: dict[str, Any]) -> None:
    print(f"# Dependency Inventory: {data['root']}")
    print()
    print("## Ecosystems")
    print(format_mapping(data["ecosystems"]) or "None detected")
    print()
    print("## Package Managers")
    print(format_mapping(data["package_managers"]) or "None detected")
    print()
    print("## Manifests")
    for item in data["manifests"]:
        note = f" notes={'; '.join(item['notes'])}" if item.get("notes") else ""
        print(
            f"- {item['path']} ({item['ecosystem']}, {item['package_manager']}): "
            f"{item['dependency_count']} direct dependency hints{note}"
        )
    if not data["manifests"]:
        print("None detected")
    print()
    print("## Lockfiles")
    for item in data["lockfiles"]:
        print(
            f"- {item['path']} ({item['ecosystem_hint']}): "
            f"{item['resolved_dependency_count_hint']} resolved dependency hints"
        )
    if not data["lockfiles"]:
        print("None detected")
    print()
    print("## Direct Dependency Pin Status")
    print(format_mapping(data["pinned_status_counts"]) or "No direct dependencies parsed")
    print()
    print("## Install Scripts")
    print(format_list(data["install_scripts"]) or "None detected")
    print()
    print("## CI Dependency Commands")
    print(format_list(data["ci_dependency_commands"]) or "None detected")
    print()
    print("## GitHub Actions")
    print(format_list(data["github_actions"]) or "None detected")
    print()
    print("## Docker Images")
    print(format_list(data["docker_images"]) or "None detected")
    print()
    print("## Download Command Hints")
    print(format_list(data["download_command_hints"]) or "None detected")
    print()
    print("## Registry Config")
    print(format_list(data["registry_config_files"]) or "None detected")
    if data["registry_urls"]:
        print()
        print("Registry URL hints:")
        print(format_list(data["registry_urls"]))
    print()
    print("## Vendored And Generated Directories")
    print("Vendored:")
    print(format_list(data["vendored_directories"]) or "None detected")
    print("Generated:")
    print(format_list(data["generated_directories"]) or "None detected")
    print()
    print("## Duplicate Dependency Hints")
    print(format_list(data["duplicate_dependency_hints"]) or "None detected")
    print()
    print("## Dependency Examples")
    for item in data["dependency_examples"]:
        spec = f" {item['spec']}" if item["spec"] else ""
        print(
            f"- {item['name']}{spec} "
            f"[{item['scope']}, {item['pin_status']}, {item['source']}]"
        )
    if not data["dependency_examples"]:
        print("None parsed")


def format_mapping(mapping: dict[str, Any]) -> str:
    return "\n".join(f"- {key}: {value}" for key, value in sorted(mapping.items()))


def format_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Summarize repository dependency inventory.")
    parser.add_argument("repo_root", nargs="?", default=".", help="Repository root to inspect.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of a text report.")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        print(f"error: repo root is not a directory: {root}", file=sys.stderr)
        return 2

    data = summarize(root)
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print_report(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
