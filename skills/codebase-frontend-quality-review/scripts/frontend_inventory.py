#!/usr/bin/env python3
"""Read-only frontend inventory helper for codebase-frontend-quality-review."""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter
from pathlib import Path
from typing import Iterable


TEXT_EXTENSIONS = {
    ".astro",
    ".css",
    ".html",
    ".js",
    ".jsx",
    ".mjs",
    ".svelte",
    ".ts",
    ".tsx",
    ".vue",
}

CODE_EXTENSIONS = {
    ".astro",
    ".js",
    ".jsx",
    ".mjs",
    ".svelte",
    ".ts",
    ".tsx",
    ".vue",
}

SKIP_DIRS = {
    ".angular",
    ".cache",
    ".codex-worktrees",
    ".mypy_cache",
    ".parcel-cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".git",
    ".hg",
    ".next",
    ".nuxt",
    ".output",
    ".svelte-kit",
    ".turbo",
    ".venv",
    ".worktrees",
    "build",
    "coverage",
    "dist",
    "env",
    "htmlcov",
    "node_modules",
    "out",
    "target",
    "venv",
    "vendor",
}

FRAMEWORK_MARKERS = {
    "next": "Next.js",
    "react": "React",
    "react-dom": "React",
    "vite": "Vite",
    "vue": "Vue",
    "nuxt": "Nuxt",
    "svelte": "Svelte",
    "@sveltejs/kit": "SvelteKit",
    "astro": "Astro",
    "@angular/core": "Angular",
    "solid-js": "Solid",
    "@remix-run/react": "Remix",
    "@tanstack/react-router": "TanStack Router",
    "react-router": "React Router",
    "react-router-dom": "React Router",
}

STATE_MARKERS = {
    "@reduxjs/toolkit": "Redux Toolkit",
    "redux": "Redux",
    "zustand": "Zustand",
    "mobx": "MobX",
    "jotai": "Jotai",
    "recoil": "Recoil",
    "@tanstack/react-query": "TanStack Query",
    "react-query": "React Query",
    "swr": "SWR",
    "pinia": "Pinia",
    "vuex": "Vuex",
    "xstate": "XState",
    "@apollo/client": "Apollo Client",
    "urql": "urql",
}

STYLING_MARKERS = {
    "tailwindcss": "Tailwind CSS",
    "styled-components": "styled-components",
    "@emotion/react": "Emotion",
    "@mui/material": "MUI",
    "antd": "Ant Design",
    "bootstrap": "Bootstrap",
    "@chakra-ui/react": "Chakra UI",
    "@radix-ui/react-dialog": "Radix UI",
    "@headlessui/react": "Headless UI",
    "sass": "Sass",
    "less": "Less",
}

ACCESSIBILITY_MARKERS = {
    "@axe-core/playwright": "axe Playwright",
    "axe-core": "axe-core",
    "jest-axe": "jest-axe",
    "eslint-plugin-jsx-a11y": "eslint-plugin-jsx-a11y",
    "@storybook/addon-a11y": "Storybook a11y",
}

TEST_MARKERS = {
    "@playwright/test": "Playwright",
    "playwright": "Playwright",
    "cypress": "Cypress",
    "vitest": "Vitest",
    "jest": "Jest",
    "@testing-library/react": "Testing Library React",
    "@testing-library/vue": "Testing Library Vue",
    "@testing-library/svelte": "Testing Library Svelte",
    "storybook": "Storybook",
    "@storybook/react": "Storybook React",
    "@storybook/vue3": "Storybook Vue",
    "@storybook/svelte": "Storybook Svelte",
}

ROUTE_FILE_PATTERNS = (
    re.compile(r"app[/\\].*(page|layout|loading|error|not-found)\.(tsx|ts|jsx|js)$"),
    re.compile(r"pages[/\\].*\.(tsx|ts|jsx|js|vue)$"),
    re.compile(r"routes[/\\].*\.(tsx|ts|jsx|js|svelte|vue)$"),
    re.compile(r"src[/\\]routes[/\\].*\.(tsx|ts|jsx|js|svelte|vue)$"),
)

