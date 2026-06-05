"""
UE5 Console Variables/Commands Reference Scraper
=================================================
Epic Developer Community 문서에서 콘솔 변수/커맨드 목록을 스크래핑해서 JSON으로 덤프합니다.

사전 준비:
    pip install playwright
    playwright install chromium

실행:
    python ue_cvar_scraper.py

출력:
    ue_cvars.json  (콘솔 변수)
    ue_cmds.json   (콘솔 커맨드)
"""

import asyncio
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 설정
# ---------------------------------------------------------------------------

TARGETS = [
    {
        "url": "https://dev.epicgames.com/documentation/ko-kr/unreal-engine/unreal-engine-console-variables-reference",
        "output": "ue_cvars.json",
        "label": "Console Variables",
    },
    {
        "url": "https://dev.epicgames.com/documentation/ko-kr/unreal-engine/unreal-engine-console-commands-reference",
        "output": "ue_cmds.json",
        "label": "Console Commands",
    },
]

# 페이지 JS 렌더링 대기 타임아웃 (ms)
PAGE_TIMEOUT = 60_000
# 콘텐츠 렌더링 대기 (ms) — 느린 환경용
CONTENT_WAIT = 5_000


# ---------------------------------------------------------------------------
# 파서
# ---------------------------------------------------------------------------

def parse_table(rows: list[dict]) -> list[dict]:
    """
    rows: [{"cells": ["Name", "Help", ...]}, ...]
    헤더 행을 키로 사용해서 dict 리스트로 변환합니다.
    """
    if not rows:
        return []

    # 헤더 감지: 첫 행이 컬럼명일 가능성이 높음
    header = rows[0]["cells"]
    # 헤더가 실제 데이터 행인지 확인 (소문자 키워드 포함 여부로 판단)
    header_keywords = {"name", "variable", "command", "help", "description", "설명", "변수", "명령"}
    if any(h.lower() in header_keywords for h in header):
        data_rows = rows[1:]
    else:
        # 헤더 없으면 임의로 name/description 으로 매핑
        header = ["name", "description"]
        data_rows = rows

    results = []
    for row in data_rows:
        cells = row["cells"]
        entry = {}
        for i, key in enumerate(header):
            entry[key] = cells[i] if i < len(cells) else ""
        results.append(entry)
    return results


# ---------------------------------------------------------------------------
# 스크래퍼 (Playwright)
# ---------------------------------------------------------------------------

async def scrape(target: dict) -> list[dict]:
    from playwright.async_api import async_playwright

    url = target["url"]
    label = target["label"]
    print(f"\n[{label}] 페이지 로딩 중...")
    print(f"  URL: {url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            locale="ko-KR",
            extra_http_headers={"Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8"},
        )
        page = await context.new_page()

        # 페이지 이동
        await page.goto(url, timeout=PAGE_TIMEOUT, wait_until="domcontentloaded")

        # 콘텐츠가 동적으로 렌더링될 때까지 대기
        # 테이블 또는 dl/dt 형태 둘 다 기다림
        try:
            await page.wait_for_selector(
                "table, dl, .documentation-content, article",
                timeout=CONTENT_WAIT,
            )
        except Exception:
            print("  [경고] 콘텐츠 셀렉터 타임아웃 — 현재 DOM으로 파싱 시도합니다.")

        # ---------------------------------------------------------------
        # 방법 1: <table> 파싱
        # ---------------------------------------------------------------
        tables = await page.query_selector_all("table")
        all_entries = []

        if tables:
            print(f"  테이블 {len(tables)}개 발견 — 파싱 중...")
            for table in tables:
                rows_el = await table.query_selector_all("tr")
                rows = []
                for row_el in rows_el:
                    cells_el = await row_el.query_selector_all("th, td")
                    cells = [
                        (await c.inner_text()).strip()
                        for c in cells_el
                    ]
                    if any(cells):
                        rows.append({"cells": cells})
                all_entries.extend(parse_table(rows))

        # ---------------------------------------------------------------
        # 방법 2: <dl>/<dt>/<dd> 파싱 (테이블 없을 경우)
        # ---------------------------------------------------------------
        if not all_entries:
            dls = await page.query_selector_all("dl")
            if dls:
                print(f"  <dl> {len(dls)}개 발견 — 파싱 중...")
                for dl in dls:
                    dts = await dl.query_selector_all("dt")
                    dds = await dl.query_selector_all("dd")
                    for dt, dd in zip(dts, dds):
                        name = (await dt.inner_text()).strip()
                        desc = (await dd.inner_text()).strip()
                        if name:
                            all_entries.append({"name": name, "description": desc})

        # ---------------------------------------------------------------
        # 방법 3: 전체 텍스트 덤프 (구조 파악 안 될 때 fallback)
        # ---------------------------------------------------------------
        if not all_entries:
            print("  [경고] 구조 인식 실패 — 전체 텍스트를 raw로 저장합니다.")
            content = await page.inner_text("body")
            all_entries = [{"raw": content}]

        await browser.close()

    print(f"  → {len(all_entries)}개 항목 수집 완료")
    return all_entries


# ---------------------------------------------------------------------------
# 후처리: 키 정규화
# ---------------------------------------------------------------------------

KEY_MAP = {
    # 영문 헤더 변형
    "variable": "name",
    "command": "name",
    "cvar": "name",
    "help": "description",
    "설명": "description",
    "변수": "name",
    "명령": "name",
    "명령어": "name",
}

def normalize_keys(entries: list[dict]) -> list[dict]:
    result = []
    for entry in entries:
        normalized = {}
        for k, v in entry.items():
            key = KEY_MAP.get(k.lower().strip(), k.lower().strip())
            normalized[key] = v
        result.append(normalized)
    return result


# ---------------------------------------------------------------------------
# 메인
# ---------------------------------------------------------------------------

async def main():
    try:
        from playwright.async_api import async_playwright  # noqa: F401
    except ImportError:
        print("Playwright가 설치되어 있지 않습니다.")
        print("다음 명령으로 설치하세요:")
        print("  pip install playwright")
        print("  playwright install chromium")
        sys.exit(1)

    for target in TARGETS:
        try:
            entries = await scrape(target)
            entries = normalize_keys(entries)

            out_path = Path(target["output"])
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(entries, f, ensure_ascii=False, indent=2)

            print(f"  저장 완료: {out_path.resolve()}")
            print(f"  샘플 (첫 3개):")
            for e in entries[:3]:
                print(f"    {json.dumps(e, ensure_ascii=False)}")

        except Exception as e:
            print(f"  [오류] {target['label']}: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
