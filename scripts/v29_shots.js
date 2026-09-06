// ═══ V29 Screenshot-Fabrik: 9 Screenshots vom :8805-Dist-Stand (identisch Live) ═══
const { chromium } = require('playwright');
const fs = require('fs');

const OUT = '/home/claw_01_rasbpi5_1/Projects/pv-wind-map/Artikel/screenshots_v29';
fs.mkdirSync(OUT, { recursive: true });

const URL = 'http://127.0.0.1:8805/index.html?v29shot=' + Date.now();
const W = 1600, H = 1000;

async function ready(page) {
  await page.waitForFunction(() => {
    const ib = document.getElementById('infobar');
    return ib && ib.textContent && ib.textContent.includes('PV') && ib.textContent.length > 12;
  }, { timeout: 60000 });
  await page.waitForTimeout(4500); // Cluster rendern
}

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 2 });

  await page.goto(URL);
  try { await page.click('#tc-accept', { timeout: 5000 }); } catch (e) {}
  await ready(page);

  const shot = async (name) => {
    await page.screenshot({ path: `${OUT}/${name}.png` });
    console.log('✓', name);
  };

  // 01 Karte DE Cluster
  await shot('01_karte_deutschland_cluster');

  // 02 CEE-Suche
  await page.fill('#search-input', 'CEE');
  await page.waitForTimeout(1800);
  await shot('02_suche_betreiber_buendelung');
  await page.click('#search-clear');
  await page.waitForTimeout(2500);

  // 03 BB FF-PV 5-10, EINZEL-Basis
  await page.selectOption('#filter-bl', 'Brandenburg');
  await page.selectOption('#filter-art', 'Freiflächensolaranlage');
  await page.selectOption('#filter-gr', '5,10');
  const grBasis = document => 0; // noop
  await page.evaluate(() => {
    const el = document.getElementById('filter-gr-basis');
    if (el) { el.value = 'einzel'; el.dispatchEvent(new Event('change', { bubbles: true })); }
  });
  await page.waitForTimeout(3500);
  await shot('03_filter_brandenburg_freiflaeche_5_10mw');
  // Reset
  await page.click('#btn-reset-filters');
  await page.waitForTimeout(2500);

  // 04 Betreiber-Tab enerparc
  await page.click('#btn-stats');
  await page.waitForTimeout(1200);
  await page.fill('#stats-filter', 'enerparc');
  await page.waitForTimeout(1800);
  
  await shot('04_statistik_betreiber_enerparc');

  // 05 Bundesländer-Donut
  const tabBl = await page.$('#stats-tabs .tab[data-tab="bundesland"]');
  if (tabBl) { await tabBl.click(); await page.waitForTimeout(1200); }
  await shot('05_statistik_bundeslaender_donut');

  // 06 Zubau
  const tabZub = await page.$('#stats-tabs .tab[data-tab="zubau"]');
  if (tabZub) { await tabZub.click(); await page.waitForTimeout(1500); }
  await shot('06_zubau_kumuliertes_wachstum');

  // 07 NAP-Gruppenansicht: Bertikow via NAP-Suche? Einfacher: selectNAP über JS
    const tabNap = await page.$('#stats-tabs .tab[data-tab="nap"]');
  if (tabNap) { await tabNap.click(); await page.waitForTimeout(900); }
  await page.fill('#nap-search', 'Bertikow');
  await page.waitForTimeout(1200);
  await page.click('#nap-suggest .nap-sug-nap'); // erstes NAP-Suggest-Element
  await page.waitForTimeout(4000); // Karte fliegt, Marker rendern
  await shot('07_nap_gruppenansicht_219');
  await page.evaluate(() => { if (typeof clearSearch === 'function') clearSearch(); });
  await page.waitForTimeout(2000);

  // 08/09 Betroffenheit enova
  await page.evaluate(() => { document.querySelector('[data-tab-btn="bff"], #btn-betroffenheit, button.btn-bff')?.click(); });
  await page.waitForTimeout(900);
  await page.fill('#bff-ref-input', 'enova');
  await page.waitForTimeout(1500);
  // Portfolio-Treffer (erster in Liste) wählen
  await page.evaluate(() => { document.querySelector('#bff-ref-results .np-row')?.click(); });
  await page.waitForTimeout(900);
  await page.waitForTimeout(1500);
  // Radius 20 km einstellen
  await page.evaluate(() => {
    const r = document.getElementById('bff-radius');
    if (r) { r.value = '20'; r.dispatchEvent(new Event('input', { bubbles: true })); }
  });
  await page.click('#bff-run');
  await page.waitForTimeout(6000);
  await shot('08_betroffenheit_summary');
  await shot('09_betroffenheit_match_tabelle');

  await browser.close();
  console.log('FERTIG');
})();
