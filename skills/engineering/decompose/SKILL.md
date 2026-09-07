---
name: decompose
description: Audit and decompose large modules into smaller, maintainable units. Use when user mentions "split", "decompose", "refactor", "monolith", "god class", "too big", "too many lines", or wants to break a large file into smaller ones. Identifies decomposition patterns, plans dependency-aware refactoring, and executes with zero breaking changes.
argument-hint: "<file path, 'audit', or 'plan'>"
allowed-tools: Read, Grep, Glob, Bash, Agent, Write, Edit, AskUserQuestion, EnterPlanMode, ExitPlanMode
---

# Module Decomposition

Break large modules into smaller, maintainable units while preserving backward compatibility.

## Setup

Detect the project's language, test runner, and source directory. If unclear, ask:
- What language? (Python, TypeScript, Go, etc.)
- Where is source code? (`src/`, `lib/`, `app/`, etc.)
- Test command? (`pytest`, `npm test`, `go test`, etc.)

Store answers mentally for this session. Adapt all instructions below to the detected stack.

## Modes

- **`/decompose audit`** — Scan for decomposition candidates, produce prioritized findings
- **`/decompose <file>`** — Analyze one file and plan its decomposition
- **`/decompose plan`** — Plan merge order for multiple findings

## Audit

Find large files and god classes. Look for files over 500 lines and classes with 15+ methods. Also scan for duplicated infrastructure across multiple files (identical method signatures like `_request`, `_headers`, `health_check` appearing in 2+ files).

Classify each candidate by pattern:

| Signal | Pattern | Details |
|--------|---------|---------|
| Single large file with distinct domain areas | **Mixin Composition** | [references/mixin-pattern.md](references/mixin-pattern.md) |
| Multiple classes with duplicated setup code | **Base Class Extraction** | [references/base-class-pattern.md](references/base-class-pattern.md) |
| Same control flow repeated 3+ times | **Helper Extraction** | [references/helper-pattern.md](references/helper-pattern.md) |
| Unused duplicate alongside active version | **Dead Code Removal** | Remove it, update imports |
| External code calling private methods | **Encapsulation Fix** | Add public wrappers, migrate callers |

Output a findings table with ID, file, lines, pattern, priority, and dependencies. Recommend a merge order: independent findings in Phase 1 (any order), dependent findings in Phase 2 (sequential), tests in Phase 3.

## Decompose a File

Read the file. Identify domain clusters (groups of related methods), shared state (`self.*` attributes), and cross-cluster method calls. Choose the right pattern from the table above and consult its reference doc.

Use `EnterPlanMode` to present the decomposition plan — target structure, method mapping, backward compatibility strategy. Execute after approval. Verify when done.

## Verification

After any decomposition, run:
1. The project's test suite — all tests must pass
2. Import check — old import paths must still work
3. For mixin pattern: verify zero method name collisions across mixins
4. Line count sanity — new total should be within ~10% of old (delta is boilerplate only)

For programmatic verification, run `python ${CLAUDE_SKILL_DIR}/scripts/verify.py <package_path>` if available.

## Gotchas

Common failure points when decomposing. Add to this list when you hit new ones.

- **Circular imports in mixin packages** — Mixin A imports a type from Mixin B which imports from A. Fix: move shared types to a `models.py` within the package.
- **`__init__` in mixins** — Only the base class or composed class should have `__init__`. Mixins are stateless method collections.
- **Forgotten re-exports** — If the old file exported `SomeEnum`, the new package's `__init__.py` must also export it. Grep the codebase for every `from old.path import X` and verify each `X` is re-exported.
- **Silent timeout regressions** — When extracting a base class, if subclasses had different default timeouts (e.g., 30s vs 60s), the base default can silently override the subclass. Always check `__init__` signatures before and after.
- **Stacked PRs checking wrong branch** — When reviewing decomposition PRs that depend on earlier PRs, always verify on the actual PR branch, not main. The PR branch has the parent changes; main does not.
- **Shim pointing to wrong subclass** — When a retired monolith class had methods from multiple domains, the shim must alias to whichever subclass has the methods callers actually used. Verify by grepping all call sites.
- **`@staticmethod` in mixin requires explicit class reference** — If a public wrapper delegates to a private `@staticmethod`, it must call `ClassName._method(args)`, not `self._method(args)`.
- **MRO order matters for `super().__init__`** — Base class must be LAST in the inheritance list. If it's first, mixins' `__init__` (if any exist accidentally) won't chain correctly.

## Principles

- **Zero breaking changes** — preserve all existing import paths
- **Mechanical moves only** — decomposition moves code, it doesn't rewrite behavior
- **One finding per PR** — don't bundle multiple refactors
- **Shims are cheap, breakage is expensive**
- **Tests first** — if the module lacks tests, add them before splitting
