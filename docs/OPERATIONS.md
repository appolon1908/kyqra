# Operations

> Historical implementation reference only. `appolon1908-hue/kyqra-crawler` is the
> canonical crawler authority. The procedures below are migration test scenarios,
> not authorization to deploy this legacy repository or enable external effects.

For an authorized isolated migration test, validate `docker compose config`, run `npm test`, back up the persistent storage volume, and confirm the relevant ingress/CA using read-only `/health` and `/ready` probes. Do not recreate unrelated shared-host containers.

The historical endpoints are `/api/v1/health`, `/metrics`, and `/admin/integration`. The latter reports endpoint, circuit state, event throughput/backlog, attempts, last success/failure, errors, and manual replay. Normal clients use tenant-filtered job, result, status, and usage APIs and cannot access this page's data without the admin key. Live callbacks and replay remain unauthorized by this source merge.

Isolated restart persistence scenario: submit a synthetic job to a test-only target with a mock Middleware receiver, stop API/outbox after an event becomes pending, restart the stack, and verify the same event ID is accepted idempotently. Recovery scenario: make the mock receiver unavailable, wait for the circuit to open, restore it, and verify half-open then closed. Rollback rehearsals must retain the volume so queued events are not lost; no production outage or firewall change is authorized here.

The historical Prometheus collector exposes outbox states and circuit state. Job/result/duplicate and queue utilization metrics require further collectors or API stats/Redis inspection. Production observability, thresholds, and release evidence belong to the canonical repository and must be separately certified.
