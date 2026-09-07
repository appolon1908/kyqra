import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

test('Docker source context excludes host dependencies and runtime secrets', () => {
  const patterns = new Set(readFileSync(new URL('../.dockerignore', import.meta.url), 'utf8').trim().split('\n'));
  for (const pattern of ['.git', '**/node_modules', '**/.env', '**/.env.*', '**/*.key', '**/storage', '**/*.db', 'evidence']) {
    assert.ok(patterns.has(pattern), `missing build-context exclusion: ${pattern}`);
  }
  assert.ok(patterns.has('!**/.env.example'), 'documented placeholders remain available');
});
