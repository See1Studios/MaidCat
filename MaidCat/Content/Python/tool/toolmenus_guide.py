"""
ToolMenus 연습 가이드
Unreal Engine 콘솔에서 실행할 수 있는 단계별 연습 코드들
"""

# =============================================================================
# 연습 실행 방법
# =============================================================================

"""
Unreal Engine의 Python 콘솔에서 다음과 같이 실행하세요:

1. 전체 연습 실행:
   exec(open(r'd:\GitHub\MaidCat\MaidCat\Content\Python\tool\toolmenus_practice.py').read())

2. 특정 단계만 실행:
   from tool.toolmenus_practice import practice_1_basic_menu_elements
   practice_1_basic_menu_elements()

3. Context 연습:
   from tool.toolmenus_practice import run_context_practice
   run_context_practice()

4. 정리:
   from tool.toolmenus_practice import cleanup_all
   cleanup_all()
"""

# =============================================================================
# 각 단계별 학습 내용
# =============================================================================

학습_단계 = {
    "1단계_기본요소": {
        "설명": "ToolMenus의 기본 구조와 메뉴 타입들 이해",
        "학습내용": [
            "tool_menus.find_menu() - 기존 메뉴 찾기",
            "unreal.MultiBlockType - 메뉴 요소 타입들",
            "주요 메뉴 위치들 파악"
        ],
        "실행코드": "practice_1_basic_menu_elements()"
    },
    
    "2단계_섹션관리": {
        "설명": "메뉴 섹션 추가/제거와 기본 엔트리 생성",
        "학습내용": [
            "menu.add_section() - 섹션 추가",
            "menu.remove_section() - 섹션 제거",
            "unreal.ToolMenuEntry() - 메뉴 엔트리 생성",
            "entry.set_string_command() - 파이썬 명령 연결"
        ],
        "실행코드": "practice_2_menu_sections()"
    },
    
    "3단계_Context감지": {
        "설명": "현재 선택된 애셋/액터/폴더 정보 가져오기",
        "학습내용": [
            "unreal.EditorUtilityLibrary.get_selected_assets()",
            "unreal.EditorUtilityLibrary.get_selected_folder_paths()",
            "unreal.EditorLevelLibrary.get_selected_level_actors()",
            "Context 정보 분석"
        ],
        "실행코드": "practice_3_context_detection()"
    },
    
    "4단계_동적메뉴": {
        "설명": "Context에 따라 다른 메뉴 항목들 생성",
        "학습내용": [
            "get_context_info() - Context 분석 함수",
            "조건부 메뉴 엔트리 생성",
            "애셋 타입별 다른 도구 제공",
            "동적 라벨과 툴팁"
        ],
        "실행코드": "practice_4_dynamic_menu_creation()"
    },
    
    "5단계_서브메뉴": {
        "설명": "계층적 서브메뉴 구조 생성",
        "학습내용": [
            "menu.add_sub_menu() - 서브메뉴 생성",
            "서브메뉴 섹션 관리",
            "Context 기반 서브메뉴 구성",
            "owner와 name 설정"
        ],
        "실행코드": "practice_5_submenu_creation()"
    },
    
    "6단계_고급Context": {
        "설명": "선택된 애셋들의 상세 분석",
        "학습내용": [
            "패키지 경로 분석",
            "애셋 관계 분석 (부모-자식)",
            "폴더별 분포 확인",
            "Material Instance 특별 처리"
        ],
        "실행코드": "practice_6_advanced_context()"
    },
    
    "7단계_정리": {
        "설명": "메뉴 정리와 새로고침",
        "학습내용": [
            "연습용 섹션들 제거",
            "tool_menus.refresh_all_widgets()",
            "깔끔한 정리 방법"
        ],
        "실행코드": "practice_7_menu_refresh_and_cleanup()"
    }
}

# =============================================================================
# Context 정보 구조 예시
# =============================================================================

context_구조_예시 = {
    'selected_assets': [],           # 선택된 애셋들의 UObject 리스트
    'selected_folders': [],          # 선택된 폴더 경로들
    'selected_actors': [],           # 선택된 액터들
    'asset_types': set(),           # 애셋 클래스 이름들 (MaterialInstanceConstant, Texture2D 등)
    'has_material_instances': False, # Material Instance 포함 여부
    'has_materials': False,         # Material 포함 여부
    'has_textures': False,          # Texture 포함 여부
    'has_meshes': False            # Mesh 포함 여부
}

# =============================================================================
# 주요 메뉴 위치들
# =============================================================================

주요_메뉴_위치 = {
    "ContentBrowser.AssetContextMenu": "콘텐츠 브라우저 애셋 우클릭 메뉴",
    "ContentBrowser.FolderContextMenu": "콘텐츠 브라우저 폴더 우클릭 메뉴", 
    "LevelEditor.ActorContextMenu": "뷰포트 액터 우클릭 메뉴",
    "LevelEditor.LevelEditorToolBar": "메인 툴바",
    "MainFrame.MainMenu": "메인 메뉴바 (File, Edit, Window 등)",
    "LevelEditor.MainMenu": "레벨 에디터 메뉴바",
    "MaterialEditor.MainMenu": "머티리얼 에디터 메뉴바"
}

# =============================================================================
# MultiBlockType 종류들
# =============================================================================

메뉴_타입들 = {
    "MENU_ENTRY": "일반 메뉴 항목",
    "SEPARATOR": "구분선", 
    "MENU_BAR": "메뉴바",
    "TOOLBAR_BUTTON": "툴바 버튼",
    "TOOL_BAR_COMBO_BUTTON": "툴바 콤보 버튼",
    "BUTTON_ROW": "버튼 행",
    "EDITABLE_TEXT": "편집 가능한 텍스트",
    "SEARCH_BOX": "검색 박스"
}

# =============================================================================
# 실제 사용 예시들
# =============================================================================

예시_코드들 = {
    "기본_엔트리_생성": """
entry = unreal.ToolMenuEntry(
    name=unreal.Name("my_entry"),
    type=unreal.MultiBlockType.MENU_ENTRY
)
entry.set_label(unreal.Text("My Tool"))
entry.set_tool_tip(unreal.Text("설명"))
entry.set_string_command(
    unreal.ToolMenuStringCommandType.PYTHON,
    custom_type=unreal.Name(""),
    string="print('Hello World!')"
)
""",

    "서브메뉴_생성": """
submenu = menu.add_sub_menu(
    owner=unreal.Name(""),
    section_name=section_name,
    name=unreal.Name("my_submenu"),
    label=unreal.Text("My Submenu"),
    tool_tip=unreal.Text("서브메뉴 설명")
)
""",

    "섹션_관리": """
section_name = unreal.Name("MySection")
menu.add_section(section_name, unreal.Text("My Section"))
menu.add_menu_entry(section_name, entry)
menu.remove_section(section_name)  # 제거
""",

    "Context_활용": """
selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
if selected_assets:
    for asset in selected_assets:
        asset_type = asset.get_class().get_name()
        if asset_type == 'MaterialInstanceConstant':
            # Material Instance 전용 메뉴 추가
            pass
"""
}

print("📚 ToolMenus 연습 가이드가 준비되었습니다!")
print("🚀 Unreal Engine 콘솔에서 다음 명령으로 시작하세요:")
print("   exec(open(r'd:\\GitHub\\MaidCat\\MaidCat\\Content\\Python\\tool\\toolmenus_practice.py').read())")