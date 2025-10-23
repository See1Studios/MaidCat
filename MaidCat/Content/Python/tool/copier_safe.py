"""
🛡️ Unreal Engine 안전한 애셋 복사 도구

⚠️ 중요: begin_advanced_copy_packages는 에디터 크래시를 일으킬 수 있습니다!

✅ 안전한 사용법:
1. Content Browser에서 복사할 애셋들을 선택
2. Python 콘솔에서 실행:
   exec(open('d:/GitHub/MaidCat/MaidCat/Content/Python/tool/copier_safe.py').read())
   safe_copy()  # 안전한 방법
   
def test_find_soft_references():
    """
    🔍 find_soft_references_to_object 함수 테스트
    선택한 애셋을 참조하는 다른 애셋들을 찾습니다
    """
    print("🔍 Soft Reference 탐지 테스트 시작...")
    print("=" * 60)
    
    # 선택된 애셋 확인
    editor_utility = unreal.EditorUtilityLibrary()
    selected_assets = editor_utility.get_selected_assets()
    
    if not selected_assets:
        print("❌ 선택된 애셋이 없습니다. Content Browser에서 애셋을 선택한 후 다시 시도하세요.")
        return False
    
    # AssetTools 가져오기
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    
    print(f"📦 선택된 애셋: {len(selected_assets)}개")
    print()
    
    total_references_found = 0
    
    for i, asset in enumerate(selected_assets, 1):
        try:
            asset_path = asset.get_path_name()
            asset_name = asset.get_name()
            asset_class = asset.get_class().get_name()
            
            print(f"🎯 [{i}/{len(selected_assets)}] 분석 중: {asset_name}")
            print(f"   경로: {asset_path}")
            print(f"   타입: {asset_class}")
            
            # 애셋을 SoftObjectPath로 변환
            soft_object_path = unreal.SoftObjectPath(asset_path)
            print(f"   SoftObjectPath: {soft_object_path}")
            
            # soft reference를 찾는 함수 호출
            print("   🔍 Soft Reference 검색 중...")
            
            referencing_objects = asset_tools.find_soft_references_to_object(soft_object_path)
            
            print(f"   📊 발견된 참조: {len(referencing_objects)}개")
            
            if referencing_objects:
                total_references_found += len(referencing_objects)
                
                print(f"   📋 참조하는 애셋들:")
                for j, ref_obj in enumerate(referencing_objects, 1):
                    try:
                        ref_path = ref_obj.get_path_name()
                        ref_name = ref_obj.get_name()
                        ref_class = ref_obj.get_class().get_name()
                        
                        print(f"      {j}. {ref_name} ({ref_class})")
                        print(f"         경로: {ref_path}")
                        
                        # 참조하는 애셋의 추가 정보
                        if hasattr(ref_obj, 'get_outer') and ref_obj.get_outer():
                            outer = ref_obj.get_outer()
                            print(f"         패키지: {outer.get_name()}")
                        
                    except Exception as e:
                        print(f"      {j}. ❌ 참조 정보 읽기 오류: {str(e)}")
                
                # 참조 관계 분석
                print(f"   🔗 참조 관계 분석:")
                material_refs = [obj for obj in referencing_objects if 'Material' in obj.get_class().get_name()]
                blueprint_refs = [obj for obj in referencing_objects if 'Blueprint' in obj.get_class().get_name()]
                mesh_refs = [obj for obj in referencing_objects if 'Mesh' in obj.get_class().get_name()]
                other_refs = [obj for obj in referencing_objects if obj not in material_refs + blueprint_refs + mesh_refs]
                
                if material_refs:
                    print(f"      🎨 머티리얼: {len(material_refs)}개")
                if blueprint_refs:
                    print(f"      📘 블루프린트: {len(blueprint_refs)}개")
                if mesh_refs:
                    print(f"      🧊 메시: {len(mesh_refs)}개")
                if other_refs:
                    print(f"      📦 기타: {len(other_refs)}개")
                    
            else:
                print("   ✅ 이 애셋을 참조하는 다른 애셋이 없습니다.")
            
            print()
            
        except Exception as e:
            print(f"   ❌ 오류 발생: {str(e)}")
            print()
    
    # 최종 요약
    print("=" * 60)
    print(f"📊 Soft Reference 검색 완료")
    print(f"   🎯 검색한 애셋: {len(selected_assets)}개")
    print(f"   🔗 총 발견된 참조: {total_references_found}개")
    print(f"   📈 평균 참조 수: {total_references_found/len(selected_assets):.1f}개/애셋")
    
    if total_references_found == 0:
        print("\n💡 팁:")
        print("   - 텍스처나 머티리얼을 선택해보세요 (더 많은 참조 관계가 있을 수 있습니다)")
        print("   - 사용 중인 애셋을 선택해보세요")
        print("   - Blueprint에서 사용되는 애셋을 선택해보세요")
    
    return total_references_found > 0


def analyze_asset_dependencies():
    """
    🕸️ 선택한 애셋의 의존성 관계 상세 분석
    """
    print("🕸️ 애셋 의존성 관계 상세 분석 시작...")
    print("=" * 60)
    
    # 선택된 애셋 확인
    editor_utility = unreal.EditorUtilityLibrary()
    selected_assets = editor_utility.get_selected_assets()
    
    if not selected_assets:
        print("❌ 선택된 애셋이 없습니다.")
        return False
    
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    
    for i, asset in enumerate(selected_assets, 1):
        try:
            asset_path = asset.get_path_name()
            asset_name = asset.get_name()
            asset_class = asset.get_class().get_name()
            
            print(f"🎯 [{i}/{len(selected_assets)}] 의존성 분석: {asset_name}")
            print(f"   📁 경로: {asset_path}")
            print(f"   🏷️ 타입: {asset_class}")
            
            # SoftObjectPath 생성
            soft_path = unreal.SoftObjectPath(asset_path)
            
            # 1. 이 애셋을 참조하는 애셋들 찾기 (Incoming References)
            print(f"\n   🔍 1. 이 애셋을 참조하는 애셋들 (Incoming References):")
            incoming_refs = asset_tools.find_soft_references_to_object(soft_path)
            
            if incoming_refs:
                print(f"      📊 {len(incoming_refs)}개 발견")
                
                # 타입별 분류
                ref_by_type = {}
                for ref in incoming_refs:
                    ref_type = ref.get_class().get_name()
                    if ref_type not in ref_by_type:
                        ref_by_type[ref_type] = []
                    ref_by_type[ref_type].append(ref)
                
                for ref_type, refs in ref_by_type.items():
                    print(f"      📂 {ref_type}: {len(refs)}개")
                    for ref in refs[:3]:  # 최대 3개만 표시
                        print(f"         - {ref.get_name()}")
                    if len(refs) > 3:
                        print(f"         ... 외 {len(refs)-3}개")
            else:
                print(f"      ✅ 없음")
            
            # 2. 애셋 정보 상세 분석
            print(f"\n   📊 2. 애셋 상세 정보:")
            
            # 파일 크기 (추정)
            try:
                # AssetRegistry를 통한 정보 조회
                asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
                asset_data = asset_registry.get_asset_by_object_path(soft_path)
                
                if asset_data:
                    print(f"      📦 패키지: {asset_data.package_name}")
                    print(f"      🏷️ 애셋 클래스: {asset_data.asset_class}")
                    
                    # 태그 정보
                    tags = asset_data.tag_values_and_ranges
                    if tags:
                        print(f"      🏷️ 태그: {len(tags)}개")
                        for tag_name in list(tags.keys())[:5]:  # 최대 5개만 표시
                            print(f"         - {tag_name}")
                
            except Exception as e:
                print(f"      ⚠️ 상세 정보 조회 실패: {str(e)}")
            
            # 3. 메모리 사용량 (로드된 경우)
            print(f"\n   � 3. 메모리 정보:")
            try:
                if hasattr(asset, 'get_resource_size_bytes'):
                    size_bytes = asset.get_resource_size_bytes()
                    size_mb = size_bytes / (1024 * 1024)
                    print(f"      📏 메모리 사용량: {size_mb:.2f} MB")
                else:
                    print(f"      ⚠️ 메모리 사용량 정보 없음")
            except Exception as e:
                print(f"      ⚠️ 메모리 정보 조회 실패: {str(e)}")
            
            print(f"\n" + "-" * 50)
            
        except Exception as e:
            print(f"   ❌ 분석 오류: {str(e)}")
            print(f"\n" + "-" * 50)
    
    print("\n✅ 의존성 분석 완료!")
    return True


def find_unused_assets():
    """
    🗑️ 사용되지 않는 애셋 찾기 (참조가 없는 애셋들)
    """
    print("🗑️ 사용되지 않는 애셋 검색 시작...")
    print("=" * 60)
    print("⚠️ 이 작업은 시간이 오래 걸릴 수 있습니다.")
    
    # 선택된 애셋 확인
    editor_utility = unreal.EditorUtilityLibrary()
    selected_assets = editor_utility.get_selected_assets()
    
    if not selected_assets:
        print("❌ 선택된 애셋이 없습니다.")
        print("💡 팁: 특정 폴더의 애셋들을 선택하여 해당 폴더의 미사용 애셋을 찾아보세요.")
        return False
    
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    unused_assets = []
    used_assets = []
    
    print(f"📦 검사할 애셋: {len(selected_assets)}개")
    print()
    
    for i, asset in enumerate(selected_assets, 1):
        try:
            asset_name = asset.get_name()
            asset_path = asset.get_path_name()
            
            print(f"🔍 [{i}/{len(selected_assets)}] 검사 중: {asset_name}")
            
            # SoftObjectPath 생성
            soft_path = unreal.SoftObjectPath(asset_path)
            
            # 참조하는 애셋들 찾기
            references = asset_tools.find_soft_references_to_object(soft_path)
            
            if references:
                used_assets.append((asset, len(references)))
                print(f"   ✅ 사용됨 ({len(references)}개 참조)")
            else:
                unused_assets.append(asset)
                print(f"   🗑️ 미사용 (참조 없음)")
            
        except Exception as e:
            print(f"   ❌ 검사 오류: {str(e)}")
    
    # 결과 정리
    print("\n" + "=" * 60)
    print(f"📊 사용되지 않는 애셋 검색 결과:")
    print(f"   🗑️ 미사용 애셋: {len(unused_assets)}개")
    print(f"   ✅ 사용 중인 애셋: {len(used_assets)}개")
    print(f"   📈 사용률: {(len(used_assets)/(len(used_assets)+len(unused_assets))*100):.1f}%")
    
    if unused_assets:
        print(f"\n🗑️ 미사용 애셋 목록:")
        for i, asset in enumerate(unused_assets, 1):
            print(f"   {i}. {asset.get_name()}")
            print(f"      경로: {asset.get_path_name()}")
            print(f"      타입: {asset.get_class().get_name()}")
        
        print(f"\n⚠️ 주의사항:")
        print(f"   - 이 결과는 Soft Reference만을 기준으로 합니다.")
        print(f"   - Hard Reference나 C++ 코드에서의 참조는 포함되지 않습니다.")
        print(f"   - 삭제하기 전에 반드시 수동으로 재확인하세요.")
    
    if used_assets:
        print(f"\n✅ 사용 중인 애셋 (참조 수 상위 5개):")
        used_assets.sort(key=lambda x: x[1], reverse=True)
        for i, (asset, ref_count) in enumerate(used_assets[:5], 1):
            print(f"   {i}. {asset.get_name()} ({ref_count}개 참조)")
    
    return len(unused_assets) > 0


# 편의 함수들
- safe_copy(): duplicate_asset을 사용한 안전한 복사
- batch_duplicate(): 대량 애셋 안전 복사
- copy_with_validation(): 검증이 포함된 복사
- run(): 안전한 메인 실행 함수

🎯 대상 경로: /Game/Test

📊 복사 방식:
✅ duplicate_asset 사용 (안전함)
❌ begin_advanced_copy_packages 사용 안함 (크래시 위험)
"""

