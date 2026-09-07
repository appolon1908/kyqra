# Legacy source validation

This repository is retained for migration reference; `appolon1908-hue/kyqra-crawler`
remains the production crawler authority. Passing CI here does not authorize a runtime
release, live crawling, credential provisioning, or downstream delivery.

## Static Compose checks

CI copies each unmodified Compose model into a temporary project directory and uses
only its committed `.env.example` as an isolated `.env` fixture. It then runs ordinary
`docker compose config --quiet`, including interpolation and consistency checks.
This accommodates Compose versions that still require service env files to exist even
with `--no-env-resolution`. The fixture is removed on success and failure.

The source Compose files and their runtime env declarations are not changed. No
runtime `.env` in the checkout is read, overwritten, or created. Only documented
non-secret examples are copied; no runtime secret store or server is accessed.
These model checks are separate from the real Docker builds against the source tree.
A separately authorized runtime deployment must validate its actual configuration,
secrets, referenced paths, connectivity, and readiness privately. CI does not run
`compose up` or claim runtime certification.

See the Docker CLI documentation:
https://docs.docker.com/reference/cli/docker/compose/config/

## Regression coverage and evidence

Required CI runs ten Python validator tests, including real Docker Compose acceptance
and invalid-model rejection tests, before full repository validation. The two real
Compose tests are skipped only when running locally without Docker; GitHub's CI runner
executes them. Node tests cover the historical control plane, fail-fast syntax checks,
canonical-source authority, strict TypeScript builds, matching Playwright/browser
security-patch versions, and Docker context exclusions. Both source Dockerfiles remain
subject to real image builds. Evidence and image revision labels identify `SOURCE_SHA`
(the checked-out PR head), not the synthetic PR merge SHA in `GITHUB_SHA`.

## Dependency findings

The inherited deployment reference pinned vulnerable Playwright 1.55.0. Its dependency
and matching browser image are patched to 1.55.1 for GHSA-7mvr-c777-76hp. The audit on
head `007bc1cb...` reported no high or critical production dependency findings, but
moderate `stream-json`/Crawlee transitive advisories remain (GHSA-528h-pc64-c93x): eight
in the deployment reference and twelve in the root package. These are dependency-chain
counts, not twenty independent vulnerabilities. No unsafe forced downgrade or audit
bypass is applied. Consult the latest exact-head audit output; passing the existing
critical threshold is not a zero-vulnerability claim or production certification.
