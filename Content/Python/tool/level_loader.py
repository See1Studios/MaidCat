import unreal
import util.name as const

# Section
SECTION_NAME = unreal.Name("LevelLoaderSection")
SECTION_LABEL = unreal.Text("Level Loader")

# Dynamic Section
DYNAMIC_SECTION_NAME = unreal.Name("LevelLoaderDynamicSection")
SUB_MENU_NAME = unreal.Name("LevelLoaderSubMenu")
SUB_MENU_LABEL = unreal.Name("레벨 추가")
SUB_MENU_TOOLTIP = unreal.Name("현재 레벨에 선택한 레벨을 추가합니다")


@unreal.uclass()
class LoadLevelEntry(unreal.ToolMenuEntryScript):
    """레벨을 현재 월드로 로드하는 커스텀 메뉴 스크립트 (아웃라이너/월드 브라우저용)"""

    @unreal.ufunction(override=True)
    def can_execute(self, context: unreal.ToolMenuContext) -> bool:
        """항상 활성화"""
        return True

    @unreal.ufunction(override=True)
    def execute(self, context: unreal.ToolMenuContext):
        """레벨을 현재 월드에 추가/로드"""
        # data.name에서 레벨 경로 가져오기
        level_path = str(self.data.name)
        
        unreal.log(f"레벨 로드 시도: {level_path}")
        
        if not level_path:
            unreal.log_error("레벨 경로가 비어있습니다!")
            return
        
        unreal.log(f"레벨 로드 시도: {level_path}")
        
        editor_level_lib = unreal.EditorLevelLibrary
        editor_asset_lib = unreal.EditorAssetLibrary
        
        try:
            # 레벨 에셋이 존재하는지 먼저 확인
            if not editor_asset_lib.does_asset_exist(level_path):
                unreal.log_error(f"레벨 에셋을 찾을 수 없습니다: {level_path}")
                unreal.EditorDialog.show_message(
                    unreal.Text("오류"),
                    unreal.Text(f"레벨 에셋을 찾을 수 없습니다:\n{level_path}"),
                    unreal.AppMsgType.OK
                )
                return

            # 현재 레벨 저장 여부 확인
            unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
            
            # 레벨 로드
            success = editor_level_lib.load_level(level_path)
            
            if success:
                level_name = level_path.split('/')[-1]
                unreal.log(f"레벨 '{level_name}'이 성공적으로 로드되었습니다.")
            else:
                level_name = level_path.split('/')[-1]
                unreal.log_error(f"레벨 '{level_name}' 로드에 실패했습니다.")
                unreal.EditorDialog.show_message(
                    unreal.Text("레벨 로드 실패"),
                    unreal.Text(f"레벨 '{level_name}' 로드에 실패했습니다."),
                    unreal.AppMsgType.OK
                )

        except Exception as e:
            error_msg = f"레벨 로드 중 오류 발생: {str(e)}"
            unreal.log_error(error_msg)
            unreal.EditorDialog.show_message(
                unreal.Text("오류"),
                unreal.Text(error_msg),
                unreal.AppMsgType.OK
            )


