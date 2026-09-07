# CLAUDE.md

Guidance for agents (Claude Code, Codex, etc.) working in this repository.
`AGENTS.md` is a symlink to this file — edit this one.

## What This Repo Is

A public marketplace of **Agent Skills** — reusable skill packages for Claude Code. Skills are self-contained folders of instructions, scripts, and reference docs that Claude loads dynamically via slash commands or auto-triggering.

## Repository Layout

- `skills/<kebab-case-name>/SKILL.md` — **required** frontmatter + instructions.
- `skills/<kebab-case-name>/LICENSE.txt` — **required** license file for each skill.
- `skills/*/references/` — optional detailed docs linked from `SKILL.md`.
- `skills/*/scripts/` — optional deterministic helper scripts.
- `skills/*/assets/` — optional templates and examples.
- `template/SKILL.md` — minimal starter for new skills (name + description, nothing else).
- `spec/agent-skills-spec.md` — local copy of the Agent Skills specification.
- `.claude-plugin/marketplace.json` — marketplace bundles and skill path metadata.

There is no package build step.

## Validate a Skill

```bash
python skills/skill-builder/scripts/validate-skill.py skills/<skill-name>/
```

Checks: SKILL.md exists with valid frontmatter, kebab-case name (max 64 chars, no "claude"/"anthropic"), description under 1024 chars with no XML tags, body under 500 lines, referenced files exist, and Gotchas section present.

## Verify a Mixin Decomposition

```bash
python skills/decompose/scripts/verify.py <package_path>
```

Checks method collisions across mixins, MRO validity, re-exports, and line counts.

## Architecture

### Skill anatomy

- `SKILL.md` is the only file Claude Code reads by default when loading a skill. Everything else is pulled in on demand.
- `references/` keeps `SKILL.md` under 500 lines — link to it rather than inlining long explanations.
- `scripts/` holds deterministic logic (e.g. `validate-skill.py`, `verify.py`) so Claude doesn't reinvent it each invocation.
- `assets/` holds templates and examples for Claude to copy and adapt.

### Key frontmatter fields

Defined in `skills/skill-builder/references/frontmatter-reference.md`. The important ones:

- `description` — How Claude decides when to auto-trigger the skill. Must include trigger phrases ("Use when...").
- `allowed-tools` — Tools Claude can use without permission prompts when the skill is active. Keep as narrow as possible.
- `disable-model-invocation: true` — Only user can invoke (for side-effect-heavy skills).
- `context: fork` — Runs in isolated subagent without conversation history.

### Variable substitutions in SKILL.md

- `$ARGUMENTS` — Args passed after the skill name.
- `${CLAUDE_SKILL_DIR}` — Directory containing the SKILL.md file.
- `` !`command` `` — Dynamic context injection (shell command output replaces the placeholder).

### Marketplace packaging

`.claude-plugin/marketplace.json` groups skills into named plugin bundles for bulk installation. Each plugin lists skill paths relative to repo root. A skill may appear in more than one bundle. Update this file when adding, removing, or regrouping published skills.

## Style Conventions

Kebab-case for skill directories and frontmatter names — `skills/team-review/` with `name: team-review`. Markdown: short sections, direct instructions, fenced code blocks for commands. Python helpers: standard-library-first, deterministic.

## Contributing a New Skill

1. Create `skills/<kebab-case-name>/` with a `SKILL.md` and `LICENSE.txt`.
2. Description must include "Use when..." trigger phrases.
3. Include a Gotchas section (even one item).
4. Keep SKILL.md body under 500 lines; move detail to `references/`.
5. Add the skill to the appropriate bundle(s) in `.claude-plugin/marketplace.json` and to `README.md`.
6. Run `validate-skill.py` on it. If it ships scripts, run them against a realistic fixture and note the command in the PR.

## Commit & PR Guidelines

Conventional Commit style, imperative mood — `feat: add api-audit skill`, `fix: update team-review trigger`. PRs should state the affected skill directories, the validation commands run, and their results. Keep generated artifacts out of the repo unless they are intentional examples under `assets/`.

## Security

Never commit secrets, tokens, private repository URLs, or machine-specific paths. Local agent state (`.claude/settings.local.json`, `.codex/`) is gitignored — keep it that way.
