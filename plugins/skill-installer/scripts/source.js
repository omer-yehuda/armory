'use strict';
/* Parse and validate where a skill comes from. Adapted from OpenAI's Codex skill-installer (Apache-2.0); see NOTICE. */

const path = require('node:path');

const NAME_RE = /^[A-Za-z0-9_.-]{1,100}$/;
const REF_RE = /^[A-Za-z0-9._/-]{1,200}$/;
const SKILL_NAME_RE = /^[a-z0-9][a-z0-9-]{0,63}$/;

class InstallError extends Error {}

function cleanPath(p) {
  if (p === undefined || p === null) return '';
  const s = String(p).replace(/\\/g, '/').replace(/^\/+|\/+$/g, '');
  if (!s) return '';
  if (/^[A-Za-z]:/.test(s) || s.split('/').some((seg) => seg === '..' || seg === '.' || seg === '')) {
    throw new InstallError(`Skill path must be a relative path inside the repo: ${p}`);
  }
  if (/[\u0000-\u001f]/.test(s)) throw new InstallError('Skill path contains control characters.');
  return s.replace(/\/SKILL\.md$/i, '').replace(/^SKILL\.md$/i, '');
}

function checkRepo(owner, repo) {
  if (!NAME_RE.test(owner || '') || !NAME_RE.test(repo || '') || owner.startsWith('.') || repo.startsWith('.')) {
    throw new InstallError('Repo must look like owner/repo (letters, digits, dot, dash, underscore).');
  }
}

function checkRef(ref) {
  if (!REF_RE.test(ref) || ref.split('/').includes('..') || ref.startsWith('-')) {
    throw new InstallError(`Invalid git ref: ${ref}`);
  }
}

// Accepts: owner/repo, owner/repo/sub/path, https://github.com/owner/repo[/tree|blob/ref/path]
function parseTarget(input, defaultRef = 'main') {
  let s = String(input || '').trim();
  if (!s) throw new InstallError('Nothing to install: give owner/repo or a GitHub URL.');
  let ref = defaultRef;
  let parts;
  if (/^[a-z]+:\/\//i.test(s)) {
    let u;
    try { u = new URL(s); } catch { throw new InstallError('Invalid URL.'); }
    if (u.protocol !== 'https:' || !['github.com', 'www.github.com'].includes(u.hostname) || u.username || u.port) {
      throw new InstallError('Only https://github.com URLs are supported.');
    }
    parts = u.pathname.split('/').filter(Boolean);
    if (parts.length < 2) throw new InstallError('GitHub URL must include owner and repo.');
    if (parts.length > 2 && (parts[2] === 'tree' || parts[2] === 'blob')) {
      if (parts.length < 4) throw new InstallError('GitHub URL is missing the branch.');
      ref = parts[3];
      parts = [parts[0], parts[1], ...parts.slice(4)];
    }
  } else {
    if (s.startsWith('github.com/')) s = s.slice('github.com/'.length);
    parts = s.split('/').filter(Boolean);
    if (parts.length < 2) throw new InstallError('Use owner/repo or owner/repo/path/to/skill.');
  }
  const owner = parts[0];
  const repo = parts[1].replace(/\.git$/, '');
  checkRepo(owner, repo);
  checkRef(ref);
  const sub = cleanPath(parts.slice(2).join('/'));
  return { owner, repo, ref, path: sub };
}

function skillNameFrom(p, override) {
  const name = override || path.posix.basename(p || '');
  if (!SKILL_NAME_RE.test(name)) {
    throw new InstallError(`Skill folder name must be lowercase letters, digits and dashes (got "${name}"). Pass a name to rename it.`);
  }
  return name;
}

module.exports = { InstallError, parseTarget, cleanPath, checkRef, skillNameFrom, SKILL_NAME_RE };
