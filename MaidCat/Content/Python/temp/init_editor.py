# /Content/Python/init_editor.py (수정된 코드)

import unreal
import importlib

# 우리가 만든 툴 스크립트 임포트
import mesh_slicer_tool

# 스크립트가 수정되었을 때 최신 버전을 가져오기 위해 reload 해주는 것이 좋습니다.
importlib.reload(mesh_slicer_tool)


def add_toolbar_button():
    """스태틱 메시 에디터 툴바에 버튼을 추가합니다."""
    
    tool_menus = unreal.ToolMenus.get()
    
    # 스태틱 메시 에디터의 툴바 메뉴 찾기
    menu_name = "AssetEditor.StaticMeshEditor.ToolBar"
    menu = tool_menus.find_menu(menu_name)
    
    if not menu:
        unreal.log_warning(f"{menu_name} 메뉴를 찾을 수 없습니다.")
        return
        
    section_name = "PythonTools"

    # 1. 버튼(Entry) 객체를 먼저 생성합니다. (위치 정보 제외)
    entry = unreal.ToolMenuEntry(
        name="SliceMeshButton",
        type=unreal.MultiBlockType.TOOL_BAR_BUTTON
    )
    
    # 2. 생성된 버튼 객체의 속성(라벨, 툴팁, 실행할 명령어)을 설정합니다.
    entry.set_label("Slice Mesh")
    entry.set_tool_tip("메시 하단에서 일정 높이를 잘라 단면을 생성합니다.")
    
    command_string = f"import mesh_slicer_tool; importlib.reload(mesh_slicer_tool); mesh_slicer_tool.slice_static_mesh_at_height()"
    entry.set_string_command(
        type=unreal.ToolMenuStringCommandType.PYTHON,
        string=command_string
    )
    
    # 3. 버튼이 들어갈 위치를 정의하는 ToolMenuInsert 객체를 생성합니다.
    # 'FindInCB' (콘텐츠 브라우저에서 찾기) 버튼 앞에 위치시킵니다.
    insert_object = unreal.ToolMenuInsert("FindInCB", unreal.ToolMenuInsertType.BEFORE)

    # 4. add_menu_entry 대신 insert_menu_entry 함수를 사용해
    #    버튼(entry)과 위치(insert_object) 정보를 함께 전달하여 메뉴에 삽입합니다.
    menu.insert_menu_entry(section_name, entry, insert_object)
    
    tool_menus.refresh_all_widgets()


# 스크립트가 로드될 때 함수 실행
add_toolbar_button()