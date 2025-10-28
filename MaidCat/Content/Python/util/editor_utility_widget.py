import unreal

def spawn(widget_blueprint_path):
    """
    언리얼 에디터 유틸리티 위젯 블루프린트를 실행하는 함수
    
    Args:
        widget_blueprint_path (str): 위젯 블루프린트의 경로 (예: "/Game/UI/MyUtilityWidget")
    
    Returns:
        bool: 성공 여부
    """
    try:
        # 에디터 유틸리티 서브시스템 가져오기
        editor_utility_subsystem = unreal.get_editor_subsystem(unreal.EditorUtilitySubsystem)
        
        if not editor_utility_subsystem:
            print("❌ EditorUtilitySubsystem을 찾을 수 없습니다.")
            return False
        
        # 위젯 블루프린트 로드
        widget_blueprint = unreal.EditorAssetLibrary.load_asset(widget_blueprint_path)
        
        if not widget_blueprint:
            print(f"❌ 위젯 블루프린트를 찾을 수 없습니다: {widget_blueprint_path}")
            return False
        
        # 위젯이 EditorUtilityWidgetBlueprint인지 확인
        if not isinstance(widget_blueprint, unreal.EditorUtilityWidgetBlueprint):
            print(f"❌ '{widget_blueprint_path}'는 EditorUtilityWidgetBlueprint가 아닙니다.")
            return False
        
        # 위젯 실행
        editor_utility_subsystem.spawn_and_register_tab(widget_blueprint)
        print(f"✅ 유틸리티 위젯 '{widget_blueprint.get_name()}'이(가) 성공적으로 실행되었습니다.")
        return True
        
    except Exception as e:
        print(f"❌ 위젯 실행 중 오류 발생: {str(e)}")
        return False

def spawn_by_name(widget_name, search_path="/Game/"):
    """
    이름으로 유틸리티 위젯을 찾아서 실행하는 함수
    
    Args:
        widget_name (str): 위젯 블루프린트의 이름
        search_path (str): 검색할 경로 (기본값: "/Game/")
    
    Returns:
        bool: 성공 여부
    """
    try:
        # 모든 에셋 목록 가져오기
        all_assets = unreal.EditorAssetLibrary.list_assets(search_path, recursive=True)
        
        # 위젯 블루프린트 찾기
        widget_blueprint_path = None
        for asset_path in all_assets:
            asset_data = unreal.EditorAssetLibrary.find_asset_data(asset_path)
            if (asset_data.asset_name == widget_name and 
                asset_data.asset_class_path.asset_name == "EditorUtilityWidgetBlueprint"):
                widget_blueprint_path = asset_path
                break
        
        if not widget_blueprint_path:
            print(f"❌ '{widget_name}' 위젯 블루프린트를 찾을 수 없습니다.")
            return False
        
        # 위젯 실행
        return spawn(widget_blueprint_path)
        
    except Exception as e:
        print(f"❌ 위젯 검색 및 실행 중 오류 발생: {str(e)}")
        return False

def close_utility_widget(widget_blueprint_path):
    """
    실행 중인 유틸리티 위젯을 닫는 함수
    
    Args:
        widget_blueprint_path (str): 위젯 블루프린트의 경로
    
    Returns:
        bool: 성공 여부
    """
    try:
        editor_utility_subsystem = unreal.get_editor_subsystem(unreal.EditorUtilitySubsystem)
        
        if not editor_utility_subsystem:
            print("❌ EditorUtilitySubsystem을 찾을 수 없습니다.")
            return False
        
        widget_blueprint = unreal.EditorAssetLibrary.load_asset(widget_blueprint_path)
        
        if not widget_blueprint:
            print(f"❌ 위젯 블루프린트를 찾을 수 없습니다: {widget_blueprint_path}")
            return False
        
        # 위젯 탭 닫기
        editor_utility_subsystem.close_tab_by_id(widget_blueprint.get_name())
        print(f"✅ 유틸리티 위젯 '{widget_blueprint.get_name()}'이(가) 닫혔습니다.")
        return True
        
    except Exception as e:
        print(f"❌ 위젯 닫기 중 오류 발생: {str(e)}")
        return False

def get_running_utility_widgets():
    """
    현재 실행 중인 유틸리티 위젯 목록을 가져오는 함수
    
    Returns:
        list: 실행 중인 위젯 목록
    """
    try:
        editor_utility_subsystem = unreal.get_editor_subsystem(unreal.EditorUtilitySubsystem)
        
        if not editor_utility_subsystem:
            print("❌ EditorUtilitySubsystem을 찾을 수 없습니다.")
            return []
        
        # 실행 중인 위젯 목록 가져오기 (이 기능은 언리얼 버전에 따라 사용 가능하지 않을 수 있음)
        running_widgets = []
        print("📋 실행 중인 유틸리티 위젯 목록:")
        
        # 현재 열린 탭들을 확인하는 방법은 제한적이므로
        # 이 함수는 참고용으로만 사용
        print("ℹ️  현재 언리얼 Python API에서는 실행 중인 위젯 목록을 직접 가져오는 기능이 제한적입니다.")
        
        return running_widgets
        
    except Exception as e:
        print(f"❌ 실행 중인 위젯 목록 가져오기 중 오류 발생: {str(e)}")
        return []
