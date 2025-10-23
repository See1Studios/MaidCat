"""
Unreal Engine begin_advanced_copy_packages 함수 상세 테스트

이 스크립트는 다음을 테스트합니다:
1. begin_advanced_copy_packages 함수의 기본 사용법
2. 대안 복사 방법들
3. 오류 처리 및 디버깅

사용법:
1. Unreal Editor에서 Content Browser에서 애셋을 선택
2. 이 스크립트를 실행
3. /Game/Test 폴더에 복사된 애셋 확인
"""

import unreal


def print_separator(title=""):
    """구분선 출력"""
    print("\n" + "=" * 60)
    if title:
        print(f" {title}")
        print("=" * 60)


def get_selected_assets():
    """선택된 애셋들 가져오기"""
    editor_utility = unreal.EditorUtilityLibrary()
    selected_assets = editor_utility.get_selected_assets()
    
    print(f"선택된 애셋 수: {len(selected_assets)}")
    for i, asset in enumerate(selected_assets, 1):
        print(f"  {i}. {asset.get_path_name()}")
        print(f"     타입: {asset.get_class().get_name()}")
    
    return selected_assets


def test_asset_tools_methods():
    """AssetTools 클래스의 다양한 메서드 테스트"""
    print_separator("AssetTools 메서드 테스트")
    
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    
    # AssetTools 인스턴스 정보 확인
    print(f"AssetTools 인스턴스: {asset_tools}")
    print(f"AssetTools 클래스: {asset_tools.get_class().get_name()}")
    
    # 사용 가능한 메서드들 확인
    available_methods = [method for method in dir(asset_tools) if not method.startswith('_')]
    print(f"사용 가능한 메서드 수: {len(available_methods)}")
    
    # begin_advanced_copy_packages 메서드 존재 확인
    if hasattr(asset_tools, 'begin_advanced_copy_packages'):
        print("✅ begin_advanced_copy_packages 메서드 존재")
        
        # 메서드 정보 확인
        method = getattr(asset_tools, 'begin_advanced_copy_packages')
        print(f"   메서드 타입: {type(method)}")
        
        # 메서드 문서 확인
        if hasattr(method, '__doc__') and method.__doc__:
            print(f"   문서: {method.__doc__}")
        else:
            print("   문서: 없음")
    else:
        print("❌ begin_advanced_copy_packages 메서드 없음")
        print("   대신 사용 가능한 복사 관련 메서드들:")
        copy_methods = [m for m in available_methods if 'copy' in m.lower() or 'duplicate' in m.lower()]
        for method in copy_methods:
            print(f"     - {method}")


def test_begin_advanced_copy_with_different_approaches():
    """다양한 방법으로 begin_advanced_copy_packages 테스트"""
    print_separator("begin_advanced_copy_packages 다양한 접근법 테스트")
    
    selected_assets = get_selected_assets()
    if not selected_assets:
        print("❌ 선택된 애셋이 없습니다.")
        return
    
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    target_path = "/Game/Test"
    
    # 방법 1: 단순 리스트로 asset paths 전달
    print("\n--- 방법 1: asset paths를 문자열 리스트로 전달 ---")
    try:
        asset_paths = [asset.get_path_name() for asset in selected_assets]
        print(f"전달할 경로들: {asset_paths}")
        
        # 간단한 콜백 함수
        def simple_callback():
            print("✅ 콜백 호출됨!")
        
        asset_tools.begin_advanced_copy_packages(
            asset_paths,
            target_path,
            simple_callback
        )
        print("✅ 방법 1 실행 성공")
        
    except Exception as e:
        print(f"❌ 방법 1 실패: {str(e)}")
    
    # 방법 2: unreal.Name 객체들의 리스트
    print("\n--- 방법 2: unreal.Name 객체 리스트로 전달 ---")
    try:
        asset_names = [unreal.Name(asset.get_path_name()) for asset in selected_assets]
        print(f"Name 객체 수: {len(asset_names)}")
        
        def name_callback():
            print("✅ Name 방식 콜백 호출됨!")
        
        asset_tools.begin_advanced_copy_packages(
            asset_names,
            target_path,
            name_callback
        )
        print("✅ 방법 2 실행 성공")
        
    except Exception as e:
        print(f"❌ 방법 2 실패: {str(e)}")
    
    # 방법 3: None 콜백으로 테스트
    print("\n--- 방법 3: None 콜백으로 테스트 ---")
    try:
        asset_names = [unreal.Name(asset.get_path_name()) for asset in selected_assets]
        
        asset_tools.begin_advanced_copy_packages(
            asset_names,
            target_path,
            None
        )
        print("✅ 방법 3 실행 성공")
        
    except Exception as e:
        print(f"❌ 방법 3 실패: {str(e)}")


