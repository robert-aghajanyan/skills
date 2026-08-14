# Provenance

Use this file when reviewing where dependencies, build tools, images, and generated artifacts come from.

## High-Risk Provenance Signals

- Direct Git dependencies without commit SHAs.
- Dependencies from personal accounts, forks, unknown registries, or temporary package names.
- Tarball, zip, curl, wget, or binary downloads in install/build scripts without checksum or signature verification.
- GitHub Actions pinned to branches or tags instead of immutable SHAs in high-trust workflows.
- Docker images without digests, especially `latest` tags or unscoped public images.
- Build plugins that execute code during install or compile, including npm lifecycle scripts, Gradle plugins, Maven plugins, setuptools build backends, Cargo build scripts, and GitHub Actions.
- Vendored source without upstream URL, version, license, checksum, or regeneration command.
- Registry config that allows dependency confusion, such as private scopes not pinned to private registries or mixed public/private sources without scope restrictions.
- Typosquatting indicators: near-name packages, unexpected scopes, newly added tiny packages that resemble popular ones, or direct dependencies that duplicate standard-library functionality.

## Review Method

1. Trace dependency source from manifest to lockfile to CI install command.
2. Check whether the resolved source is immutable: content hash, integrity field, digest, commit SHA, or signed release.
3. Review install scripts and build hooks before recommending upgrades. A minor version bump can introduce new executable install behavior.
4. Review generated clients and vendored code for provenance comments, generation command, source schema, and repeatability.
5. For private packages, verify scope mapping and registry configuration without exposing tokens.

## Human Confirmation Items

- Whether a registry, fork, or vendor is approved by the organization.
- Whether GitHub Actions must be SHA-pinned in this repo.
- Whether Docker base images must use approved internal mirrors.
- Whether vendored code has an accepted exception.

## Safe Recommendations

- Pin mutable external references to immutable SHAs or digests where policy requires it.
- Add checksum or signature verification for downloaded binaries.
- Move private scopes to explicit private registries and fail closed on missing auth.
- Document vendored code source, version, license, and regeneration path.
- Disable install scripts only when the build does not require them, and validate with repo-native tests.
