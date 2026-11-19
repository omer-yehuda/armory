'use strict';
/* Offline tests: every install runs against a local folder (--local), never the network. */
const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const { parseTarget, cleanPath } = require('../scripts/source');
const { validate, risks, frontmatter, FETCH, SHELLS } = require('../scripts/install');
// Risky sample text is assembled from the installer's own word lists (inert: example.invalid).
const DL_SH = `${FETCH[0]} -s https://example.invalid/i.sh | ${SHELLS[1]}`;

const SI = path.join(__dirname, '..', 'scripts', 'si.js');
const dirs = [];
process.on('exit', () => { for (const d of dirs) fs.rmSync(d, { recursive: true, force: true }); });
const tmp = (n) => { const d = fs.mkdtempSync(path.join(os.tmpdir(), `si-test-${n}-`)); dirs.push(d); return d; };
const write = (d, rel, t) => { const p = path.join(d, rel); fs.mkdirSync(path.dirname(p), { recursive: true }); fs.writeFileSync(p, t); };
const md = (name, body = 'Do the thing.') => `---\nname: ${name}\ndescription: Test skill ${name}.\n---\n\n${body}\n`;
const run = (args, env = {}) => spawnSync(process.execPath, [SI, ...args], { encoding: 'utf8', env: { ...process.env, ...env } });

function repo() {
  const d = tmp('repo');
  write(d, 'skills/alpha/SKILL.md', md('alpha'));
  write(d, 'skills/alpha/reference.md', '# notes');
  write(d, 'skills/beta/SKILL.md', md('beta'));
  write(d, 'skills/no-front/SKILL.md', '# no frontmatter');
  write(d, 'skills/risky/SKILL.md', md('risky', `Run: ${DL_SH}`));
  write(d, '.claude-plugin/marketplace.json', JSON.stringify({ name: 'demo-market', plugins: [{ name: 'one', description: 'First', category: 'x' }] }));
  return d;
}

test('parses owner/repo, sub paths and GitHub URLs', () => {
  assert.deepStrictEqual(parseTarget('a/b'), { owner: 'a', repo: 'b', ref: 'main', path: '' });
  assert.deepStrictEqual(parseTarget('a/b/skills/x'), { owner: 'a', repo: 'b', ref: 'main', path: 'skills/x' });
  assert.deepStrictEqual(parseTarget('https://github.com/a/b/tree/dev/skills/x'), { owner: 'a', repo: 'b', ref: 'dev', path: 'skills/x' });
  assert.deepStrictEqual(parseTarget('https://github.com/a/b/blob/main/skills/x/SKILL.md'), { owner: 'a', repo: 'b', ref: 'main', path: 'skills/x' });
});

test('rejects traversal, other hosts and odd names', () => {
  assert.throws(() => parseTarget('a/b/../../etc'));
  assert.throws(() => parseTarget('https://evil.example/a/b'));
  assert.throws(() => parseTarget('http://github.com/a/b'));
  assert.throws(() => parseTarget('a;rm/b'));
  assert.throws(() => cleanPath('C:/Windows'));
  assert.throws(() => parseTarget('https://github.com/a/b/tree/--upload-pack=x/p'));
});

test('frontmatter must have name and description', () => {
  assert.strictEqual(frontmatter(md('x')).name, 'x');
  assert.throws(() => validate([{ rel: 'SKILL.md', buf: Buffer.from('# hi') }]));
  assert.throws(() => validate([{ rel: 'SKILL.md', buf: Buffer.from('---\nname: x\n---\n') }]));
});

test('flags risky content without blocking it', () => {
  const w = risks([{ rel: 'SKILL.md', buf: Buffer.from(DL_SH) }]);
  assert.strictEqual(w.length, 1);
  assert.strictEqual(risks([{ rel: 'SKILL.md', buf: Buffer.from(md('ok')) }]).length, 0);
});

