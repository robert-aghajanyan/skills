# Output Format

Use concise, evidence-first output. For assessment-only work, lead with the candidate ledger.

## Assessment Summary

Include:

- repo/ref inspected
- mode: assessment-only; state that no files were modified
- commands and files used for discovery
- candidate counts by classification
- highest-risk uncertainty
- overall confidence score and the evidence behind it

## Candidate Ledger

Use one row or short subsection per candidate:

- **Candidate**: path, symbol, command, artifact, dependency, or workflow
- **Type**: duplicate logic, wrapper sprawl, stale option, unused symbol, orphaned artifact, or dependency island
- **Classification**: removal-ready, consolidate-ready, deprecate/migrate, needs human confirmation, or do-not-touch
- **Evidence**: exact references, commands, manifests, docs, tests, or search results
- **Impact If Removed**: what would break, disappear, simplify, or need migration
- **Recommendation**: future removal, future consolidation, migrate callers, deprecate, leave alone, or investigate further
- **Confidence**: 0-100 score plus label, with the top reasons the score is not higher
- **Evidence Gaps**: what is not yet proven
- **Follow-Up Evidence Plan**: exact searches, owner checks, parity checks, runtime probes, or dependency/artifact checks needed to improve confidence
- **Pre-Deletion Validation**: tests, builds, smoke checks, artifact regeneration, staged deprecation checks, or owner confirmations required before a separate implementation workflow removes anything

## Prioritized Cleanup Plan

Group candidates into small batches:

1. safe artifact/dependency cleanup candidates
2. low-risk caller migration candidates
3. wrapper consolidation candidates with compatibility preserved
4. deprecation candidates requiring owner confirmation
5. high-risk or do-not-touch items

Each batch should be independently reviewable and reversible.

## Follow-Up Validation Plan

When any candidate is below 90 confidence or marked deprecate/migrate or needs human confirmation, include a follow-up plan grouped by priority:

- quickest checks that can eliminate false positives
- runtime or integration checks that prove active usage
- parity tests needed before consolidation
- owner confirmations needed for public, external, scheduled, or plugin surfaces
- final validation command set required before deletion

Do not recommend immediate deletion for candidates whose follow-up plan still contains unresolved external reachability or behavioral parity questions.

## Assessment Closeout

At the end, report:

- no files modified
- commands run
- commands not run and why
- remaining candidates and residual risks
- handoff plan for a separate implementation workflow, if requested
