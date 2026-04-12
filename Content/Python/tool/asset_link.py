import unreal
import json
import os

# ================================
# JSON 파일 관리
# ================================

def get_json_file_path():
    """JSON 파일의 절대 경로를 반환"""
    project_dir = unreal.Paths.project_dir()
    json_path = os.path.join(project_dir, 'material_web_links.json')
    return json_path


def load_asset_web_links():
    """JSON 파일에서 애셋-웹링크 매핑 로드"""
    try:
        json_path = get_json_file_path()
        
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('material_web_links', {})
        else:
            _prompt_create_data_file(json_path)
            return {}
    except Exception as e:
        print(f"❌ JSON 파일 로드 실패: {e}")
        return {}


def _prompt_create_data_file(json_path):
    """데이터 파일이 없을 때 새로 생성할지 물어보기"""
    try:
        title = "데이터 파일 없음"
        message = f"애셋 웹링크 데이터 파일이 없습니다.\n\n새로 생성하시겠습니까?\n\n경로: {json_path}"
        
        result = unreal.EditorDialog.show_message(
            unreal.Text(title),
            unreal.Text(message),
            unreal.AppMsgType.YES_NO
        )
        
        if result == unreal.AppReturnType.YES:
            _create_empty_data_file(json_path)
            
    except Exception as e:
        print(f"❌ 데이터 파일 생성 다이얼로그 실패: {e}")


def _create_empty_data_file(json_path):
    """빈 데이터 파일 생성"""
    try:
        # 기본 구조의 빈 JSON 파일 생성
        empty_data = {
            "material_web_links": {},
            "_comment": "MaidCat Asset Web Links - 애셋과 웹페이지 연결 정보"
        }
        
        # 디렉토리 생성 (필요한 경우)
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        
        # 파일 생성
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(empty_data, f, indent=2, ensure_ascii=False)
        
    except Exception as e:
        print(f"❌ 데이터 파일 생성 실패: {e}")


# ================================
# 메인 핸들러 함수
# ================================
def handle_asset_button_click(context):
    """애셋 버튼 클릭 처리"""
    ctx = context.find_by_class(unreal.AssetEditorToolkitMenuContext)
    objects = ctx.get_editing_objects()
    
    for obj in objects:
        _process_asset_hierarchy(obj)


def _process_asset_hierarchy(asset):
    """애셋 계층구조를 탐색하여 웹링크 찾기 (우선순위별)"""
    candidates = []
    
    # Asset Registry에서 추가 정보 가져오기
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    asset_data = asset_registry.get_asset_by_object_path(asset.get_path_name())
    
    # 1. 현재 애셋 자체
    current_path = unreal.EditorAssetLibrary.get_path_name_for_loaded_asset(asset)
    current_package_path = asset.get_package().get_name()
    current_name = asset.get_name()
    current_class = asset.get_class().get_name()
    
    candidates.extend([
        (current_package_path, f"현재 애셋 (패키지): {current_name}"),
        (current_path, f"현재 애셋 (경로): {current_name}"),
        (current_name, f"현재 애셋 (이름): {current_name}")
    ])
    
    # 2. Asset Data에서 추가 정보 수집
    if asset_data:
        # 애셋 태그들 (메타데이터)
        asset_tags = asset_data.tag_values_and_names
        for tag_name, tag_value in asset_tags.items():
            if tag_value and str(tag_value).strip():
                candidates.append((str(tag_value), f"태그 {tag_name}: {tag_value}"))
        
        # 애셋 클래스 경로
        asset_class_path = str(asset_data.asset_class_path)
        if asset_class_path:
            candidates.append((asset_class_path, f"클래스 경로: {asset_class_path}"))
        
        # 패키지 패스 정보
        package_path = str(asset_data.package_path)
        if package_path and package_path != current_package_path:
            candidates.append((package_path, f"패키지 패스: {package_path}"))
        
        # 추가적인 Asset Registry 정보들
        try:
            # 애셋의 의존성 정보 (있는 경우)
            dependencies = asset_registry.get_dependencies(
                asset_data.package_name, 
                unreal.AssetRegistryDependencyOptions()
            )
            if dependencies:
                count = 0
                for dep in dependencies:
                    if count >= 3:  # 최대 3개까지만
                        break
                    dep_name = str(dep)
                    if dep_name and not dep_name.startswith('/Script/'):  # 스크립트 의존성 제외
                        candidates.append((dep_name, f"의존성: {dep_name}"))
                        count += 1
        except:
            pass  # 의존성 정보가 없어도 계속 진행
    
    # 3. 부모 애셋들 (MaterialInstance 등의 경우)
    parent_assets = _get_parent_chain(asset)
    for i, parent in enumerate(parent_assets):
        parent_path = unreal.EditorAssetLibrary.get_path_name_for_loaded_asset(parent)
        parent_package_path = parent.get_package().get_name()
        parent_name = parent.get_name()
        
        level = "부모" if i == 0 else f"{i+1}단계 부모"
        candidates.extend([
            (parent_package_path, f"{level} 애셋 (패키지): {parent_name}"),
            (parent_path, f"{level} 애셋 (경로): {parent_name}"),
            (parent_name, f"{level} 애셋 (이름): {parent_name}")
        ])
        
        # 부모 애셋의 Asset Data도 확인
        parent_asset_data = asset_registry.get_asset_by_object_path(parent.get_path_name())
        if parent_asset_data:
            parent_tags = parent_asset_data.tag_values_and_names
            for tag_name, tag_value in parent_tags.items():
                if tag_value and str(tag_value).strip():
                    candidates.append((str(tag_value), f"{level} 태그 {tag_name}: {tag_value}"))
    
    # 4. 클래스 타입 및 관련 정보
    candidates.append((current_class, f"클래스 타입: {current_class}"))
    
    # 클래스 계층구조 (부모 클래스들)
    class_hierarchy = _get_class_hierarchy(asset.get_class())
    for i, parent_class in enumerate(class_hierarchy):
        candidates.append((parent_class, f"부모 클래스 {i+1}: {parent_class}"))
    
    # 우선순위별로 JSON에서 검색
    _search_candidates_in_json(candidates, current_package_path, current_path, current_name)


