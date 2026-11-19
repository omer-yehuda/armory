#!/usr/bin/env node
/*
 * Builds the Army command-center map: one self-contained HTML page (fonts embedded, no network needed)
 * generated from the plugin's own files: units.json, agent doctrine, specialist playbooks and skills.
 *
 *   node build-map.js [--out FILE]          default: ./army-map.html
 *
 * Zero dependencies. Used by the /army:map skill and to build the public docs site.
 */
'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const args = process.argv.slice(2);
const outIdx = args.indexOf('--out');
const OUT = path.resolve(outIdx >= 0 ? args[outIdx + 1] : 'army-map.html');
const read = (p) => fs.readFileSync(p, 'utf8');

function body(text) { return text.replace(/^---\n[\s\S]*?\n---\n?/, ''); }
function section(text, name) {
  const m = text.match(new RegExp(`## ${name}\\n([\\s\\S]*?)(\\n<!--|\\n## |$)`));
  return m ? m[1].trim() : '';
}

function units() {
  const cfg = JSON.parse(read(path.join(ROOT, 'units.json'))).units;
  return cfg.map((u) => {
    const file = path.join(ROOT, 'agents', `${u.id}.md`);
    const b = fs.existsSync(file) ? body(read(file)) : '';
    const specialists = [];
    const re = /^- \*\*(.+?)\*\*: (.+?)\. Playbook: `\$\{CLAUDE_PLUGIN_ROOT\}\/doctrine\/(.+?)\.md`/gm;
    let m;
    while ((m = re.exec(b))) specialists.push({ name: m[1], does: m[2], playbook: m[3] });
    return {
      id: u.id, title: u.title, group: u.group, mono: u.mono, callsign: u.callsign, use: u.use,
      description: u.description, full: u.full, lean: u.lean, effort: u.effort || '', tools: u.tools,
      specialists, doctrine: section(b, 'Unit doctrine'), procedure: section(b, 'Procedure'),
    };
  });
}

function playbooks(list) {
  const out = {};
  for (const u of list) for (const s of u.specialists) {
    const p = path.join(ROOT, 'doctrine', s.playbook + '.md');
    if (fs.existsSync(p)) out[s.playbook] = read(p);
  }
  return out;
}

function skills() {
  const dir = path.join(ROOT, 'skills');
  return fs.readdirSync(dir).filter((d) => fs.existsSync(path.join(dir, d, 'SKILL.md'))).sort().map((d) => {
    const t = read(path.join(dir, d, 'SKILL.md'));
    const fm = (t.match(/^---\n([\s\S]*?)\n---/) || [])[1] || '';
    const get = (k) => ((fm.match(new RegExp(`^${k}:\\s*(.*)$`, 'm')) || [])[1] || '').replace(/^["']|["']$/g, '');
    return { name: get('name') || d, description: get('description'), hint: get('argument-hint') };
  });
}

function fontFaces() {
  const dir = path.join(__dirname, 'fonts');
  const faces = [
    ['Saira Stencil One', 400, 'saira-stencil-one-latin-400-normal.woff2'],
    ['Barlow', 400, 'barlow-latin-400-normal.woff2'],
    ['Barlow', 600, 'barlow-latin-600-normal.woff2'],
    ['Barlow', 700, 'barlow-latin-700-normal.woff2'],
    ['Special Elite', 400, 'special-elite-latin-400-normal.woff2'],
  ];
  return faces.filter(([, , f]) => fs.existsSync(path.join(dir, f))).map(([family, weight, f]) =>
    `@font-face{font-family:"${family}";font-weight:${weight};font-style:normal;font-display:swap;src:url(data:font/woff2;base64,${fs.readFileSync(path.join(dir, f)).toString('base64')}) format("woff2")}`).join('\n');
}

function main() {
  const manifest = JSON.parse(read(path.join(ROOT, '.claude-plugin', 'plugin.json')));
  const list = units();
  const data = {
    version: manifest.version, repository: manifest.repository || '', generated: new Date().toISOString().slice(0, 10),
    units: list, playbooks: playbooks(list), skills: skills(),
  };
  const json = JSON.stringify(data).replace(/</g, '\\u003c');
  const html = read(path.join(__dirname, 'map-template.html'))
    .replace('/*__FONTS__*/', () => fontFaces())
    .replace('/*__ARMY_DATA__*/null', () => json);
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.writeFileSync(OUT, html);
  const specs = list.reduce((n, u) => n + u.specialists.length, 0);
  process.stdout.write(JSON.stringify({ ok: true, out: OUT, units: list.length, specialists: specs, skills: data.skills.length, kb: Math.round(html.length / 1024) }) + '\n');
}

main();
