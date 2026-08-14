---
name: codebase-decomposition
description: Audit, plan, and execute behavior-preserving decomposition of large codebase modules. Use when user asks to split a file, decompose a module, refactor a monolith or god class, or break up code that is "too big" without changing behavior.
---

# Codebase Decomposition

Break large modules into smaller, maintainable units while preserving backward compatibility.

## Inputs

Infer the mode from the user's request:

- Repo-wide audit when they ask which files should be split.
- Single-file decomposition when they point at one module.
- Merge-order planning when they already have several findings and want an execution sequence.

Inspect the repo before asking clarifying questions. Ask only if the language, source roots, or test command are still ambiguous after inspection.

## Audit

Find large files and god classes. Look for files over 500 lines, classes with 15+ methods, and duplicated infrastructure across multiple files.

Classify each candidate by pattern:

| Signal | Pattern | Details |
|--------|---------|---------|
| Single large file with distinct domain areas | **Mixin Composition** | [references/mixin-pattern.md](references/mixin-pattern.md) |
| Multiple classes with duplicated setup code | **Base Class Extraction** | [references/base-class-pattern.md](references/base-class-pattern.md) |
| Same control flow repeated 3+ times | **Helper Extraction** | [references/helper-pattern.md](references/helper-pattern.md) |
| Unused duplicate alongside active version | **Dead Code Removal** | Remove it, update imports |
| External code calling private methods | **Encapsulation Fix** | Add public wrappers, migrate callers |

Produce a findings table with ID, file, approximate lines, pattern, priority, dependencies, and recommended merge order.

## Decompose a File

Read the target file. Identify domain clusters, shared state, and cross-cluster calls. Choose the best pattern from the table above and consult its reference.

Present a concise plan before editing:

- target structure
- method-to-module mapping
- backward-compatibility strategy
- verification steps

Wait for user approval before editing when the refactor is non-trivial or touches public APIs.

## Verification

After any decomposition, run:

1. The relevant test suite.
2. Import checks for old import paths.
3. For mixin pattern: verify zero method name collisions across mixins.
4. A line-count sanity check: total lines should stay within roughly 10% of the original unless tests or shims justify the delta.

If this skill is installed in the default personal location, you can use the bundled verifier:

```bash
python "${CLAUDE_SKILL_DIR}/scripts/verify.py" <package_path>
```

## Gotchas

- **Circular imports in mixin packages**: move shared types to `models.py`.
- **`__init__` in mixins**: keep initialization in the composed class or base class, not the mixins.
- **Forgotten re-exports**: when a file becomes a package, re-export every previously public symbol from `__init__.py`.
- **Silent timeout regressions**: preserve subclass-specific defaults when extracting a base class.
- **Shim points at the wrong replacement**: grep all call sites before choosing which new class or function backs the compatibility shim.
- **`@staticmethod` wrappers need explicit class references**: call `ClassName._method(...)`, not `self._method(...)`, when the target stays static.
- **MRO order matters**: the base class should be last in the inheritance list for mixin composition.

## Principles

- **Zero breaking changes**: preserve import paths unless the user explicitly approves a breaking change.
- **Mechanical moves first**: separate behavior changes from structural refactors.
- **One finding per PR**: keep merge risk low.
- **Characterization tests before major splits**: if the module has weak coverage, add targeted tests before moving code.
