# 08 und 09 sind IDENTISCH (gleiche Größe 3068202)! Der Screenshot 09 muss die Match-Tabelle
# zeigen — aber das Panel zeigt eh beides. Trotzdem: 09 = reiner Scroll auf die Tabelle wäre besser.
# Prüfen ob 08 wirklich anders aussieht... gleiche Dateigröße = gleiches Bild (page.screenshot ohne
# Scroll). Der Vision-Check von 08 zeigte Panel mit Tabelle sichtbar (8 von 58 Zeilen).
# Für 09: nach unten scrollen, damit die Tabelle im Fokus ist:
import asyncio
from playwright.async_api import async_playwright

OUT = '/home/claw_01_rasbpi5_1/Projects/pv-wind-map/Artikel/screenshots_v29'

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1600, 'height': 1000}, device_scale_factor=2)
        await page.goto('http://127.0.0.1:8805/index.html?v29shot9=%d' % 9)
        try:
            await page.click('#tc-accept', timeout=5000)
        except Exception:
            pass
        await page.wait_for_function(
            "() => { const ib = document.getElementById('infobar'); return ib && ib.textContent && ib.textContent.length > 12; }",
            timeout=60000)
        await page.wait_for_timeout(3000)
        await page.evaluate("() => { document.getElementById('btn-stats').click(); }")
        await page.wait_for_timeout(1000)
        await page.evaluate("() => { document.querySelector('#stats-tabs .tab[data-tab=\"betroffen\"]').click(); }")
        await page.wait_for_timeout(900)
        await page.fill('#bff-ref-input', 'enova')
        await page.wait_for_timeout(1600)
        await page.evaluate("() => { document.querySelector('#bff-ref-results .np-row')?.click(); }")
        await page.wait_for_timeout(900)
        await page.evaluate("""() => {
            const on = document.getElementById('bff-radius-on');
            if (on && !on.checked) on.click();
            const r = document.getElementById('bff-radius');
            if (r) { r.value = '20'; r.dispatchEvent(new Event('input', {bubbles:true})); }
        }""")
        await page.evaluate("() => { document.getElementById('bff-run').click(); }")
        await page.wait_for_timeout(8000)
        # 08: Panel-Top (Referenz+Optionen+Summary)
        await page.evaluate("() => { const sb = document.getElementById('stats-body'); if (sb) sb.scrollTop = 0; }")
        await page.wait_for_timeout(400)
        await page.screenshot(path=f'{OUT}/08_betroffenheit_summary.png')
        print('✓ 08 neu')
        # 09: zu Ergebnistabelle scrollen
        await page.evaluate("""() => {
            const sum = document.getElementById('bff-summary');
            const sb = document.getElementById('stats-body');
            if (sum && sb) {
                const top = sum.getBoundingClientRect().top - sb.getBoundingClientRect().top + sb.scrollTop;
                sb.scrollTop = top + sum.offsetHeight - 160;
            }
        }""")
        await page.wait_for_timeout(400)
        await page.screenshot(path=f'{OUT}/09_betroffenheit_match_tabelle.png')
        print('✓ 09 neu (gescrollt)')
        await browser.close()

asyncio.run(main())
