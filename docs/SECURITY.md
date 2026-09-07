# Security

- Bind the public API only behind the existing trusted-TLS reverse proxy. Keep automatic certificate renewal; SSH remains key-only.
- Permit Kyqra `10.40.0.2` to the confirmed middleware TLS ingress on `10.40.0.1` only. Redis, SQLite storage, queues, browser debugging, and Docker socket stay private.
- Use one tenant-scoped API key per tenant and distinct `KYQRA_MIDDLEWARE_API_KEY` / `KYQRA_MIDDLEWARE_HMAC_SECRET`. Rotate through the host secret store and restart only Kyqra API/outbox containers.
- Never log credentials, signatures, authorization headers, page login material, or secret-bearing payloads. Structured logs include correlation and operational identifiers.
- No Kyqra code or container has Odoo or n8n database credentials. Direct PostgreSQL writes are prohibited.
- Crawls must respect access controls, site terms, authentication boundaries, rate limits, paywalls, CAPTCHAs, and anti-abuse controls.
