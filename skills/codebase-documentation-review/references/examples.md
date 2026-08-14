# Examples

Use this reference when reviewing tutorial code, snippets, sample configs, sample requests, walkthroughs, screenshots, fixture docs, SDK examples, CLI examples, and copy-paste commands.

## Evidence To Compare

- Current imports, packages, public APIs, CLI flags, config schemas, fixtures, generated clients, sample apps, tests, and documented command outputs.
- Package scripts, language-specific format or compile tools, and minimal runtime commands that can validate examples safely.

## Checks

- Snippets compile, parse, or are clearly marked as pseudocode.
- Imports, packages, symbols, method names, flags, paths, env vars, and config keys are current.
- Example requests and responses match implementation or generated schemas.
- Sample output is still representative, especially for fields users depend on.
- Examples include required setup context without repeating the entire setup guide.
- Copy-paste commands include working directory assumptions when needed.
- Screenshots and diagrams match current UI, CLI output, API behavior, or architecture.
- Examples do not depend on private local state, hidden seed data, or unmentioned credentials.

## Common Findings

- A code block imports a renamed module or calls a removed SDK method.
- A CLI example uses a flag that the parser no longer accepts.
- A sample config omits a required key added in code.
- A tutorial references a fixture or path that moved.
- A screenshot or sample response shows fields that users will no longer see.

## Calibration

It is acceptable for examples to be minimal. Flag minimalism only when the omitted context makes the example fail, teaches the wrong contract, or hides a required operational step.
