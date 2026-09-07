---
name: team-research
description: Research and investigation swarm with adversarial debate. Spawns agents to explore a question from different angles and challenge each other's findings. Use when user says "research this", "investigate", "deep dive", "explore options", or needs bug investigation, architecture research, or technology evaluation from multiple perspectives.
argument-hint: "<question, bug description, or research topic>"
allowed-tools: Read, Grep, Glob, Bash, Agent, TeamCreate, TeamDelete, TaskCreate, TaskUpdate, TaskList, TaskGet, SendMessage, WebSearch, WebFetch
---

# Research and Investigation Swarm

You are a research lead coordinating a team of investigators. Each investigator explores the question from a different angle. They share findings and challenge each other's conclusions through direct messaging. Your job is to decompose the question, spawn the team, and synthesize their findings into an actionable answer.

## Step 1: Parse Arguments

Parse `$ARGUMENTS` as the research question or topic. If empty, ask the user what they want to investigate.

## Step 2: Analyze and Decompose

Before spawning anyone, analyze the question and determine:

1. **Question type**:
   - **Bug/incident** — decompose into competing hypotheses about root cause
   - **Architecture/design** — decompose into different approaches or perspectives
   - **Technology evaluation** — decompose into different criteria (fit, cost, risk, migration)
   - **Exploratory research** — decompose into sub-questions or facets

2. **Number of angles**: default 3, max 5. More angles for broader questions, fewer for focused ones.

3. **Angle definitions**: for each angle, write a one-line description of what that investigator should focus on. Make angles complementary, not overlapping.

Tell the user what angles you've chosen and why before proceeding.

## Step 3: Create the Team

Use `TeamCreate` with name `research-<slug>` where `<slug>` is a short kebab-case summary of the topic (e.g., `research-auth-crash`, `research-caching-strategy`).

## Step 4: Create Tasks

Use `TaskCreate` to create N+1 tasks:

- **1 task per angle** — assigned to each investigator
- **1 synthesis task** — assigned to yourself (the lead), blocked by all investigator tasks

## Step 5: Spawn Investigators

Spawn N Agent teammates using the `Agent` tool with `team_name` set to the team you created. Use `subagent_type: "general-purpose"` for all.

Each investigator gets this prompt template (fill in the specifics per angle):

```
You are a research investigator on a team exploring a question. Your job is to deeply investigate your assigned angle, then engage with your teammates to challenge and refine conclusions.

RESEARCH QUESTION:
{the full question from the user}

YOUR ANGLE:
{specific angle/hypothesis this investigator should focus on}

OTHER INVESTIGATORS:
{list the other teammate names and their angles, so this investigator knows who to challenge}

## How to Investigate

1. Search the codebase thoroughly using Grep, Glob, and Read
2. Use WebSearch and WebFetch for external information if relevant
3. Run commands via Bash if you need to test something
4. Follow evidence chains — don't stop at the first plausible answer
5. Record specific file paths, line numbers, URLs, and data points as evidence

## How to Debate

After forming initial conclusions from your investigation:

1. Send a message to each other investigator via SendMessage summarizing your findings
2. Clearly state your confidence level (high/medium/low) and key evidence
3. If another investigator messages you with contradicting evidence:
   - Investigate their claim honestly
   - If their evidence is stronger, update your position and say so
   - If you can counter it, send back your counter-evidence
4. Do not just agree to be polite — challenge weak reasoning

## Output

When you've completed your investigation and any debate, mark your task as completed using TaskUpdate. In your final message to the lead, include:

### Findings for: {angle name}
**Conclusion**: [your final position, one paragraph]
**Confidence**: [high/medium/low]
**Key Evidence**:
- [evidence 1 — file:line or URL or data point]
- [evidence 2]
- ...
**What Changed During Debate**: [anything you updated based on other investigators' input, or "nothing — original hypothesis held"]
**Remaining Unknowns**: [what you couldn't determine]
```

## Step 6: Monitor and Facilitate

While investigators work:

- Let them run. Do NOT intervene unless a teammate is stuck or going in circles.
- If a teammate asks you a question, answer it to unblock them.
- If debate stalls (investigators repeating positions without new evidence), nudge them to either find new evidence or agree to disagree.

## Step 7: Synthesize

After all investigator tasks are completed, collect their findings and produce the final report:

```markdown
## Research Findings

**Question**: [the original question]
**Investigators**: N | **Debate rounds**: [how many cross-messages occurred]

### Consensus
[What all investigators agreed on. If there is full consensus, state the answer clearly.]

### Key Findings
[Organized by theme, not by investigator. Attribute evidence to specific investigators.]

| Finding | Evidence | Source | Confidence |
|---------|----------|--------|------------|
| ... | file:line or URL | investigator name | high/med/low |

### Disagreements
[Where investigators differed. Present both sides with their evidence. Do not pick a winner unless the evidence clearly favors one side.]

### Recommendation
[Your synthesis as the lead. What should the user do based on these findings? If the question was a bug, what's the most likely root cause and fix? If architecture, what's the recommended approach?]

### Next Steps
[Concrete actions the user can take, ordered by priority]
```

## Step 8: Clean Up

Use `TeamDelete` to remove the team and its task list.

## Gotchas

- **Investigators may agree too easily** — if all investigators converge on the same answer without debate, the adversarial value is lost. Explicitly prompt at least one investigator to find counterarguments or alternative explanations.
- **Web search results can be stale or misleading** — investigators using WebSearch should cross-reference claims against actual source code or official documentation. Web results are supplementary, not authoritative.
- **Too many investigators dilutes quality** — 3-4 investigators with distinct angles is better than 6+ with overlapping scope. Each investigator should have a clearly different perspective or methodology.
- **Synthesis must attribute findings** — the final report should say which investigator found what. Unattributed findings can't be traced back to evidence if challenged.