@unreal.uclass()
class AppendLevelEntry(unreal.ToolMenuEntryScript):
    """레벨을 현재 월드에 추가하는 커스텀 메뉴 스크립트"""

    @unreal.ufunction(override=True)
    def can_execute(self, context: unreal.ToolMenuContext) -> bool:
        """항상 활성화"""
        return True

    @unreal.ufunction(override=True)
    def execute(self, context: unreal.ToolMenuContext):
        """레벨을 현재 월드에 스트리밍 레벨로 추가"""
        # data.name에서 레벨 경로 가져오기
        level_path = str(self.data.name)
        
        unreal.log(f"레벨 추가 시도: {level_path}")
        
        if not level_path:
            unreal.log_error("레벨 경로가 비어있습니다!")
            return
        
        unreal.log(f"레벨 추가 시도: {level_path}")
        
        ue_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        editor_world = ue_subsystem.get_editor_world()
        editor_asset_lib = unreal.EditorAssetLibrary

        try:
            # 레벨 에셋이 존재하는지 먼저 확인
            if not editor_asset_lib.does_asset_exist(level_path):
                unreal.log_error(f"레벨 에셋을 찾을 수 없습니다: {level_path}")
                unreal.EditorDialog.show_message(
                    unreal.Text("오류"),
                    unreal.Text(f"레벨 에셋을 찾을 수 없습니다:\n{level_path}"),
                    unreal.AppMsgType.OK
                )
                return

            # 레벨을 월드에 추가 (LevelStreamingDynamic 사용)
            new_streaming_level = unreal.EditorLevelUtils.add_level_to_world(
                editor_world,
                level_path,
                unreal.LevelStreamingDynamic
            )

            if new_streaming_level:
                level_name = level_path.split('/')[-1]
                unreal.log(f"레벨 '{level_name}'이 성공적으로 추가되었습니다.")

                # 레벨을 로드하고 보이게 설정 (editor_property 사용)
                new_streaming_level.set_editor_property("should_be_loaded", True)
                new_streaming_level.set_editor_property("should_be_visible", True)

                # 월드 아웃라이너 새로고침
                editor_asset_lib.sync_browser_to_objects([level_path])
            else:
                level_name = level_path.split('/')[-1]
                unreal.log_error(f"레벨 '{level_name}' 추가에 실패했습니다.")
                unreal.EditorDialog.show_message(
                    unreal.Text("레벨 추가 실패"),
                    unreal.Text(f"레벨 '{level_name}' 추가에 실패했습니다.\n\n가능한 원인:\n- 레벨이 이미 로드되어 있음\n- 레벨 파일에 문제가 있음"),
                    unreal.AppMsgType.OK
                )

        except Exception as e:
            error_msg = f"레벨 추가 중 오류 발생: {str(e)}"
            unreal.log_error(error_msg)
            unreal.EditorDialog.show_message(
                unreal.Text("오류"),
                unreal.Text(error_msg),
                unreal.AppMsgType.OK
            )