def _get_class_hierarchy(asset_class):
    """클래스의 상속 계층구조를 반환"""
    hierarchy = []
    current_class = asset_class
    max_depth = 5  # 무한 루프 방지
    
    for _ in range(max_depth):
        parent_class = current_class.get_super_class()
        if parent_class and parent_class != current_class:
            parent_name = parent_class.get_name()
            if parent_name not in ['Object', 'UObject']:  # 기본 오브젝트 클래스는 제외
                hierarchy.append(parent_name)
                current_class = parent_class
            else:
                break
        else:
            break
    
    return hierarchy


def _get_parent_chain(asset):
    """애셋의 부모 체인을 반환 (최대 3단계까지)"""
    parents = []
    current = asset
    max_depth = 3
    
    for _ in range(max_depth):
        parent = None
        
        # MaterialInstance의 부모 머티리얼
        if hasattr(current, 'get_editor_property'):
            try:
                parent = current.get_editor_property('parent')
            except:
                pass
        
        # 다른 타입의 부모 관계도 여기에 추가 가능
        # if isinstance(current, unreal.SomeOtherType):
        #     parent = current.get_some_parent()
        
        if parent and parent != current:
            parents.append(parent)
            current = parent
        else:
            break
    
    return parents


def _search_candidates_in_json(candidates, fallback_package_path, fallback_path, fallback_name):
    """후보들을 순서대로 JSON에서 검색"""
    try:
        asset_links = load_asset_web_links()
        
        # 우선순위별로 검색
        for search_key, description in candidates:
            asset_info = asset_links.get(search_key)
            if asset_info:
                print(f"✅ 매칭됨: {description}")
                _handle_asset_found(asset_info, search_key, description)
                return
        
        # 모든 후보에서 매칭 실패
        _handle_asset_not_found(fallback_package_path, fallback_path, fallback_name)
            
    except Exception as e:
        print(f"❌ JSON 조회 오류: {e}")


def _handle_asset_found(asset_info, search_key, search_type):
    """매칭된 애셋 정보 처리"""
    description = asset_info.get('description', '')
    url = asset_info.get('url', '')
    
    if url:
        _open_web_browser(url)
    else:
        print(f"❌ URL이 설정되지 않았습니다: {search_key}")


def _handle_asset_not_found(package_path, asset_path, asset_name):
    """애셋을 찾지 못한 경우 처리"""
    # 사용자에게 새로 추가할지 물어보기
    _prompt_add_new_asset(package_path, asset_path, asset_name)


