// node scripts/analyze.js
// 说明：与 data.js 放在同一目录，node >=14
const fs = require('fs');
const vm = require('vm');
const path = require('path');

const DATA_FILE = path.join(__dirname, '..', 'data.js'); // 调整路径：脚本在 scripts/ 下
const TODAY = new Date('2026-02-17T00:00:00Z'); // 根据你给定的当前时间（可修改）

function safeLoadData(filePath) {
  const code = fs.readFileSync(filePath, 'utf-8');
  const sandbox = { window: {} };
  try {
    vm.createContext(sandbox);
    // run the file in sandbox; data.js assigns window.injData etc.
    vm.runInContext(code, sandbox, { timeout: 1000 });
    const { injData, usdt45Data, usdtFinanceData } = sandbox.window;
    return { injData: injData || [], usdt45Data: usdt45Data || [], usdtFinanceData: usdtFinanceData || [] };
  } catch (err) {
    console.error('载入 data.js 出错:', err);
    process.exit(1);
  }
}

function parseAmount(v) {
  if (v === null || v === undefined) return 0;
  if (typeof v === 'number') return v;
  // remove thousands separators, currency symbols, whitespace
  const s = String(v).replace(/[,￥$]/g, '').trim();
  const n = parseFloat(s);
  return isNaN(n) ? 0 : n;
}

function parseDateGuess(s) {
  if (!s) return null;
  // if ISO-like or contains '/' and year
  try {
    const str = String(s).trim();
    // if contains year like 2026 or '/'
    if (/\d{4}[\/\-]/.test(str) || /\d{4}/.test(str)) {
      const d = new Date(str);
      if (!isNaN(d)) return d;
    }
    // formats like "1月14日" or "1月14日 23:00" or "2026/2/2 13:59"
    const m = str.match(/(\d{1,2})\s*月\s*(\d{1,2})\s*日(?:\s*(\d{1,2}:\d{1,2}))?/);
    if (m) {
      const month = Number(m[1]);
      const day = Number(m[2]);
      // assume 2026 (based on your current date)
      const timePart = m[3] || '00:00';
      const iso = `2026-${String(month).padStart(2,'0')}-${String(day).padStart(2,'0')}T${timePart}:00Z`;
      const d = new Date(iso);
      if (!isNaN(d)) return d;
    }
    // fallback: try Date()
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
    // normalize fields - support different key names used in your files
    const product = rec['产品名称'] || rec['产品'] || rec['product_name'] || 'unknown';
    const amount = parseAmount(rec['购买金额'] || rec['认购额度'] || rec['认购额度'] || rec['amount'] || rec['认购金额'] || rec['购买金额']);
    const user = rec['用户'] || rec['会员ID'] || rec['phone'] || 'unknown';
    const endRaw = rec['结束时间'] || rec['结束'] || rec['end'] || rec['结束时间'];
    const endDate = parseDateGuess(endRaw);

    total += amount;

    // product aggregation
    const p = perProduct.get(product) || { product, count: 0, total: 0 };
    p.count += 1;
    p.total += amount;
    perProduct.set(product, p);

    // user aggregation
    const u = perUser.get(user) || { user, count: 0, total: 0, products: [] };
    u.count += 1;
    u.total += amount;
    u.products.push({ product, amount, endRaw, endDate: endDate ? endDate.toISOString() : null });
    perUser.set(user, u);

    // due / not due by endDate compared to TODAY
    if (endDate) {
      if (endDate <= TODAY) dueTotal += amount;
      else notDueTotal += amount;
    } else {
      // if no end date, treat as not due
      notDueTotal += amount;
    }
  }

  // top users
  const topUsers = Array.from(perUser.values()).sort((a,b)=>b.total - a.total).slice(0, 20);
  return {
    total_subscribed: Number(total.toFixed(2)),
    total_refunded: 0.0, // 没有退款明细，默认 0
    due_not_refunded: Number(dueTotal.toFixed(2)),
    not_due_total: Number(notDueTotal.toFixed(2)),
    perProduct: Array.from(perProduct.values()).map(x => ({ product: x.product, count: x.count, total: Number(x.total.toFixed(2)) })),
    topUsers
  };
}

function buildAllRecords(data) {
  // data is object with arrays; combine into a single list but keep source info
  const arr = [];
  for (const rec of data.injData) {
    arr.push({ ...rec, _source: 'injData' });
  }
  for (const rec of data.usdt45Data) {
    arr.push({ ...rec, _source: 'usdt45Data' });
  }
  for (const rec of data.usdtFinanceData) {
    arr.push({ ...rec, _source: 'usdtFinanceData' });
  }
  return arr;
}

// main
const data = safeLoadData(DATA_FILE);
const allRecords = buildAllRecords(data);
const report = summarize(allRecords);

// print summary
console.log('===== 总览 =====');
console.log(JSON.stringify({
  total_subscribed: report.total_subscribed,
  total_refunded: report.total_refunded,
  due_not_refunded: report.due_not_refunded,
  not_due_total: report.not_due_total
}, null, 2));

console.log('\n===== 产品汇总（按产品） =====');
console.table(report.perProduct);

console.log('\n===== Top 用户（按认购总额） =====');
report.topUsers.forEach((u, idx) => {
  console.log(`${idx+1}. ${u.user} - 总额: ${u.total.toFixed(2)} - 笔数: ${u.count}`);
});

// helper: 查询单个用户（例）
function queryUser(id) {
  const u = report.topUsers.find(x => x.user === id) || null;
  if (!u) {
    // try perUser map
    // reload perUser quickly
    const perUserMap = new Map();
    for (const rec of allRecords) {
      const user = rec['用户'] || rec['会员ID'] || rec['phone'] || 'unknown';
      const amount = parseAmount(rec['购买金额'] || rec['认购额度']);
      const item = perUserMap.get(user) || { user, total:0, count:0, products: [] };
      item.total += amount; item.count += 1;
      item.products.push(rec);
      perUserMap.set(user, item);
    }
    return perUserMap.get(id) || null;
  }
  return u;
}

// 如果需要示例查询某个手机号，写在 args
const arg = process.argv[2];
if (arg) {
  console.log('\n===== 查询用户: ' + arg + ' =====');
  const perUserMap = new Map();
  for (const rec of allRecords) {
    const user = rec['用户'] || rec['会员ID'] || rec['phone'] || 'unknown';
    const amount = parseAmount(rec['购买金额'] || rec['认购额度']);
    const item = perUserMap.get(user) || { user, total:0, count:0, products: [] };
    item.total += amount; item.count += 1;
    item.products.push(rec);
    perUserMap.set(user, item);
  }
  const u = perUserMap.get(arg);
  if (!u) console.log('未找到该用户');
  else console.log(JSON.stringify(u, null, 2));
}