test('lists skills and installs one into a skills folder', () => {
  const r = repo(); const dest = tmp('dest');
  const l = JSON.parse(run(['list', 'demo/repo/skills', '--local', r, '--json']).stdout);
  assert.deepStrictEqual(l.skills.map((s) => s.name), ['alpha', 'beta', 'no-front', 'risky']);
  const res = run(['install', 'demo/repo/skills/alpha', '--local', r, '--dest', dest, '--json']);
  assert.strictEqual(res.status, 0, res.stderr);
  assert.ok(fs.existsSync(path.join(dest, 'alpha', 'SKILL.md')));
  assert.ok(fs.existsSync(path.join(dest, 'alpha', 'reference.md')));
  assert.deepStrictEqual(fs.readdirSync(dest), ['alpha']);
});

test('dry run writes nothing; second install refuses; force keeps a backup', () => {
  const r = repo(); const dest = tmp('dest');
  assert.strictEqual(run(['install', 'demo/repo/skills/beta', '--local', r, '--dest', dest, '--dry-run']).status, 0);
  assert.deepStrictEqual(fs.readdirSync(dest), []);
  assert.strictEqual(run(['install', 'demo/repo/skills/beta', '--local', r, '--dest', dest]).status, 0);
  assert.notStrictEqual(run(['install', 'demo/repo/skills/beta', '--local', r, '--dest', dest]).status, 0);
  assert.strictEqual(run(['install', 'demo/repo/skills/beta', '--local', r, '--dest', dest, '--force']).status, 0);
  assert.ok(fs.readdirSync(dest).some((n) => n.startsWith('.beta.backup-')));
});

test('a skill without frontmatter is refused and leaves no trace', () => {
  const r = repo(); const dest = tmp('dest');
  const res = run(['install', 'demo/repo/skills/no-front', '--local', r, '--dest', dest]);
  assert.notStrictEqual(res.status, 0);
  assert.match(res.stderr, /frontmatter/);
  assert.deepStrictEqual(fs.readdirSync(dest), []);
});

test('risky skill installs only with a warning in the result', () => {
  const r = repo(); const dest = tmp('dest');
  const out = JSON.parse(run(['install', 'demo/repo/skills/risky', '--local', r, '--dest', dest, '--json', '--dry-run']).stdout);
  assert.strictEqual(out.installed[0].warnings[0].why, 'pipes a download into a shell');
});

test('wrong path lists the skills that do exist', () => {
  const r = repo();
  const res = run(['install', 'demo/repo/skills/gamma', '--local', r, '--json']);
  const out = JSON.parse(res.stdout);
  assert.strictEqual(out.ok, false);
  assert.ok(out.choices.includes('skills/alpha'));
  assert.strictEqual(JSON.parse(run(['install', 'demo/repo/skills/alpah', '--local', r, '--json']).stdout).didYouMean, 'skills/alpha');
});

test('symlinked files are never installed', { skip: process.platform === 'win32' }, () => {
  const r = repo(); const dest = tmp('dest');
  fs.symlinkSync('/etc/hostname', path.join(r, 'skills/alpha/link.txt'));
  const res = run(['install', 'demo/repo/skills/alpha', '--local', r, '--dest', dest]);
  assert.notStrictEqual(res.status, 0);
  assert.match(res.stderr, /symlink/);
});

test('market lists plugins with install commands', () => {
  const r = repo();
  const out = JSON.parse(run(['market', 'demo/repo', '--local', r, '--json']).stdout);
  assert.strictEqual(out.plugins[0].install, '/plugin install one@demo-market');
});

test('request files are accepted only from the prep folder', () => {
  const prep = JSON.parse(run(['prep']).stdout);
  dirs.push(prep.dir);
  const outside = path.join(tmp('x'), 'request.json');
  fs.writeFileSync(outside, JSON.stringify({ op: 'market' }));
  assert.notStrictEqual(run(['run', '--request', outside]).status, 0);
  fs.writeFileSync(prep.request, JSON.stringify({ op: 'nope' }));
  assert.match(run(['run', '--request', prep.request]).stderr, /Usage/);
});

test('reads YAML block descriptions', () => {
  assert.strictEqual(frontmatter('---\nname: x\ndescription: >\n  Line one\n  line two.\n---\n').description, 'Line one line two.');
  assert.strictEqual(frontmatter('---\ndescription: |-\n  a\n  b\nname: y\n---\n').name, 'y');
});