ROUTE_CALL_PATTERNS = (
    re.compile(r"<Route\b[^>]*(?:path|to)=['\"]([^'\"]+)['\"]"),
    re.compile(r"\bpath:\s*['\"]([^'\"]+)['\"]"),
    re.compile(r"\bcreateFileRoute\(['\"]([^'\"]+)['\"]\)"),
)

FORM_PATTERNS = (
    re.compile(r"<form\b", re.IGNORECASE),
    re.compile(r"\buseForm\s*\("),
    re.compile(r"\bFormik\b"),
    re.compile(r"\bvee-validate\b"),
    re.compile(r"\bzodResolver\b"),
    re.compile(r"\byupResolver\b"),
)

API_PATTERNS = (
    re.compile(r"\bfetch\s*\("),
    re.compile(r"\baxios\."),
    re.compile(r"\bgraphql\s*`"),
    re.compile(r"\buseQuery\s*\("),
    re.compile(r"\buseMutation\s*\("),
)

STATE_PATTERNS = (
    re.compile(r"\bcreate\s*\("),
    re.compile(r"\bcreateSlice\s*\("),
    re.compile(r"\buseReducer\s*\("),
    re.compile(r"\bcreateContext\s*\("),
    re.compile(r"\bdefineStore\s*\("),
    re.compile(r"\bwritable\s*\("),
)

COMPONENT_PATTERNS = (
    re.compile(r"function\s+([A-Z][A-Za-z0-9_]*)\s*\("),
    re.compile(r"const\s+([A-Z][A-Za-z0-9_]*)\s*=\s*(?:\([^=]*\)|[^=]+)\s*=>"),
    re.compile(r"export\s+default\s+function\s+([A-Z][A-Za-z0-9_]*)\s*\("),
)


def iter_files(root: Path) -> Iterable[Path]:
    for current_root, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        base = Path(current_root)
        for name in files:
            path = base / name
            if path.suffix in TEXT_EXTENSIONS or name in {"package.json", "vite.config.ts", "vite.config.js"}:
                yield path


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def read_text(path: Path, limit: int = 500_000) -> str:
    try:
        data = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    return data[:limit]


def load_package_jsons(root: Path) -> list[tuple[Path, dict]]:
    packages = []
    for package_path in root.rglob("package.json"):
        relative_parts = package_path.relative_to(root).parts
        if any(part in SKIP_DIRS for part in relative_parts):
            continue
        try:
            packages.append((package_path, json.loads(package_path.read_text(encoding="utf-8"))))
        except (OSError, json.JSONDecodeError):
            packages.append((package_path, {}))
    return packages


def package_names(packages: list[tuple[Path, dict]]) -> set[str]:
    names: set[str] = set()
    for _, package in packages:
        for section in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
            deps = package.get(section, {})
            if isinstance(deps, dict):
                names.update(deps)
    return names


def detect_from_packages(packages: list[tuple[Path, dict]], markers: dict[str, str]) -> list[str]:
    names = package_names(packages)
    return sorted({label for package, label in markers.items() if package in names})


def collect_scripts(packages: list[tuple[Path, dict]], root: Path) -> list[str]:
    rows = []
    for path, package in packages:
        scripts = package.get("scripts", {})
        if not isinstance(scripts, dict):
            continue
        interesting = [
            name
            for name in scripts
            if re.search(r"(dev|start|build|preview|storybook|test|lint|typecheck|e2e|cy|playwright)", name)
        ]
        if interesting:
            rendered = ", ".join(f"{name}: {scripts[name]}" for name in sorted(interesting))
            rows.append(f"{rel(path, root)} -> {rendered}")
    return rows


