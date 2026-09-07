# Evidence Rules

Cleanup advice is only useful when it is backed by evidence. Treat every candidate as unproven until checked.

## Minimum Evidence

For each recommendation, include:

- path or manifest entry
- candidate category: safe, likely, risky, or do-not-touch
- evidence gathered, with exact commands or tools
- risk assessment
- recommended action
- validation needed or already performed

## Reference Checks

Use repo-native and language-aware checks before generic guesses:

- `git status --short --branch`
- `git ls-files`, `git ls-files --others --ignored --exclude-standard`, and `git check-ignore -v`
- `rg` for file names, symbols, command names, import paths, package names, and generated output names
- package-manager tools such as `npm ls`, `npm query`, `pnpm why`, `yarn why`, `pipdeptree`, `pip show`, `poetry show`, `uv tree`, `cargo metadata`, `go list`, `bundle info`, or equivalent
- build, test, CI, Makefile, task-runner, Docker, deployment, and release configs
- import graph or dead-code tools already used by the repo

Prefer exact repo commands over introducing new tools. If a tool is missing or would require network access, note that limitation.

## Dynamic Usage

Mark as "needs human confirmation" when usage may come from:

- reflection or dynamic imports
- plugin discovery, entrypoints, hooks, or naming conventions
- config, environment variables, templates, or generated code
- external callers, public APIs, CLIs, scheduled jobs, deployment platforms, or CI
- tests or fixtures selected by glob patterns

Absence from static search is not enough evidence for these cases.

## Strong Evidence Examples

Strong evidence can include:

- tracked artifact is ignored by the repo and reproducible from a documented command
- dependency has no imports, no package script usage, no config usage, and package-manager metadata shows no required relationship
- script has no references in docs, CI, package scripts, Make targets, task runners, or release automation
- doc command fails or points to renamed files, while current repo-native command succeeds
- duplicate utility has identical behavior covered by tests and all references already use the canonical implementation

## Weak Evidence Examples

Do not delete based only on:

- "looks old"
- no recent commits
- filename seems temporary
- source search found no direct import
- dependency not imported in application code
- test file seems redundant
- generated-looking file without proving how it is regenerated
