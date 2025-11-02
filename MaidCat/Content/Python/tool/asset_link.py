"""
MaidCat Asset Web Link Handler

모든 애셋 타입에 대한 웹링크 기능을 담당하는 모듈
- JSON 기반 애셋-웹링크 매핑
- 기존 material_web_links.json 형식 유지

Author: MaidCat Team
"""

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
            print(f"⚠️ JSON 파일을 찾을 수 없습니다: {json_path}")
            return {}
    except Exception as e:
        print(f"❌ JSON 파일 로드 실패: {e}")
        return {}


# ================================
# 메인 핸들러 함수
# ================================

def handle_material_button_click(context):
    """기존 머티리얼 버튼 클릭 처리 (호환성을 위해 유지)"""
    handle_asset_button_click(context)


def handle_asset_button_click(context):
    """애셋 버튼 클릭 처리"""
    ctx = context.find_by_class(unreal.AssetEditorToolkitMenuContext)
    objects = ctx.get_editing_objects()
    
    for obj in objects:
        # MaterialInstanceConstant만 지원 (기존 로직 유지)
        if obj.get_class().get_name() != "MaterialInstanceConstant":
            continue
        
        # 애셋의 경로 출력
        asset_path = unreal.EditorAssetLibrary.get_path_name_for_loaded_asset(obj)
        print(f"Asset Path: {asset_path}")
        
        # 부모 애셋 정보 가져오기
        parent_asset = obj.get_editor_property('parent')
        if parent_asset:
            _process_parent_asset(parent_asset)
        else:
            print("❌ 부모 애셋을 찾을 수 없습니다.")


def _process_parent_asset(parent_asset):
    """부모 애셋 정보 처리 및 웹페이지 열기"""
    # 부모 애셋의 다양한 경로 정보 수집
    parent_path = unreal.EditorAssetLibrary.get_path_name_for_loaded_asset(parent_asset)
    parent_package_path = parent_asset.get_package().get_name()
    parent_name = parent_asset.get_name()
    
    print(f"Parent Asset: {parent_name}")
    print(f"Parent Asset Path: {parent_path}")
    print(f"Parent Asset Package Path: {parent_package_path}")
    
    # JSON에서 웹주소 조회 및 웹페이지 열기
    _open_web_page_from_json(parent_package_path, parent_path, parent_name)


def _open_web_page_from_json(package_path, asset_path, asset_name):
    """JSON에서 애셋 정보를 찾아 웹페이지 열기 (3단계 매칭)"""
    try:
        # 최신 JSON 데이터 로드
        asset_links = load_asset_web_links()
        
        # 3단계 매칭 시도
        search_attempts = [
            (package_path, "패키지 경로"),
            (asset_path, "전체 경로"), 
            (asset_name, "애셋 이름")
        ]
        
        for search_key, search_type in search_attempts:
            asset_info = asset_links.get(search_key)
            if asset_info:
                _handle_asset_found(asset_info, search_key, search_type)
                return
        
        # 모든 매칭 실패 시
        _handle_asset_not_found(package_path, asset_path, asset_name, asset_links)
            
    except Exception as e:
        print(f"❌ JSON 조회 오류: {e}")


def _handle_asset_found(asset_info, search_key, search_type):
    """매칭된 애셋 정보 처리"""
    description = asset_info.get('description', '')
    url = asset_info.get('url', '')
    
    if url:
        print(f"✅ 애셋 매칭 ({search_type}): {search_key}")
        print(f"📖 설명: {description}")
        print(f"🌐 웹페이지 열기: {url}")
        _open_web_browser(url)
    else:
        print(f"❌ URL이 설정되지 않았습니다: {search_key}")


def _handle_asset_not_found(package_path, asset_path, asset_name, asset_links):
    """애셋을 찾지 못한 경우 처리"""
    print(f"❌ JSON에서 애셋을 찾을 수 없습니다:")
    print(f"   - 패키지 경로: {package_path}")
    print(f"   - 전체 경로: {asset_path}")
    print(f"   - 이름: {asset_name}")
    print(f"💡 JSON에 등록된 애셋: {list(asset_links.keys())}")


def _open_web_browser(url):
    """웹브라우저에서 URL 열기 (fallback 포함)"""
    try:
        import webbrowser
        webbrowser.open(url)
        print(f"✅ 웹브라우저에서 열렸습니다: {url}")
    except Exception as e:
        print(f"❌ 웹브라우저 열기 실패: {e}")
        # 대안: 언리얼 엔진의 시스템 브라우저 사용
        try:
            unreal.SystemLibrary.launch_url(url)
            print(f"✅ 시스템 브라우저에서 열렸습니다: {url}")
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
        
        print(f"✅ 애셋 정보가 JSON에 추가되었습니다: {asset_path}")
        
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
            
            print(f"✅ 애셋 정보가 JSON에서 제거되었습니다: {asset_path}")
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