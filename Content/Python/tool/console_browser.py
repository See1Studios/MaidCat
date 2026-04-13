"""
ConsoleBrowser — TAPython Chameleon 툴
========================================

언리얼 엔진의 CVar(콘솔 변수)와 CCmds(콘솔 커맨드)를 탭별로 검색·관리하는 툴.
console_cat 을 대체하며, console_cat 에 대한 의존성은 없음.

## 탭 구성
- CVar  : DumpCVars.csv 로드. 2열 리스트(Name / Help). 선택 시 상세 정보 표시.
- CCmds : DumpCCmds.csv 로드. 2열 리스트(Name / Help).
- Favs  : 즐겨찾기. 4열 리스트(Name / 값 / Memo / Help). 목록 다중 관리.

## CSV 로드 흐름
1. init() 호출 시 CSV 존재 여부 확인
2. 없으면 자동으로 rebuild() 호출 (DumpCVars / DumpCCmds 콘솔 커맨드 실행)
3. 이후 [🔨 Rebuild] 버튼으로 수동 갱신 가능

## 즐겨찾기 데이터 구조
- _favs_db: dict[(tier, name), list[entry]]
  - tier: "shared" | "local"
  - entry: {"name", "value", "set_by", "help", "memo", "custom_values": [str, ...]}
- 저장 위치
  - shared : MaidCat/Content/Python/data/console_browser_favorites.json  (git 관리)
  - local  : {ProjectSaved}/Logs/ConsoleBrowser/favorites.json

## 번역 시스템
- _trans_cache: dict[name, translated_help]  (영→한 번역 결과)
- 저장 위치 (우선순위 순)
  1. MaidCat/Content/Python/data/console_browser_translations.json  (git 관리, 팀 공유)
  2. {ProjectSaved}/Logs/ConsoleBrowser/console_browser_translations.json  (폴백)
- Perforce 환경이면 공유 파일 수정 전 자동 p4 edit
- 번역 엔진: Claude API (ANTHROPIC_API_KEY 환경변수) / Google Translate 공개 API
- [🌐] 토글로 원문↔번역 전환, [🔄] 로 파일 새로고침, [📝] 로 파일 직접 편집

## UI ↔ Python 콜백 매핑 (console_browser.json → console_browser.py)
- 탭 전환       : on_tab_cvars / on_tab_ccmds / on_tab_favs
- 검색          : on_search_changed(text)
- 리스트 선택   : on_cvar_selection_changed / on_ccmds_selection_changed / on_favs_selection_changed
- 즐겨찾기 목록 : on_fav_list_changed(display_name) / add_fav_list / delete_fav_list
- 즐겨찾기 항목 : add_to_favs / remove_from_favs / on_fav_double_click(idx)
- 메모          : save_memo (버튼) / on_memo_committed (Enter)
- 커스텀 값     : on_custom_value_committed(text) / add_custom_value / exec_fav_value(val_idx) / delete_fav_value(val_idx)
- 번역          : on_toggle_trans / on_engine_changed(engine) / translate_detail / cancel_translate / reload_trans_cache / open_trans_file
- 기타          : rebuild / export_favs

## 설정 영속성
- {ProjectSaved}/Logs/ConsoleBrowser/settings.json
- 저장 항목: show_translation (bool), translation_engine (str)

## 주요 내부 메서드
- _reload_all()        : CSV 재로드 + 필터 + 리스트 갱신
- _filter_all(query)   : 세 탭 동시 필터링, 즐겨찾기 선택은 이름 기준 보존
- _refresh_all_lists() : ChameleonData API로 리스트 위젯 갱신
- _show_detail(...)    : 상세 텍스트 박스 갱신 (번역 모드 반영)
- _favs_refreshing     : 리스트 갱신 중 spurious selection 콜백 억제 플래그
"""

import ctypes
import csv
import datetime
import json
import os
import shutil
import subprocess
import threading
import time
import tkinter as tk
import tkinter.filedialog as filedialog
import urllib.parse
import urllib.request
import unreal
from pathlib import Path

_VK_RETURN = 0x0D

def _is_enter_pressed() -> bool:
    """OnTextCommitted 콜백 시점에 Enter 키가 실제로 눌린 경우인지 확인"""
    return bool(ctypes.windll.user32.GetAsyncKeyState(_VK_RETURN) & 0x8001)

# ── Widget aka names ──────────────────────────────────────────────────────────
AKA_STATUS          = "StatusText"
AKA_SEARCH          = "SearchInput"
AKA_TAB_CVARS       = "TabCVars"
AKA_TAB_CCMDS       = "TabCCmds"
AKA_TAB_FAVS        = "TabFavs"
AKA_LIST_CVARS      = "ListCVars"
AKA_LIST_CCMDS      = "ListCCmds"
AKA_LIST_FAVS       = "ListFavs"
AKA_DETAIL          = "DetailText"
AKA_CUSTOM_VALUE    = "CustomValueInput"
AKA_VALUES_PANEL    = "ValuesPanel"
AKA_MEMO_INPUT      = "MemoInput"
AKA_MEMO_ROW        = "MemoRow"
AKA_FAVS_TOOLS      = "FavsTools"
AKA_ENGINE_SELECTOR = "EngineSelector"
AKA_FAVS_SELECTOR   = "FavsSelector"
AKA_FAVS_NEW_NAME   = "FavsNewName"
AKA_TOGGLE_TRANS    = "ToggleTrans"
AKA_PROGRESS_ROW    = "ProgressRow"
AKA_PROGRESS_BAR    = "ProgressBar"
AKA_PROGRESS_LABEL  = "ProgressLabel"
AKA_NEW_FAV_SHARED  = "NewFavShared"
AKA_BTN_ADD_FAV     = "BtnAddFav"
AKA_BTN_REM_FAV     = "BtnRemFav"

# ── 상수 ──────────────────────────────────────────────────────────────────────
CSV_CVARS        = "DumpCVars.csv"
CSV_CCMDS        = "DumpCCmds.csv"
FAVS_LOCAL_FILE  = "favorites.json"
FAVS_SHARED_FILE = "console_browser_favorites.json"
TRANS_CACHE_FILE = "console_browser_translations.json"
SETTINGS_FILE    = "settings.json"
DEFAULT_LIST     = "Default"

