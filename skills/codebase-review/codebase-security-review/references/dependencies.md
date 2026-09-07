# Dependency And Supply Chain Checks

Use this reference for package manifests, lockfiles, generated clients, container images, plugins, actions, build scripts, and runtime extension points.

## Inventory

- Package manifests and lockfiles: npm, pnpm, yarn, pip, uv, poetry, pipenv, Go, Rust, Maven, Gradle, Ruby, PHP, .NET, and system packages.
- Build and CI: Dockerfiles, compose files, GitHub Actions, reusable workflows, Makefiles, shell scripts, release scripts, artifact publishing, and code generation.
- Runtime extension points: plugins, marketplace packages, dynamic imports, model tools, browser extensions, webhooks, template packs, and user-supplied scripts.

## Review Checks

- Untrusted code execution during install, build, test, codegen, postinstall, plugin loading, or model/tool invocation.
- Dependency confusion: private package names without scoped registries, mixed registries, implicit registry fallback, or missing lockfiles.
- Unpinned or weakly pinned dependencies, actions, images, curl-to-shell installers, and base images.
- Lockfile drift or generated code that does not match manifests.
- Known vulnerable dependencies, especially auth, parsing, template, archive, crypto, HTTP, deserialization, and sandbox packages.
- Transitive trust in CLIs that receive secrets, write deployment artifacts, or run in CI with elevated tokens.
- License or provenance risks only when they can affect deployment, legal approval, or runtime trust; keep generic license inventory out of security findings unless it matters.

## Validation

- Prefer repo-native audit commands when available: package manager audit, dependency review, vulnerability scanner, or CI security job.
- Do not assume network audit output is current unless it was run during the review.
- If scans cannot run because network or credentials are unavailable, keep dependency vulnerability claims conditional and focus on observed unsafe trust patterns.
- Negative tests should target the vulnerable integration path, not just the package version.