import unreal


def ensure_test_directory():
    """Test 디렉토리가 존재하는지 확인하고 없으면 생성"""
    target_path = "/Game/Test"
    editor_asset_lib = unreal.EditorAssetLibrary()
    
    if not editor_asset_lib.does_directory_exist(target_path):
        print(f"📁 {target_path} 디렉토리를 생성 중...")
        success = editor_asset_lib.make_directory(target_path)
        if success:
            print("✅ 디렉토리 생성 성공")
        else:
            print("❌ 디렉토리 생성 실패")
            return False
    else:
        print(f"✅ {target_path} 디렉토리 존재")
    
    return True


def safe_duplicate_asset(asset, target_path, name_suffix="_Copy"):
    """
    🛡️ 단일 애셋 안전 복사
    """
    try:
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        asset_name = asset.get_name()
        new_name = f"{asset_name}{name_suffix}"
        
        duplicated_asset = asset_tools.duplicate_asset(
            new_name,
            target_path,
            asset
        )
        
        return duplicated_asset
        
    except Exception as e:
        print(f"❌ 복사 오류: {str(e)}")
        return None


def safe_copy():
    """
    🛡️ 안전한 애셋 복사 - duplicate_asset 사용 (에디터 크래시 방지)
    """
    print("🛡️ 안전한 애셋 복사 시작...")
    print("=" * 50)
    
    # Test 디렉토리 확인/생성
    if not ensure_test_directory():
        return False
    
    # 선택된 애셋 확인
    editor_utility = unreal.EditorUtilityLibrary()
    selected_assets = editor_utility.get_selected_assets()
    
    if not selected_assets:
        print("❌ 선택된 애셋이 없습니다. Content Browser에서 애셋을 선택한 후 다시 시도하세요.")
        return False
    
    print(f"📦 선택된 애셋 목록:")
    for i, asset in enumerate(selected_assets, 1):
        print(f"  {i}. {asset.get_path_name()}")
        print(f"     타입: {asset.get_class().get_name()}")
    
    # 안전한 복사 실행
    target_path = "/Game/Test"
    success_count = 0
    
    for i, asset in enumerate(selected_assets, 1):
        try:
            asset_path = asset.get_path_name()
            asset_name = asset.get_name()
            new_name = f"{asset_name}_Copy"
            
            print(f"  {i}/{len(selected_assets)}. 복사 중: {asset_name} -> {new_name}")
            
            duplicated_asset = safe_duplicate_asset(asset, target_path)
            
            if duplicated_asset:
                print(f"     ✅ 성공: {duplicated_asset.get_path_name()}")
                success_count += 1
            else:
                print(f"     ❌ 실패: None 반환")
                
        except Exception as e:
            print(f"     ❌ 오류: {str(e)}")
    
    print(f"\n📊 복사 완료: {success_count}/{len(selected_assets)}개 성공")
    
    if success_count > 0:
        print(f"📁 복사된 애셋들을 {target_path}에서 확인하세요!")
        return True
    else:
        return False


