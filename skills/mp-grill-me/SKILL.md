---
name: mp-grill-me
description: Stress-test a plan or design through a relentless one-question-at-a-time interview until decisions and dependencies are resolved. Use when the user says "grill me", "stress-test this plan", "interview me about this design", or asks to walk a decision tree.
---

# Grill Me

Use this skill to interrogate a plan, design, proposal, or implementation approach until the agent and user share a precise understanding of what should happen and why.

## Instructions

Parse the current user request directly. Identify the plan or design under discussion, the desired outcome, and any constraints the user already gave.

Ask exactly one question at a time. For every question, include your recommended answer before waiting for the user.

Default question format:

```markdown
**Question:** ...

**Recommended Answer:** ...

**Why This Matters:** ...
```

Keep each question specific enough that the user can answer it directly. Avoid multi-part questions unless the parts are inseparable.

## Codebase Exploration Rule

If a question can be answered by inspecting the repository, files, prior artifacts, issues, PRs, or commands available in the current environment, inspect them instead of asking the user.

When exploration answers a branch:

- State the finding briefly.
- Reference exact files, paths, URLs, commits, issues, or commands where useful.
- Continue to the next unresolved decision with one question.

Use the repo's existing patterns and artifacts as evidence. Prefer `rg` and targeted file reads for codebase discovery.

## Interview Flow

1. Build a lightweight decision tree from the user's plan.
2. Resolve prerequisites first, then dependent choices.
3. Challenge assumptions, boundaries, failure modes, rollout, ownership, verification, and rollback.
4. After each user answer, update the working understanding and choose the next highest-leverage unresolved branch.
5. Keep going until the design has no material unresolved decisions, or until the user stops the interview.

Use a direct but constructive tone. Be rigorous without turning the exchange into a debate about already-settled facts.

## Recommended Answer Guidance

The recommended answer should be opinionated and practical. Base it on:

- The user's stated constraints.
- The codebase or artifact evidence discovered locally.
- The smallest decision that preserves future flexibility.
- The highest-risk failure mode if the choice is wrong.

If the recommendation depends on an unknown fact, say what assumption it rests on and ask the user to confirm or correct that assumption.

## Completion

When the decision tree is resolved, produce a concise closeout only if useful:

- agreed decisions
- open risks or assumptions
- immediate next steps
- artifacts that should be created or updated

Do not write plans, code, PRDs, tickets, or implementation changes unless the user explicitly asks to switch from interview mode into execution.

## Validation

Before using this skill in a real exchange, check that the next response:

- asks only one question
- includes a recommended answer
- does not ask for facts that local artifacts can answer
- identifies the decision branch being resolved

## Gotchas

- "Relentless" means thorough and sequential, not rude or repetitive.
- Do not batch a checklist of questions. The skill's value is resolving dependencies one branch at a time.
- Do not keep asking about a branch after the user has answered it unless a contradiction or new dependency appears.
- If the user only wants a critique rather than an interview, give the critique instead of forcing the grill-me protocol.