# ── 데이터 폴더 ───────────────────────────────────────────────────────────────

def _data_dir() -> Path:
    """플러그인 데이터 폴더 — git 관리, 배포 포함 (tool/ 상위의 Python/data/)"""
    return Path(__file__).parent.parent / "data"


# ── Perforce 연동 ─────────────────────────────────────────────────────────────

def _p4_read_settings() -> dict | None:
    """SourceControlSettings.ini 에서 Perforce 접속 정보 읽기"""
    ini_path = (
        Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()))
        / "Config" / "WindowsEditor" / "SourceControlSettings.ini"
    )
    if not ini_path.exists():
        return None
    settings: dict[str, str] = {}
    section = None
    for line in ini_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("["):
            section = line[1:line.find("]")]
        elif "=" in line:
            key, _, value = line.partition("=")
            if section == "PerforceSourceControl.PerforceSourceControlSettings":
                settings[key.strip()] = value.strip()
            elif section == "SourceControl.SourceControlSettings" and key.strip() == "Provider":
                settings["Provider"] = value.strip()
    return settings or None


def _p4_run(cmd: list[str], settings: dict, timeout: int = 3) -> subprocess.CompletedProcess:
    env = {**os.environ}
    if "Port"      in settings: env["P4PORT"]  = settings["Port"]
    if "UserName"  in settings: env["P4USER"]  = settings["UserName"]
    if "Workspace" in settings: env["P4CLIENT"] = settings["Workspace"]
    return subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=timeout)


def _p4_ensure_writable(path: Path) -> bool:
    """파일이 쓰기 가능한지 확인하고, Perforce 관리 중이면 자동 체크아웃.
    이미 쓰기 가능하거나 파일이 없으면 True 반환 (신규 생성 허용).
    """
    if not path.exists() or os.access(str(path), os.W_OK):
        return True
    settings = _p4_read_settings()
    if not settings or settings.get("Provider") != "Perforce":
        return False
    try:
        if _p4_run(["p4", "fstat", str(path)], settings).returncode != 0:
            return False  # Perforce 관리 파일 아님
        result = _p4_run(["p4", "edit", str(path)], settings)
        if result.returncode == 0:
            unreal.log(f"ConsoleBrowser: Perforce 체크아웃 완료 — {path.name}")
            return True
        unreal.log_warning(f"ConsoleBrowser: Perforce 체크아웃 실패 — {result.stderr.strip()}")
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        unreal.log_warning(f"ConsoleBrowser: p4 명령 실패 — {e}")
    return False


# ── 번역 엔진 ─────────────────────────────────────────────────────────────────

_CLAUDE_PATH: str | None = None  # None = 미확인, 첫 호출 시 1회 탐색

# ── 번역 큐 / 진행 상태 ───────────────────────────────────────────────────────
# 백그라운드 스레드는 _signal_queue에 데이터 튜플만 넣고,
# 메인 스레드의 slate_pre_tick 콜백이 큐를 소진하며 UI를 갱신한다.
import queue as _queue
_signal_queue: _queue.SimpleQueue = _queue.SimpleQueue()
_cancel_flag  = threading.Event()
_tick_handle  = None


def _get_claude_path() -> str | None:
    global _CLAUDE_PATH
    if _CLAUDE_PATH is None:
        found = shutil.which("claude")
        _CLAUDE_PATH = found or ""
        unreal.log(f"ConsoleBrowser: claude 경로 → {_CLAUDE_PATH!r}")
    return _CLAUDE_PATH or None


def _translate_with_claude(text: str) -> str | None:
    claude = _get_claude_path()
    if not claude:
        return None
    try:
        prompt = (
            "Translate the following Unreal Engine console variable description "
            "from English to Korean. Output only the Korean translation, no explanations:\n\n"
            + text
        )
        r = subprocess.run(
            [claude, "-p", prompt],
            capture_output=True, text=True, encoding="utf-8", timeout=60,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        if r.returncode == 0:
            result = r.stdout.strip()
            if result:
                return result
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError, Exception) as e:
        unreal.log_warning(f"ConsoleBrowser: claude 번역 실패 → {e}")
    return None


