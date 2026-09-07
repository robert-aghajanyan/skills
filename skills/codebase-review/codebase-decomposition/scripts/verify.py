#!/usr/bin/env python3
"""
Verify a mixin-based package decomposition is correct.

Usage:
    python verify.py <package_path>

Example:
    python verify.py src/agents/notifier
    python verify.py /abs/path/to/src/clients/datadog
"""

from __future__ import annotations

import importlib
import inspect
import os
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PackageInfo:
    path: Path
    init: Path
    modules: list[Path]
    module_path: str
    project_root: Path


def derive_module_path(path: Path, project_root: Path) -> str:
    resolved = path.resolve()
    root = project_root.resolve()
    try:
        relative = resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(
            f"{resolved} is not inside the current working directory {root}. "
            "Run the script from the repo root or pass a package path under the current directory."
        ) from exc
    return ".".join(relative.parts)


def find_package_info(package_path: str) -> PackageInfo:
    path = Path(package_path).expanduser()
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    else:
        path = path.resolve()

    if not path.is_dir():
        print(f"ERROR: {package_path} is not a directory")
        sys.exit(1)

    init_file = path / "__init__.py"
    if not init_file.exists():
        print(f"ERROR: {path}/__init__.py not found")
        sys.exit(1)

    project_root = Path.cwd().resolve()
    try:
        module_path = derive_module_path(path, project_root)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

    modules = sorted(m for m in path.glob("*.py") if m.name != "__init__.py")
    return PackageInfo(
        path=path,
        init=init_file,
        modules=modules,
        module_path=module_path,
        project_root=project_root,
    )


def import_module(name: str):
    try:
        return importlib.import_module(name)
    except Exception as exc:
        print(f"  SKIP: Could not import {name}: {exc}")
        return None


def import_modules(package_info: PackageInfo) -> tuple[object | None, list[object]]:
    if str(package_info.project_root) not in sys.path:
        sys.path.insert(0, str(package_info.project_root))
    package_module = import_module(package_info.module_path)
    submodules = []
    for module in package_info.modules:
        imported = import_module(f"{package_info.module_path}.{module.stem}")
        if imported is not None:
            submodules.append(imported)
    return package_module, submodules


def check_method_collisions(package_info: PackageInfo, submodules: list[object]) -> bool:
    print("\n--- Method Collision Check ---")

    classes: dict[str, set[str]] = {}
    for module in submodules:
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ != module.__name__:
                continue
            if "Mixin" not in name:
                continue
            methods = {method for method in obj.__dict__ if not method.startswith("__")}
            classes[f"{module.__name__}.{name}"] = methods

    if not classes:
        print("  SKIP: No Mixin classes found in package modules")
        return True

    print(f"  Found {len(classes)} mixins")
    collisions = []
    names = list(classes.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            overlap = classes[names[i]] & classes[names[j]]
            if overlap:
                collisions.append((names[i], names[j], sorted(overlap)))

    if collisions:
        print("  FAIL: Method collisions found!")
        for left, right, overlap in collisions:
            print(f"    {left} vs {right}: {', '.join(overlap)}")
        return False
    print("  PASS: Zero method collisions")
    return True


def check_mro(package_module) -> bool:
    print("\n--- MRO Check ---")
    if package_module is None:
        print("  SKIP: Package import failed")
        return False

    candidates = []
    for name, obj in inspect.getmembers(package_module, inspect.isclass):
        if obj.__module__ != package_module.__name__:
            continue
        if "Mixin" in name or name.startswith("_"):
            continue
        if len(getattr(obj, "__mro__", ())) <= 3:
            continue
        candidates.append((name, obj))

    if not candidates:
        print("  SKIP: No composed class found in package")
        return True

    for name, obj in candidates:
        mro = [klass.__name__ for klass in obj.__mro__]
        print(f"  {name} MRO: {' -> '.join(mro)}")
    print(f"  PASS: MRO resolves for {len(candidates)} composed class(es)")
    return True


def check_reexports(package_module, submodules: list[object]) -> bool:
    print("\n--- Re-export Check ---")
    if package_module is None:
        print("  SKIP: Package import failed")
        return False

    package_names = set(dir(package_module))
    ok = True

    if hasattr(package_module, "__all__"):
        exported = set(package_module.__all__)
        missing = exported - package_names
        if missing:
            print(f"  FAIL: __all__ lists names not importable from package: {sorted(missing)}")
            ok = False
        else:
            print(f"  PASS: All {len(exported)} names in __all__ are importable")
    else:
        print("  WARNING: No __all__ defined on package")

    submodule_exports = {}
    for module in submodules:
        if hasattr(module, "__all__"):
            submodule_exports[module.__name__] = set(module.__all__)

    if not submodule_exports:
        print("  INFO: No submodule __all__ declarations to compare")
        return ok

    missing_from_package = {}
    for module_name, exports in submodule_exports.items():
        missing = exports - package_names
        if missing:
            missing_from_package[module_name] = sorted(missing)

    if missing_from_package:
        print("  WARNING: Some names exported by submodules are not re-exported by the package")
        for module_name, names in missing_from_package.items():
            print(f"    {module_name}: {', '.join(names)}")
    else:
        print("  PASS: Package re-exports all names declared in submodule __all__")
    return ok


def check_line_counts(package_info: PackageInfo) -> None:
    print("\n--- Line Count Report ---")
    total = 0
    for module in [package_info.init] + package_info.modules:
        lines = len(module.read_text().splitlines())
        total += lines
        print(f"  {module.name:30s} {lines:>6} lines")
    print(f"  {'TOTAL':30s} {total:>6} lines")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python verify.py <package_path>")
        print("Example: python verify.py src/agents/notifier")
        sys.exit(1)

    package_info = find_package_info(sys.argv[1])
    print(f"Verifying package: {package_info.path}")
    print(f"Module path: {package_info.module_path}")
    print(f"Modules: {len(package_info.modules)}")

    package_module, submodules = import_modules(package_info)

    check_line_counts(package_info)
    checks = [
        check_method_collisions(package_info, submodules),
        check_mro(package_module),
        check_reexports(package_module, submodules),
    ]

    print("\n--- Done ---")
    if not all(checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
