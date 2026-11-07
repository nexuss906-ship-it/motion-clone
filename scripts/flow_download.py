"""Download the newest N videos from the open Flow project (newest first) through the Flow MCP's Chrome session.
Needed because flow_download_videos looks for a per-tile 'Download' button that Flow moved into the
'More options' menu. This only reads/downloads the user's own clips; it never generates anything.

usage: <flow-mcp venv python> -I flow_download.py <count> <out_dir> [port=9333]
(venv python: ~/.claude/mcp-servers/flow/.venv/Scripts/python.exe - it has playwright)
"""
import asyncio, re, sys
from pathlib import Path
from playwright.async_api import async_playwright

N, OUT = int(sys.argv[1]), Path(sys.argv[2])
PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 9333
OUT.mkdir(parents=True, exist_ok=True)

async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
        page = next(p for c in b.contexts for p in c.pages if "flow.google.com/project" in p.url)
        vids = page.locator("video")
        print("videos on page:", await vids.count())
        for i in range(N):
            await page.keyboard.press("Escape")
            v = vids.nth(i)
            await v.scroll_into_view_if_needed(); await v.hover(); await page.wait_for_timeout(700)
            tile = v.locator("xpath=ancestor::*[.//button[@aria-label='More options']][1]")
            await tile.get_by_role("button", name="More options").first.click(); await page.wait_for_timeout(600)
            await page.get_by_role("menuitem", name=re.compile("Download")).first.click(); await page.wait_for_timeout(600)
            async with page.expect_download(timeout=180000) as d:
                await page.get_by_role("menuitem", name=re.compile("720p|Original", re.I)).first.click()
            dest = OUT / f"newest_{i + 1}.mp4"
            await (await d.value).save_as(str(dest))
            print(dest, dest.stat().st_size)
            await page.wait_for_timeout(1500)  # human pace
        await page.keyboard.press("Escape")

asyncio.run(main())
