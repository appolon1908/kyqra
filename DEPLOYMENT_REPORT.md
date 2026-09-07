# Control-plane alignment deployment report

## Repository authority — September 7, 2026

Historical migration reference only. `appolon1908-hue/kyqra-crawler` is the canonical
crawler runtime; this legacy repository must not create a second production API,
queue, credential set, Middleware contract, or deployment. PR #2 integrates source
history and CI, not a production release. No runtime deployment, live crawling,
secret provisioning, callback replay, or downstream delivery is authorized here.

The observations below were recorded on August 15, 2026. They are not current
production certification or a verified statement about today's Middleware allowlist.
Revalidate any applicable contract and activation evidence in the canonical repository.

## Historical report — August 15, 2026

### Implemented in branch

Versioned event envelopes, correlation/request propagation, tenant-scoped job APIs, Redis scheduler separation, Crawlee/Playwright worker, normalized/provenance-preserving results, tenant-local deduplication, durable SQLite WAL outbox, HMAC authentication, bounded retries, DLQ/manual audited replay, middleware circuit breaker, split health, metrics, structured redacted logging, persistent Docker services, and operator UI.

### Production activation status at that time

Not activated. Production SSH authentication was unavailable from this environment. The inspected middleware control-plane branch rejected required `crawler.*` events because it allowed only `kyqra.*`. Private TLS listener, firewall path, CA/mTLS materials, runtime service secrets, restart persistence, and live middleware/n8n acceptance remained unverified. No production host or unrelated container was changed.

### Historical activation evidence checklist

This checklist is retained for migration comparison only, not as permission to deploy this repository.

1. Confirm existing private HTTPS ingress and `/health`/`/ready` from `10.40.0.2`.
2. Provision dedicated Kyqra API/HMAC secrets and, if enabled, mTLS certificate/CA mounts.
3. Validate the middleware allowlist for the mandated event namespace and run valid/invalid/replay/idempotency tests.
4. Run outage/circuit/recovery and container/server restart tests, validate tenant isolation and public port exposure in an authorized isolated environment.
5. Confirm middleware-triggered n8n synthetic workflow and Odoo service-layer idempotency; attach evidence in the canonical repository before activation.
