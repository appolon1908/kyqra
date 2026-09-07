import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';

const root = new URL('../', import.meta.url);
const manifest = JSON.parse(readFileSync(new URL('package.json', root), 'utf8'));

function runSyntaxCheck(firstSource) {
  const directory = mkdtempSync(join(tmpdir(), 'kyqra-syntax-'));
  try {
    mkdirSync(join(directory, 'src'));
    mkdirSync(join(directory, 'test'));
    writeFileSync(join(directory, 'src', 'a.js'), firstSource);
    writeFileSync(join(directory, 'src', 'z.js'), 'const valid = true;\n');
    writeFileSync(join(directory, 'test', 'last.js'), 'const valid = true;\n');
    const result = spawnSync('sh', ['-c', manifest.scripts.check], {
      cwd: directory,
      encoding: 'utf8',
      timeout: 10000,
    });
    assert.ifError(result.error);
    return result;
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
}

test('syntax check does not hide an early failure behind later valid files', () => {
  const result = runSyntaxCheck('const invalid = ;\n');
  assert.notEqual(result.status, 0, 'the first syntax error must fail the command');
  assert.match(result.stderr, /SyntaxError/);
});

test('syntax check accepts valid source and test files', () => {
  const result = runSyntaxCheck('const valid = true;\n');
  assert.equal(result.status, 0, result.stderr);
});

test('README keeps canonical crawler authority after merging legacy source', () => {
  const readme = readFileSync(new URL('README.md', root), 'utf8');
  assert.match(readme, /deprecated for new crawler development/);
  assert.match(readme, /appolon1908-hue\/kyqra-crawler/);
  assert.match(readme, /second production crawler API/);
  assert.match(readme, /does not authorize runtime deployment/);
});

test('deployment report distinguishes historical observations from activation authority', () => {
  const report = readFileSync(new URL('DEPLOYMENT_REPORT.md', root), 'utf8');
  assert.match(report, /Historical migration reference only/);
  assert.match(report, /appolon1908-hue\/kyqra-crawler/);
  assert.match(report, /not current\s+production certification/);
  assert.match(report, /No runtime deployment/);
});
