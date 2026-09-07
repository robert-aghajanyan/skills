# Release Notes

## 2026-05-21 - Fail-Closed Ledger Hardening

- Enforced `mode: fast-strict` in the evidence ledger validator.
- Required `final_calibration.head_sha` to be present and match the current ledger head.
- Required the four core team-review lenses for every clean-review run, not only parallel runs.
- Added CLI smoke coverage for the validator in addition to direct Python API tests.
- Added golden ledger fixtures and manifest-based checksum provenance for the installed local skill.

## Provenance

This installed copy is a local skill package at `~/.claude/skills/pr-clean-review`.
No source repository or source commit is available from this directory. Use `manifest.json`
for file-level checksum provenance.
