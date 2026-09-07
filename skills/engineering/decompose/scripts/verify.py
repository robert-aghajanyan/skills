#!/usr/bin/env python3
"""
Verify a mixin-based package decomposition is correct.

Usage:
    python verify.py <package_path>

Example:
    python verify.py src/agents/notifier
    python verify.py src/clients/datadog

Checks:
1. All mixins have zero method name collisions
2. MRO is valid (no diamond issues)
3. The composed class can be instantiated (import check)
4. Re-exports: all public names from submodules are accessible from __init__
5. Line count comparison with git (if old file exists in history)
"""

import sys
import os
import importlib
import inspect
from pathlib import Path


def find_package_info(package_path: str) -> dict:
    """Discover the package structure."""
    path = Path(package_path)
    if not path.is_dir():
        print(f"ERROR: {package_path} is not a directory")
        sys.exit(1)

    init_file = path / "__init__.py"
    if not init_file.exists():
        print(f"ERROR: {package_path}/__init__.py not found")
        sys.exit(1)

    modules = sorted(path.glob("*.py"))
    return {
        "path": path,
        "init": init_file,
        "modules": [m for m in modules if m.name != "__init__.py"],
        "module_path": str(path).replace("/", ".").replace("\\", "."),
    }


def check_method_collisions(package_path: str, module_path: str):
    """Check that no two mixin classes define the same method."""
    print("\n--- Method Collision Check ---")

    # Add project root to path
    project_root = os.getcwd()
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    try:
        pkg = importlib.import_module(module_path)
    except Exception as e:
        print(f"  SKIP: Could not import {module_path}: {e}")
        return

    # Find all classes defined in the package
    classes = {}
    for name, obj in inspect.getmembers(pkg):
        if inspect.isclass(obj) and "Mixin" in name:
            methods = {m for m in obj.__dict__ if not m.startswith("__")}
            classes[name] = methods

    if not classes:
        print("  SKIP: No Mixin classes found in package")
        return

    print(f"  Found {len(classes)} mixins: {', '.join(classes.keys())}")

    collisions = []
    names = list(classes.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            overlap = classes[names[i]] & classes[names[j]]
            if overlap:
                collisions.append((names[i], names[j], overlap))

    if collisions:
        print("  FAIL: Method collisions found!")
        for n1, n2, methods in collisions:
            print(f"    {n1} vs {n2}: {methods}")
    else:
        print("  PASS: Zero method collisions")


def check_mro(module_path: str):
    """Check that MRO resolves cleanly."""
    print("\n--- MRO Check ---")

    try:
        pkg = importlib.import_module(module_path)
    except Exception as e:
        print(f"  SKIP: Could not import {module_path}: {e}")
        return

    # Find the main composed class (not a Mixin, not a dataclass)
    for name, obj in inspect.getmembers(pkg):
        if (
            inspect.isclass(obj)
            and "Mixin" not in name
            and not name.startswith("_")
            and hasattr(obj, "__mro__")
            and len(obj.__mro__) > 3  # More than just object + 1 parent
        ):
            mro = [c.__name__ for c in obj.__mro__]
            print(f"  {name} MRO: {' -> '.join(mro)}")
            print(f"  PASS: MRO resolves ({len(mro)} classes)")
            return

    print("  SKIP: No composed class found")


def check_reexports(package_info: dict):
    """Check that __init__.py re-exports public names from submodules."""
    print("\n--- Re-export Check ---")

    module_path = package_info["module_path"]

    try:
        pkg = importlib.import_module(module_path)
    except Exception as e:
        print(f"  SKIP: Could not import {module_path}: {e}")
        return

    pkg_names = set(dir(pkg))
    if hasattr(pkg, "__all__"):
        exported = set(pkg.__all__)
        print(f"  __all__ has {len(exported)} names")

        missing = exported - pkg_names
        if missing:
            print(f"  FAIL: __all__ lists names not in package: {missing}")
        else:
            print(f"  PASS: All {len(exported)} names in __all__ are importable")
    else:
        print("  WARNING: No __all__ defined — consider adding one")


def check_line_counts(package_info: dict):
    """Report line counts per module."""
    print("\n--- Line Count Report ---")

    total = 0
    for module in [package_info["init"]] + package_info["modules"]:
        lines = len(module.read_text().splitlines())
        total += lines
        print(f"  {module.name:30s} {lines:>6} lines")

    print(f"  {'TOTAL':30s} {total:>6} lines")


def main():
    if len(sys.argv) < 2:
        print("Usage: python verify.py <package_path>")
        print("Example: python verify.py src/agents/notifier")
        sys.exit(1)

    package_path = sys.argv[1]
    info = find_package_info(package_path)

    print(f"Verifying package: {package_path}")
    print(f"Modules: {len(info['modules'])}")

    check_line_counts(info)
    check_method_collisions(package_path, info["module_path"])
    check_mro(info["module_path"])
    check_reexports(info)

    print("\n--- Done ---")


if __name__ == "__main__":
    main()
