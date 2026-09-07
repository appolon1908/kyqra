# Legacy source validation

This repository is retained for migration reference; `appolon1908-hue/kyqra-crawler`
remains the production crawler authority. Passing CI here does not authorize a runtime
release, live crawling, credential provisioning, or downstream delivery.

## Static Compose checks

CI uses the committed `.env.example` for variable interpolation and
`docker compose config --no-env-resolution --quiet` to validate the source model.
Service-level runtime `env_file` contents are intentionally not loaded. The source
Compose files and their required runtime `.env` declarations are not changed, and
consistency validation and interpolation remain enabled. A separately authorized
runtime deployment must validate its actual secret-bearing configuration privately.
CI must not create a runtime `.env`, copy secrets, run `compose up`, or suppress errors.

See the Docker CLI documentation:
https://docs.docker.com/reference/cli/docker/compose/config/

## Regression coverage and evidence

The Required CI workflow runs seven Python validator tests before the full repository
validator. Node tests cover the historical control plane, fail-fast syntax checks,
canonical-source authority, strict TypeScript builds, and matching Playwright/browser
security-patch versions. Both source Dockerfiles remain subject to real image builds.
Evidence and image revision labels identify `SOURCE_SHA` (the checked-out PR head),
not the synthetic pull-request merge SHA exposed separately as `GITHUB_SHA`.

## Dependency findings

The inherited deployment reference pinned vulnerable Playwright 1.55.0. Its dependency
and matching browser image are patched to 1.55.1 for GHSA-7mvr-c777-76hp. The audit on
the preceding repair head also reported moderate `stream-json`/Crawlee transitive
advisories (GHSA-528h-pc64-c93x); no unsafe forced dependency downgrade or audit bypass
is applied. Consult the latest exact-head audit output; passing the existing critical
threshold does not mean there are zero vulnerabilities or that production is certified.
