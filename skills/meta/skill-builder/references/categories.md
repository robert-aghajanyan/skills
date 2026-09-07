# Skill Categories

Adapted from Thariq Shihipar's "Lessons from Building Claude Code: How We Use Skills." Category names are paraphrased for clarity. Skills that fit cleanly into one category work best. If a skill straddles several, consider splitting it.

## 1. Library & API Reference
Explains how to correctly use a library, CLI, or SDK. Includes gotchas, code snippets, and footguns.
- **Key content**: Reference code snippets, common mistakes, API patterns
- **Example**: `billing-lib` — your internal billing library edge cases

## 2. Product Verification
Describes how to test or verify that code is working. Often paired with tools like Playwright or tmux.
- **Key content**: Test scripts, assertion patterns, state verification
- **Example**: `checkout-verifier` — drives checkout UI with test cards, verifies invoice state
- **Tip**: Worth investing heavily in. Having Claude record video or enforce programmatic assertions at each step pays off.

## 3. Data Fetching & Analysis
Connects to data and monitoring stacks. Includes credentials, dashboard IDs, query patterns.
- **Key content**: Helper libraries, table/field mappings, common query workflows
- **Example**: `grafana` — datasource UIDs, cluster names, problem-to-dashboard lookup table

## 4. Business Process & Team Automation
Automates repetitive workflows into one command. Often simple instructions with dependencies on other skills or MCPs.
- **Key content**: Workflow steps, output format, log files for memory
- **Example**: `standup-post` — aggregates tickets, GitHub, Slack into formatted standup
- **Tip**: Saving previous results in log files helps the model stay consistent across runs.

## 5. Code Scaffolding & Templates
Generates framework boilerplate for a specific codebase function. Useful when scaffolding has natural language requirements.
- **Key content**: Templates, annotation patterns, generated file structure
- **Example**: `new-migration` — migration template plus common gotchas

## 6. Code Quality & Review
Enforces code quality and helps review code. Can include deterministic scripts. Good for hooks or GitHub Actions.
- **Key content**: Review checklists, style rules, testing practices
- **Example**: `adversarial-review` — spawns fresh-eyes subagent, iterates until findings degrade to nitpicks

## 7. CI/CD & Deployment
Helps fetch, push, and deploy code. May reference other skills.
- **Key content**: Build steps, deploy procedures, rollback patterns
- **Example**: `babysit-pr` — monitors PR, retries flaky CI, resolves merge conflicts, enables auto-merge

## 8. Runbooks
Takes a symptom (alert, error, Slack thread) and walks through investigation to produce a structured report.
- **Key content**: Symptom-to-tool mappings, query patterns, report templates
- **Example**: `oncall-runner` — fetches alert, checks usual suspects, formats finding
- **Structure tip**: Hub-and-spoke — SKILL.md dispatches to per-symptom files.

## 9. Infrastructure Operations
Routine maintenance with guardrails for destructive actions.
- **Key content**: Discovery steps, confirmation gates, cleanup procedures
- **Example**: `orphan-cleanup` — finds orphaned resources, posts to Slack, waits for confirm, then cleans up