@unreal.uclass()
class LevelLoaderDynamicSection(unreal.ToolMenuSectionDynamic):
    """레벨 목록을 동적으로 생성하는 섹션"""

    @unreal.ufunction(override=True)
    def construct_sections(self, menu: unreal.ToolMenu, context: unreal.ToolMenuContext) -> None:
        """동적 섹션 생성 - 프로젝트의 모든 레벨을 폴더별로 그룹화하여 메뉴에 추가"""
        
        # AssetRegistry를 통해 World 타입 애셋 검색
        asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
        
        # World 클래스로 필터링
        filter = unreal.ARFilter(
            class_paths=[unreal.TopLevelAssetPath("/Script/Engine", "World")],
            package_paths=["/Game"],
            recursive_paths=True
        )
        
        # 레벨 애셋 검색
        level_assets = asset_registry.get_assets(filter)
        
        if not level_assets:
            # 레벨이 없으면 빈 메뉴
            return
        
        # 레벨을 폴더별로 그룹화
        folder_dict = {}  # {폴더_경로: [레벨_경로들]}
        
        for asset_data in level_assets:
            package_path = str(asset_data.package_name)
            
            # 폴더 경로 추출 (/Game/Folder/SubFolder/Level -> /Game/Folder/SubFolder)
            parts = package_path.rsplit('/', 1)
            if len(parts) == 2:
                folder_path = parts[0]
                level_name = parts[1]
            else:
                folder_path = "/Game"
                level_name = package_path
            
            if folder_path not in folder_dict:
                folder_dict[folder_path] = []
            folder_dict[folder_path].append(package_path)
        
        if not folder_dict:
            # 레벨이 없으면 빈 메뉴
            return
        
        # 폴더 경로 정렬
        sorted_folders = sorted(folder_dict.keys())
        
        # 폴더명 중복 체크를 위한 딕셔너리
        folder_name_count = {}
        for folder_path in sorted_folders:
            folder_name = folder_path.split('/')[-1] if folder_path != "/Game" else "Root"
            folder_name_count[folder_name] = folder_name_count.get(folder_name, 0) + 1
        
        # 메뉴 이름 가져오기
        menu_name_value = menu.menu_name
        
        # 각 폴더별로 섹션 생성
        for folder_path in sorted_folders:
            # 폴더 표시 이름 생성
            if folder_path == "/Game":
                display_name = "Root"
            else:
                folder_name = folder_path.split('/')[-1]
                # 같은 이름의 폴더가 여러 개면 상위 폴더 포함
                if folder_name_count[folder_name] > 1:
                    parts = folder_path.split('/')
                    # 마지막 2단계 표시 (상위폴더/폴더명)
                    if len(parts) >= 3:
                        display_name = f"{parts[-2]}/{folder_name}"
                    else:                        display_name = folder_name
                else:
                    display_name = folder_name
            
            # 섹션 이름 생성 (고유해야 함)
            section_name = unreal.Name(f"LevelFolder_{folder_path.replace('/', '_')}")
            
            # 섹션 추가
            section = menu.add_section(section_name, unreal.Text(f"📁 {display_name}"))
            
            # 해당 폴더의 레벨들을 정렬
            level_paths = sorted(folder_dict[folder_path])
            
            # 각 레벨에 대해 메뉴 항목 생성
            for level_path in level_paths:
                level_name = level_path.split('/')[-1]
                
                # 로드 메뉴 항목 (Replace) - name에 경로 저장
                load_script = LoadLevelEntry()
                load_script.init_entry(
                    const.OWNER,
                    menu_name_value,
                    section_name,
                    unreal.Name(level_path),  # name = 레벨 경로 (여기서 저장!)
                    unreal.Text(f"📂 {level_name}"),  # label = 레벨 이름
                    unreal.Text(f"현재 레벨을 닫고 '{level_name}' 레벨을 로드합니다.\n경로: {level_path}")
                )
                load_script.data.icon = unreal.ScriptSlateIcon(const.EDITOR_STYLE_NAME,const.ICONS_WORLD)
                load_script.register_menu_entry()
                menu.add_menu_entry_object(load_script)
                
                # 추가 메뉴 항목 (Streaming) - name에 경로 저장
                append_script = AppendLevelEntry()
                append_script.init_entry(
                    const.OWNER,
                    menu_name_value,
                    section_name,
                    unreal.Name(level_path),  # name = 레벨 경로 (여기서 저장!)
                    unreal.Text(f"{level_name}"),  # label = 레벨 이름
                    unreal.Text(f"'{level_name}' 레벨을 스트리밍 레벨로 추가합니다.\n경로: {level_path}")
                )
                append_script.data.icon = unreal.ScriptSlateIcon(const.EDITOR_STYLE_NAME,const.ICONS_WORLD2)
                append_script.register_menu_entry()
                menu.add_menu_entry_object(append_script)


def register_to(menu_name: unreal.Name):
    """레벨 로더 동적 섹션을 메뉴에 등록"""
    tool_menus = unreal.ToolMenus.get()
    menu = tool_menus.extend_menu(menu_name)
    menu.add_section(SECTION_NAME, SECTION_LABEL)
    sub_menu = menu.add_sub_menu(const.OWNER, SECTION_NAME, SUB_MENU_NAME,SUB_MENU_LABEL, SUB_MENU_TOOLTIP)
    sub_menu.style_name = "EditorStyle.Icons.World"
    # 동적 섹션 추가
    dynamic_section = LevelLoaderDynamicSection()
    sub_menu.add_dynamic_section(DYNAMIC_SECTION_NAME, dynamic_section)
    unreal.log(f"레벨 로더 동적 섹션 등록 완료: {menu.menu_name}")

def unregister():
    """레벨 로더 메뉴 등록 해제"""
    tool_menus = unreal.ToolMenus.get()
    tool_menus.unregister_owner_by_name(const.OWNER)
    tool_menus.refresh_all_widgets()
    unreal.log("레벨 로더 메뉴 등록 해제 완료")