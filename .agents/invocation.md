# Model-invoked vs user-invoked

Every `SKILL.md` in this repo is a skill. The one axis that splits them is **invocation**: who can reach it.

- **User-invoked**: reachable **only by the human typing its name**. Set `disable-model-invocation: true` in the frontmatter (Claude Code) and `policy.allow_implicit_invocation: false` in `agents/openai.yaml` (Codex). Use it for skills that write, delete, commit, publish, or spend a lot of tokens, and for interview-style skills the human has to drive.
- **Model-invoked**: reachable by **model or user**. Omit `disable-model-invocation` and omit the `policy` block from `agents/openai.yaml`. The `description` keeps rich trigger phrasing ("Use when the user asks for...") so auto-invocation fires.

The test for staying model-invoked: _could the model usefully reach for this on its own, and is it safe if it guesses wrong?_ Reuse is a reason to extract a skill, not a reason to make it model-invoked.

A skill is user-invoked in **both** harnesses or neither. Keep the frontmatter and the `agents/openai.yaml` in sync.

## The invariant this creates

No skill can start a user-invoked skill. Not by calling the Skill tool with its name, not by any other route. Only the human can.

This is load-bearing here, because most destructive skills in this repo are user-invoked: `codebase-cleanup` deletes files, `codebase-decomposition` rewrites modules, `pr-review-fix` commits. The suite that finds the work cannot be the thing that does the work.

## Dependencies between skills

Express an operative dependency as an explicit instruction to call the Skill tool with the named skill:

> Call the Skill tool with "team-review".

Not a bare `/team-review` left for the model to interpret, and not a deep `../other-skill/FILE.md` cross-reference. The Skill tool takes one skill per call: two skills is two calls.

When a step's precondition is a **user-invoked** skill, phrase it as an instruction for the human:

> Tell the user to run `/codebase-cleanup`; this skill cannot start it.

Router prose that just names skills for a human to pick from (`which-skill`, the bucket `README.md`s) is not invoking anything, so it keeps plain skill names as labels.

## Where this is recorded

- Per skill: `SKILL.md` frontmatter plus `agents/openai.yaml`.
- Per bucket: each promoted bucket's `README.md` groups entries under **User-invoked** and **Model-invoked**.
- Repo-wide: the top-level `README.md`, and the map inside `skills/meta/which-skill/SKILL.md`.
- Enforced: `scripts/check-consistency.py`.
