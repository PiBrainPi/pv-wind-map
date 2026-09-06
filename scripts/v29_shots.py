# ═══ V29 Screenshot-Fabrik (Python-Playwright) ═══
import asyncio
from playwright.async_api import async_playwright

OUT = '/home/claw_01_rasbpi5_1/Projects/pv-wind-map/Artikel/screenshots_v29'
import os
os.makedirs(OUT, exist_ok=True)

URL = 'http://127.0.0.1:8805/index.html?v29shot=%d' % int(asyncio.get_event_loop().time()*1000)

async def ready(page):
    await page.wait_for_function(
        "() => { const ib = document.getElementById('infobar'); return ib && ib.textContent && ib.textContent.includes('PV') && ib.textContent.length > 12; }",
        timeout=60000)
    await page.wait_for_timeout(4500)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1600, 'height': 1000}, device_scale_factor=2)
        await page.goto(URL)
        try:
            await page.click('#tc-accept', timeout=5000)
        except Exception:
            pass
        await ready(page)

        async def shot(name):
            await page.screenshot(path=f'{OUT}/{name}.png')
            print('✓', name, flush=True)

        # 01 Karte DE Cluster
        await shot('01_karte_deutschland_cluster')

        # 02 CEE-Suche
        await page.fill('#search-input', 'CEE')
        await page.wait_for_timeout(1800)
        await shot('02_suche_betreiber_buendelung')
        await page.click('#search-clear')
        await page.wait_for_timeout(2500)

        # 03 BB FF-PV 5-10, EINZEL-Basis
        await page.select_option('#filter-bl', 'Brandenburg')
        await page.select_option('#filter-art', 'Freiflächensolaranlage')
        await page.select_option('#filter-gr', '5,10')
        await page.evaluate("""() => {
            const el = document.getElementById('filter-gr-basis');
            if (el) { el.value = 'einzel'; el.dispatchEvent(new Event('change', {bubbles: true})); }
        }""")
        await page.wait_for_timeout(3500)
        await shot('03_filter_brandenburg_freiflaeche_5_10mw')
        await page.click('#btn-reset-filters')
        await page.wait_for_timeout(2500)

        # 04 Betreiber-Tab enerparc
        await page.click('#btn-stats')
        await page.wait_for_timeout(1200)
        await page.fill('#stats-filter', 'enerparc')
        await page.wait_for_timeout(1800)
        await shot('04_statistik_betreiber_enerparc')

        # 05 Bundesländer-Donut
        tab = await page.query_selector('#stats-tabs .tab[data-tab="bundesland"]')
        if tab:
            await tab.click()
            await page.wait_for_timeout(1200)
        await shot('05_statistik_bundeslaender_donut')

        # 06 Zubau
        tab = await page.query_selector('#stats-tabs .tab[data-tab="zubau"]')
        if tab:
            await tab.click()
            await page.wait_for_timeout(1500)
        await shot('06_zubau_kumuliertes_wachstum')

        # 07 NAP: Bertikow → Klick → Karte (nur NAP+Anlagen, V29-Verhalten) → Gruppenansicht?
        tab = await page.query_selector('#stats-tabs .tab[data-tab="nap"]')
        if tab:
            await tab.click()
            await page.wait_for_timeout(900)
        await page.fill('#nap-search', 'Bertikow')
        await page.wait_for_timeout(1200)
        sug = await page.query_selector('#nap-suggest .nap-sug-nap')
        if sug:
            await sug.click()
            await page.wait_for_timeout(4500)
        await shot('07_nap_gruppenansicht_219')
        await page.evaluate("() => { if (typeof clearSearch === 'function') clearSearch(); }")
        await page.wait_for_timeout(2000)

        # 08/09 Betroffenheit enova — Tab im Stats-Panel: data-tab="betroffen"
        tab = await page.query_selector('#stats-tabs .tab[data-tab="betroffen"]')
        if tab:
            await tab.click()
            await page.wait_for_timeout(900)
        await page.fill('#bff-ref-input', 'enova')
        await page.wait_for_timeout(1500)
        await page.evaluate("() => { document.querySelector('#bff-ref-results .np-row')?.click(); }")
        await page.wait_for_timeout(900)
        await page.evaluate("""() => {
            const r = document.getElementById('bff-radius');
            if (r) { r.value = '20'; r.dispatchEvent(new Event('input', {bubbles: true})); }
            const on = document.getElementById('bff-radius-on');
            if (on && !on.checked) { on.click(); }
        }""")
        await page.click('#bff-run')
        await page.wait_for_timeout(7000)
        await shot('08_betroffenheit_summary')
        await shot('09_betroffenheit_match_tabelle')

        await browser.close()
        print('FERTIG')

asyncio.run(main())
