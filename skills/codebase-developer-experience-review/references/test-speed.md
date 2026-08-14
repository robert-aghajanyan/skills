# Test Speed

Use this reference when reviewing whether routine tests are fast, focused, and reproducible enough for daily development.

## Evidence To Collect

- Test commands from docs, package scripts, Makefiles, task runners, CI jobs, tox/nox config, pytest/Jest/Vitest/Cargo/Go/Maven/Gradle config, and framework-specific files.
- Test organization: unit, integration, e2e, smoke, contract, snapshot, fixtures, generated data, external service requirements, markers/tags, and watch modes.
- Runtime signals: measured command duration when safe, CI timing, cache usage, parallelism, service startup time, and test selection flags.

## Checks

- Developers have a fast default command for routine local validation.
- Full, slow, integration, e2e, and credential-dependent tests are clearly separated from focused checks.
- Docs explain how to run a single file, test name, package, marker, or changed subset.
- CI and local commands use compatible flags, fixtures, and environment assumptions.
- Slow tests are slow for real coverage reasons, not accidental sleeps, network calls, serial execution, or broad fixture setup.
- Test failure output points to the failing behavior without requiring large log archaeology.

## Common Findings

- The only documented test command runs the full integration suite and takes long enough that developers avoid it.
- Focused test flags exist in the framework but are not documented or wrapped by a script.
- CI uses parallelism or service containers that local commands do not account for.
- Unit tests silently require cloud credentials, databases, or generated assets without a quick skip or setup path.
- Snapshot or fixture regeneration commands are hidden, causing noisy local failures.

## Calibration

Measured time is strongest evidence. If you cannot run tests, use static evidence and say the speed risk is inferred from suite scope, service dependencies, or CI timing.