def _translate_text_google(text: str) -> str | None:
    """Google Translate 공개 API로 영→한 번역"""
    if not text or text.isspace():
        return ""
    try:
        url = (
            "https://translate.googleapis.com/translate_a/single"
            f"?client=gtx&sl=en&tl=ko&dt=t&q={urllib.parse.quote(text)}"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp:
            if resp.status != 200:
                return None
            result = json.loads(resp.read().decode("utf-8"))
            return "".join(seg[0] for seg in result[0] if seg[0]) or None
    except Exception as e:
        unreal.log_error(f"ConsoleBrowser: Google 번역 오류: {e}")
        return None


def _translate_text(text: str, engine_pref: str = "Auto") -> tuple[str | None, str]:
    """번역 엔진 선택에 따라 번역.
    engine_pref: "Auto" | "Claude" | "Google"
    Returns: (번역문 또는 None, 사용된 엔진 이름)
    """
    if engine_pref == "Claude":
        result = _translate_with_claude(text)
        return (result, "Claude") if result else (None, "Claude")
    if engine_pref == "Google":
        return _translate_text_google(text), "Google"
    # Auto: Claude 우선, 실패 시 Google
    result = _translate_with_claude(text)
    if result:
        return result, "Claude"
    return _translate_text_google(text), "Google"

_INVALID_FILENAME_CHARS = str.maketrans({c: "_" for c in r'<>:"/\|?* '})


def _safe_filename(name: str) -> str:
    safe = name.translate(_INVALID_FILENAME_CHARS).strip("_")
    return safe[:200]


class ConsoleBrowser:

    def __init__(self, json_path: str) -> None:
        self.json_path = json_path
        self.data: unreal.ChameleonData = unreal.PythonBPLib.get_chameleon_data(json_path)
        self._cvar_entries:   list[dict] = []
        self._ccmds_entries:  list[dict] = []
        self._cvar_filtered:  list[dict] = []
        self._ccmds_filtered: list[dict] = []
        self._favs_filtered:  list[dict] = []
        self._active_tab      = "CVar"
        self._last_query      = ""
        self._cvar_sel:  set[int] = set()
        self._ccmds_sel: set[int] = set()
        self._favs_sel:  set[int] = set()
        self._switching_tab = False
        self._cv_last_exec_time = 0.0
        self._values_panel_count = 0
        # 즐겨찾기 다중 목록: {(tier, name): [entries]}  tier = "shared" | "local"
        self._favs_db:        dict[tuple[str, str], list] = {}
        self._active_fav_list: tuple[str, str] = ("local", DEFAULT_LIST)
        # 번역 캐시: {name: translated_help}
        self._trans_cache:    dict[str, str] = {}
        self._settings:       dict           = {}
        self._favs_refreshing = False   # 리프레시 중 selection 콜백 무시용

    # _favs → 현재 활성 목록의 뷰
    @property
    def _favs(self) -> list:
        return self._favs_db.setdefault(self._active_fav_list, [])

    @_favs.setter
    def _favs(self, value: list) -> None:
        self._favs_db[self._active_fav_list] = value

    # ── 초기화 ───────────────────────────────────────────────────────────────

    def init(self) -> None:
        self._load_settings()
        self._load_favs()
        self._load_trans_cache()
        cvars_missing = not Path(self._logs_path(CSV_CVARS)).exists()
        ccmds_missing = not Path(self._logs_path(CSV_CCMDS)).exists()
        if cvars_missing or ccmds_missing:
            self.rebuild()
        else:
            self._reload_all()
        self._show_tab("CVar")
        self._apply_settings()

    # ── Rebuild ──────────────────────────────────────────────────────────────

    def rebuild(self) -> None:
        """CVars/CCmds CSV 강제 재생성 후 로드"""
        self._set_status("재생성 중...")
        world = unreal.EditorLevelLibrary.get_editor_world()
        unreal.SystemLibrary.execute_console_command(
            world, f'DumpCVars -showhelp -csv="{self._logs_path(CSV_CVARS)}"'
        )
        unreal.SystemLibrary.execute_console_command(
            world, f'DumpCCmds -showhelp -csv="{self._logs_path(CSV_CCMDS)}"'
        )
        self._reload_all()

    # ── 탭 전환 ──────────────────────────────────────────────────────────────

    def on_tab_cvars(self) -> None:
        if not self._switching_tab:
            self._show_tab("CVar")

    def on_tab_ccmds(self) -> None:
        if not self._switching_tab:
            self._show_tab("CCmds")

    def on_tab_favs(self) -> None:
        if not self._switching_tab:
            self._show_tab("Favs")

    # ── 검색 ─────────────────────────────────────────────────────────────────

    def on_search_changed(self, text: str) -> None:
        self._last_query = text.strip()
        self._filter_all(self._last_query)
        self._refresh_all_lists()

    # ── 선택 콜백 (OnSelectionChanged — 인자 없음) ────────────────────────────

    def on_cvar_selection_changed(self) -> None:
        self._cvar_sel = set(self.data.get_list_view_multi_column_selection(AKA_LIST_CVARS))
        if len(self._cvar_sel) == 1:
            self._show_detail(self._cvar_filtered, next(iter(self._cvar_sel)))

    def on_ccmds_selection_changed(self) -> None:
        self._ccmds_sel = set(self.data.get_list_view_multi_column_selection(AKA_LIST_CCMDS))
        if len(self._ccmds_sel) == 1:
            self._show_detail(self._ccmds_filtered, next(iter(self._ccmds_sel)))

    def on_favs_selection_changed(self) -> None:
        if self._favs_refreshing:
            self._favs_refreshing = False  # 한 번만 무시 후 해제
            return
        self._favs_sel = set(self.data.get_list_view_multi_column_selection(AKA_LIST_FAVS))
        if len(self._favs_sel) != 1:
            self._refresh_values_panel()
            return
        idx = next(iter(self._favs_sel))
        if not (0 <= idx < len(self._favs_filtered)):
            self._refresh_values_panel()
            return
        self._show_detail(self._favs_filtered, idx)
        entry = self._favs_filtered[idx]
        self.data.set_text(AKA_CUSTOM_VALUE, "")
        self.data.set_text(AKA_MEMO_INPUT, entry.get("memo", ""))
        self._refresh_values_panel()

    # ── 즐겨찾기 목록 관리 ───────────────────────────────────────────────────

    def on_fav_list_changed(self, display_name: str) -> None:
        """콤보박스 목록 선택"""
        if display_name.startswith("[공유] "):
            key: tuple[str, str] = ("shared", display_name[len("[공유] "):])
        else:
            key = ("local", display_name)
        if key not in self._favs_db:
            return
        self._active_fav_list = key
        self._favs_sel.clear()
        self._filter_all(self._last_query)
        self._refresh_all_lists()

    def add_fav_list(self) -> None:
        """새 즐겨찾기 목록 추가"""
        name = self.data.get_text(AKA_FAVS_NEW_NAME).strip()
        if not name:
            self._set_status("새 목록 이름을 입력하세요")
            return
        is_shared = self.data.get_is_checked(AKA_NEW_FAV_SHARED)
        key: tuple[str, str] = ("shared" if is_shared else "local", name)
        if key in self._favs_db:
            tier_label = "공유" if is_shared else "로컬"
            self._set_status(f"이미 존재하는 목록: {name} ({tier_label})")
            return
        self._favs_db[key] = []
        self._active_fav_list = key
        self._save_favs()
        self.data.set_text(AKA_FAVS_NEW_NAME, "")
        self._update_fav_selector()
        self._filter_all(self._last_query)
        self._refresh_all_lists()
        tier = "공유" if is_shared else "로컬"
        self._set_status(f"목록 추가: {name} ({tier})")

    def delete_fav_list(self) -> None:
        """현재 즐겨찾기 목록 삭제 (Default는 삭제 불가)"""
        if self._active_fav_list[1] == DEFAULT_LIST:
            self._set_status("기본 목록은 삭제할 수 없습니다")
            return
        count = len(self._favs)
        confirmed = unreal.PythonBPLib.confirm_dialog(
            f'"{self._active_fav_list[1]}" 목록을 삭제하시겠습니까?\n({count:,}개 항목이 모두 제거됩니다)',
            "목록 삭제 확인",
        )
        if not confirmed:
            return
        removed = self._active_fav_list
        del self._favs_db[removed]
        self._active_fav_list = next(
            (k for k in self._favs_db if k != removed),
            ("local", DEFAULT_LIST)
        )
        self._save_favs()
        self._update_fav_selector()
        self._favs_sel.clear()
        self._filter_all(self._last_query)
        self._refresh_all_lists()
        self._set_status(f"목록 삭제: {removed[1]}")

    # ── 즐겨찾기 항목 조작 ───────────────────────────────────────────────────

    def add_to_favs(self) -> None:
        if self._active_tab == "CVar":
            sel, entries = self._cvar_sel, self._cvar_filtered
        elif self._active_tab == "CCmds":
            sel, entries = self._ccmds_sel, self._ccmds_filtered
        else:
            self._set_status("Variables 또는 Commands 탭에서 항목을 선택하세요")
            return

        if not sel:
            self._set_status("추가할 항목을 선택하세요")
            return

        existing = {f["name"] for f in self._favs}
        to_add = [entries[i] for i in sorted(sel)
                  if i < len(entries) and entries[i]["name"] not in existing]
        skipped = len(sel) - len(to_add)

        if not to_add:
            self._set_status("선택한 항목이 이미 모두 즐겨찾기에 있습니다")
            return

        for e in to_add:
            self._favs.append({**e, "custom_values": [], "memo": ""})
        sel.clear()
        self._save_favs()
        self._filter_all(self._last_query)
        self._refresh_all_lists()
        msg = f"[{self._active_fav_list[1]}] 추가: {len(to_add)}개  (총 {len(self._favs):,}개)"
        if skipped:
            msg += f"  ({skipped}개 중복)"
        self._set_status(msg)

    def remove_from_favs(self) -> None:
        if not self._favs_sel:
            self._set_status("제거할 항목을 선택하세요")
            return
        names = {self._favs_filtered[i]["name"]
                 for i in self._favs_sel if i < len(self._favs_filtered)}
        if not names:
            return
        count = len(names)
        self._favs = [f for f in self._favs if f["name"] not in names]
        self._favs_sel.clear()
        self._save_favs()
        self._filter_all(self._last_query)
        self._refresh_all_lists()
        self._set_status(f"제거: {count}개  (총 {len(self._favs):,}개)")

    def save_memo(self) -> None:
        """저장 버튼 클릭으로 메모 저장"""
        self._do_save_memo()

    def on_memo_committed(self) -> None:
        """Enter 키로 메모 저장"""
        if _is_enter_pressed():
            self._do_save_memo()

    def _do_save_memo(self) -> None:
        if len(self._favs_sel) != 1:
            self._set_status("메모를 저장할 항목을 하나 선택하세요")
            return
        idx = next(iter(self._favs_sel))
        if not (0 <= idx < len(self._favs_filtered)):
            return
        target_name = self._favs_filtered[idx]["name"]
        memo = self.data.get_text(AKA_MEMO_INPUT)
        for f in self._favs:
            if f["name"] == target_name:
                f["memo"] = memo
                break
        self._save_favs()
        self._filter_all(self._last_query)
        self._favs_sel = {i for i, e in enumerate(self._favs_filtered) if e["name"] == target_name}
        self._refresh_all_lists()
        self._set_status(f"메모 저장: {target_name}")

    def on_custom_value_committed(self, text: str) -> None:
        """값 필드 Enter — 탐색 실행 (저장하지 않음, 포커스 이탈 무시)"""
        if not _is_enter_pressed():
            return
        now = time.time()
        if now - self._cv_last_exec_time < 0.3:
            return
        self._cv_last_exec_time = now
        if len(self._favs_sel) != 1:
            return
        idx = next(iter(self._favs_sel))
        if not (0 <= idx < len(self._favs_filtered)):
            return
        entry = self._favs_filtered[idx]
        exec_value = text.strip() or entry.get("value", "").strip()
        cmd = f"{entry['name']} {exec_value}".strip() if exec_value else entry["name"]
        world = unreal.EditorLevelLibrary.get_editor_world()
        unreal.SystemLibrary.execute_console_command(world, cmd)
        self._set_status(f"▶ 탐색: {cmd}")
        self._rebuild_if_auto(entry)

    def add_custom_value(self) -> None:
        """값 배열에 새 값 추가"""
        new_val = self.data.get_text(AKA_CUSTOM_VALUE).strip()
        if not new_val:
            self._set_status("추가할 값을 입력하세요")
            return
        if len(self._favs_sel) != 1:
            self._set_status("항목을 선택하세요")
            return
        idx = next(iter(self._favs_sel))
        if not (0 <= idx < len(self._favs_filtered)):
            return
        entry = self._favs_filtered[idx]
        values: list = entry.setdefault("custom_values", [])
        if new_val in values:
            self._set_status(f"이미 등록된 값: {new_val}")
            return
        values.append(new_val)
        target_name = entry["name"]
        self._save_favs()
        self.data.set_text(AKA_CUSTOM_VALUE, "")
        self._filter_all(self._last_query)
        self._favs_sel = {i for i, e in enumerate(self._favs_filtered) if e["name"] == target_name}
        self._refresh_all_lists()
        self._set_status(f"값 추가: {new_val}")

    def exec_fav_value(self, val_idx: int) -> None:
        """값 버튼 클릭 — 해당 값으로 명령 실행"""
        if len(self._favs_sel) != 1:
            return
        idx = next(iter(self._favs_sel))
        if not (0 <= idx < len(self._favs_filtered)):
            return
        entry = self._favs_filtered[idx]
        values = entry.get("custom_values", [])
        if not (0 <= val_idx < len(values)):
            return
        val = values[val_idx]
        cmd = f"{entry['name']} {val}".strip() if val else entry["name"]
        world = unreal.EditorLevelLibrary.get_editor_world()
        unreal.SystemLibrary.execute_console_command(world, cmd)
        self._set_status(f"▶ 실행: {cmd}")

    def delete_fav_value(self, val_idx: int) -> None:
        """값 배열에서 항목 제거"""
        if len(self._favs_sel) != 1:
            return
        idx = next(iter(self._favs_sel))
        if not (0 <= idx < len(self._favs_filtered)):
            return
        entry = self._favs_filtered[idx]
        values = entry.get("custom_values", [])
        if not (0 <= val_idx < len(values)):
            return
        removed = values.pop(val_idx)
        target_name = entry["name"]
        self._save_favs()
        self._filter_all(self._last_query)
        self._favs_sel = {i for i, e in enumerate(self._favs_filtered) if e["name"] == target_name}
        self._refresh_all_lists()
        self._set_status(f"값 삭제: {removed}")

    def on_fav_double_click(self, idx: int) -> None:
        """더블클릭 — custom_value(없으면 원래 value)와 함께 명령 실행"""
        if not (0 <= idx < len(self._favs_filtered)):
            return
        entry = self._favs_filtered[idx]
        values = entry.get("custom_values", [])
        exec_value = values[0] if values else entry.get("value", "").strip()
        cmd = f"{entry['name']} {exec_value}".strip() if exec_value else entry["name"]
        world = unreal.EditorLevelLibrary.get_editor_world()
        unreal.SystemLibrary.execute_console_command(world, cmd)
        self._set_status(f"▶ 실행: {cmd}")
        self._rebuild_if_auto(entry)

    # ── 내보내기 / DB 분할 ───────────────────────────────────────────────────

    def export_favs(self) -> None:
        """현재 즐겨찾기 목록 전체를 CSV로 내보내기"""
        entries = self._favs  # 검색 필터 무관, 목록 전체
        if not entries:
            self._set_status("내보낼 즐겨찾기 항목이 없습니다")
            return
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"Favs_{_safe_filename(self._active_fav_list[1])}_{timestamp}.csv"
        default_dir = self._saved_dir() / "Logs" / "ConsoleBrowser"
        default_dir.mkdir(parents=True, exist_ok=True)

        root = tk.Tk()
        root.withdraw()
        root.wm_attributes("-topmost", True)
        chosen = filedialog.asksaveasfilename(
            parent=root,
            title="즐겨찾기 내보내기",
            initialdir=str(default_dir),
            initialfile=default_name,
            defaultextension=".csv",
            filetypes=[("CSV 파일", "*.csv"), ("모든 파일", "*.*")],
        )
        root.destroy()
        if not chosen:
            return

        out_path = Path(chosen)
        fieldnames = ["name", "value", "set_by", "help", "memo"]
        with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(entries)
        self._set_status(f"내보내기 완료: {out_path.name}  ({len(entries):,}개)")
        unreal.log(f"✅ ConsoleBrowser 즐겨찾기 내보내기: {out_path}")

    # ── 내부 헬퍼 ────────────────────────────────────────────────────────────

    def _rebuild_if_auto(self, entry: dict) -> None:
        if entry.get("type") == "CVar":
            self.rebuild()

    def _refresh_values_panel(self) -> None:
        """ValuesPanel의 버튼 쌍을 현재 선택 항목의 custom_values 기준으로 재생성"""
        for i in range(self._values_panel_count - 1, -1, -1):
            self.data.remove_widget_at(AKA_VALUES_PANEL, i)
        self._values_panel_count = 0

        if len(self._favs_sel) != 1:
            return
        idx = next(iter(self._favs_sel))
        if not (0 <= idx < len(self._favs_filtered)):
            return

        values = self._favs_filtered[idx].get("custom_values", [])
        for i, val in enumerate(values):
            label = val[:10] + "…" if len(val) > 10 else val
            slot = {
                "AutoWidth": True,
                "VAlign": "Center",
                "Padding": [0, 0, 4, 0],
                "SHorizontalBox": {
                    "Slots": [
                        {
                            "AutoWidth": True,
                            "SButton": {
                                "Text": label,
                                "ContentPadding": [6, 2],
                                "ToolTipText": val,
                                "OnClick": f"console_browser.exec_fav_value({i})",
                            },
                        },
                        {
                            "AutoWidth": True,
                            "SButton": {
                                "Text": "✕",
                                "ContentPadding": [1, 2],
                                "OnClick": f"console_browser.delete_fav_value({i})",
                            },
                        },
                    ]
                },
            }
            self.data.append_slot_from_json(AKA_VALUES_PANEL, json.dumps(slot))
        self._values_panel_count = len(values)

    def _show_detail(self, entries: list, index: int) -> None:
        if not (0 <= index < len(entries)):
            return
        e = entries[index]
        show_trans = self.data.get_is_checked(AKA_TOGGLE_TRANS)
        cached = self._trans_cache.get(e["name"])
        if show_trans:
            help_text = cached if cached else "(번역 없음 — 🔄 로 번역 파일 새로고침)"
        else:
            help_text = e["help"]
        lines = [
            f"[{e.get('type', '?')}]  {e['name']}",
            f"Value:  {e.get('value', '')}",
            f"Set By: {e.get('set_by', '')}",
            f"\nHelp:\n{help_text}",
        ]
        if e.get("custom_values"):
            lines.append(f"\n실행 값: {', '.join(e['custom_values'])}")
        if e.get("memo"):
            lines.append(f"\nMemo:\n{e['memo']}")
        self.data.set_text(AKA_DETAIL, "\n".join(lines))

    def _saved_dir(self) -> Path:
        return Path(unreal.Paths.convert_relative_path_to_full(
            unreal.Paths.project_saved_dir()
        ))

    def _logs_path(self, filename: str) -> str:
        return str(self._saved_dir() / "Logs" / filename)

    def _load_favs(self) -> None:
        self._favs_db = {}

        def _load_file(path: Path, tier: str) -> None:
            if not path.exists():
                return
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
                data = {DEFAULT_LIST: raw} if isinstance(raw, list) else raw
                for name, entries in data.items():
                    self._favs_db[(tier, name)] = entries
            except Exception as e:
                unreal.log_warning(f"ConsoleBrowser: 즐겨찾기 로드 오류 ({tier}): {e}")

        _load_file(_data_dir() / FAVS_SHARED_FILE, "shared")
        _load_file(self._saved_dir() / "Logs" / "ConsoleBrowser" / FAVS_LOCAL_FILE, "local")

        if not self._favs_db:
            self._favs_db = {("local", DEFAULT_LIST): []}

        # custom_value(str) → custom_values(list) 마이그레이션
        for entries in self._favs_db.values():
            for item in entries:
                if "custom_value" in item:
                    cv = item.pop("custom_value")
                    item.setdefault("custom_values", [cv] if cv else [])
                else:
                    item.setdefault("custom_values", [])

        self._active_fav_list = next(iter(self._favs_db))

    def _save_favs(self) -> None:
        shared = {name: e for (tier, name), e in self._favs_db.items() if tier == "shared"}
        local  = {name: e for (tier, name), e in self._favs_db.items() if tier == "local"}

        if shared:
            path = _data_dir() / FAVS_SHARED_FILE
            path.parent.mkdir(parents=True, exist_ok=True)
            _p4_ensure_writable(path)
            try:
                path.write_text(json.dumps(shared, ensure_ascii=False, indent=2), encoding="utf-8")
            except OSError as e:
                unreal.log_warning(f"ConsoleBrowser: 공유 즐겨찾기 저장 실패: {e}")

        path = self._saved_dir() / "Logs" / "ConsoleBrowser" / FAVS_LOCAL_FILE
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(local, ensure_ascii=False, indent=2), encoding="utf-8")

    def _plugin_trans_path(self) -> Path:
        """플러그인 배포 번역 파일 경로 (git 관리, 팀 공유용)"""
        return _data_dir() / TRANS_CACHE_FILE

    def _fallback_trans_path(self) -> Path:
        """플러그인 디렉터리 쓰기 불가 시 폴백 (프로젝트 Saved/)"""
        return self._saved_dir() / "Logs" / "ConsoleBrowser" / TRANS_CACHE_FILE

    def _settings_path(self) -> Path:
        return self._saved_dir() / "Logs" / "ConsoleBrowser" / SETTINGS_FILE

    def _load_settings(self) -> None:
        path = self._settings_path()
        try:
            self._settings = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        except Exception as e:
            unreal.log_warning(f"ConsoleBrowser: 설정 로드 오류: {e}")
            self._settings = {}

    def _save_settings(self) -> None:
        path = self._settings_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self._settings, ensure_ascii=False, indent=2), encoding="utf-8")

    def _apply_settings(self) -> None:
        """로드된 설정을 UI에 반영"""
        if "show_translation" in self._settings:
            self.data.set_is_checked(AKA_TOGGLE_TRANS, self._settings["show_translation"])
        if "translation_engine" in self._settings:
            engine = self._settings["translation_engine"]
            engines = ["Auto", "Claude", "Google"]
            if engine in engines:
                engines.remove(engine)
                engines.insert(0, engine)
            self.data.set_combo_box_items(AKA_ENGINE_SELECTOR, engines)
        self._refresh_all_lists()

    def on_engine_changed(self, engine: str) -> None:
        """번역 엔진 변경 시 설정 저장"""
        self._settings["translation_engine"] = engine
        self._save_settings()

    def _load_trans_cache(self) -> None:
        plugin_path = self._plugin_trans_path()
        # 구버전 경로 자동 마이그레이션 (Saved/translations.json 또는 tool/ 경유)
        old_paths = [
            Path(__file__).parent / TRANS_CACHE_FILE,                          # tool/ (이전 위치)
            self._saved_dir() / "Logs" / "ConsoleBrowser" / "translations.json",  # 최초 위치
        ]
        old_path = next((p for p in old_paths if p.exists()), None)
        if not plugin_path.exists() and old_path and old_path.exists():
            try:
                plugin_path.write_text(old_path.read_text(encoding="utf-8"), encoding="utf-8")
                old_path.unlink()
                unreal.log(f"ConsoleBrowser: 번역 캐시 마이그레이션 완료 → {plugin_path}")
            except OSError:
                pass
        for path in (plugin_path, self._fallback_trans_path()):
            if path.exists():
                try:
                    self._trans_cache = json.loads(path.read_text(encoding="utf-8"))
                    return
                except Exception as e:
                    unreal.log_warning(f"ConsoleBrowser: 번역 캐시 로드 오류: {e}")
        self._trans_cache = {}

    def _save_trans_cache(self) -> None:
        path = self._plugin_trans_path()
        _p4_ensure_writable(path)
        try:
            path.write_text(json.dumps(self._trans_cache, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError:
            path = self._fallback_trans_path()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(self._trans_cache, ensure_ascii=False, indent=2), encoding="utf-8")
            unreal.log_warning(f"ConsoleBrowser: 플러그인 디렉터리 쓰기 불가, 폴백 사용: {path}")

    def _update_fav_selector(self) -> None:
        """콤보박스 항목 갱신 — 활성 목록을 맨 앞에, 공유 목록은 [공유] 접두사"""
        def _display(key: tuple[str, str]) -> str:
            tier, name = key
            return f"[공유] {name}" if tier == "shared" else name

        keys = list(self._favs_db.keys())
        if self._active_fav_list in keys:
            keys.remove(self._active_fav_list)
            keys.insert(0, self._active_fav_list)
        self.data.set_combo_box_items(AKA_FAVS_SELECTOR, [_display(k) for k in keys])

    # 탭별 버튼 배경색 (활성, 비활성)  — SButton.set_button_color_and_opacity 전용
    _TAB_BTN_COLORS = {
        AKA_TAB_CVARS: (unreal.LinearColor(0.05, 0.40, 1.00, 1.0), unreal.LinearColor(0.15, 0.15, 0.15, 1.0)),  # Blue
        AKA_TAB_CCMDS: (unreal.LinearColor(0.05, 0.70, 0.25, 1.0), unreal.LinearColor(0.15, 0.15, 0.15, 1.0)),  # Green
        AKA_TAB_FAVS:  (unreal.LinearColor(0.85, 0.10, 0.10, 1.0), unreal.LinearColor(0.15, 0.15, 0.15, 1.0)),  # Red
    }
    _TAB_AKA = {"CVar": AKA_TAB_CVARS, "CCmds": AKA_TAB_CCMDS, "Favs": AKA_TAB_FAVS}

    def _show_tab(self, tab: str) -> None:
        self._switching_tab = True
        self._active_tab = tab
        is_favs = tab == "Favs"
        active_aka = self._TAB_AKA[tab]
        for aka, (active_color, inactive_color) in self._TAB_BTN_COLORS.items():
            self.data.set_button_color_and_opacity(aka, active_color if aka == active_aka else inactive_color)
        self.data.set_visibility(AKA_BTN_ADD_FAV, "Collapsed" if is_favs else "Visible")
        self.data.set_visibility(AKA_BTN_REM_FAV, "Visible"   if is_favs else "Collapsed")
        self.data.set_visibility(AKA_FAVS_TOOLS,  "Visible"   if is_favs else "Collapsed")
        self.data.set_visibility(AKA_LIST_CVARS,  "Visible" if tab == "CVar"  else "Collapsed")
        self.data.set_visibility(AKA_LIST_CCMDS,  "Visible" if tab == "CCmds" else "Collapsed")
        self.data.set_visibility(AKA_LIST_FAVS,   "Visible" if is_favs else "Collapsed")
        self.data.set_visibility(AKA_MEMO_ROW,    "Visible" if is_favs else "Collapsed")
        self._switching_tab = False
        self._update_status()

    def _reload_all(self) -> None:
        self._cvar_entries  = self._load_csv(self._logs_path(CSV_CVARS), "CVar")
        self._ccmds_entries = self._load_csv(self._logs_path(CSV_CCMDS), "CCmds")
        self._update_fav_selector()
        self._filter_all(self._last_query)
        self._refresh_all_lists()

    def _load_csv(self, path: str, entry_type: str) -> list[dict]:
        p = Path(path)
        if not p.exists():
            return []
        try:
            with open(p, encoding="utf-8-sig", newline="") as f:
                rows = list(csv.DictReader(f))
        except Exception as e:
            unreal.log_warning(f"ConsoleBrowser: CSV 로드 오류 ({Path(path).name}): {e}")
            return []
        if not rows:
            return []
        keys = list(rows[0].keys())
        name_key   = next((k for k in keys if "name"  in k.lower()), keys[0] if keys else None)
        value_key  = next((k for k in keys if "value" in k.lower()), None)
        set_by_key = next((k for k in keys if "set"   in k.lower()), None)
        help_key   = next((k for k in keys if "help"  in k.lower()), None)
        return [
            {
                "type":   entry_type,
                "name":   row.get(name_key,   "").strip(),
                "value":  row.get(value_key,  "").strip() if value_key  else "",
                "set_by": row.get(set_by_key, "").strip() if set_by_key else "",
                "help":   row.get(help_key,   "").strip() if help_key   else "",
            }
            for row in rows
            if name_key and row.get(name_key, "").strip()
        ]

    def _filter_all(self, query: str) -> None:
        self._cvar_sel.clear()
        self._ccmds_sel.clear()
        # 즐겨찾기 선택은 이름 기준으로 보존 (rebuild/filter 후 인덱스 재계산)
        selected_names = {self._favs_filtered[i]["name"] for i in self._favs_sel if i < len(self._favs_filtered)}
        if not query:
            self._cvar_filtered  = self._cvar_entries[:]
            self._ccmds_filtered = self._ccmds_entries[:]
            self._favs_filtered  = self._favs[:]
        else:
            q = query.lower()
            self._cvar_filtered = [
                e for e in self._cvar_entries
                if q in e["name"].lower() or q in e["help"].lower()
            ]
            self._ccmds_filtered = [
                e for e in self._ccmds_entries
                if q in e["name"].lower() or q in e["help"].lower()
            ]
            self._favs_filtered = [
                e for e in self._favs
                if q in e["name"].lower() or q in e["help"].lower()
                or any(q in v.lower() for v in e.get("custom_values", []))
                or q in e.get("memo", "").lower()
            ]
        self._favs_sel = {i for i, e in enumerate(self._favs_filtered) if e["name"] in selected_names}

    @staticmethod
    def _flat_help(text: str, limit: int) -> str:
        """리스트 셀용: 줄바꿈을 공백으로 치환하고 길이 제한"""
        return text.replace("\n", " ").replace("\r", "")[:limit]

    def _refresh_all_lists(self) -> None:
        show_trans = self.data.get_is_checked(AKA_TOGGLE_TRANS)

        def _help(e: dict, limit: int) -> str:
            text = self._trans_cache.get(e["name"], e["help"]) if show_trans else e["help"]
            return self._flat_help(text, limit)

        flat_cvars: list[str] = []
        for e in self._cvar_filtered:
            flat_cvars.extend([e["name"], e["value"], e["set_by"], _help(e, 120)])
        self.data.set_list_view_multi_column_items(AKA_LIST_CVARS, flat_cvars, 4)

        flat_ccmds: list[str] = []
        for e in self._ccmds_filtered:
            flat_ccmds.extend([e["name"], _help(e, 200)])
        self.data.set_list_view_multi_column_items(AKA_LIST_CCMDS, flat_ccmds, 2)

        flat_favs: list[str] = []
        for e in self._favs_filtered:
            flat_favs.extend([
                e["name"],
                ", ".join(e.get("custom_values", [])),
                e.get("memo", ""),
                _help(e, 120),
            ])
        saved_favs_sel = set(self._favs_sel)
        if saved_favs_sel:
            self._favs_refreshing = True
        self.data.set_list_view_multi_column_items(AKA_LIST_FAVS, flat_favs, 4)
        if saved_favs_sel:
            self._favs_sel = saved_favs_sel
            self.data.set_list_view_multi_column_selections(AKA_LIST_FAVS, list(saved_favs_sel))
        if self._active_tab == "Favs":
            self._refresh_values_panel()

        self._update_status()

    def _update_status(self) -> None:
        if self._active_tab == "CVar":
            shown, total = len(self._cvar_filtered), len(self._cvar_entries)
            status = "CSV 없음 — [Rebuild] 버튼을 눌러 생성하세요" if total == 0 else f"{shown:,} / {total:,} 개"
        elif self._active_tab == "CCmds":
            shown, total = len(self._ccmds_filtered), len(self._ccmds_entries)
            status = "CSV 없음 — [Rebuild] 버튼을 눌러 생성하세요" if total == 0 else f"{shown:,} / {total:,} 개"
        else:
            shown, total = len(self._favs_filtered), len(self._favs)
            list_label = f"[{self._active_fav_list[1]}]  "
            status = (list_label + "비어 있음 — Variables/Commands 탭에서 항목 선택 후 [★ 추가]"
                      if total == 0 else list_label + f"{shown:,} / {total:,} 개")
        self._set_status(status)

    def on_toggle_trans(self) -> None:
        """원문 / 번역문 토글 — 리스트 및 상세 정보를 다시 렌더"""
        self._settings["show_translation"] = self.data.get_is_checked(AKA_TOGGLE_TRANS)
        self._save_settings()
        self._refresh_all_lists()
        if self._active_tab == "CVar":
            sel, entries = self._cvar_sel, self._cvar_filtered
        elif self._active_tab == "CCmds":
            sel, entries = self._ccmds_sel, self._ccmds_filtered
        elif self._active_tab == "Favs":
            sel, entries = self._favs_sel, self._favs_filtered
        else:
            return
        if len(sel) == 1:
            self._show_detail(entries, next(iter(sel)))

    def translate_detail(self) -> None:
        """선택한 항목들을 순서대로 번역 (Claude → Google fallback, 다중 선택 지원)"""
        if self._active_tab == "CVar":
            sel, entries = self._cvar_sel, self._cvar_filtered
        elif self._active_tab == "CCmds":
            sel, entries = self._ccmds_sel, self._ccmds_filtered
        elif self._active_tab == "Favs":
            sel, entries = self._favs_sel, self._favs_filtered
        else:
            return

        items = [
            (entries[i]["name"], entries[i].get("help", "").strip())
            for i in sorted(sel)
            if i < len(entries) and entries[i].get("help", "").strip()
        ]
        if not items:
            self._set_status("번역할 항목을 선택하세요")
            return

        total = len(items)
        engine_pref = self.data.get_combo_box_selected_item(AKA_ENGINE_SELECTOR)
        engine_hint = engine_pref if engine_pref != "Auto" else ("Claude" if _get_claude_path() else "Google")
        self._set_status(f"번역 대기 중... ({engine_hint})  0 / {total}")
        self.data.set_progress_bar_percent(AKA_PROGRESS_BAR, 0.0)
        self.data.set_text(AKA_PROGRESS_LABEL, f"0 / {total}")
        self.data.set_visibility(AKA_PROGRESS_ROW, "Visible")

        global _tick_handle, _cancel_flag
        _cancel_flag.clear()

        # ── tick 콜백: 큐를 소진하며 메인 스레드에서 UI 갱신 ──
        def _tick(delta: float) -> None:
            global _tick_handle
            while not _signal_queue.empty():
                msg = _signal_queue.get_nowait()

                if msg[0] == "item":
                    _, name, translated, engine, current, tot = msg
                    self._trans_cache[name] = translated
                    self._save_trans_cache()
                    self.data.set_progress_bar_percent(AKA_PROGRESS_BAR, current / tot)
                    self.data.set_text(AKA_PROGRESS_LABEL, f"{current} / {tot}")
                    self._refresh_all_lists()
                    self._set_status(f"[{engine}] {name}  ({current}/{tot})")

                elif msg[0] == "fail":
                    _, name, current, tot = msg
                    self.data.set_progress_bar_percent(AKA_PROGRESS_BAR, current / tot)
                    self.data.set_text(AKA_PROGRESS_LABEL, f"{current} / {tot}")
                    self._set_status(f"번역 실패: {name}  ({current}/{tot})")

                elif msg[0] in ("done", "cancelled"):
                    _, done_count, tot = msg
                    unreal.unregister_slate_pre_tick_callback(_tick_handle)
                    _tick_handle = None
                    self.data.set_visibility(AKA_PROGRESS_ROW, "Collapsed")
                    self.data.set_is_checked(AKA_TOGGLE_TRANS, True)
                    self._refresh_all_lists()
                    verb = "완료" if msg[0] == "done" else "취소됨"
                    self._set_status(f"번역 {verb}: {done_count} / {tot}개")

        if _tick_handle is None:
            _tick_handle = unreal.register_slate_pre_tick_callback(_tick)

        # ── 백그라운드 스레드: 번역만, Unreal API 호출 없음 ──
        def _run(items=items, total=total, engine_pref=engine_pref):
            for current, (name, help_text) in enumerate(items, 1):
                if _cancel_flag.is_set():
                    _signal_queue.put(("cancelled", current - 1, total))
                    return
                translated, engine = _translate_text(help_text, engine_pref)
                if translated:
                    _signal_queue.put(("item", name, translated, engine, current, total))
                else:
                    _signal_queue.put(("fail", name, current, total))
            _signal_queue.put(("done", total, total))

        threading.Thread(target=_run, daemon=True).start()

    def cancel_translate(self) -> None:
        """진행 중인 번역 취소"""
        _cancel_flag.set()

    def reload_trans_cache(self) -> None:
        """번역 파일을 디스크에서 다시 읽어 반영"""
        self._load_trans_cache()
        self._refresh_all_lists()
        self._set_status(f"번역 파일 새로고침 완료 ({len(self._trans_cache):,}개)")

    def open_trans_file(self) -> None:
        """번역 파일을 기본 편집기로 열기"""
        plugin_path = self._plugin_trans_path()
        fallback_path = self._fallback_trans_path()
        # 실제 존재하는 파일 우선, 없으면 plugin_path 생성 후 열기
        if plugin_path.exists():
            path = plugin_path
        elif fallback_path.exists():
            path = fallback_path
        else:
            plugin_path.parent.mkdir(parents=True, exist_ok=True)
            plugin_path.write_text("{}\n", encoding="utf-8")
            path = plugin_path
        import subprocess
        subprocess.Popen(["start", "", str(path)], shell=True)
        self._set_status(f"번역 파일 열기: {path.name}")

    def _set_status(self, text: str) -> None:
        self.data.set_text(AKA_STATUS, text)


def launch() -> None:
    json_path = Path(__file__).with_suffix(".json").as_posix()
    unreal.ChameleonData.launch_chameleon_tool(json_path)


if __name__ == "__main__":
    launch()
