# CI/CD authority

## Repository

- Repository: `appolon1908-hue/kyqra`
- Class: `service`
- Purpose: Kyqra Node.js crawler/service
- Implementation authority: `package.json`, `src/`, `Dockerfile`, and `docker-compose.yml`

## Persistent branches

This repository uses the following persistent branch train:

```text
development
test
staging
production
main
```

Feature and repair branches should start from `development`. Promotion should proceed by reviewed pull request:

```text
feature/fix -> development -> test -> staging -> production -> main
```

The initial branch bootstrap places the same CI/CD policy commit on all five persistent branches. That bootstrap is not runtime deployment evidence.

## Required CI

`.github/workflows/required-ci.yml` runs on every branch push, pull request, and manual dispatch. It proves an exact clean checkout, runs a checksum-verified Gitleaks scan, validates JSON/YAML/Markdown, installs and audits Node dependencies, checks JavaScript syntax, runs declared scripts, validates Compose, builds Dockerfiles, and uploads sanitized evidence.

## Every-branch audit

`.github/workflows/all-branches-audit.yml` runs daily and manually. It fetches every branch tip and validates each in an isolated worktree, including legacy branches that predate this policy.

## Continuous delivery

`.github/workflows/continuous-delivery.yml` runs only on `development`, `test`, `staging`, `production`, and `main`. It creates deterministic source/build bundles, records the exact Git SHA/tree, calculates SHA-256 checksums, and can publish an immutable GHCR candidate from `staging`, `production`, or `main` only when a Dockerfile and committed Node lockfile are present.

Runtime deployment and all external effects remain unauthorized by this repository policy. A server deployment requires a separate protected-environment workflow with exact digest readback, health checks, rollback, and runtime credentials.

## Repository-specific blocker

The current `package.json` uses mutable `latest` dependency specifications and has no committed lockfile. Required CI validates the source, but immutable image publication remains blocked until dependencies are pinned and a reviewed lockfile is committed.

## Required GitHub settings

Protect `development`, `test`, `staging`, `production`, and `main` or apply equivalent repository rulesets. Require `required-ci`, approving review, resolved conversations, linear history, no force pushes, no deletion, and up-to-date protected promotions.
