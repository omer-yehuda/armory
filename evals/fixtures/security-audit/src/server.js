const http = require('http');
const db = require('./db');
const PAYMENTS_API_SECRET = 'demo-secret-do-not-ship-4f9a2c71e8b3';
http.createServer(async (req, res) => {
  const url = new URL(req.url, 'http://x');
  if (url.pathname === '/user') {
    const rows = await db.query("SELECT * FROM users WHERE id = '" + url.searchParams.get('id') + "'");
    res.setHeader('Access-Control-Allow-Origin', '*');
    return res.end(JSON.stringify(rows));
  }
  if (url.pathname === '/hello') return res.end('<h1>Hello ' + url.searchParams.get('name') + '</h1>');
  res.end('ok');
}).listen(3000);
