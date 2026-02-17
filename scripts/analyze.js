// node scripts/analyze.js
const fs = require('fs');
const vm = require('vm');
const path = require('path');

const DATA_FILE = path.join(__dirname, '..', 'data.js');
const TODAY = new Date('2026-02-17T00:00:00Z');

function safeLoadData(filePath) {
  const code = fs.readFileSync(filePath, 'utf-8');
  const sandbox = { window: {} };
  vm.createContext(sandbox);
  vm.runInContext(code, sandbox, { timeout: 2000 });
  const { injData, usdt45Data, usdtFinanceData } = sandbox.window;
  return { injData: injData || [], usdt45Data: usdt45Data || [], usdtFinanceData: usdtFinanceData || [] };
}

function parseAmount(v) {
  if (v === null || v === undefined) return 0;
  if (typeof v === 'number') return v;
  const s = String(v).replace(/[,￥$]/g, '').trim();
  const n = parseFloat(s);
  return isNaN(n) ? 0 : n;
}

function parseDateGuess(s) {
  if (!s) return null;
  try {
    const str = String(s).trim();
    if (/\d{4}[\/\-]/.test(str) || /\d{4}/.test(str)) {
      const d = new Date(str);
      if (!isNaN(d)) return d;
    }
    const m = str.match(/(\d{1,2})\s*月\s*(\d{1,2})\s*日(?:\s*(\d{1,2}:\d{1,2}))?/);
    if (m) {
      const month = Number(m[1]);
      const day = Number(m[2]);
      const timePart = m[3] || '00:00';
      const iso = `2026-${String(month).padStart(2,'0')}-${String(day).padStart(2,'0')}T${timePart}:00Z`;
      const d = new Date(iso);
      if (!isNaN(d)) return d;
    }
    const d2 = new Date(str);
    if (!isNaN(d2)) return d2;
  } catch (e) {}
  return null;
}

function summarize(allRecords) {
  let total = 0;
  let dueTotal = 0;
  let notDueTotal = 0;
  const perProduct = new Map();
  const perUser = new Map();

  for (const rec of allRecords) {
    const product = rec['产品名称'] || rec['产品'] || 'unknown';
    const amount = parseAmount(rec['购买金额'] || rec['认购额度']);
    const user = rec['用户'] || rec['会员ID'] || 'unknown';
    const endRaw = rec['结束时间'] || rec['结束'] || null;
    const endDate = parseDateGuess(endRaw);

    total += amount;

    const p = perProduct.get(product) || { product, count: 0, total: 0 };
    p.count += 1;
    p.total += amount;
    perProduct.set(product, p);

    const u = perUser.get(user) || { user, count: 0, total: 0, products: [] };
    u.count += 1;
    u.total += amount;
    u.products.push({ product, amount, endRaw, endDate: endDate ? endDate.toISOString() : null });
    perUser.set(user, u);

    if (endDate) {
      if (endDate <= TODAY) dueTotal += amount;
      else notDueTotal += amount;
    } else notDueTotal += amount;
  }

  const topUsers = Array.from(perUser.values()).sort((a,b)=>b.total - a.total).slice(0, 50);
  return {
    total_subscribed: Number(total.toFixed(2)),
    total_refunded: 0.0,
    due_not_refunded: Number(dueTotal.toFixed(2)),
    not_due_total: Number(notDueTotal.toFixed(2)),
    perProduct: Array.from(perProduct.values()).map(x => ({ product: x.product, count: x.count, total: Number(x.total.toFixed(2)) })),
    perUser,
    topUsers
  };
}

function buildAllRecords(data) {
  const arr = [];
  for (const rec of data.injData) arr.push({ ...rec, _source: 'injData' });
  for (const rec of data.usdt45Data) arr.push({ ...rec, _source: 'usdt45Data' });
  for (const rec of data.usdtFinanceData) arr.push({ ...rec, _source: 'usdtFinanceData' });
  return arr;
}

const data = safeLoadData(DATA_FILE);
const allRecords = buildAllRecords(data);
const report = summarize(allRecords);

console.log('===== 总览 =====');
console.log(JSON.stringify({ total_subscribed: report.total_subscribed, total_refunded: report.total_refunded, due_not_refunded: report.due_not_refunded, not_due_total: report.not_due_total }, null, 2));

console.log('\n===== 产品汇总（按产品） =====');
console.table(report.perProduct);

console.log('\n===== Top 用户（按认购总额） =====');
report.topUsers.slice(0,20).forEach((u, idx) => {
  console.log(`${idx+1}. ${u.user} - 总额: ${u.total.toFixed(2)} - 笔数: ${u.count}`);
});

// 支持命令行查询: node scripts/analyze.js 13392776413
const arg = process.argv[2];
if (arg) {
  const u = report.perUser.get(arg);
  if (!u) console.log('未找到该用户');
  else console.log(JSON.stringify(u, null, 2));
}
