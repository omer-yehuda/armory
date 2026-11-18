// Run: node --test plugins/army/tests
'use strict';
const test = require('node:test');
const assert = require('node:assert');
const { checkCommand } = require('../scripts/army.js');

const GATED = [
  'git push origin main',
  'git push --force',
  'git reset --hard HEAD~1',
  'git clean -fd',
  'git checkout -- src/app.ts',
  'git restore src/app.ts',
  'git branch -D feature',
  'git rebase -i main',
  'rm -rf dist',
  'rm file.txt',
  'cd src && rm old.ts',
  'find . -name "*.log" -delete',
  'npm publish',
  'docker push me/app:latest',
  'vercel --prod',
  'vercel',
  'netlify deploy --prod',
  'firebase deploy',
  'flyctl deploy',
  'kubectl apply -f k8s/',
  'terraform apply -auto-approve',
  'npx prisma migrate deploy',
  'psql -c "DROP TABLE users"',
  'gh pr merge 12 --squash',
  'gh release create v1.0.0',
  'npm install lodash',
  'npm i -D vitest',
  'pnpm add zod',
  'yarn add react-query',
  'bun add hono',
  'pip install requests',
  'python -m pip install fastapi',
  'pip install -r requirements.txt flask',
  'uv add httpx',
  'poetry add pydantic',
  'sudo apt-get install jq',
  'FOO=1 npm install axios',
];

const ALLOWED = [
  'git status',
  'git diff',
  'git add -A && git commit -m "feat: x"',
  'git restore --staged src/app.ts',
  'git checkout -b feature',
  'npm install',
  'npm ci',
  'npm test',
  'npm run build',
  'pnpm install',
  'pnpm i',
  'yarn',
  'yarn install',
  'pip install -r requirements.txt',
  'pip install -e .',
  'pip install .',
  'uv sync',
  'pytest -q',
  'vercel dev',
  'vercel env pull',
  'ls -la',
  'grep -rn "TODO" src',
  'node scripts/build.js',
  'npx tsc --noEmit',
  'npx prisma generate',
  'docker build -t app .',
  'echo "remove the warning"',
];

test('gated commands are flagged', () => {
  for (const cmd of GATED) assert.ok(checkCommand(cmd), `expected gate for: ${cmd}`);
});

test('safe commands pass', () => {
  for (const cmd of ALLOWED) assert.strictEqual(checkCommand(cmd), null, `unexpected gate for: ${cmd} -> ${checkCommand(cmd)}`);
});
