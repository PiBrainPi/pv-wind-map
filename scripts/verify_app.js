#!/usr/bin/env node
// verify_app.js — UI-Verifikation einer Karten-HTML (Multi-File ODER Singlefile)
// Teil der Prüfvorschrift nach Pipeline-Update (User-Beschluss 19.09.2026).
// Aufruf: node scripts/verify_app.js <pfad-zur-html> [chrome-binary]
// Exit 0 = alle Checks grün · Exit 1 = mindestens ein Check rot.
// Details: docs/update.md § „Prüfvorschrift nach Pipeline-Update (PFLICHT)"
const { chromium } = require('playwright-core');
const path = require('path');

const FILE = process.argv[2];
const CHROME = process.argv[3] || process.env.HOME + '/.cache/ms-playwright/chromium-1223/chrome-linux/chrome';

if (!FILE) { console.error('Aufruf: node scripts/verify_app.js <html> [chrome]'); process.exit(1); }
const URL = 'file://' + path.resolve(FILE);

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: CHROME, args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage();
  const errors = [];
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text().slice(0, 200)); });
  page.on('pageerror', e => errors.push('PAGEERROR: ' + e.toString().slice(0, 200)));
  await page.addInitScript(() => { try { localStorage.setItem('pvw_tiles_consent', 'osm'); } catch (e) {} });
  await page.goto(URL, { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForTimeout(15000);

  const checks = [];
  const check = (name, cond, detail) => { checks.push({ name, ok: !!cond, detail: detail || '' }); };

  // 1) Karte + Infobar
  const base = await page.evaluate(() => {
    const infobar = (document.querySelector('#infobar') || {}).textContent || '';
    const m = infobar.match(/(\d[\d.]{3,})\s*Wind\s*·\s*(\d[\d.]{3,})\s*PV/);
    return {
      hasLeaflet: typeof window.L !== 'undefined',
      infobar, wind: m ? +m[1].replace(/\./g, '') : 0, pv: m ? +m[2].replace(/\./g, '') : 0,
      markers: document.querySelectorAll('.leaflet-pane .leaflet-interactive, .leaflet-marker-icon').length,
    };
  });
  check('Leaflet geladen', base.hasLeaflet);
  // Zahlen mindestens plausibel (nicht 0/alt) — exakte Grenzen pro Datenstand setzt der Aufrufer
  check('Infobar Wind+PV', base.wind > 0 && base.pv > 0, `${base.wind} Wind / ${base.pv} PV`);
  check('Karten-Marker gerendert', base.markers > 0, `${base.markers} Layer`);

  // 2) Statistik-Panel + alle 11 Tabs mit echten Klicks
  await page.click('#btn-stats');
  await page.waitForTimeout(1500);
  const tabs = ['betreiber', 'hersteller', 'typ', 'groesse', 'bundesland', 'landkreis', 'nap', 'spannung', 'historie', 'zubau', 'betroffen'];
  for (const t of tabs) {
    try {
      await page.click(`[data-tab="${t}"]`);
      await page.waitForTimeout(900);
      const r = await page.evaluate((tab) => {
        const btn = document.querySelector(`[data-tab="${tab}"]`);
        const body = (document.querySelector('#stats-body') || document.querySelector('#stats-panel') || {});
        const txt = (body.textContent || '').trim();
        const rows = document.querySelectorAll('#stats-body table tbody tr, #stats-body svg').length;
        return { active: !!(btn && btn.className.includes('active')), textLen: txt.length, rows };
      }, t);
      check(`Tab ${t}`, r.active && (r.textLen > 300 || r.rows > 0), `textLen=${r.textLen} rows=${r.rows}`);
    } catch (e) {
      check(`Tab ${t}`, false, e.message.slice(0, 80));
    }
  }

  // 3) Historie-Charts (3 SVGs) im Historie-Tab
  await page.click('[data-tab="historie"]');
  await page.waitForTimeout(2000);
  const histSvgs = await page.evaluate(() => document.querySelectorAll('#historie-charts svg').length);
  check('Historie-Charts (3 SVGs)', histSvgs === 3, `${histSvgs} SVGs`);

  // 4) Zubau-Heatmap vorhanden
  await page.click('[data-tab="zubau"]');
  await page.waitForTimeout(2000);
  const zubau = await page.evaluate(() => !!document.querySelector('#zubau-heatmap-wrap, [id*="zubau-heatmap"]'));
  check('Zubau-Heatmap', zubau);

  // 5) 0 JS-Errors im ganzen Lauf
  check('0 JS-Errors', errors.length === 0, errors.slice(0, 3).join(' | '));

  await browser.close();

  const failed = checks.filter(c => !c.ok);
  for (const c of checks) {
    console.log(`${c.ok ? '✅' : '🚨'} ${c.name}${c.detail ? ' — ' + c.detail : ''}`);
  }
  const build = path.basename(FILE);
  if (failed.length === 0) {
    console.log(`VERIFY_APP OK — ${build}: ${checks.length}/${checks.length} Checks grün`);
    process.exit(0);
  } else {
    console.log(`VERIFY_APP FAILED — ${build}: ${failed.length}/${checks.length} Checks rot: ${failed.map(f => f.name).join(', ')}`);
    process.exit(1);
  }
})().catch(e => { console.error('VERIFY_APP FATAL:', e.message.slice(0, 200)); process.exit(1); });
