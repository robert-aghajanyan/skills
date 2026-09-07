---
name: codebase-dependency-supply-chain-review
description: Review repositories for dependency, package, lockfile, license, provenance, and software supply-chain risk. Use when the user asks for dependency review, supply-chain review, package risk, lockfile hygiene, license review, dependency freshness, vulnerable dependencies, package provenance, vendored code, or dependency cleanup.
---

# Dependency Supply-Chain Review

Use this skill to review any repository's dependency surface and software supply-chain posture. Findings must be grounded in local repository evidence first; separate local evidence from any online advisory or freshness data.

## Workflow

1. Define the review target, repo root, trusted baseline, changed files, deployment context, and whether network access is allowed.
2. Build a dependency map: package managers, manifests, lockfiles, vendored code, generated clients, Docker images, CI install steps, runtime images, build plugins, GitHub Actions, and package registries. When useful, start with the read-only helper:

   ```bash
   python "${CLAUDE_SKILL_DIR}/scripts/dependency_inventory.py" <repo-root>
   ```

3. Check consistency and hygiene: manifest vs lockfile drift, multiple lockfiles, stale lockfiles, unpinned ranges, unused dependency candidates, duplicate packages, dev/runtime dependency confusion, and generated dependency artifacts.
4. Review supply-chain risk: install/postinstall scripts, direct Git URL dependencies, unverified binaries, vendored code, abandoned packages, typosquatting indicators, dependency confusion risks, broad version ranges, unknown provenance, and mutable external references.
5. Review license and policy risk: missing license metadata, incompatible licenses, bundled third-party code, unclear attribution, and production dependencies with restrictive terms.
6. Review vulnerability posture with repo-native audit tooling where available. If live vulnerability or freshness data requires network access, ask before using it. Clearly label confirmed local evidence separately from online advisory results.
7. For each finding, include the affected manifest or lockfile, dependency name and version/range, evidence, risk, confidence, recommended action, and validation command.
8. Prefer minimal, compatible, tested dependency changes. Do not recommend upgrades blindly.

## Reference Guide

- Package manager and manifest mapping: [references/package-managers.md](references/package-managers.md)
- Lockfile drift and consistency checks: [references/lockfiles.md](references/lockfiles.md)
- License and attribution review: [references/licenses.md](references/licenses.md)
- Provenance and supply-chain risk patterns: [references/provenance.md](references/provenance.md)
- Vulnerability triage: [references/vulnerability-triage.md](references/vulnerability-triage.md)
- Report structure and finding template: [references/output-format.md](references/output-format.md)

## Output

Use [references/output-format.md](references/output-format.md). Findings should be ordered by severity: Blocker, High, Medium, Low, Nit. Include sections for dependency map, lockfile and manifest hygiene, supply-chain risks, license concerns, vulnerability/freshness findings, safe cleanup candidates, validation commands, and items requiring human or policy confirmation.

## Gotchas

- Do not run install, audit, or freshness commands that need network access without user approval.
- Do not treat every non-exact version range as a vulnerability; explain the reachable risk and the lockfile context.
- Do not claim license incompatibility unless the repository policy or distribution model supports that conclusion.
- Do not expose secret registry tokens, private package URLs, or credentials in findings.
- Generated and vendored code may be intentional; verify ownership, regeneration path, and attribution before recommending removal.
