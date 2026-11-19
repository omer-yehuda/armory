#!/usr/bin/env node
/*
 * Builds the interactive Army map: a single self-contained HTML page generated from the plugin's
 * own files (agents, doctrine playbooks, skills, and the order-of-battle table), so it never drifts
 * from the real army.
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

// Presentation metadata. Units not listed here still appear (group "Other"), so new units never break the map.
const META = {
  recon:               { title: 'Recon',                 group: 'Command',      mono: 'RC' },
  ops:                 { title: 'Operations & Planning', group: 'Command',      mono: 'OP' },
  'inspector-general': { title: 'Inspector General',     group: 'Command',      mono: 'IG' },
  history:             { title: 'History & Doctrine',    group: 'Command',      mono: 'HI' },
  rnd:                 { title: 'R&D',                   group: 'Command',      mono: 'RD' },
  'special-ops':       { title: 'Special Operations',    group: 'Command',      mono: 'SO' },
  intel:               { title: 'Intelligence',          group: 'Intelligence', mono: 'IN' },
  data:                { title: 'Data',                  group: 'Intelligence', mono: 'DA' },
  engineering:         { title: 'Engineering',           group: 'Build',        mono: 'EN' },
  ux:                  { title: 'UX & Design',           group: 'Build',        mono: 'UX' },
  logistics:           { title: 'Logistics (DevOps)',    group: 'Build',        mono: 'LG' },
  rescue:              { title: 'Search & Rescue',       group: 'Build',        mono: 'SR' },
  defense:             { title: 'Defense (Security)',    group: 'Protect',      mono: 'DF' },
  legal:               { title: 'Legal',                 group: 'Protect',      mono: 'LE' },
  comms:               { title: 'Communications',        group: 'Market',       mono: 'CO' },
  growth:              { title: 'Growth',                group: 'Market',       mono: 'GR' },
  treasury:            { title: 'Treasury',              group: 'Market',       mono: 'TR' },
  sales:               { title: 'Sales & Customers',     group: 'Market',       mono: 'SA' },
};

function read(p) { return fs.readFileSync(p, 'utf8'); }

function frontmatter(text) {
  const m = text.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
  if (!m) return { fm: {}, body: text };
  const fm = {};
  for (const line of m[1].split('\n')) {
    const kv = line.match(/^([A-Za-z_-]+):\s*(.*)$/);
    if (kv) fm[kv[1]] = kv[2].replace(/^["']|["']$/g, '');
  }
  return { fm, body: m[2] };
}

// Lean/full models from the order-of-battle table in the raise skill.
function orderOfBattle() {
  const text = read(path.join(ROOT, 'skills', 'raise', 'SKILL.md'));
  const map = {};
  const re = /^\|\s*`army:([a-z-]+)`\s*\|\s*([^|]+?)\s*\|\s*(\w+)\s*\|\s*(\w+)\s*\|/gm;
  let m;
  while ((m = re.exec(text))) map[m[1]] = { use: m[2], full: m[3], lean: m[4] };
  return map;
}

function units() {
  const oob = orderOfBattle();
  const dir = path.join(ROOT, 'agents');
  const list = [];
  for (const f of fs.readdirSync(dir).filter((n) => n.endsWith('.md')).sort()) {
    const { fm, body } = frontmatter(read(path.join(dir, f)));
    const name = fm.name || f.replace(/\.md$/, '');
    const meta = META[name] || { title: name, group: 'Other', mono: name.slice(0, 2).toUpperCase() };
    const specialists = [];
    const re = /^- \*\*(.+?)\*\*: (.+?)\. Playbook: `\$\{CLAUDE_PLUGIN_ROOT\}\/doctrine\/(.+?)\.md`/gm;
    let m;
    while ((m = re.exec(body))) specialists.push({ name: m[1], does: m[2], playbook: m[3] });
    const doctrine = (body.match(/## Unit doctrine\n([\s\S]*?)(\n<!--|\n## |$)/) || [])[1] || '';
    const procedure = (body.match(/## Procedure\n([\s\S]*?)(\n<!--|\n## |$)/) || [])[1] || '';
    const o = oob[name] || {};
    list.push({
      id: name, title: meta.title, group: meta.group, mono: meta.mono,
      description: (fm.description || '').replace(/\s*Dispatched by the army chief of staff.*$/, ''),
      use: o.use || '', full: o.full || fm.model || 'inherit', lean: o.lean || fm.model || 'inherit',
      effort: fm.effort || '', specialists, doctrine: doctrine.trim(), procedure: procedure.trim(),
    });
  }
  const order = Object.keys(META);
  const rank = (id) => (order.indexOf(id) === -1 ? 999 : order.indexOf(id));
  return list.sort((a, b) => rank(a.id) - rank(b.id));
}

function playbooks(unitList) {
  const out = {};
  for (const u of unitList) for (const s of u.specialists) {
    const p = path.join(ROOT, 'doctrine', s.playbook + '.md');
    if (fs.existsSync(p)) out[s.playbook] = read(p);
  }
  return out;
}

function skills() {
  const dir = path.join(ROOT, 'skills');
  return fs.readdirSync(dir).filter((d) => fs.existsSync(path.join(dir, d, 'SKILL.md'))).sort().map((d) => {
    const { fm } = frontmatter(read(path.join(dir, d, 'SKILL.md')));
    return { name: fm.name || d, description: fm.description || '', hint: fm['argument-hint'] || '' };
  });
}

function main() {
  const manifest = JSON.parse(read(path.join(ROOT, '.claude-plugin', 'plugin.json')));
  const unitList = units();
  const data = {
    version: manifest.version,
    repository: manifest.repository || '',
    generated: new Date().toISOString().slice(0, 10),
    units: unitList,
    playbooks: playbooks(unitList),
    skills: skills(),
  };
  const json = JSON.stringify(data).replace(/</g, '\\u003c');
  const template = read(path.join(__dirname, 'map-template.html'));
  const html = template.replace('/*__ARMY_DATA__*/null', json);
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.writeFileSync(OUT, html);
  const specs = unitList.reduce((n, u) => n + u.specialists.length, 0);
  process.stdout.write(JSON.stringify({ ok: true, out: OUT, units: unitList.length, specialists: specs, skills: data.skills.length }) + '\n');
}

main();
