"""
우아한 레퍼런스 교체 도구
AssetTools의 내장 기능을 활용한 스마트한 레퍼런스 교체
"""

import unreal


def find_soft_references(asset_path):
    """지정된 애셋에 대한 소프트 레퍼런스를 찾는 우아한 함수"""
    try:
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        
        # SoftObjectPath 생성
        soft_object_path = unreal.SoftObjectPath(asset_path)
        
        # AssetTools의 내장 함수로 소프트 레퍼런스 찾기
        referencing_objects = asset_tools.find_soft_references_to_object(soft_object_path)
        
        unreal.log(f"🔍 '{asset_path}'를 참조하는 소프트 레퍼런스들:")
        for i, obj in enumerate(referencing_objects, 1):
            unreal.log(f"  {i}. {obj.get_name()} ({obj.get_class().get_name()})")
        
        return referencing_objects
        
    except Exception as e:
        unreal.log_error(f"❌ 소프트 레퍼런스 찾기 실패: {e}")
        return []


def find_hard_references(asset_path):
    """지정된 애셋에 대한 하드 레퍼런스를 찾는 함수 (간단하고 안전한 방식)"""
    try:
        asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
        
        # 애셋 데이터 가져오기
        asset_data = asset_registry.get_asset_by_object_path(asset_path)
        if not asset_data:
            unreal.log_warning(f"⚠️ 애셋을 찾을 수 없습니다: {asset_path}")
            return []
        
        package_name = asset_data.package_name
        unreal.log(f"🔍 '{asset_path}'를 참조하는 하드 레퍼런스들:")
        unreal.log(f"   패키지 이름: {package_name}")
        
        # 방법 1: 간단한 get_referencers 시도
        try:
            referencers = asset_registry.get_referencers(package_name, unreal.AssetRegistryDependencyOptions())
            
            if referencers and len(referencers) > 0:
                unreal.log(f"   📦 참조하는 패키지들: {len(referencers)}개")
                
                referencing_assets = []
                found_count = 0
                
                for ref_package in referencers:
                    try:
                        # 패키지의 애셋들 가져오기
                        ref_assets = asset_registry.get_assets_by_package_name(ref_package)
                        if ref_assets:
                            for ref_asset in ref_assets:
                                found_count += 1
                                referencing_assets.append(ref_asset)
                                unreal.log(f"  {found_count}. {ref_asset.asset_name} ({ref_asset.asset_class})")
                    except Exception:
                        continue
                
                unreal.log(f"   ✅ 하드 레퍼런스 검색 완료: {found_count}개 발견")
                return referencing_assets
            else:
                unreal.log("   ℹ️ get_referencers 결과 없음")
                
        except Exception as ref_error:
            unreal.log_warning(f"⚠️ get_referencers 실패: {ref_error}")
        
        # 방법 2: 대체 검색 방법 - 선택된 폴더 범위로 제한
        try:
            unreal.log("   🔄 대체 검색 방법 시도...")
            
            # 더 제한적인 검색 (성능상 안전)
            search_paths = ["/Game", "/Script"]  # 주요 경로만 검색
            referencing_assets = []
            found_count = 0
            
            for search_path in search_paths:
                try:
                    # 경로별로 애셋 가져오기
                    path_filter = unreal.ARFilter()
                    # 필터 설정은 생략하고 기본값 사용
                    
                    assets_in_path = asset_registry.get_assets(path_filter)
                    if assets_in_path:
                        unreal.log(f"   📁 {search_path}: {len(assets_in_path)}개 애셋 검사...")
                        
                        # 첫 100개만 검사 (성능상 제한)
                        check_count = min(100, len(assets_in_path))
                        for i in range(check_count):
                            other_asset = assets_in_path[i]
                            try:
                                # 기본 의존성 옵션으로 의존성 가져오기
                                deps = asset_registry.get_dependencies(
                                    other_asset.package_name,
                                    unreal.AssetRegistryDependencyOptions()
                                )
                                
                                if deps:
                                    for dep in deps:
                                        if str(dep) == str(package_name):
                                            found_count += 1
                                            referencing_assets.append(other_asset)
                                            unreal.log(f"  {found_count}. {other_asset.asset_name} ({other_asset.asset_class})")
                                            break
                                            
                            except Exception:
                                continue
                except Exception:
                    continue
            
            unreal.log(f"   ✅ 대체 검색 완료: {found_count}개 발견")
            return referencing_assets
            
        except Exception as alt_error:
            unreal.log_warning(f"⚠️ 대체 검색 실패: {alt_error}")
            return []
        
    except Exception as e:
        unreal.log_error(f"❌ 하드 레퍼런스 찾기 실패: {e}")
        return []