def batch_duplicate(target_path="/Game/Test", name_suffix="_Batch"):
    """
    🔄 대량 애셋 안전 복사 - 하나씩 순차적으로 처리
    """
    print("🔄 대량 애셋 안전 복사 시작...")
    print("=" * 50)
    
    # Test 디렉토리 확인/생성
    if not ensure_test_directory():
        return False
    
    # 선택된 애셋 확인
    editor_utility = unreal.EditorUtilityLibrary()
    selected_assets = editor_utility.get_selected_assets()
    
    if not selected_assets:
        print("❌ 선택된 애셋이 없습니다.")
        return False
    
    print(f"📦 복사할 애셋: {len(selected_assets)}개")
    print(f"🎯 대상 경로: {target_path}")
    print(f"📝 이름 접미사: {name_suffix}")
    
    success_count = 0
    failed_assets = []
    
    for i, asset in enumerate(selected_assets, 1):
        try:
            asset_name = asset.get_name()
            asset_path = asset.get_path_name()
            
            print(f"📋 [{i}/{len(selected_assets)}] 복사 중: {asset_name}")
            
            duplicated_asset = safe_duplicate_asset(asset, target_path, name_suffix)
            
            if duplicated_asset:
                duplicated_path = duplicated_asset.get_path_name()
                print(f"   ✅ 성공: {duplicated_path}")
                success_count += 1
            else:
                print(f"   ❌ 실패")
                failed_assets.append(asset_name)
                
        except Exception as e:
            print(f"   ❌ 오류: {str(e)}")
            failed_assets.append(asset_name)
        
        # 진행률 표시
        progress = (i / len(selected_assets)) * 100
        print(f"   📊 진행률: {progress:.1f}%")
        print()
    
    # 최종 결과 출력
    print("=" * 50)
    print(f"📊 복사 완료 결과:")
    print(f"   ✅ 성공: {success_count}개")
    print(f"   ❌ 실패: {len(failed_assets)}개")
    print(f"   📈 성공률: {(success_count/len(selected_assets)*100):.1f}%")
    
    if failed_assets:
        print(f"❌ 실패한 애셋들:")
        for asset_name in failed_assets:
            print(f"   - {asset_name}")
    
    if success_count > 0:
        print(f"📁 복사된 애셋들을 {target_path}에서 확인하세요!")
        return True
    else:
        return False


