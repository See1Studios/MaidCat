import unreal
import os
import json
import tempfile
import subprocess
import sys

import tool.ue_serializer as ue_serializer
import importlib

# 동적 상수들 - 런타임에 결정
TOOL_MENUS = unreal.ToolMenus.get()  # 도구 메뉴 인스턴스 (전역 접근용)

# 메뉴 기본 정보
OWNER_NAME = unreal.Name("MyCustomMenu")  # 메뉴 소유자 이름 (unregister시 사용)
MENU_TARGET = unreal.Name("ContentBrowser.AssetContextMenu")  # 대상 메뉴 (아래 참고)
SECTION_NAME = unreal.Name("CustomActions")  # 섹션 이름
SECTION_LABEL = unreal.Text("Custom Actions")  # 섹션 표시 이름

# 메뉴 항목 정보
ENTRY_NAME = unreal.Name("SerializeToJSON")  # 메뉴 항목 ID
ENTRY_LABEL = unreal.Text("JSON으로 내보내기")  # 메뉴 항목 표시 이름
ENTRY_TOOLTIP = unreal.Text("선택된 오브젝트를 JSON으로 직렬화하여 편집기로 엽니다")  # 툴팁 텍스트

# 서브메뉴 사용 여부 및 정보
USE_SUBMENU = False  # True면 서브메뉴 생성, False면 단일 항목
SUBMENU_NAME = unreal.Name("MyCustomSubmenu")  # 서브메뉴 ID
SUBMENU_LABEL = unreal.Text("고급 액션...")  # 서브메뉴 표시 이름
SUBMENU_TOOLTIP = unreal.Text("고급 커스텀 액션들")  # 서브메뉴 툴팁

# 동적 메뉴 사용 여부
USE_DYNAMIC_SECTION = False  # True면 동적 섹션 추가
DYNAMIC_SECTION_NAME = unreal.Name("DynamicItems")  # 동적 섹션 이름
# 메뉴 삽입 설정
INSERT_NAME = unreal.Name("")  # 삽입 위치 기준이 되는 메뉴 항목 이름 (비워두면 마지막에 추가)
SECTION_INSERT_NAME = unreal.Name("")  # 섹션 삽입 위치 기준이 되는 섹션 이름 (비워두면 마지막에 추가)

# 메뉴별 컨텍스트 클래스 매핑 (startswith로 매칭)
MENU_CONTEXT_MAP = {
    # ContentBrowser 관련
    "ContentBrowser.ItemContextMenu": unreal.ContentBrowserDataMenuContext_FileMenu,
    "ContentBrowser.FolderContextMenu": unreal.ContentBrowserDataMenuContext_FolderMenu,
    "ContentBrowser.AssetContextMenu": unreal.ContentBrowserAssetContextMenuContext,
    # AssetEditor 관련
    "AssetEditor": unreal.AssetEditorToolkitMenuContext,
}

def get_context_objects(context : unreal.ToolMenuContext):
    objects = []
    menu_target_str = str(MENU_TARGET)
    
    # 메뉴 타겟에서 컨텍스트 클래스 찾기 (startswith)
    context_class = None
    for key in MENU_CONTEXT_MAP:
        if menu_target_str.startswith(key):
            context_class = MENU_CONTEXT_MAP[key]
            break
    
    if context_class is None:
        # 메인 메뉴 등 컨텍스트가 없는 경우
        return objects
    
    try:
        target_context = context.find_by_class(context_class)
        if target_context:
            # 컨텍스트 타입별로 다른 속성 사용
            if isinstance(target_context, unreal.ContentBrowserAssetContextMenuContext):
                if target_context.selected_assets:
                    objects.extend(target_context.selected_assets)
            elif isinstance(target_context, (unreal.ContentBrowserDataMenuContext_FileMenu, unreal.ContentBrowserDataMenuContext_FolderMenu)):
                if target_context.selected_items:
                    objects.extend(target_context.selected_items)
            elif isinstance(target_context, unreal.AssetEditorToolkitMenuContext):
                # AssetEditor의 경우 현재 편집 중인 에셋
                if hasattr(target_context, 'get_edited_objects'):
                    edited_objects = target_context.get_edited_objects()
                    if edited_objects:
                        objects.extend(edited_objects)
    except Exception as e:
        unreal.log_warning(f"컨텍스트 오브젝트 가져오기 오류: {e}")
    
    return objects

