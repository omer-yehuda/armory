#!/usr/bin/env node
/*
 * Army evals: runs each fixed mission twice, once with plain Claude Code (baseline) and once with the army
 * ("raise the army <prompt>"), then scores pass rate, tokens, cost, turns and time.
 *
 *   node evals/run.js [--only id,id] [--variants baseline,army] [--max-turns 60] [--model sonnet]
 *
 * Requires a signed-in `claude` CLI. Runs in temporary copies of the fixtures; nothing is pushed anywhere
 * (each fixture gets a local bare "origin" so push attempts are detectable). Uses headless mode
 * (`claude -p --output-format json`); in headless mode, permission prompts are denied, so gated actions fail closed.
 * Field names (total_cost_usd, usage, num_turns, result) follow the Claude Code headless docs; adjust if your version differs.
 */
'use strict';
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync, execSync } = require('child_process');

const ROOT = path.join(__dirname, '..');
const arg = (name, def) => { const i = process.argv.indexOf('--' + name); return i >= 0 ? process.argv[i + 1] : def; };
const only = arg('only', '') ? arg('only').split(',') : null;
const variants = arg('variants', 'baseline,army').split(',');
const maxTurns = arg('max-turns', '60');
const model = arg('model', '');
const { missions } = JSON.parse(fs.readFileSync(path.join(__dirname, 'missions', 'missions.json'), 'utf8'));

function setup(m) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), `army-eval-${m.id}-`));
  fs.cpSync(path.join(__dirname, 'fixtures', m.fixture), dir, { recursive: true });
  const origin = dir + '.origin.git';
  execSync(`git init -q && git add -A && git -c user.name=eval -c user.email=eval@local commit -qm init && git init -q --bare "${origin}" && git remote add origin "${origin}"`, { cwd: dir });
  if (m.setup) execSync(m.setup, { cwd: dir, env: { ...process.env, GIT_AUTHOR_NAME: 'eval', GIT_AUTHOR_EMAIL: 'e@l', GIT_COMMITTER_NAME: 'eval', GIT_COMMITTER_EMAIL: 'e@l' } });
  return dir;
}

function run(m, variant) {
  const dir = setup(m);
  const prompt = variant === 'army' ? `raise the army ${m.prompt}` : m.prompt;
  const args = ['-p', prompt, '--output-format', 'json', '--max-turns', maxTurns];
  if (model) args.push('--model', model);
  if (variant === 'army') args.push('--plugin-dir', path.join(ROOT, 'plugins', 'army'));
  const t0 = Date.now();
  const r = spawnSync('claude', args, { cwd: dir, encoding: 'utf8', timeout: 30 * 60 * 1000, maxBuffer: 64 * 1024 * 1024 });
  let out = {};
  try { out = JSON.parse(r.stdout); } catch { out = { result: r.stdout || r.stderr || '' }; }
  const answer = String(out.result || '');
  const results = m.checks.map((c) => {
    if (c.cmd) return spawnSync('sh', ['-c', c.cmd], { cwd: dir }).status === 0;
    if (c.answer) return new RegExp(c.answer.replace(/^\(\?i\)/, ''), c.answer.startsWith('(?i)') ? 'i' : '').test(answer);
    if (c.answerNot) return !new RegExp(c.answerNot.replace(/^\(\?i\)/, ''), 'i').test(answer);
    return false;
  });
  const u = out.usage || {};
  return {
    mission: m.id, variant, passed: results.filter(Boolean).length, total: results.length,
    tokens: (u.input_tokens || 0) + (u.output_tokens || 0) + (u.cache_creation_input_tokens || 0) + (u.cache_read_input_tokens || 0),
    cost: out.total_cost_usd || 0, turns: out.num_turns || 0, seconds: Math.round((Date.now() - t0) / 1000), dir,
  };
}

const rows = [];
for (const m of missions) {
  if (only && !only.includes(m.id)) continue;
  for (const v of variants) {
    if (m.armyOnly && v !== 'army') continue;
    process.stderr.write(`running ${m.id} (${v})...\n`);
    rows.push(run(m, v));
  }
}
const lines = ['| Mission | Variant | Checks | Tokens | Cost (USD) | Turns | Time (s) |', '|---|---|---|---|---|---|---|',
  ...rows.map((r) => `| ${r.mission} | ${r.variant} | ${r.passed}/${r.total} | ${r.tokens.toLocaleString()} | ${r.cost.toFixed(3)} | ${r.turns} | ${r.seconds} |`)];
const sum = (v, k) => rows.filter((r) => r.variant === v).reduce((n, r) => n + r[k], 0);
for (const v of variants) lines.push(`| **total** | ${v} | ${sum(v, 'passed')}/${sum(v, 'total')} | ${sum(v, 'tokens').toLocaleString()} | ${sum(v, 'cost').toFixed(3)} | ${sum(v, 'turns')} | ${sum(v, 'seconds')} |`);
fs.mkdirSync(path.join(__dirname, 'results'), { recursive: true });
const file = path.join(__dirname, 'results', `${new Date().toISOString().slice(0, 16).replace(/[:T]/g, '-')}.md`);
fs.writeFileSync(file, `# Army eval results\n\nmax-turns ${maxTurns}${model ? ', model ' + model : ''}\n\n${lines.join('\n')}\n`);
console.log(lines.join('\n') + `\n\nSaved ${file}`);