def copy_with_validation():
    """
    🔍 검증이 포함된 안전한 복사
    """
    print("🔍 검증이 포함된 안전한 복사 시작...")
    print("=" * 50)
    
    # 선택된 애셋 확인
    editor_utility = unreal.EditorUtilityLibrary()
    selected_assets = editor_utility.get_selected_assets()
    
    if not selected_assets:
        print("❌ 선택된 애셋이 없습니다.")
        return False
    
    # 애셋 검증
    print("🔍 애셋 검증 중...")
    valid_assets = []
    invalid_assets = []
    
    for asset in selected_assets:
        try:
            asset_path = asset.get_path_name()
            asset_name = asset.get_name()
            asset_class = asset.get_class().get_name()
            
            # 기본 검증
            if asset_path and asset_name and asset_class:
                # 애셋이 로드 가능한지 확인
                if unreal.EditorAssetLibrary.does_asset_exist(asset_path):
                    valid_assets.append(asset)
                    print(f"   ✅ 유효: {asset_name} ({asset_class})")
                else:
                    invalid_assets.append((asset_name, "애셋이 존재하지 않음"))
                    print(f"   ❌ 무효: {asset_name} - 애셋이 존재하지 않음")
            else:
                invalid_assets.append((asset_name, "애셋 정보 불완전"))
                print(f"   ❌ 무효: {asset_name} - 애셋 정보 불완전")
                
        except Exception as e:
            invalid_assets.append((asset.get_name(), str(e)))
            print(f"   ❌ 검증 오류: {asset.get_name()} - {str(e)}")
    
    print(f"\n📊 검증 결과:")
    print(f"   ✅ 유효한 애셋: {len(valid_assets)}개")
    print(f"   ❌ 무효한 애셋: {len(invalid_assets)}개")
    
    if not valid_assets:
        print("❌ 복사할 수 있는 유효한 애셋이 없습니다.")
        return False
    
    if invalid_assets:
        print(f"\n⚠️ 무효한 애셋들 (건너뛸 예정):")
        for asset_name, reason in invalid_assets:
            print(f"   - {asset_name}: {reason}")
    
    # 대상 디렉토리 확인
    if not ensure_test_directory():
        return False
    
    # 유효한 애셋들만 복사
    print(f"\n🚀 {len(valid_assets)}개의 유효한 애셋 복사 시작...")
    
    target_path = "/Game/Test"
    success_count = 0
    
    for i, asset in enumerate(valid_assets, 1):
        duplicated_asset = safe_duplicate_asset(asset, target_path, "_Validated")
        if duplicated_asset:
            print(f"   {i}. ✅ {asset.get_name()} -> {duplicated_asset.get_name()}")
            success_count += 1
        else:
            print(f"   {i}. ❌ {asset.get_name()} 복사 실패")
    
    result = success_count > 0
    
    if result:
        print("✅ 검증이 포함된 복사가 완료되었습니다!")
    else:
        print("❌ 복사 중 문제가 발생했습니다.")
    
    return result


