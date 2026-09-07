# Repository Profile — `kyqra`

## Identity

- **Repository:** `appolon1908-hue/kyqra`
- **Category:** Legacy crawler repository
- **Visibility:** `public`
- **Default branch:** `main`
- **Authority:** Historical migration reference only; `kyqra-crawler` is canonical
- **Status:** Deprecated for new crawler development and retained for history.

## Purpose

Preserves the earlier Dockerized Kyqra crawler/scraper design, operational notes, and migration context while future fixes, contracts, tests, and releases live in `kyqra-crawler`.

## Owns

- Historical crawler source and documentation
- Migration comparison material
- Rollback/reference evidence for the old lineage

## Does not own

- A second production crawler API, queue, job ledger, credential set, or deployment
- New feature development
- Direct Odoo or product-database writes

## Key integrations

- `kyqra-crawler`
- Middleware as the governed write/control boundary
- Kong and n8n through canonical contracts

## Current priorities

1. Keep authority/deprecation language explicit
2. Preserve useful migration and rollback evidence
3. Remove any implication that historical quick-start commands are production approval
4. Archive after the canonical migration and retention window are complete

## Governance and safety

- Changes should be documentation, migration, security, or preservation work only.
- Use pull requests and exact-head validation; merging source never authorizes deployment.
- Never commit secrets, credentials, private keys, customer data, database dumps, or secret-bearing evidence.
- Do not create new runtime, queue, provider, or production authority here.
- This document does not deploy software or activate production.

## Account-wide catalog

See `appolon1908-hue/documentaions/REPOSITORY_CATALOG.md`.
