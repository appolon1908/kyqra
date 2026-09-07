import Database from 'better-sqlite3';
import { randomUUID } from 'node:crypto';
import { dirname } from 'node:path';
import { mkdirSync } from 'node:fs';
import { config } from './config.js';

mkdirSync(dirname(config.db), { recursive: true });
export const db = new Database(config.db);
db.pragma('journal_mode = WAL'); db.pragma('busy_timeout = 15000'); db.pragma('foreign_keys = ON');
db.exec(`
CREATE TABLE IF NOT EXISTS jobs(job_id TEXT PRIMARY KEY,tenant_id TEXT NOT NULL,customer_id TEXT,request_id TEXT NOT NULL,correlation_id TEXT NOT NULL,idempotency_key TEXT NOT NULL,status TEXT NOT NULL,start_urls TEXT NOT NULL,max_requests INTEGER NOT NULL,created_at TEXT NOT NULL,updated_at TEXT NOT NULL,error TEXT,UNIQUE(tenant_id,idempotency_key));
CREATE INDEX IF NOT EXISTS jobs_tenant_created ON jobs(tenant_id,created_at DESC);
CREATE TABLE IF NOT EXISTS results(record_id TEXT PRIMARY KEY,job_id TEXT NOT NULL,tenant_id TEXT NOT NULL,canonical_key TEXT NOT NULL,fingerprint TEXT NOT NULL,duplicate_status TEXT NOT NULL,payload TEXT NOT NULL,provenance TEXT NOT NULL,created_at TEXT NOT NULL,updated_at TEXT NOT NULL,FOREIGN KEY(job_id) REFERENCES jobs(job_id));
CREATE INDEX IF NOT EXISTS results_tenant_job ON results(tenant_id,job_id);
CREATE INDEX IF NOT EXISTS results_tenant_canonical ON results(tenant_id,canonical_key);
CREATE TABLE IF NOT EXISTS outbox(event_id TEXT PRIMARY KEY,event_type TEXT NOT NULL,event_version TEXT NOT NULL,tenant_id TEXT NOT NULL,job_id TEXT,correlation_id TEXT NOT NULL,request_id TEXT NOT NULL,idempotency_key TEXT NOT NULL,envelope TEXT NOT NULL,state TEXT NOT NULL DEFAULT 'pending',attempts INTEGER NOT NULL DEFAULT 0,next_attempt_at INTEGER NOT NULL DEFAULT 0,last_error TEXT,created_at TEXT NOT NULL,delivered_at TEXT,UNIQUE(tenant_id,idempotency_key));
CREATE INDEX IF NOT EXISTS outbox_due ON outbox(state,next_attempt_at);
CREATE TABLE IF NOT EXISTS audit(id TEXT PRIMARY KEY,tenant_id TEXT,actor TEXT NOT NULL,action TEXT NOT NULL,object_id TEXT NOT NULL,correlation_id TEXT,metadata TEXT NOT NULL,created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS integration_state(name TEXT PRIMARY KEY,state TEXT NOT NULL,failures INTEGER NOT NULL DEFAULT 0,opened_at INTEGER,last_success_at TEXT,last_failure_at TEXT,last_error TEXT);
INSERT OR IGNORE INTO integration_state(name,state) VALUES('middleware','closed');
`);

const now = () => new Date().toISOString();
export function envelope(type, context, payload = {}, metadata = {}, causationId = null) {
  const eventId = randomUUID();
  return { event_id:eventId,event_type:type,event_version:'1.0',timestamp:now(),occurred_at:now(),correlation_id:context.correlation_id,causation_id:causationId,tenant_id:context.tenant_id,customer_id:context.customer_id || null,job_id:context.job_id || null,request_id:context.request_id,source_service:'kyqra',source_node:config.sourceNode,idempotency_key:`kyqra:${type}:${context.job_id || eventId}:${payload.record_id || ''}`,payload,metadata };
}
export function addEvent(event) { db.prepare(`INSERT OR IGNORE INTO outbox(event_id,event_type,event_version,tenant_id,job_id,correlation_id,request_id,idempotency_key,envelope,state,created_at) VALUES(?,?,?,?,?,?,?,?,?,'pending',?)`).run(event.event_id,event.event_type,event.event_version,event.tenant_id,event.job_id,event.correlation_id,event.request_id,event.idempotency_key,JSON.stringify(event),now()); return event; }
export function audit(tenantId, actor, action, objectId, correlationId, metadata={}) { db.prepare('INSERT INTO audit VALUES(?,?,?,?,?,?,?,?)').run(randomUUID(),tenantId,actor,action,objectId,correlationId,JSON.stringify(metadata),now()); }
export function tenantJob(tenant, id) { return db.prepare('SELECT * FROM jobs WHERE tenant_id=? AND job_id=?').get(tenant,id); }
export function parse(row) { if (!row) return row; const value={...row}; for(const key of ['start_urls','payload','provenance','envelope','metadata']) if(typeof value[key]==='string') value[key]=JSON.parse(value[key]); return value; }