@unreal.uclass()
class CustomMenuScript(unreal.ToolMenuEntryScript):
    """커스텀 메뉴 스크립트"""
    
    @unreal.ufunction(override=True)
    def can_execute(self, context : unreal.ToolMenuContext):
        """활성화 조건 - 필요시 수정"""
        # 메뉴 타겟에서 컨텍스트 클래스 찾기 (startswith)
        menu_target_str = str(MENU_TARGET)
        context_class = None
        for key in MENU_CONTEXT_MAP:
            if menu_target_str.startswith(key):
                context_class = MENU_CONTEXT_MAP[key]
                break
        
        # 메인 메뉴는 항상 활성화
        if context_class is None:
            return True
        
        # 컨텍스트 오브젝트가 있으면 활성화
        context_objects = get_context_objects(context)
        return len(context_objects) > 0 if context_objects else True
    
    @unreal.ufunction(override=True) 
    def execute(self, context : unreal.ToolMenuContext):
        """선택된 오브젝트를 JSON으로 직렬화하고 편집기로 열기"""
        unreal.log(f"🎯 {ENTRY_LABEL} 실행!")
        
        # 컨텍스트 오브젝트들 가져오기
        context_objects = get_context_objects(context)
        
        if context_objects:
            unreal.log(f"📁 컨텍스트 오브젝트: {len(context_objects)}개")
            for obj in context_objects:
                if hasattr(obj, 'get_virtual_path'):
                    virtual_path = str(obj.get_virtual_path())
                    unreal.log(f"  - {virtual_path}")
                else:
                    obj_name = str(obj.get_name() if hasattr(obj, 'get_name') else obj)
                    unreal.log(f"  - {obj_name}")
            
            # JSON으로 직렬화하고 편집기로 열기
            importlib.reload(ue_serializer)
            ue_serializer.test_selected_asset()
        else:
            unreal.log("⚠️ 컨텍스트 오브젝트가 없습니다")
            unreal.log("💡 ContentBrowser에서 에셋을 선택한 후 다시 시도해주세요.")

@unreal.uclass()
class CustomDynamicSection(unreal.ToolMenuSectionDynamic):
    """동적 메뉴 섹션 - 선택 항목에 따라 메뉴 생성"""
    
    @unreal.ufunction(override=True)
    def construct_sections(self, menu, context : unreal.ToolMenuContext):
        """📝 여기에 동적 메뉴 구성 로직을 구현하세요!"""
        context_objects = get_context_objects(context)
        if not context_objects:
            return
        
        unreal.log(f"🔄 동적 메뉴 구성: {len(context_objects)}개 오브젝트")
        
        # 각 컨텍스트 오브젝트에 대해 메뉴 추가
        for i, obj in enumerate(context_objects):
            item_path = str(obj.get_virtual_path())
            self._add_menu_entry(menu, item_path, i)
    

    
    def _add_menu_entry(self, menu, item_path, index):
        """동적 메뉴 항목 추가"""
        item_name = os.path.basename(item_path) or f"Item_{index}"
        _add_menu_entry_to_menu(
            menu=menu,
            section=DYNAMIC_SECTION_NAME,
            name=unreal.Name(f'DynamicItem_{index}'),
            label=unreal.Text(f"처리: {item_name}"),
            tooltip=unreal.Text(f"{item_name} 처리")
        )

def _add_menu_entry_to_menu(menu, section, name, label, tooltip):
    """메뉴에 항목 추가하는 통합 함수"""
    entry = CustomMenuScript()
    entry.data = unreal.ToolMenuEntryScriptData(
        owner_name=OWNER_NAME,
        menu=menu.menu_name,
        section=section,
        name=name,
        label=label,
        tool_tip=tooltip,
        icon=unreal.ScriptSlateIcon(),
        insert_position=unreal.ToolMenuInsert(INSERT_NAME, unreal.ToolMenuInsertType.DEFAULT)
    )
    entry.register_menu_entry()
    menu.add_menu_entry_object(entry)

def _add_basic_entry(menu):
    """기본 메뉴 항목 추가"""
    _add_menu_entry_to_menu(
        menu=menu,
        section=SECTION_NAME,
        name=ENTRY_NAME,
        label=ENTRY_LABEL,
        tooltip=ENTRY_TOOLTIP
    )

def register():
    """메뉴 등록 - 상수 설정에 따라 자동 처리"""
    try:
        menu = TOOL_MENUS.extend_menu(MENU_TARGET)
        
        # 섹션 추가
        menu.add_section(SECTION_NAME, SECTION_LABEL)
        
        if USE_SUBMENU:
            # 서브메뉴 방식
            submenu = menu.add_sub_menu(
                owner=OWNER_NAME,
                section_name=SECTION_NAME,
                name=SUBMENU_NAME,
                label=SUBMENU_LABEL,
                tool_tip=SUBMENU_TOOLTIP
            )
            
            if submenu and USE_DYNAMIC_SECTION:
                # 동적 섹션 추가
                dynamic_section = CustomDynamicSection()
                submenu.add_dynamic_section(DYNAMIC_SECTION_NAME, dynamic_section)
            elif submenu:
                # 기본 항목 추가
                _add_basic_entry(submenu)
        else:
            # 직접 메뉴 항목 추가
            _add_basic_entry(menu)
        
        TOOL_MENUS.refresh_all_widgets()
        unreal.log(f"✅ {ENTRY_LABEL} 메뉴 등록 완료!")
        return True
        
    except Exception as e:
        unreal.log_error(f"❌ 메뉴 등록 오류: {e}")
        return False

def unregister():
    """메뉴 해제 - OWNER_NAME으로 등록된 모든 항목 제거"""
    TOOL_MENUS.unregister_owner_by_name(OWNER_NAME)

if __name__ == "__main__":
    register()