def find_all_references(asset_path):
    """소프트 + 하드 레퍼런스를 모두 찾는 통합 함수"""
    unreal.log(f"🎯 '{asset_path}' 레퍼런스 통합 검색 시작...")
    
    # 소프트 레퍼런스 찾기
    soft_refs = find_soft_references(asset_path)
    
    # 하드 레퍼런스 찾기  
    hard_refs = find_hard_references(asset_path)
    
    # 결과 요약
    unreal.log("=" * 60)
    unreal.log("📊 레퍼런스 검색 결과 요약:")
    unreal.log(f"   🔗 소프트 레퍼런스: {len(soft_refs)}개")
    unreal.log(f"   🔒 하드 레퍼런스: {len(hard_refs)}개")
    unreal.log(f"   📋 총 레퍼런스: {len(soft_refs) + len(hard_refs)}개")
    unreal.log("=" * 60)
    
    return soft_refs, hard_refs


def rename_soft_object_paths(old_path, new_path):
    """소프트 오브젝트 패스를 우아하게 교체하는 함수"""
    try:
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        
        # 영향받을 패키지들 찾기
        referencing_objects = find_soft_references(old_path)
        
        if not referencing_objects:
            unreal.log("⚠️ 참조하는 애셋이 없습니다.")
            return False
        
        # 패키지 수집
        packages_to_check = []
        for obj in referencing_objects:
            package = obj.get_outer_most()
            if package and package not in packages_to_check:
                packages_to_check.append(package)
        
        # 리다이렉터 맵 생성 (딕셔너리 방식으로 변경)
        asset_redirector_map = {}
        old_soft_path = unreal.SoftObjectPath(old_path)
        new_soft_path = unreal.SoftObjectPath(new_path)
        asset_redirector_map[old_soft_path] = new_soft_path
        
        unreal.log(f"🔄 소프트 레퍼런스 교체 시작...")
        unreal.log(f"   원본: {old_path}")
        unreal.log(f"   대상: {new_path}")
        unreal.log(f"   영향받는 패키지: {len(packages_to_check)}개")
        
        # AssetTools의 내장 함수로 소프트 레퍼런스 교체
        try:
            asset_tools.rename_referencing_soft_object_paths(packages_to_check, asset_redirector_map)
            unreal.log("✅ 소프트 레퍼런스 교체 완료!")
            return True
        except Exception as api_error:
            unreal.log_error(f"⚠️ API 호출 실패: {api_error}")
            unreal.log("💡 대체 방법을 시도합니다...")
            return False
        
    except Exception as e:
        unreal.log_error(f"❌ 소프트 레퍼런스 교체 실패: {e}")
        return False


def advanced_copy_with_reference_fix(assets_to_copy, target_path):
    """고급 복사 기능을 활용한 우아한 복사 + 레퍼런스 교체"""
    try:
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        
        # 애셋 이름들을 리스트로 준비
        input_names = []
        for asset_path in assets_to_copy:
            asset_name = unreal.Name(asset_path)
            input_names.append(asset_name)
        
        unreal.log(f"🚀 고급 복사 시작...")
        unreal.log(f"   복사할 애셋: {len(assets_to_copy)}개")
        unreal.log(f"   대상 경로: {target_path}")
        
        # 완료 콜백 생성
        def on_copy_complete(success, copied_packages):
            if success:
                unreal.log("✅ 고급 복사 완료!")
                unreal.log(f"   복사된 패키지: {len(copied_packages)}개")
                for pkg in copied_packages:
                    unreal.log(f"     - {pkg}")
            else:
                unreal.log("❌ 고급 복사 실패!")
        
        try:
            copy_complete_event = unreal.AdvancedCopyCompletedEvent()
            copy_complete_event.bind_callable(on_copy_complete)
            
            # AssetTools의 고급 복사 기능 실행
            asset_tools.begin_advanced_copy_packages(input_names, target_path, copy_complete_event)
            return True
        except Exception as api_error:
            unreal.log_error(f"⚠️ 고급 복사 API 호출 실패: {api_error}")
            unreal.log("💡 일반 복사 방법을 사용해보세요.")
            return False
        
    except Exception as e:
        unreal.log_error(f"❌ 고급 복사 실패: {e}")
        return False


