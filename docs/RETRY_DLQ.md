# Retry, outbox, and DLQ

State changes and outbox inserts share the local SQLite WAL transaction where initiated. The database resides on the persistent `crawler_storage` volume. The delivery worker claims due `pending`/`retrying` records and marks `delivered` only after middleware acceptance.

`MIDDLEWARE_RETRY_SCHEDULE_SECONDS` defaults to `60,300,900,3600`. Transport, 408/425/429, and 5xx failures retry; permanent failures or exhaustion become `dead-lettered`. Retries are bounded.

Five consecutive failures open the circuit by default. It stops delivery until the reset interval, then admits a half-open probe. Success closes it automatically. Crawling continues while the outbox is durable. Operators inspect and replay DLQ events at `/admin/integration`; replay writes an audit row and never changes event identity.
