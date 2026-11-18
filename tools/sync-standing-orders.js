#!/usr/bin/env node
// Copies plugins/army/doctrine/shared/standing-orders.md into every agent file between the
// BEGIN/END STANDING ORDERS markers. The orders are inlined (not read at runtime) so each unit
// gets them in its system prompt without spending a tool call.
// Usage: node tools/sync-standing-orders.js [--check]
'use strict';
const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..', 'plugins', 'army');
const orders = fs.readFileSync(path.join(root, 'doctrine', 'shared', 'standing-orders.md'), 'utf8').trim();
const re = /<!-- BEGIN STANDING ORDERS -->[\s\S]*?<!-- END STANDING ORDERS -->/;
const block = `<!-- BEGIN STANDING ORDERS -->\n${orders}\n<!-- END STANDING ORDERS -->`;
const check = process.argv.includes('--check');
let stale = 0;

for (const f of fs.readdirSync(path.join(root, 'agents')).filter((n) => n.endsWith('.md'))) {
  const file = path.join(root, 'agents', f);
  const text = fs.readFileSync(file, 'utf8');
  if (!re.test(text)) continue;
  const next = text.replace(re, block);
  if (next !== text) {
    stale++;
    if (!check) fs.writeFileSync(file, next);
    console.log(`${check ? 'stale' : 'synced'}: agents/${f}`);
  }
}
if (check && stale) process.exit(1);
console.log(check ? 'standing orders up to date' : 'done');