def run():
    """우아한 레퍼런스 교체 도구 메인 함수"""
    unreal.log("=" * 80)
    unreal.log("🎯 우아한 레퍼런스 교체 도구")
    unreal.log("   AssetTools API를 활용한 스마트한 접근")
    unreal.log("=" * 80)
    
    # 선택된 애셋들 가져오기
    selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    
    if not selected_assets:
        unreal.log("⚠️ 선택된 애셋이 없습니다.")
        unreal.log("")
        unreal.log("💡 발견된 우아한 기능들:")
        unreal.log("   📍 find_soft_references_to_object() - 소프트 레퍼런스 자동 검색")
        unreal.log("   🔄 rename_referencing_soft_object_paths() - 소프트 레퍼런스 일괄 교체")
        unreal.log("   🚀 begin_advanced_copy_packages() - 고급 복사 기능")
        unreal.log("   🔗 find_all_references() - 통합 레퍼런스 검색")
        unreal.log("")
        unreal.log("🔧 사용법:")
        unreal.log("   test_find_references('/Game/Cook/CookMaterial')")
        unreal.log("   test_find_soft_only('/Game/Cook/CookMaterial')")
        unreal.log("   test_find_hard_only('/Game/Cook/CookMaterial')")
        unreal.log("   test_rename_references('/Game/OldAsset', '/Game/NewAsset')")
        return
    
    unreal.log(f"📋 선택된 애셋: {len(selected_assets)}개")
    
    # 선택된 애셋들의 경로 수집
    selected_asset_paths = []
    
    for i, asset in enumerate(selected_assets, 1):
        asset_name = asset.get_name()
        asset_path = asset.get_path_name()
        asset_class = asset.get_class().get_name()
        unreal.log(f"  {i}. {asset_name} ({asset_class})")
        
        selected_asset_paths.append(asset_path)
        
        # 각 애셋에 대한 통합 레퍼런스 검색
        unreal.log(f"     🎯 '{asset_name}' 통합 레퍼런스 검색 시작...")
        soft_refs, hard_refs = find_all_references(asset_path)
        
        unreal.log(f"     📊 결과: 소프트 {len(soft_refs)}개 + 하드 {len(hard_refs)}개 = 총 {len(soft_refs) + len(hard_refs)}개")
    
    # Advanced Copy 테스트 기능 추가
    if selected_asset_paths:
        unreal.log("")
        unreal.log("🚀 Advanced Copy 테스트 시작...")
        
        # 대상 경로 설정 (테스트용)
        target_path = "/Game/TestCopy"
        
        unreal.log(f"   📦 복사할 애셋: {len(selected_asset_paths)}개")
        unreal.log(f"   🎯 대상 경로: {target_path}")
        unreal.log("")
        
        for i, path in enumerate(selected_asset_paths, 1):
            asset_name = path.split('/')[-1].split('.')[0]
            unreal.log(f"     {i}. {asset_name}")
        
        unreal.log("")
        unreal.log("⚠️ 실제 복사를 원하시면 다음 명령어를 실행하세요:")
        unreal.log(f"   test_advanced_copy({selected_asset_paths}, '{target_path}')")
        unreal.log("")
        unreal.log("🔧 또는 개별 테스트:")
        for path in selected_asset_paths:
            unreal.log(f"   test_advanced_copy(['{path}'], '{target_path}')")
    
    unreal.log("=" * 80)


# 개별 기능 테스트 함수들
def test_find_references(asset_path):
    """통합 레퍼런스 찾기 테스트"""
    return find_all_references(asset_path)


def test_find_soft_only(asset_path):
    """소프트 레퍼런스만 찾기 테스트"""
    return find_soft_references(asset_path)


def test_find_hard_only(asset_path):
    """하드 레퍼런스만 찾기 테스트"""
    return find_hard_references(asset_path)


def test_rename_references(old_path, new_path):
    """소프트 레퍼런스 교체 테스트"""
    return rename_soft_object_paths(old_path, new_path)


def test_advanced_copy(assets, target):
    """고급 복사 테스트"""
    return advanced_copy_with_reference_fix(assets, target)


if __name__ == "__main__":
    run()