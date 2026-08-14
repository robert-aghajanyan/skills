# Release Notes

This file records the local package contract for the `production-readiness-gate` skill. Keep it current whenever behavior, validation, fixtures, provenance, or support files change.

## 1.1.1

Date: 2026-05-21

### Changed

- Added golden transcript examples for the response-contract fixtures so expected outputs are auditable without relying only on marker lists.
- Extended the semantic smoke test to validate golden transcript examples, release notes, manifest source metadata, and source tag fields when present.
- Added optional `--source-tag` manifest provenance support.
- Promoted the Playground copy as the local source package for this installed skill.

### Validation

- `python3 "/Users/rob/.claude/skills/skill-builder/scripts/validate-skill.py" "/Users/rob/.claude/skills/production-readiness-gate"`
- `python3 "${CLAUDE_SKILL_DIR}/scripts/smoke_production_readiness_gate.py" "/Users/rob/.claude/skills/production-readiness-gate"`

### Source Provenance

The installed copy should be stamped from the local source package at `<local-source-checkout>/production-readiness-gate`.

When a source commit exists, regenerate the installed manifest with:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/update_manifest.py" \
  "/Users/rob/.claude/skills/production-readiness-gate" \
  --source-repo "<local-source-checkout>/production-readiness-gate" \
  --source-commit "<commit-sha>" \
  --source-tag "<tag-name>" \
  --version "1.1.1"
```

If no source commit exists, do not claim commit-level provenance. Use manifest checksums as the source-of-truth evidence.
