#!/usr/bin/env node
/*
 * Army control script. Zero dependencies, cross-platform (Node 18+).
 *
 *   army.js start  [--turbo] [--data DIR] [--project DIR]   begin a mission in the current project
 *   army.js end    [--data DIR]                               close the active mission
 *   army.js mode   [lean|full] [--data DIR]                   show or set the model profile
 *   army.js gates  [on|off]    [--data DIR]                   show or set the safety gates
 *   army.js status [--data DIR]                               show config, mission state, memory size
 *   army.js gate                                              PreToolUse hook (reads hook JSON on stdin)
 *
 * Per-user config lives in the plugin data dir (CLAUDE_PLUGIN_DATA), so every user has their own.
 * Per-project memory lives in <project>/.army/, which is excluded from git via .git/info/exclude
 * (local only, nothing is added to .gitignore or committed).
 */
'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');
const { execFileSync } = require('child_process');

const DEFAULT_CONFIG = { mode: 'lean', gates: true };
const MODES = ['lean', 'full'];
const MISSION_MAX_AGE_MS = 12 * 60 * 60 * 1000; // a forgotten "active" flag stops gating after 12h
const LESSONS_MAX_CHARS = 12000;

// ---------- args ----------
function parseArgs(argv) {
  const out = { _: [], flags: {} };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--turbo') out.flags.turbo = true;
    else if (a === '--data' || a === '--project') out.flags[a.slice(2)] = argv[++i];
    else out._.push(a);
  }
  return out;
}

// ---------- config (per user) ----------
function dataDir(flags) {
  const fromFlag = flags.data && !flags.data.includes('${') ? flags.data : '';
  const dir = fromFlag || process.env.CLAUDE_PLUGIN_DATA || path.join(os.homedir(), '.claude', 'army-data');
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}

function loadConfig(flags) {
  const file = path.join(dataDir(flags), 'config.json');
  try {
    return { ...DEFAULT_CONFIG, ...JSON.parse(fs.readFileSync(file, 'utf8')) };
  } catch {
    return { ...DEFAULT_CONFIG };
  }
}

function saveConfig(flags, cfg) {
  const file = path.join(dataDir(flags), 'config.json');
  fs.writeFileSync(file, JSON.stringify(cfg, null, 2) + '\n');
}

