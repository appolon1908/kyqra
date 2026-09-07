export const config = {
  db: process.env.STATE_DB || '/app/storage/kyqra.db',
  redis: process.env.REDIS_URL || 'redis://redis:6379',
  middlewareUrl: new URL(process.env.MIDDLEWARE_EVENTS_PATH || '/api/v1/events/kyqra', process.env.MIDDLEWARE_BASE_URL || 'https://10.40.0.1:443').toString(),
  apiKey: process.env.KYQRA_MIDDLEWARE_API_KEY || '',
  hmacSecret: process.env.KYQRA_MIDDLEWARE_HMAC_SECRET || '',
  retries: (process.env.MIDDLEWARE_RETRY_SCHEDULE_SECONDS || '60,300,900,3600').split(',').map(Number),
  circuitThreshold: Number(process.env.MIDDLEWARE_CIRCUIT_FAILURE_THRESHOLD || 5),
  circuitResetSeconds: Number(process.env.MIDDLEWARE_CIRCUIT_RESET_SECONDS || 60),
  sourceNode: process.env.HOSTNAME || 'unknown',
};
