'use strict';
/* Check a downloaded skill and copy it into a Claude skills folder. Adapted from OpenAI's Codex
   skill-installer (Apache-2.0); see NOTICE. */

const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { InstallError, SKILL_NAME_RE } = require('./source');

function destRoot(scope, cwd = process.cwd()) {
  if (scope === 'project') return path.join(cwd, '.claude', 'skills');
  if (scope && scope !== 'user') throw new InstallError('Scope must be "user" or "project".');
  const base = process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude');
  return path.join(base, 'skills');
}

function frontmatter(text) {
  const body = text.charCodeAt(0) === 0xfeff ? text.slice(1) : text;
  const m = /^---\r?\n([\s\S]*?)\r?\n---/.exec(body);
  if (!m) return null;
  const out = {};
  const lines = m[1].split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    const kv = /^([A-Za-z0-9_-]+):\s*(.*)$/.exec(lines[i]);
    if (!kv) continue;
    let v = kv[2].trim();
    if (/^[>|][+-]?$/.test(v) || v === '') { // YAML block scalar or value on the next indented lines
      const block = [];
      while (i + 1 < lines.length && (/^\s+\S/.test(lines[i + 1]) || lines[i + 1].trim() === '')) block.push(lines[++i].trim());
      v = block.filter(Boolean).join(v.startsWith('|') ? '\n' : ' ');
    }
    out[kv[1]] = v.replace(/^["']|["']$/g, '').trim();
  }
  return out;
}

// Problems that block the install.
function validate(files) {
  const skill = files.find((f) => f.rel === 'SKILL.md');
  if (!skill) throw new InstallError('SKILL.md not found in the selected folder.');
  const fm = frontmatter(skill.buf.toString('utf8'));
  if (!fm) throw new InstallError('SKILL.md has no frontmatter (--- name / description ---).');
  if (!fm.name) throw new InstallError('SKILL.md frontmatter has no name.');
  if (!fm.description) throw new InstallError('SKILL.md frontmatter has no description.');
  for (const f of files) {
    const norm = path.posix.normalize(f.rel);
    if (norm.startsWith('../') || path.posix.isAbsolute(norm) || /[\u0000-\u001f]/.test(norm)) {
      throw new InstallError(`Unsafe file path in skill: ${f.rel}`);
    }
  }
  return fm;
}

// Things worth a second look. Not a verdict: suggest /customs:inspect for a real scan.
// Word lists are kept apart from the matchers so this file never contains a full risky command itself.
const FETCH = ['curl', 'wget', 'iwr', 'Invoke-WebRequest'];
const SHELLS = ['sh', 'bash', 'zsh', 'dash', 'iex', 'Invoke-Expression'];
const SECRET_PATHS = ['.ssh/id_', '.aws/credentials'];
const OVERRIDE = [['ignore', 'previous', 'instructions'], ['ignore', 'prior', 'instructions'], ['disregard', 'the', 'system', 'prompt']];
const esc = (w) => w.replace(/[.*+?^${}()|[\]\\/]/g, '\\$&');
const DL_TO_SHELL = new RegExp(`\\b(${FETCH.map(esc).join('|')})\\b[^\\n]{0,200}[|]\\s*(sudo\\s+)?(${SHELLS.map(esc).join('|')})\\b`, 'i');
const B64_RUN = new RegExp(['base64\\s+(-d|--decode)[^\\n]{0,80}[|]\\s*(ba)?sh', 'FromBase64String'].join('|'), 'i');
const WIPE = new RegExp(['\\brm\\s+-[a-z]*r[a-z]*\\s+(', '/', '|~|\\$HOME)(\\s|$)'].join(''), 'i');
const OVERRIDE_RE = new RegExp(OVERRIDE.map((ws) => ws.join('\\s+(all\\s+)?')).join('|'), 'i');
const hidden = (text) => { for (const ch of text) { const c = ch.codePointAt(0); if ((c >= 0x200b && c <= 0x200f) || (c >= 0x202a && c <= 0x202e) || (c >= 0x2066 && c <= 0x2069)) return true; } return false; };

const RISKS = [
  ['pipes a download into a shell', (t) => DL_TO_SHELL.test(t)],
  ['decodes and runs base64', (t) => B64_RUN.test(t)],
  ['deletes whole folders', (t) => WIPE.test(t)],
  ['reads secrets or SSH keys', (t) => SECRET_PATHS.some((p) => t.includes(p))],
  ['tells Claude to drop its earlier rules', (t) => OVERRIDE_RE.test(t)],
  ['hides text with invisible characters', hidden],
];

function risks(files) {
  const found = [];
  for (const f of files) {
    if (f.buf.length > 2 * 1024 * 1024 || f.buf.includes(0)) continue;
    const text = f.buf.toString('utf8');
    for (const [label, test] of RISKS) if (test(text)) found.push({ file: f.rel, why: label });
  }
  return found;
}

function hasScripts(files) {
  return files.some((f) => /\.(sh|ps1|py|js|mjs|cjs|ts|bat|cmd|exe)$/i.test(f.rel));
}

// Write to a temp folder next to the destination, then rename: never a half-installed skill.
function write(root, name, files, { force = false } = {}) {
  if (!SKILL_NAME_RE.test(name)) throw new InstallError(`Invalid skill name: ${name}`);
  fs.mkdirSync(root, { recursive: true });
  const dest = path.join(root, name);
  let backup = null;
  if (fs.existsSync(dest)) {
    if (fs.lstatSync(dest).isSymbolicLink()) throw new InstallError(`Destination is a symlink, not touching it: ${dest}`);
    if (!force) throw new InstallError(`Already installed: ${dest} (ask to update it to replace it; the old copy is kept as a backup).`);
  }
  const stage = fs.mkdtempSync(path.join(root, `.${name}.installing-`));
  try {
    for (const f of files) {
      const out = path.join(stage, ...f.rel.split('/'));
      if (!out.startsWith(stage + path.sep)) throw new InstallError(`Unsafe file path in skill: ${f.rel}`);
      fs.mkdirSync(path.dirname(out), { recursive: true });
      fs.writeFileSync(out, f.buf, { flag: 'wx' });
    }
    if (fs.existsSync(dest)) {
      backup = path.join(root, `.${name}.backup-${Date.now()}`);
      fs.renameSync(dest, backup);
    }
    fs.renameSync(stage, dest);
  } catch (e) {
    fs.rmSync(stage, { recursive: true, force: true });
    if (backup && !fs.existsSync(dest)) fs.renameSync(backup, dest);
    throw e;
  }
  return { dest, backup };
}

function installedNames(root) {
  if (!fs.existsSync(root)) return new Set();
  return new Set(fs.readdirSync(root, { withFileTypes: true }).filter((d) => d.isDirectory() && !d.name.startsWith('.')).map((d) => d.name));
}

module.exports = { FETCH, SHELLS, destRoot, frontmatter, validate, risks, hasScripts, write, installedNames };
