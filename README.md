# Agent Skills

Public repository for Agent Skills — reusable skill packages for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

Skills are folders of instructions, scripts, and resources that Claude loads dynamically for specialized tasks. They extend Claude's capabilities without modifying its core behavior.

## Available Skills

| Skill | Description | Category |
|-------|-------------|----------|
| [decompose](skills/decompose/) | Audit and decompose large modules into smaller, maintainable units | Code Quality & Review |
| [optimize-prompt-caching](skills/optimize-prompt-caching/) | Audit and optimize LLM prompt caching in any codebase | Code Quality & Review |
| [skill-builder](skills/skill-builder/) | Create well-designed Claude Code skills from scratch | Code Scaffolding |
| [team-research](skills/team-research/) | Research and investigation swarm with adversarial debate | Business Process & Automation |
| [team-review](skills/team-review/) | Thorough PR review with 4 specialized agent teams | Code Quality & Review |

## Installation

### Install all skills

```bash
claude install-skill https://github.com/robert-aghajanyan/skills
```

### Install a specific skill

```bash
claude install-skill https://github.com/robert-aghajanyan/skills/tree/main/skills/decompose
```

## Usage

Once installed, skills are available as slash commands:

```
/decompose <file path>        # Decompose a large module
/optimize-prompt-caching      # Audit prompt caching
/skill-builder                # Create a new skill
/team-research <topic>        # Multi-agent research swarm
/team-review <PR>             # Multi-agent PR review
```

Claude also auto-triggers skills based on natural language — for example, saying "this file is too big, split it up" will activate the decompose skill.

## Skill Structure

Each skill is a self-contained directory under `skills/`:

```
skills/my-skill/
  SKILL.md           # Required: frontmatter + instructions
  LICENSE.txt        # License file
  references/        # Optional: detailed docs loaded on demand
  scripts/           # Optional: deterministic helper scripts
  assets/            # Optional: templates, examples
```

The core file is `SKILL.md` with YAML frontmatter:

```yaml
---
name: my-skill
description: What it does. Use when user says "trigger phrase".
---

# Instructions here
```

See the [template](template/) directory for a minimal starter, or use `/skill-builder` to create one interactively.

## Specification

For the full Agent Skills specification, see [agentskills.io](https://agentskills.io/specification).

## Contributing

1. Fork this repository
2. Create your skill directory under `skills/`
3. Include a `SKILL.md` with valid frontmatter and a `LICENSE.txt`
4. Validate with: `python skills/skill-builder/scripts/validate-skill.py skills/your-skill/`
5. Submit a pull request

## License

Individual skills are licensed under the Apache License 2.0 unless otherwise noted. See each skill's `LICENSE.txt` for details.
