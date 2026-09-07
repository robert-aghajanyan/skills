# Output Format

Use this structure for dependency and supply-chain review reports. Keep it concise, evidence-first, and separated by confirmed vs conditional risk.

## Dependency Map

- Repository target and baseline reviewed.
- Package managers and ecosystems detected.
- Manifests and lockfiles reviewed.
- Runtime images, Dockerfiles, CI install steps, GitHub Actions, build plugins, generated clients, vendored code, and registry config.
- Commands run and whether they used network access.

## Findings

Order findings by severity: Blocker, High, Medium, Low, Nit. Use this template for each finding:

```markdown
### [Severity] Short Finding Title

- Affected file: `path`
- Dependency: `name` at `version/range`
- Evidence: exact manifest, lockfile, script, CI, or code evidence
- Risk: practical impact for this repository
- Confidence: High/Medium/Low, with reason
- Recommended action: minimal compatible fix
- Validation command: repo-native command or focused check
```

## Required Sections

### Lockfile And Manifest Hygiene

Cover manifest vs lockfile drift, multiple lockfiles, stale or missing lockfiles, unpinned ranges, duplicate packages, dev/runtime confusion, and generated dependency artifacts.

### Supply-Chain Risks

Cover install scripts, direct Git or URL dependencies, unverified binaries, vendored code, unknown package provenance, dependency confusion, typosquatting indicators, broad ranges, mutable Docker images, and floating GitHub Action refs.

### License Concerns

Cover missing license metadata, restrictive or policy-sensitive licenses, bundled third-party code, unclear attribution, and any items needing legal or policy confirmation.

### Vulnerability And Freshness Findings

Separate local evidence from live advisory or freshness data. Include scanner commands and whether they were run.

### Safe Cleanup Candidates

List low-risk cleanup opportunities such as unused dependency candidates, duplicate packages, stale generated dependency directories, obsolete lockfiles, or dev dependencies that can be moved. Label these as candidates unless verified.

### Validation Commands

List the exact commands run and recommended next commands. Mark commands that may need network access, credentials, or package installation.

### Items Requiring Human Or Policy Confirmation

List questions that depend on organizational policy, legal review, approved registries, vendor allowlists, or deployment/distribution model.

## Calibration

Before finalizing:

- Remove findings that lack concrete local evidence.
- Merge duplicate findings across ecosystems when they share one root cause.
- Downgrade issues that are policy preferences without reachable risk.
- Keep upgrade recommendations minimal and testable.