def list_test_folder_contents():
    """Test 폴더 내용 출력"""
    print("=== /Game/Test 폴더 내용 ===")
    
    target_path = "/Game/Test"
    editor_asset_lib = unreal.EditorAssetLibrary()
    
    try:
        if editor_asset_lib.does_directory_exist(target_path):
            assets = editor_asset_lib.list_assets(target_path, recursive=False)
            print(f"애셋 수: {len(assets)}")
            
            for i, asset_path in enumerate(assets, 1):
                print(f"  {i}. {asset_path}")
        else:
            print("❌ 디렉토리가 존재하지 않습니다.")
            
    except Exception as e:
        print(f"❌ 오류: {str(e)}")


def emergency_clean():
    """
    🧹 비상 정리 - Test 폴더의 모든 애셋 삭제
    """
    print("🧹 비상 정리 시작...")
    print("⚠️ /Game/Test 폴더의 모든 애셋을 삭제합니다!")
    
    try:
        target_path = "/Game/Test"
        editor_asset_lib = unreal.EditorAssetLibrary()
        
        if not editor_asset_lib.does_directory_exist(target_path):
            print("📁 대상 디렉토리가 존재하지 않습니다.")
            return
        
        assets = editor_asset_lib.list_assets(target_path, recursive=False)
        
        if not assets:
            print("📁 폴더가 이미 비어있습니다.")
            return
        
        print(f"🗑️ 삭제할 애셋: {len(assets)}개")
        
        deleted_count = 0
        for asset_path in assets:
            try:
                success = editor_asset_lib.delete_asset(asset_path)
                if success:
                    print(f"   ✅ 삭제: {asset_path}")
                    deleted_count += 1
                else:
                    print(f"   ❌ 삭제 실패: {asset_path}")
            except Exception as e:
                print(f"   ❌ 오류: {asset_path} - {str(e)}")
        
        print(f"📊 정리 완료: {deleted_count}/{len(assets)}개 삭제됨")
        
    except Exception as e:
        print(f"❌ 비상 정리 중 오류: {str(e)}")


