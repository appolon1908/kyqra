import pino from 'pino';
export const log = pino({ base: { service: process.env.SERVICE_NAME || 'kyqra' }, redact: ['req.headers.authorization', 'req.headers.x-api-key', '*.apiKey', '*.secret', '*.signature'] });