def _prompt_add_new_asset(package_path, asset_path, asset_name):
    """사용자에게 새 애셋 정보 추가 여부를 물어보기"""
    try:
        # 언리얼 엔진의 다이얼로그 사용
        title = "애셋 정보 없음"
        message = f"'{asset_name}' 애셋에 대한 웹링크 정보가 없습니다.\n\n새로 추가하시겠습니까?"
        
        # 언리얼 엔진 다이얼로그로 Yes/No 선택
        result = unreal.EditorDialog.show_message(
            unreal.Text(title), 
            unreal.Text(message), 
            unreal.AppMsgType.YES_NO
        )
        
        if result == unreal.AppReturnType.YES:
            # JSON 파일을 기본 편집기로 열기
            json_path = get_json_file_path()
            try:
                import subprocess
                import platform
                
                system = platform.system()
                if system == "Windows":
                    subprocess.run(['start', json_path], shell=True, check=True)
                elif system == "Darwin":  # macOS
                    subprocess.run(['open', json_path], check=True)
                else:  # Linux
                    subprocess.run(['xdg-open', json_path], check=True)
                
                print("💡 다음 형식으로 애셋 정보를 추가하세요:")
                print(f'    "{package_path}": {{')
                print(f'        "description": "설명을 입력하세요",')
                print(f'        "url": "https://웹주소.com"')
                print(f'    }}')
                
            except Exception as e:
                print(f"❌ 파일 열기 실패: {e}")
                print("💡 수동으로 다음 함수를 사용하여 추가할 수 있습니다:")
                print(f"   asset_link.add_asset_to_json(")
                print(f"       asset_path='{package_path}',")
                print(f"       description='설명을 입력하세요',")
                print(f"       url='https://웹주소.com'")
                print(f"   )")
        else:
            print("❌ 사용자가 새 애셋 정보 추가를 취소했습니다.")
            
    except Exception as e:
        print(f"❌ 다이얼로그 표시 실패: {e}")
        print("💡 수동으로 다음 함수를 사용하여 추가할 수 있습니다:")
        print(f"   asset_link.add_asset_to_json('{package_path}', '설명', 'URL')")


def _open_web_browser(url):
    """웹브라우저에서 URL 열기 (fallback 포함)"""
    try:
        import webbrowser
        webbrowser.open(url)
    except Exception as e:
        print(f"❌ 웹브라우저 열기 실패: {e}")
        # 대안: 언리얼 엔진의 시스템 브라우저 사용
        try:
            unreal.SystemLibrary.launch_url(url)
        except:
            print(f"❌ 시스템 브라우저 열기도 실패했습니다: {url}")


# ================================
# JSON 관리 유틸리티 함수들
# ================================

def add_asset_to_json(asset_path, description, url):
    """JSON 파일에 새 애셋 정보 추가"""
    try:
        json_path = get_json_file_path()
        
        # 기존 데이터 로드
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"material_web_links": {}}
        
        # 새 정보 추가
        data["material_web_links"][asset_path] = {
            "description": description,
            "url": url
        }
        
        # 파일 저장
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
    except Exception as e:
        print(f"❌ JSON 저장 실패: {e}")


def remove_asset_from_json(asset_path):
    """JSON 파일에서 애셋 정보 제거"""
    try:
        json_path = get_json_file_path()
        
        if not os.path.exists(json_path):
            print("❌ JSON 파일이 존재하지 않습니다.")
            return
        
        # 기존 데이터 로드
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 정보 제거
        if asset_path in data.get("material_web_links", {}):
            del data["material_web_links"][asset_path]
            
            # 파일 저장
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            print(f"❌ JSON에서 해당 애셋을 찾을 수 없습니다: {asset_path}")
        
    except Exception as e:
        print(f"❌ JSON 제거 실패: {e}")


def list_assets_in_json():
    """JSON에 등록된 모든 애셋 목록 출력"""
    try:
        asset_links = load_asset_web_links()
        
        if asset_links:
            print("📋 JSON에 등록된 애셋 목록:")
            for i, (path, info) in enumerate(asset_links.items(), 1):
                print(f"{i:2d}. {path}")
                print(f"    📖 {info.get('description', 'N/A')}")
                print(f"    🌐 {info.get('url', 'N/A')}")
                print()
        else:
            print("❌ JSON에 등록된 애셋이 없습니다.")
    
    except Exception as e:
        print(f"❌ JSON 목록 조회 실패: {e}")


# ================================
# 호환성을 위한 기존 함수명들
# ================================

def add_material_to_json(material_path, description, url):
    """기존 함수명 호환성 유지"""
    add_asset_to_json(material_path, description, url)


def remove_material_from_json(material_path):
    """기존 함수명 호환성 유지"""
    remove_asset_from_json(material_path)


def list_materials_in_json():
    """기존 함수명 호환성 유지"""
    list_assets_in_json()