def run():
    """🛡️ 안전한 메인 실행 함수"""
    print("🛡️ 안전한 Unreal Engine 애셋 복사 도구")
    print("=" * 60)
    print("✅ duplicate_asset 방식 사용 (안전함)")
    print("❌ begin_advanced_copy_packages 사용 안함 (크래시 방지)")
    print()
    
    # 선택된 애셋 확인
    editor_utility = unreal.EditorUtilityLibrary()
    selected_assets = editor_utility.get_selected_assets()
    
    if not selected_assets:
        print("❌ 선택된 애셋이 없습니다.")
        print("📋 사용법:")
        print("   1. Content Browser에서 애셋 선택")
        print("   2. run() 다시 실행")
        return
    
    print(f"📦 선택된 애셋: {len(selected_assets)}개")
    
    # 안전한 복사 실행
    print("\n🚀 안전한 복사 방법으로 진행합니다...")
    success = safe_copy()
    
    if success:
        print("\n✅ 안전한 복사가 완료되었습니다!")
        list_test_folder_contents()
    else:
        print("\n❌ 복사 중 문제가 발생했습니다.")
    
    print("\n" + "=" * 60)
    print("🛡️ 안전한 복사 완료!")


def help_menu():
    """📋 도움말 메뉴"""
    print("📋 Unreal Engine 안전한 애셋 복사 도구 도움말")
    print("=" * 60)
    print()
    print("🛡️ 안전한 함수들 (권장):")
    print("   safe_copy()              - 기본 안전한 복사")
    print("   batch_duplicate()        - 대량 애셋 안전 복사")
    print("   copy_with_validation()   - 검증이 포함된 복사")
    print("   run()                    - 안전한 메인 실행")
    print()
    print("🔧 유틸리티 함수들:")
    print("   list_test_folder_contents() - Test 폴더 내용 확인")
    print("   emergency_clean()           - 비상 정리 (Test 폴더 비우기)")
    print("   help_menu()                 - 이 도움말")
    print()
    print("📋 기본 사용법:")
    print("   1. Content Browser에서 애셋 선택")
    print("   2. safe_copy() 또는 run() 실행")
    print("   3. /Game/Test 폴더에서 결과 확인")
    print()
    print("🎯 대상 경로: /Game/Test")
    print("✅ 복사 방식: duplicate_asset (안전함)")


# 빠른 실행 함수
def quick():
    """🚀 빠른 안전한 복사"""
    safe_copy()


# 기본 실행 (파일 로드 시)
if __name__ == "__main__":
    print("🛡️ 안전한 애셋 복사 도구가 로드되었습니다!")
    print("💡 도움말을 보려면: help_menu()")
    print("🚀 빠른 실행: safe_copy() 또는 run()")