// ---------- git helpers ----------
function git(args, cwd) {
  try {
    return execFileSync('git', args, { cwd, stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim();
  } catch {
    return '';
  }
}

function projectRoot(flags) {
  if (flags.project) return path.resolve(flags.project);
  return git(['rev-parse', '--show-toplevel']) || process.cwd();
}

function ensureGitExcluded(root) {
  const rel = git(['rev-parse', '--git-path', 'info/exclude'], root);
  if (!rel) return false; // not a git repo: nothing can be committed anyway
  const file = path.isAbsolute(rel) ? rel : path.join(root, rel);
  let content = '';
  try { content = fs.readFileSync(file, 'utf8'); } catch { /* new file */ }
  if (!/^\/?\.army\/?\s*$/m.test(content)) {
    fs.mkdirSync(path.dirname(file), { recursive: true });
    const sep = content && !content.endsWith('\n') ? '\n' : '';
    fs.appendFileSync(file, `${sep}# army plugin local memory\n.army/\n`);
  }
  return true;
}

// ---------- project state ----------
function findArmyDir(start) {
  let dir = path.resolve(start || process.cwd());
  for (;;) {
    const candidate = path.join(dir, '.army');
    if (fs.existsSync(path.join(candidate, 'state.json'))) return candidate;
    const parent = path.dirname(dir);
    if (parent === dir) return null;
    dir = parent;
  }
}

function readJson(file, fallback) {
  try { return JSON.parse(fs.readFileSync(file, 'utf8')); } catch { return fallback; }
}

function missionIsActive(armyDir) {
  if (!armyDir) return false;
  const st = readJson(path.join(armyDir, 'state.json'), null);
  if (!st || !st.active) return false;
  const age = Date.now() - Date.parse(st.startedAt || 0);
  return Number.isFinite(age) && age < MISSION_MAX_AGE_MS;
}

function reconStatus(root, armyDir) {
  const file = path.join(armyDir, 'recon.md');
  if (!fs.existsSync(file)) return 'missing';
  const text = fs.readFileSync(file, 'utf8');
  const m = text.match(/^commit:\s*(\S+)/m);
  const head = git(['rev-parse', 'HEAD'], root);
  if (head && m) return m[1] === head ? 'fresh' : 'stale';
  const ageH = (Date.now() - fs.statSync(file).mtimeMs) / 3.6e6;
  return ageH < 24 ? 'fresh' : 'stale';
}

function slugTime() {
  const d = new Date();
  const p = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}-${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}`;
}

// ---------- commands ----------
function cmdStart(flags) {
  const cfg = loadConfig(flags);
  const root = projectRoot(flags);
  const armyDir = path.join(root, '.army');
  const missionId = slugTime();
  fs.mkdirSync(path.join(armyDir, 'missions', missionId), { recursive: true });
  const gitExcluded = ensureGitExcluded(root);
  const state = { active: true, startedAt: new Date().toISOString(), missionId, turbo: !!flags.turbo, mode: cfg.mode };
  fs.writeFileSync(path.join(armyDir, 'state.json'), JSON.stringify(state, null, 2) + '\n');

  let lessons = '';
  try { lessons = fs.readFileSync(path.join(armyDir, 'lessons.md'), 'utf8'); } catch { /* none yet */ }
  if (lessons.length > LESSONS_MAX_CHARS) lessons = lessons.slice(-LESSONS_MAX_CHARS);

  print({
    mode: cfg.mode,
    gates: cfg.gates ? 'on' : 'off',
    turbo: !!flags.turbo,
    projectRoot: root,
    armyDir,
    missionId,
    missionDir: path.join(armyDir, 'missions', missionId),
    gitExcluded,
    recon: reconStatus(root, armyDir),
    lessons: lessons || '(no lessons yet)',
  });
}

function cmdEnd() {
  const armyDir = findArmyDir(process.cwd());
  if (!armyDir) return print({ ok: false, error: 'no army state found in this project' });
  const file = path.join(armyDir, 'state.json');
  const st = readJson(file, {});
  st.active = false;
  st.endedAt = new Date().toISOString();
  fs.writeFileSync(file, JSON.stringify(st, null, 2) + '\n');
  print({ ok: true, missionId: st.missionId, endedAt: st.endedAt });
}

function cmdMode(flags, value) {
  const cfg = loadConfig(flags);
  if (value) {
    if (!MODES.includes(value)) return print({ ok: false, error: `mode must be one of: ${MODES.join(', ')}` });
    cfg.mode = value;
    saveConfig(flags, cfg);
  }
  print({ ok: true, mode: cfg.mode });
}

function cmdGates(flags, value) {
  const cfg = loadConfig(flags);
  if (value) {
    if (!['on', 'off'].includes(value)) return print({ ok: false, error: 'gates must be on or off' });
    cfg.gates = value === 'on';
    saveConfig(flags, cfg);
  }
  print({ ok: true, gates: cfg.gates ? 'on' : 'off' });
}

function cmdStatus(flags) {
  const cfg = loadConfig(flags);
  const armyDir = findArmyDir(process.cwd()) || path.join(projectRoot(flags), '.army');
  const st = readJson(path.join(armyDir, 'state.json'), null);
  let lessonLines = 0;
  try { lessonLines = fs.readFileSync(path.join(armyDir, 'lessons.md'), 'utf8').split('\n').filter(Boolean).length; } catch { /* none */ }
  let missions = 0;
  try { missions = fs.readdirSync(path.join(armyDir, 'missions')).length; } catch { /* none */ }
  print({
    mode: cfg.mode,
    gates: cfg.gates ? 'on' : 'off',
    configDir: dataDir(flags),
    armyDir: fs.existsSync(armyDir) ? armyDir : '(not created yet)',
    activeMission: missionIsActive(armyDir) ? st.missionId : null,
    missionsLogged: missions,
    lessonLines,
  });
}

// ---------- safety gate ----------
const GATE_RULES = [
  [/\bgit\s+push\b/, 'git push'],
  [/\bgit\s+reset\s+--hard\b/, 'git reset --hard (discards work)'],
  [/\bgit\s+clean\b[^\n]*\s-[a-zA-Z]*f/, 'git clean -f (deletes untracked files)'],
  [/\bgit\s+checkout\s+(\S+\s+)?--\s/, 'discarding local changes (git checkout --)'],
  [/\bgit\s+restore\b(?![^\n]*--staged)/, 'discarding local changes (git restore)'],
  [/\bgit\s+branch\s+(-D\b|--delete\s+--force|-d\s+-f)/, 'force-deleting a branch'],
  [/\bgit\s+(rebase|filter-branch|filter-repo)\b/, 'rewriting git history'],
  [/\bgit\s+stash\s+(drop|clear)\b/, 'dropping stashed work'],
  [/(^|[\s;&|(`])(rm|rmdir|unlink|shred)\s/, 'deleting files'],
  [/\bfind\b[^\n]*\s-delete\b/, 'deleting files (find -delete)'],
  [/\bRemove-Item\b|(^|[\s;&|])(del|erase|rd)\s+\/[sqf]/i, 'deleting files'],
  [/\b(dd\s+if=|mkfs\b)/, 'raw disk write'],
  [/\b(npm|pnpm|yarn|bun)\s+publish\b/, 'publishing a package'],
  [/\b(twine\s+upload|poetry\s+publish|uv\s+publish|cargo\s+publish|gem\s+push)\b/, 'publishing a package'],
  [/\bdocker\s+(push|system\s+prune|volume\s+(rm|prune)|image\s+prune)\b/, 'docker push / prune'],
  [/\bvercel\b(?!\s+(dev|build|env|link|login|logout|whoami|pull|ls|list|inspect|logs|--version|-v|help)\b)/, 'Vercel deployment'],
  [/\bnetlify\s+deploy\b/, 'Netlify deployment'],
  [/\bfirebase\s+deploy\b/, 'Firebase deployment'],
  [/\b(fly|flyctl)\s+(deploy|destroy|apps\s+destroy)\b/, 'Fly.io deployment'],
  [/\brailway\s+(up|deploy|down)\b/, 'Railway deployment'],
  [/\bwrangler\s+(deploy|publish|delete)\b/, 'Cloudflare deployment'],
  [/\b(serverless|sls)\s+(deploy|remove)\b/, 'Serverless deployment'],
  [/\bgcloud\b[^\n]*\s(deploy|delete)\b/, 'Google Cloud deploy/delete'],
  [/\baws\b[^\n]*\s(deploy|delete-\S+|terminate-\S+|rb|rm|mv|sync)\b/, 'AWS change'],
  [/\baz\b[^\n]*\s(deploy|delete|create)\b/, 'Azure change'],
  [/\bkubectl\s+(apply|delete|replace|rollout|scale|drain|patch|create|edit)\b/, 'Kubernetes change'],
  [/\bhelm\s+(install|upgrade|uninstall|delete|rollback)\b/, 'Helm release change'],
  [/\bterraform\s+(apply|destroy|import|state\s+rm)\b/, 'Terraform infrastructure change'],
  [/\bpulumi\s+(up|destroy)\b/, 'Pulumi infrastructure change'],
  [/\bsupabase\s+(db\s+(push|reset)|functions\s+deploy|projects\s+delete)\b/, 'Supabase change'],
  [/\bprisma\s+(migrate\s+(deploy|reset)|db\s+push)\b/, 'database schema change'],
  [/\b(drop\s+(table|database|schema|collection|index)|truncate\s+table)\b/i, 'dropping data'],
  [/\bdropDatabase\s*\(|\.drop\s*\(\s*\)/, 'dropping data'],
  [/\bgh\s+(release\s+(create|delete)|pr\s+merge|repo\s+(delete|archive|edit|rename)|secret\s+(set|delete)|workflow\s+run)\b/, 'GitHub change'],
  [/\bheroku\s+(apps:destroy|pg:reset|releases:rollback)\b/, 'Heroku change'],
];

