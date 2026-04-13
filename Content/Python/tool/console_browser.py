"""
ConsoleBrowser — Chameleon 툴
UE CVar / CCmds 덤프 CSV를 로드해 탭별로 검색.
즐겨찾기는 여러 목록으로 관리, 각 항목에 메모 첨부 가능.

초기 로드: CSV가 있으면 바로 사용, 없으면 안내 표시
강제 재생성: [Rebuild] 버튼
"""

import ctypes
import csv
import datetime
import json
import time
import tkinter as tk
import tkinter.filedialog as filedialog
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
AKA_TOOLBAR_NORMAL  = "ToolbarNormal"
AKA_TOOLBAR_FAVS    = "ToolbarFavs"
AKA_FAVS_SELECTOR   = "FavsSelector"
AKA_FAVS_NEW_NAME   = "FavsNewName"
AKA_AUTO_REBUILD    = "AutoRebuild"

# ── 상수 ──────────────────────────────────────────────────────────────────────
CSV_CVARS        = "DumpCVars.csv"
CSV_CCMDS        = "DumpCCmds.csv"
FAVS_FILE        = "favorites.json"
DEFAULT_LIST     = "Default"

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
        # 즐겨찾기 다중 목록: {list_name: [entries]}
        self._favs_db:        dict[str, list] = {}
        self._active_fav_list = DEFAULT_LIST

    # _favs → 현재 활성 목록의 뷰
    @property
    def _favs(self) -> list:
        return self._favs_db.setdefault(self._active_fav_list, [])

    @_favs.setter
    def _favs(self, value: list) -> None:
        self._favs_db[self._active_fav_list] = value

    # ── 초기화 ───────────────────────────────────────────────────────────────

    def init(self) -> None:
        self._load_favs()
        self._reload_all()
        self._show_tab("CVar")

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

    def on_fav_list_changed(self, list_name: str) -> None:
        """콤보박스 목록 선택"""
        if list_name not in self._favs_db:
            return
        self._active_fav_list = list_name
        self._favs_sel.clear()
        self._filter_all(self._last_query)
        self._refresh_all_lists()

    def add_fav_list(self) -> None:
        """새 즐겨찾기 목록 추가"""
        name = self.data.get_text(AKA_FAVS_NEW_NAME).strip()
        if not name:
            self._set_status("새 목록 이름을 입력하세요")
            return
        if name in self._favs_db:
            self._set_status(f"이미 존재하는 목록: {name}")
            return
        self._favs_db[name] = []
        self._active_fav_list = name
        self._save_favs()
        self.data.set_text(AKA_FAVS_NEW_NAME, "")
        self._update_fav_selector()
        self._filter_all(self._last_query)
        self._refresh_all_lists()
        self._set_status(f"목록 추가: {name}")

    def delete_fav_list(self) -> None:
        """현재 즐겨찾기 목록 삭제 (Default는 삭제 불가)"""
        if self._active_fav_list == DEFAULT_LIST:
            self._set_status("기본 목록은 삭제할 수 없습니다")
            return
        count = len(self._favs)
        confirmed = unreal.PythonBPLib.confirm_dialog(
            f'"{self._active_fav_list}" 목록을 삭제하시겠습니까?\n({count:,}개 항목이 모두 제거됩니다)',
            "목록 삭제 확인",
        )
        if not confirmed:
            return
        removed = self._active_fav_list
        del self._favs_db[removed]
        self._active_fav_list = DEFAULT_LIST
        self._save_favs()
        self._update_fav_selector()
        self._favs_sel.clear()
        self._filter_all(self._last_query)
        self._refresh_all_lists()
        self._set_status(f"목록 삭제: {removed}")

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
        msg = f"[{self._active_fav_list}] 추가: {len(to_add)}개  (총 {len(self._favs):,}개)"
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
        self._rebuild_if_auto(entry)

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
        default_name = f"Favs_{_safe_filename(self._active_fav_list)}_{timestamp}.csv"
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

    def split_to_db(self) -> None:
        all_data = [("CVars", self._cvar_entries), ("CCmds", self._ccmds_entries)]
        if not any(e for _, e in all_data):
            self._set_status("데이터 없음 — [Rebuild] 버튼을 누르세요")
            return
        db_root = self._saved_dir() / "Logs" / "ConsoleBrowser"
        total = 0
        for type_name, entries in all_data:
            if not entries:
                continue
            type_dir = db_root / type_name
            type_dir.mkdir(parents=True, exist_ok=True)
            for f in type_dir.glob("*.json"):
                f.unlink()
            groups: dict[str, list] = {}
            for e in entries:
                parts = e["name"].split(".")
                domain = ".".join(parts[:-1]) if len(parts) > 1 else "_root"
                groups.setdefault(domain, []).append(e)
            for domain, group in sorted(groups.items()):
                payload = {
                    "domain": domain, "count": len(group),
                    "entries": [
                        {"leaf": e["name"].rsplit(".", 1)[-1], "full_name": e["name"],
                         "value": e.get("value", ""), "set_by": e.get("set_by", ""),
                         "help": e["help"]}
                        for e in sorted(group, key=lambda x: x["name"])
                    ],
                }
                (type_dir / (_safe_filename(domain) + ".json")).write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
                )
                total += 1
        self._set_status(f"DB 분할: {total}개 파일 → {db_root}")

    # ── 내부 헬퍼 ────────────────────────────────────────────────────────────

    def _rebuild_if_auto(self, entry: dict) -> None:
        if entry.get("type") == "CVar" and self.data.get_is_checked(AKA_AUTO_REBUILD):
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
        lines = [
            f"[{e.get('type', '?')}]  {e['name']}",
            f"Value:  {e.get('value', '')}",
            f"Set By: {e.get('set_by', '')}",
            f"\nHelp:\n{e['help']}",
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
        path = self._saved_dir() / "Logs" / "ConsoleBrowser" / FAVS_FILE
        if not path.exists():
            self._favs_db = {DEFAULT_LIST: []}
            self._active_fav_list = DEFAULT_LIST
            return
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            # 구형 포맷 (list) → 자동 마이그레이션
            if isinstance(raw, list):
                self._favs_db = {DEFAULT_LIST: raw}
            else:
                self._favs_db = raw
        except Exception as e:
            unreal.log_warning(f"ConsoleBrowser: 즐겨찾기 로드 오류: {e}")
            self._favs_db = {DEFAULT_LIST: []}
        if not self._favs_db:
            self._favs_db = {DEFAULT_LIST: []}
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
        path = self._saved_dir() / "Logs" / "ConsoleBrowser" / FAVS_FILE
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self._favs_db, ensure_ascii=False, indent=2), encoding="utf-8")

    def _update_fav_selector(self) -> None:
        """콤보박스 항목 갱신 — 활성 목록을 맨 앞에"""
        names = list(self._favs_db.keys())
        if self._active_fav_list in names:
            names.remove(self._active_fav_list)
            names.insert(0, self._active_fav_list)
        self.data.set_combo_box_items(AKA_FAVS_SELECTOR, names)

    def _show_tab(self, tab: str) -> None:
        self._switching_tab = True
        self._active_tab = tab
        is_favs = tab == "Favs"
        self.data.set_is_checked(AKA_TAB_CVARS, tab == "CVar")
        self.data.set_is_checked(AKA_TAB_CCMDS, tab == "CCmds")
        self.data.set_is_checked(AKA_TAB_FAVS,  is_favs)
        self.data.set_visibility(AKA_TOOLBAR_NORMAL, "Collapsed" if is_favs else "Visible")
        self.data.set_visibility(AKA_TOOLBAR_FAVS,   "Visible"   if is_favs else "Collapsed")
        self.data.set_visibility(AKA_LIST_CVARS,     "Visible"   if tab == "CVar"  else "Collapsed")
        self.data.set_visibility(AKA_LIST_CCMDS,     "Visible"   if tab == "CCmds" else "Collapsed")
        self.data.set_visibility(AKA_LIST_FAVS,  "Visible" if is_favs else "Collapsed")
        self.data.set_visibility(AKA_MEMO_ROW,   "Visible" if is_favs else "Collapsed")
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
        self._favs_sel.clear()
        if not query:
            self._cvar_filtered  = self._cvar_entries[:]
            self._ccmds_filtered = self._ccmds_entries[:]
            self._favs_filtered  = self._favs[:]
            return
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

    @staticmethod
    def _flat_help(text: str, limit: int) -> str:
        """리스트 셀용: 줄바꿈을 공백으로 치환하고 길이 제한"""
        return text.replace("\n", " ").replace("\r", "")[:limit]

    def _refresh_all_lists(self) -> None:
        flat_cvars: list[str] = []
        for e in self._cvar_filtered:
            flat_cvars.extend([e["name"], e["value"], e["set_by"],
                               self._flat_help(e["help"], 120)])
        self.data.set_list_view_multi_column_items(AKA_LIST_CVARS, flat_cvars, 4)

        flat_ccmds: list[str] = []
        for e in self._ccmds_filtered:
            flat_ccmds.extend([e["name"], self._flat_help(e["help"], 200)])
        self.data.set_list_view_multi_column_items(AKA_LIST_CCMDS, flat_ccmds, 2)

        flat_favs: list[str] = []
        for e in self._favs_filtered:
            flat_favs.extend([
                e["name"],
                ", ".join(e.get("custom_values", [])),
                e.get("memo", ""),
            ])
        self.data.set_list_view_multi_column_items(AKA_LIST_FAVS, flat_favs, 3)
        if self._favs_sel:
            self.data.set_list_view_multi_column_selections(AKA_LIST_FAVS, list(self._favs_sel))
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
            list_label = f"[{self._active_fav_list}]  "
            status = (list_label + "비어 있음 — Variables/Commands 탭에서 항목 선택 후 [★ 추가]"
                      if total == 0 else list_label + f"{shown:,} / {total:,} 개")
        self._set_status(status)

    def _set_status(self, text: str) -> None:
        self.data.set_text(AKA_STATUS, text)


def launch() -> None:
    json_path = Path(__file__).with_suffix(".json").as_posix()
    unreal.ChameleonData.launch_chameleon_tool(json_path)


if __name__ == "__main__":
    launch()
