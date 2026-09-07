# Middleware integration

> Historical implementation reference only. `appolon1908-hue/kyqra-crawler` is the
> canonical crawler authority. Do not provision credentials, alter Middleware, or
> deploy this legacy repository based on these historical instructions.

The historical default destination is `https://10.40.0.1:443/api/v1/events/kyqra`. Any applicable migration must confirm the existing private ingress; no listener is created by this repository.

The historical request contract is JSON plus `Authorization: Bearer <KYQRA_MIDDLEWARE_API_KEY>`, `Idempotency-Key`, `X-Event-Id`, `X-Timestamp`, and `X-Signature`. The HMAC-SHA256 input is `timestamp + "\\n" + event_id + "\\nkyqra\\n" + exact_body`; signatures are hex with `sha256=` prefix. Kyqra aliases are also sent in `X-Kyqra-*`. The corresponding Middleware contract requires constant-time API-key/signature checks, a 300-second freshness window, event/idempotency replay protection, and the original successful disposition for an identical replay. These requirements are not evidence that the current production receiver satisfies them.

mTLS files were intended to be mounted at `/run/secrets`, only after confirming the ingress trust chain. Secrets belong in the host runtime env/secret store, never Git.

Historical compatibility note (August 15, 2026): the inspected middleware branch permitted only `kyqra.*`, while this implementation used `crawler.*`. This is not a verified statement about the current Middleware allowlist. Reconcile the namespace in the canonical repository and Middleware before any separately authorized activation; do not route around Middleware.
