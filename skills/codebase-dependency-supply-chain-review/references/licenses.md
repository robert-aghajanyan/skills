# Licenses

Use this file to identify license and attribution risks. Treat legal conclusions as policy-confirmation items unless the repository has an explicit license policy.

## Evidence Sources

- Manifest license fields: `package.json`, `pyproject.toml`, `Cargo.toml`, gemspecs, `composer.json`, Maven POMs, Gradle metadata, NuGet metadata.
- Lockfiles and installed package metadata when available.
- Repository files: `LICENSE`, `NOTICE`, `THIRD_PARTY_NOTICES`, `COPYING`, `vendor/**/LICENSE*`, `third_party/**/LICENSE*`.
- Generated client headers and vendored code comments.
- SBOM files such as CycloneDX, SPDX, `bom.json`, `sbom.spdx.json`, or release attestations.

## Risk Patterns

- Missing license metadata for production dependencies or vendored code.
- Copyleft or network-copyleft licenses in distributed products or hosted services, including GPL, AGPL, LGPL, EPL, MPL, and similarly restrictive terms.
- Commercial, source-available, evaluation, field-of-use, or custom licenses in production paths.
- Bundled third-party source without a license file, notice file, provenance link, or regeneration path.
- Dual-licensed dependencies where the selected license is unclear.
- Generated clients copied from another repo without preserving upstream notices.

## Review Method

1. Identify distribution model: internal tool, hosted service, shipped binary, SDK, library, container image, or customer-facing artifact.
2. Separate production dependencies from dev/test/build-only dependencies.
3. Look for bundled code and generated code before relying only on package manifest metadata.
4. Check whether repository notices cover the dependencies actually shipped.
5. Mark anything requiring legal or policy interpretation as human confirmation, not a definitive legal finding.

## Reporting Guidance

- Include dependency name, version or range, source file, license string if available, and why the license may matter for this repository.
- Do not use vague labels like "bad license." Explain the policy or distribution concern.
- Recommend minimal actions: add missing attribution, clarify license selection, replace only when policy requires it, or get legal approval.
