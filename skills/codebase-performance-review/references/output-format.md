# Output Format

Use this report shape for performance reviews.

## Executive Summary

State:

- Overall performance risk level.
- Top 2-4 confirmed risks.
- Most important scale variable.
- Whether more measurement is needed before code changes.

## Performance Surface Map

List the important surfaces and classify each as hot, scale-sensitive, startup-sensitive, cost-sensitive, memory-sensitive, or low priority.

Include:

- APIs and user-facing flows.
- CLIs, jobs, workers, scheduled tasks, reports, and batch processors.
- External clients, database access, file IO, cache layers, startup paths, and slow tests.
- Known traffic, data size, cadence, or input bounds when available.

## Findings By Severity

Order findings by Blocker, High, Medium, Low, Nit.

Each finding must include:

- Title.
- Severity.
- Confidence: High, Medium, or Low.
- Evidence: file and line references.
- Trigger: input size, traffic pattern, schedule, data shape, or usage pattern.
- Impact: latency, throughput, cost, memory, startup, CI time, timeout, backlog, or operational pressure.
- Recommended fix.
- Validation method.

Use confirmed findings for issues directly supported by code evidence. Use the risky-but-unconfirmed section for plausible concerns that need measurement.

## Quick Wins

List low-risk fixes that are likely to pay off quickly, such as removing repeated work, adding limits, using existing batching APIs, avoiding per-item logging, or reusing initialized clients.

Do not include speculative caches or concurrency as quick wins unless correctness risks are handled.

## Measurement Plan

Name the exact benchmark, profile, trace, query-count check, load test, integration test, or timing command that would confirm the risk or validate the fix.

Where possible, include:

- Dataset or request size.
- Baseline metric.
- Success threshold.
- Command to run.
- What to inspect in the output.

## Risky But Unconfirmed Areas

Use this section for hypotheses. For each item, say:

- Why it looks risky.
- What evidence is missing.
- How to measure it.
- What threshold would turn it into a confirmed finding.

## Validation Commands

List commands actually run first, then commands recommended but not run. If a command was skipped or failed, say why.