def test_duplicate_asset_alternative():
    """duplicate_asset을 이용한 대안 방법"""
    print_separator("duplicate_asset 대안 방법 테스트")
    
    selected_assets = get_selected_assets()
    if not selected_assets:
        print("❌ 선택된 애셋이 없습니다.")
        return
    
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    target_path = "/Game/Test"
    
    # 각 애셋을 개별적으로 복사
    for i, asset in enumerate(selected_assets, 1):
        try:
            asset_name = asset.get_name()
            new_name = f"{asset_name}_AdvCopyTest_{i}"
            
            print(f"복사 중 {i}/{len(selected_assets)}: {asset_name} -> {new_name}")
            
            duplicated = asset_tools.duplicate_asset(
                new_name,
                target_path,
                asset
            )
            
            if duplicated:
                print(f"✅ 성공: {duplicated.get_path_name()}")
            else:
                print(f"❌ 실패: None 반환")
                
        except Exception as e:
            print(f"❌ 오류: {str(e)}")


def check_target_directory():
    """대상 디렉토리 상태 확인"""
    print_separator("대상 디렉토리 확인")
    
    target_path = "/Game/Test"
    
    # EditorAssetLibrary를 사용해 디렉토리 내용 확인
    try:
        # 디렉토리가 존재하는지 확인
        editor_asset_lib = unreal.EditorAssetLibrary()
        
        # 디렉토리 생성 시도
        if not editor_asset_lib.does_directory_exist(target_path):
            print(f"📁 디렉토리가 존재하지 않음: {target_path}")
            print("   디렉토리를 생성해보겠습니다...")
            
            success = editor_asset_lib.make_directory(target_path)
            if success:
                print("✅ 디렉토리 생성 성공")
            else:
                print("❌ 디렉토리 생성 실패")
        else:
            print(f"✅ 디렉토리 존재: {target_path}")
        
        # 디렉토리 내용 확인
        assets_in_dir = editor_asset_lib.list_assets(target_path, recursive=False)
        print(f"디렉토리 내 애셋 수: {len(assets_in_dir)}")
        
        for asset_path in assets_in_dir[:10]:  # 최대 10개만 표시
            print(f"  - {asset_path}")
        
        if len(assets_in_dir) > 10:
            print(f"  ... 외 {len(assets_in_dir) - 10}개")
            
    except Exception as e:
        print(f"❌ 디렉토리 확인 중 오류: {str(e)}")


def main():
    """메인 테스트 실행"""
    print("🚀 Unreal Engine begin_advanced_copy_packages 상세 테스트 시작")
    
    # 1. 대상 디렉토리 확인
    check_target_directory()
    
    # 2. AssetTools 메서드 확인
    test_asset_tools_methods()
    
    # 3. 다양한 방법으로 begin_advanced_copy_packages 테스트
    test_begin_advanced_copy_with_different_approaches()
    
    # 4. 대안 방법 테스트
    test_duplicate_asset_alternative()
    
    print_separator("테스트 완료")
    print("✅ 모든 테스트가 완료되었습니다.")
    print("📁 /Game/Test 폴더를 확인해보세요.")


if __name__ == "__main__":
    main()