const INSTALLERS = [
  // [manager tokens..., verbs that add packages]
  { cmd: ['npm'], verbs: ['install', 'i', 'in', 'add', 'isntall'], kind: 'node' },
  { cmd: ['pnpm'], verbs: ['add', 'install', 'i'], kind: 'node' },
  { cmd: ['yarn'], verbs: ['add'], kind: 'node' },
  { cmd: ['bun'], verbs: ['add', 'install', 'i'], kind: 'node' },
  { cmd: ['pip'], verbs: ['install'], kind: 'pip' },
  { cmd: ['pip3'], verbs: ['install'], kind: 'pip' },
  { cmd: ['uv', 'pip'], verbs: ['install'], kind: 'pip' },
  { cmd: ['uv'], verbs: ['add'], kind: 'any' },
  { cmd: ['poetry'], verbs: ['add'], kind: 'any' },
  { cmd: ['pipenv'], verbs: ['install'], kind: 'any' },
  { cmd: ['pipx'], verbs: ['install'], kind: 'any' },
  { cmd: ['conda'], verbs: ['install'], kind: 'any' },
  { cmd: ['brew'], verbs: ['install'], kind: 'any' },
  { cmd: ['apt'], verbs: ['install'], kind: 'any' },
  { cmd: ['apt-get'], verbs: ['install'], kind: 'any' },
  { cmd: ['cargo'], verbs: ['add', 'install'], kind: 'any' },
  { cmd: ['go'], verbs: ['get', 'install'], kind: 'any' },
  { cmd: ['gem'], verbs: ['install'], kind: 'any' },
  { cmd: ['composer'], verbs: ['require'], kind: 'any' },
  { cmd: ['dotnet', 'add'], verbs: ['package'], kind: 'any' },
];

