# CLAUDE.md

Guidance for agents (Claude Code, Codex, etc.) working in this repository.
`AGENTS.md` is a symlink to this file — edit this one.

## What This Repo Is

A public marketplace of **Agent Skills** — reusable skill packages for Claude Code, shipped as **one** plugin. Skills are self-contained folders of instructions, scripts, and reference docs that Claude loads dynamically.

## Layout

Skills live in bucket folders under `skills/`:

- `codebase-review/` — dimension-specific deep reviews of an existing repo
- `pr-review/` — review, fix, and merge-readiness workflows for PRs
- `engineering/` — daily code work
- `planning/` — stress-testing plans, turning them into specs and tickets
- `productivity/` — general workflow tools, not code-specific
- `meta/` — building skills, and navigating this repo
- `in-progress/` — beta: public on purpose, not shipped in the plugin
- `deprecated/` — retired, not shipped in the plugin

The first six are **promoted**: the plugin ships exactly those. See [ADR 0002](.agents/adr/0002-bucket-folders-and-the-promoted-set.md).

Each skill is `skills/<bucket>/<name>/` containing:

- `SKILL.md` — **required.** Frontmatter + instructions. The only file Claude reads when loading the skill; everything else is pulled in on demand.
- `LICENSE.txt` — **required.**
- `agents/openai.yaml` — **required.** Codex display metadata and invocation policy.
- `references/` — optional detail, linked from `SKILL.md`, keeps it under 500 lines.
- `scripts/` — optional deterministic helpers.
- `assets/` — optional templates and examples.

Also: `template/SKILL.md` (starter), `spec/agent-skills-spec.md` (local spec copy), `.agents/` (repo conventions and ADRs).

## Invocation: the one axis that splits skills

Every skill is **user-invoked** (`disable-model-invocation: true` plus `policy.allow_implicit_invocation: false` in `agents/openai.yaml`) or **model-invoked** (neither). A skill is user-invoked in both harnesses or neither.

Anything that deletes, rewrites, commits, publishes, or spends a lot of tokens is user-invoked. **No skill can start a user-invoked skill** — only the human can. When a step depends on one, say "tell the user to run `/name`", never "call the Skill tool". Full rules in [.agents/invocation.md](.agents/invocation.md).

Operative dependencies on model-invoked skills are written as `Call the Skill tool with "name"` — one skill per call, not a bare `/name`, not a `../other-skill/FILE.md` link.

## Upstream: the mp-* skills

Every skill prefixed `mp-` is a **port** of a skill from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT), not a fork. Content matches upstream byte for byte; only the following are changed, and only these:

- the skill name gains the `mp-` prefix, and cross-skill references are rewritten to our namespace;
- upstream `code-review`, `research`, and `ask-matt` references point at our `team-review`, `team-research`, and `which-skill`, which is why those three are not ported;
- `mp-setup` (upstream `setup-matt-pocock-skills`) is debranded, whitelisted in the sync checker.

**Do not hand-edit an `mp-` skill.** A local improvement belongs upstream, or in a new non-`mp-` skill. To re-sync:

```bash
python3 scripts/check-upstream-sync.py          # summary of drift
python3 scripts/check-upstream-sync.py --diff   # what actually changed
```

It clones upstream, reverses our renames, and diffs. Zero drift is the expected state. See [ADR 0004](.agents/adr/0004-mp-skills-are-ports-not-forks.md).

## Checks

```bash
python3 skills/meta/skill-builder/scripts/validate-skill.py skills/<bucket>/<name>/
python3 scripts/check-consistency.py
claude plugin validate . --strict
```

`validate-skill.py` checks frontmatter, kebab-case name (max 64 chars, no "claude"/"anthropic"), description under 1024 chars with no XML tags, body under 500 lines, referenced files exist, and a Gotchas section.

`check-consistency.py` is the one that catches drift: a promoted skill missing from `plugin.json`, a bucket README, the top-level README, or the `which-skill` map; a non-promoted skill leaking into the plugin; the two manifest versions disagreeing; a skill whose invocation axis differs between harnesses.

All three run in CI ([.github/workflows/ci.yml](.github/workflows/ci.yml)).

`python3 scripts/check-upstream-sync.py` checks the `mp-` ports against upstream.

`python3 skills/engineering/decompose/scripts/verify.py <package_path>` verifies a mixin decomposition (method collisions, MRO, re-exports, line counts).

## Adding a Skill

1. Pick a bucket. Create `skills/<bucket>/<kebab-case-name>/` with `SKILL.md`, `LICENSE.txt`, and `agents/openai.yaml`.
2. Decide the invocation axis and set it in **both** files.
3. Model-invoked descriptions carry rich trigger phrasing ("Use when..."). User-invoked descriptions are a human-facing one-liner.
4. Include a Gotchas section (even one item). Keep the body under 500 lines.
5. If promoted, add it to `.claude-plugin/plugin.json`, its bucket `README.md`, the top-level `README.md`, and the map in `skills/meta/which-skill/SKILL.md`.
6. Run the three checks above. If it ships scripts, run them against a realistic fixture and note the command in the PR.

The `which-skill` router lies the moment a skill is added, renamed, or removed without updating it. Re-read it whenever the set changes.

## Releasing

One version number, in `.claude-plugin/plugin.json`; `marketplace.json`'s `metadata.version` mirrors it. Bump both together and tag. Claude Code uses the plugin `version` to decide when installed users see an update. See [ADR 0003](.agents/adr/0003-version-lives-only-in-plugin-json.md).

## Style

Kebab-case for skill directories and frontmatter names. Markdown: short sections, direct instructions, fenced code blocks. Python helpers: standard-library-first, deterministic. Conventional Commits, imperative mood.

Install wording is copied verbatim from [.agents/install-block.md](.agents/install-block.md). Change it there first, then propagate. `claude install-skill` is not a command; never write it.

## Security

Never commit secrets, tokens, private repository URLs, or machine-specific paths — no `/Users/<name>/...` in a skill, use `${CLAUDE_SKILL_DIR}`. Keep `allowed-tools` as narrow as possible. Local agent state (`.claude/settings.local.json`, `.codex/`) is gitignored; keep it that way.
