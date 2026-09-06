# Nur noch 08/09 fehlen (Betroffenheit). Der Klick auf #btn-reset-filters scheiterte vermutlich
# beim 07-Nachlauf... nein, 07 existiert. Der Fehler kam NACH 07: clearSearch() → ok, dann
# Tab "betroffen" — oder bereits beim Reset-Klick (der liegt VOR 04!). Moment: 03 endet mit
# btn-reset-filters-Klick — und 04-07 existieren, also lief der durch. Der Hänger ist also
# zwischen 07 und 08. Kandidaten: Tab-Wechsel betroffen, bff-Radius-Checkbox, bff-run.
# Mini-Skript nur für 08/09 mit robusten Klicks (JS-Click statt Playwright-Click):
import asyncio
from playwright.async_api import async_playwright

OUT = '/home/claw_01_rasbpi5_1/Projects/pv-wind-map/Artikel/screenshots_v29'
URL = 'http://127.0.0.1:8805/index.html?v29shot8=%d'

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1600, 'height': 1000}, device_scale_factor=2)
        await page.goto(URL % 8)
        try:
            await page.click('#tc-accept', timeout=5000)
        except Exception:
            pass
        await page.wait_for_function(
            "() => { const ib = document.getElementById('infobar'); return ib && ib.textContent && ib.textContent.length > 12; }",
            timeout=60000)
        await page.wait_for_timeout(3000)
        # Statistik öffnen + Tab Betroffenheit (alles per JS, klick-sicher)
        await page.evaluate("() => { document.getElementById('btn-stats').click(); }")
        await page.wait_for_timeout(1000)
        await page.evaluate("() => { document.querySelector('#stats-tabs .tab[data-tab=\"betroffen\"]').click(); }")
        await page.wait_for_timeout(900)
        await page.fill('#bff-ref-input', 'enova')
        await page.wait_for_timeout(1600)
        await page.evaluate("() => { document.querySelector('#bff-ref-results .np-row')?.click(); }")
        await page.wait_for_timeout(900)
        ok_radius = await page.evaluate("""() => {
            const on = document.getElementById('bff-radius-on');
            if (on && !on.checked) on.click();
            const r = document.getElementById('bff-radius');
            if (r) { r.value = '20'; r.dispatchEvent(new Event('input', {bubbles:true})); r.dispatchEvent(new Event('change', {bubbles:true})); }
            return {checked: on ? on.checked : null, val: r ? r.value : null};
        }""")
        print('radius state:', ok_radius)
        await page.evaluate("() => { document.getElementById('bff-run').click(); }")
        await page.wait_for_timeout(8000)
        await page.screenshot(path=f'{OUT}/08_betroffenheit_summary.png')
        print('✓ 08')
        await page.screenshot(path=f'{OUT}/09_betroffenheit_match_tabelle.png')
        print('✓ 09')
        await browser.close()

asyncio.run(main())