const PIP_VALUE_FLAGS = new Set(['-r', '--requirement', '-c', '--constraint', '-e', '--editable', '-i', '--index-url',
  '--extra-index-url', '-t', '--target', '-f', '--find-links', '--prefix', '--root', '--python']);

function splitSegments(command) {
  return command.split(/&&|\|\||[;|\n]/).map((s) => s.trim()).filter(Boolean);
}

function normalizeTokens(segment) {
  let tokens = segment.split(/\s+/).filter(Boolean);
  // drop leading env assignments, sudo, and "python -m"
  while (tokens.length && (/^[A-Za-z_][A-Za-z0-9_]*=/.test(tokens[0]) || tokens[0] === 'sudo' || tokens[0] === 'env')) tokens.shift();
  if (/^python(3(\.\d+)?)?$/.test(tokens[0] || '') && tokens[1] === '-m') tokens = tokens.slice(2);
  return tokens.map((t) => t.replace(/^['"]|['"]$/g, ''));
}

function addsDependency(segment) {
  const tokens = normalizeTokens(segment);
  for (const inst of INSTALLERS) {
    const n = inst.cmd.length;
    if (tokens.length <= n) continue;
    if (!inst.cmd.every((c, i) => tokens[i] === c)) continue;
    const verb = tokens[n];
    if (!inst.verbs.includes(verb)) continue;
    const rest = tokens.slice(n + 1);
    for (let i = 0; i < rest.length; i++) {
      const t = rest[i];
      if (t.startsWith('-')) {
        if (inst.kind === 'pip' && PIP_VALUE_FLAGS.has(t)) i++; // skip the flag's value
        continue;
      }
      if (inst.kind === 'pip' && (t === '.' || t.startsWith('./'))) continue;
      return `adding a new dependency (${tokens.slice(0, n + 1).join(' ')} ${t})`;
    }
  }
  return null;
}

function checkCommand(command) {
  if (!command || typeof command !== 'string') return null;
  for (const [re, label] of GATE_RULES) if (re.test(command)) return label;
  for (const seg of splitSegments(command)) {
    const dep = addsDependency(seg);
    if (dep) return dep;
  }
  return null;
}

function cmdGate() {
  let input = {};
  try { input = JSON.parse(fs.readFileSync(0, 'utf8') || '{}'); } catch { process.exit(0); }
  if (input.tool_name !== 'Bash') process.exit(0);
  const cfg = loadConfig({});
  if (!cfg.gates) process.exit(0);
  if (!missionIsActive(findArmyDir(input.cwd || process.cwd()))) process.exit(0);
  const reason = checkCommand(input.tool_input && input.tool_input.command);
  if (!reason) process.exit(0);
  process.stdout.write(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: 'PreToolUse',
      permissionDecision: 'ask',
      permissionDecisionReason: `Army safety gate: ${reason}. This is irreversible or adds a dependency, so it needs your approval. (Turn gates off with /army:gates off.)`,
    },
  }));
  process.exit(0);
}

// ---------- main ----------
function print(obj) {
  process.stdout.write(JSON.stringify(obj, null, 2) + '\n');
}

function main() {
  const { _: pos, flags } = parseArgs(process.argv.slice(2));
  const [cmd, value] = pos;
  switch (cmd) {
    case 'start': return cmdStart(flags);
    case 'end': return cmdEnd(flags);
    case 'mode': return cmdMode(flags, value);
    case 'gates': return cmdGates(flags, value);
    case 'status': return cmdStatus(flags);
    case 'gate': return cmdGate();
    default:
      process.stdout.write('usage: army.js <start|end|mode|gates|status|gate> [value] [--turbo] [--data DIR]\n');
      process.exit(cmd ? 1 : 0);
  }
}

if (require.main === module) main();
module.exports = { checkCommand, addsDependency };