def collect_matches(root: Path) -> dict[str, list[str]]:
    route_files: list[str] = []
    route_literals: Counter[str] = Counter()
    components: Counter[str] = Counter()
    forms: list[str] = []
    api_clients: list[str] = []
    state_files: list[str] = []
    style_files: list[str] = []
    tests: list[str] = []
    storybook_files: list[str] = []

    for path in iter_files(root):
        relative = rel(path, root)
        lower = relative.lower()
        if any(pattern.search(relative) for pattern in ROUTE_FILE_PATTERNS):
            route_files.append(relative)
        if path.suffix in {".css", ".scss", ".sass", ".less"} or "style" in lower or "theme" in lower:
            style_files.append(relative)
        if re.search(r"(\.test\.|\.spec\.|__tests__|/tests?/|playwright|cypress)", lower):
            tests.append(relative)
        if re.search(r"(\.stories\.|storybook)", lower):
            storybook_files.append(relative)

        is_code = path.suffix in CODE_EXTENSIONS
        text = read_text(path)
        if not text:
            continue

        if is_code:
            for pattern in ROUTE_CALL_PATTERNS:
                for match in pattern.findall(text):
                    route_literals[match] += 1
            for pattern in COMPONENT_PATTERNS:
                for match in pattern.findall(text):
                    components[match] += 1
        if any(pattern.search(text) for pattern in FORM_PATTERNS):
            forms.append(relative)
        if is_code and (any(pattern.search(text) for pattern in API_PATTERNS) or re.search(r"(api|client|service)", lower)):
            api_clients.append(relative)
        if is_code and (any(pattern.search(text) for pattern in STATE_PATTERNS) or re.search(r"(store|state|context|provider|slice|query)", lower)):
            state_files.append(relative)

    return {
        "route_files": sorted(route_files)[:80],
        "route_literals": [route for route, _ in route_literals.most_common(80)],
        "components": [name for name, _ in components.most_common(80)],
        "forms": sorted(set(forms))[:80],
        "api_clients": sorted(set(api_clients))[:80],
        "state_files": sorted(set(state_files))[:80],
        "style_files": sorted(set(style_files))[:80],
        "tests": sorted(set(tests))[:80],
        "storybook_files": sorted(set(storybook_files))[:80],
    }


def print_section(title: str, rows: list[str]) -> None:
    print(f"\n## {title}")
    if not rows:
        print("- Not detected")
        return
    for row in rows:
        print(f"- {row}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize frontend structure without modifying files.")
    parser.add_argument("repo", nargs="?", default=".", help="Repository root to inspect")
    args = parser.parse_args()

    root = Path(args.repo).expanduser().resolve()
    if not root.exists():
        parser.error(f"repo path does not exist: {root}")
    if not root.is_dir():
        parser.error(f"repo path is not a directory: {root}")

    packages = load_package_jsons(root)
    matches = collect_matches(root)

    print(f"# Frontend Inventory: {root}")
    print("\nRead-only heuristic summary. Validate important claims by reading the code.")

    print_section("Package Files", [rel(path, root) for path, _ in packages])
    print_section("Frameworks", detect_from_packages(packages, FRAMEWORK_MARKERS))
    print_section("State And Data Libraries", detect_from_packages(packages, STATE_MARKERS))
    print_section("Styling And Design System", detect_from_packages(packages, STYLING_MARKERS))
    print_section("Accessibility Tooling", detect_from_packages(packages, ACCESSIBILITY_MARKERS))
    print_section("Test And Preview Tooling", detect_from_packages(packages, TEST_MARKERS))
    print_section("Build, Dev, Preview, And Test Commands", collect_scripts(packages, root))
    print_section("Route Files", matches["route_files"])
    print_section("Route Literals", matches["route_literals"])
    print_section("Major Component Names", matches["components"])
    print_section("Forms", matches["forms"])
    print_section("API Client Or Data Files", matches["api_clients"])
    print_section("State Store Or Provider Files", matches["state_files"])
    print_section("Styling Files", matches["style_files"])
    print_section("Tests", matches["tests"])
    print_section("Storybook Or Preview Files", matches["storybook_files"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
