"""
UE5 Docs 페이지 구조 탐색기
============================
스크래퍼를 만들기 전에 페이지의 DOM 구조를 파악합니다.
실행하면 콘솔에 페이지 구조 요약을 출력하고
page_dump.html / page_text.txt 를 저장합니다.

실행:
    python ue_cvar_inspect.py
"""

import asyncio
from pathlib import Path

URL = "https://dev.epicgames.com/documentation/ko-kr/unreal-engine/unreal-engine-console-variables-reference"
WAIT_MS = 8_000  # JS 렌더링 대기 시간 (느리면 늘리세요)


async def inspect():
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            locale="ko-KR",
            extra_http_headers={"Accept-Language": "ko-KR,ko;q=0.9"},
        )
        page = await context.new_page()

        print(f"페이지 로딩: {URL}")
        await page.goto(URL, wait_until="networkidle", timeout=60_000)
        await page.wait_for_timeout(WAIT_MS)

        # ── DOM 요약 출력 ──────────────────────────────────────────────
        summary = await page.evaluate("""() => {
            const counts = {};
            ['table','tr','th','td','dl','dt','dd','h1','h2','h3','h4','section','article','div[class]'].forEach(sel => {
                try { counts[sel] = document.querySelectorAll(sel).length; } catch(e) {}
            });

            // 첫 번째 테이블 헤더 샘플
            const firstTable = document.querySelector('table');
            const tableHeaders = firstTable
                ? [...firstTable.querySelectorAll('th,td')].slice(0,10).map(e => e.innerText.trim())
                : [];

            // 첫 번째 dl 샘플
            const firstDl = document.querySelector('dl');
            const dlSample = firstDl
                ? [...firstDl.querySelectorAll('dt')].slice(0,5).map(e => e.innerText.trim())
                : [];

            // 주요 class 목록 (data 관련)
            const classes = new Set();
            document.querySelectorAll('[class]').forEach(el => {
                el.className.split(' ').forEach(c => {
                    if (c && (c.includes('row') || c.includes('cell') || c.includes('table') ||
                              c.includes('cvar') || c.includes('var') || c.includes('doc') ||
                              c.includes('content') || c.includes('entry'))) {
                        classes.add(c);
                    }
                });
            });

            return { counts, tableHeaders, dlSample, classes: [...classes].slice(0, 30) };
        }""")

        print("\n=== DOM 요소 개수 ===")
        for k, v in summary["counts"].items():
            if v > 0:
                print(f"  {k}: {v}")

        print("\n=== 첫 테이블 헤더 셀 (최대 10개) ===")
        for h in summary["tableHeaders"]:
            print(f"  {repr(h)}")

        print("\n=== 첫 <dl> dt 샘플 (최대 5개) ===")
        for d in summary["dlSample"]:
            print(f"  {repr(d)}")

        print("\n=== 데이터 관련 CSS 클래스 ===")
        for c in summary["classes"]:
            print(f"  .{c}")

        # ── HTML / 텍스트 저장 ─────────────────────────────────────────
        html = await page.content()
        Path("page_dump.html").write_text(html, encoding="utf-8")
        print("\npage_dump.html 저장 완료 (브라우저로 열어서 구조 확인 가능)")

        text = await page.inner_text("body")
        Path("page_text.txt").write_text(text, encoding="utf-8")
        print("page_text.txt 저장 완료 (텍스트만 추출)")

        # ── 첫 20줄 텍스트 미리보기 ───────────────────────────────────
        lines = [l for l in text.splitlines() if l.strip()]
        print("\n=== 본문 텍스트 첫 30줄 ===")
        for line in lines[:30]:
            print(f"  {line}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(inspect())
