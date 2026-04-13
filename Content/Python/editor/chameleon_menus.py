"""
Chameleon 툴 메뉴 등록 모듈
MaidCat의 Chameleon 기반 에디터 툴들을 Level Editor 메인 메뉴 Tools 에 추가합니다.
"""

import unreal
from pathlib import Path

_MENU_OWNER = unreal.Name("MaidCat.ChameleonMenus")
_TOOLS_MENU  = unreal.Name("LevelEditor.MainMenu.Tools")
_SECTION     = unreal.Name("MaidCatChameleonSection")

# Content/Python 루트 (이 파일 기준: editor/../ = Content/Python/)
_PYTHON_ROOT = Path(__file__).parent.parent


def _chameleon_json(relative: str) -> str:
    """Content/Python 루트 기준 상대 경로로 JSON 절대 경로 반환 (forward slash)

    TAPython이 %JsonPath를 Python 문자열 리터럴로 치환할 때
    Windows 백슬래시(\\U, \\P 등)가 유니코드 이스케이프로 오해될 수 있으므로
    항상 forward slash 경로를 사용합니다.
    """
    return (_PYTHON_ROOT / relative).as_posix()


# ── Chameleon 툴 실행 스크립트 정의 ──────────────────────────────────────────

@unreal.uclass()
class _OpenConsoleBrowserScript(unreal.ToolMenuEntryScript):
    """Console Browser Chameleon 툴을 여는 메뉴 항목"""

    @unreal.ufunction(override=True)
    def execute(self, context: unreal.ToolMenuContext) -> None:
        unreal.ChameleonData.launch_chameleon_tool(
            _chameleon_json("tool/console_browser.json")
        )


# ── 등록/해제 ────────────────────────────────────────────────────────────────

def register() -> None:
    """MaidCat Chameleon 툴 메뉴 등록"""
    try:
        tool_menus = unreal.ToolMenus.get()
        menu = tool_menus.extend_menu(_TOOLS_MENU)
        menu.add_section(_SECTION, unreal.Text("MaidCat"))

        _register_entry(menu, _OpenConsoleBrowserScript(),
                        name="MaidCat_ConsoleBrowser",
                        label="Console Browser",
                        tooltip="UE CVar/Console Variable 검색 툴")

        tool_menus.refresh_all_widgets()
        unreal.log("✅ MaidCat Chameleon 메뉴 등록 완료")

    except Exception as e:
        unreal.log_error(f"❌ Chameleon 메뉴 등록 실패: {e}")


def unregister() -> None:
    """MaidCat Chameleon 툴 메뉴 해제"""
    try:
        tool_menus = unreal.ToolMenus.get()
        tool_menus.unregister_owner_by_name(str(_MENU_OWNER))
        tool_menus.refresh_all_widgets()
    except Exception as e:
        unreal.log_error(f"❌ Chameleon 메뉴 해제 실패: {e}")


# ── 내부 헬퍼 ────────────────────────────────────────────────────────────────

def _register_entry(menu: unreal.ToolMenu,
                    script: unreal.ToolMenuEntryScript,
                    name: str, label: str, tooltip: str) -> None:
    """메뉴 항목 스크립트를 초기화하고 등록"""
    script.init_entry(
        _MENU_OWNER,
        _TOOLS_MENU,
        _SECTION,
        unreal.Name(name),
        unreal.Text(label),
        unreal.Text(tooltip),
    )
    script.register_menu_entry()
