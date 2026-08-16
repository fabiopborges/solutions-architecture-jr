import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, '..', '..', '..');
const FIXED_POINT = '45f0611dfc0dc824e9a13a12efcac207a8a2bdce';
const ARCHIFY_ZIP_BLOB = '4249d32a5a07deb63152a06ac8c2cf4784d25136';
const ARCHIFY_PACKAGE_BLOB = '238d6237ff0c942d459e7ec257f19386522306a0';

function git(args) {
  const result = spawnSync('git', args, { cwd: repoRoot, encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
  return result.stdout.trim();
}

test('core Skill, ZIP, packer, package-smoke, and existing workflows are unchanged vs the fixed point', () => {
  assert.equal(git(['rev-parse', `${FIXED_POINT}:archify.zip`]), ARCHIFY_ZIP_BLOB);
  assert.equal(git(['rev-parse', 'HEAD:archify.zip']), ARCHIFY_ZIP_BLOB);
  assert.equal(git(['hash-object', 'archify.zip']), ARCHIFY_ZIP_BLOB);
  assert.equal(git(['rev-parse', `${FIXED_POINT}:archify/package.json`]), ARCHIFY_PACKAGE_BLOB);
  assert.equal(git(['hash-object', 'archify/package.json']), ARCHIFY_PACKAGE_BLOB);
  assert.equal(git(['diff', `${FIXED_POINT}...`, '--', 'archify', 'archify.zip']), '');
  assert.equal(git(['diff', `${FIXED_POINT}...`, '--', 'scripts/build-zip.sh', 'scripts/package-smoke.mjs']), '');
  assert.equal(git(['diff', `${FIXED_POINT}...`, '--', '.github/workflows/ci.yml', '.github/workflows/release.yml']), '');
});

test('the repository still has exactly one checked-in Archify SKILL.md and no generated DSH payload', () => {
  const skillFiles = git(['ls-files', '*SKILL.md']).split('\n').filter(Boolean);
  assert.deepEqual(skillFiles, ['archify/SKILL.md']);
  assert.equal(fs.existsSync(path.join(repoRoot, 'integrations/deepseek-harness/skills')), false);
  const trackedSkills = git(['ls-files', 'integrations/deepseek-harness/skills']);
  assert.equal(trackedSkills, '');
});

test('Archify core does not import, detect, or branch on DeepSeek Harness', () => {
  const grep = spawnSync('git', [
    'grep',
    '-n',
    '-E',
    'deepseek-harness|@deepseek-ai/dsh|DSH_HOME|DSH_AGENTS_HOME|archify-dsh',
    '--',
    'archify',
    'scripts/build-zip.sh',
    'scripts/package-smoke.mjs',
  ], { cwd: repoRoot, encoding: 'utf8' });
  assert.equal(grep.status, 1, grep.stderr || grep.stdout);
  assert.equal(grep.stdout.trim(), '');
});

test('full-depth Skills CLI discovery still finds only one skill named archify', () => {
  const result = spawnSync('npx', ['-y', 'skills', 'add', repoRoot, '--list', '--full-depth'], {
    cwd: repoRoot,
    encoding: 'utf8',
  });
  assert.equal(result.status, 0, result.stderr || result.stdout);
  const names = [...result.stdout.matchAll(/^\s*[-*]\s+(\S+)/gm)].map((match) => match[1])
    .filter((name) => name === 'archify' || /archify/i.test(name));
  const unique = new Set(
    [...result.stdout.matchAll(/\barchify\b/gi)].map((match) => match[0].toLowerCase()),
  );
  assert.ok(result.stdout.includes('archify'), result.stdout);
  assert.equal(unique.size, 1, result.stdout);
  assert.ok(names.length <= 1 || new Set(names).size === 1, result.stdout);
});
