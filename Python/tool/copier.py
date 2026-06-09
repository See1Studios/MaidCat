import unreal


def test_find_soft_references():
    """
    find_soft_references_to_object 함수 테스트
    선택한 애셋을 참조하는 다른 애셋들을 찾습니다
    """
    print("🔍 Soft Reference 탐지 테스트 시작...")
    print("=" * 60)
    
    # AssetTools와 선택된 애셋 가져오기
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    
    if not selected_assets:
        print("❌ 선택된 애셋이 없습니다.")
        return False
    
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
            
            # 중요: 애셋 객체를 SoftObjectPath로 변환해야 함
            soft_object_path = unreal.SoftObjectPath(asset_path)
            print(f"   SoftObjectPath 생성: {type(soft_object_path)}")
            
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
                        
                    except Exception as e:
                        print(f"      {j}. ❌ 참조 정보 읽기 오류: {str(e)}")
                
                # 참조 관계 분석
                print(f"   🔗 참조 관계 분석:")
                material_refs = [obj for obj in referencing_objects if 'Material' in obj.get_class().get_name()]
                blueprint_refs = [obj for obj in referencing_objects if 'Blueprint' in obj.get_class().get_name()]
                mesh_refs = [obj for obj in referencing_objects if 'Mesh' in obj.get_class().get_name()]
                texture_refs = [obj for obj in referencing_objects if 'Texture' in obj.get_class().get_name()]
                other_refs = [obj for obj in referencing_objects if obj not in material_refs + blueprint_refs + mesh_refs + texture_refs]
                
                if material_refs:
                    print(f"      🎨 머티리얼: {len(material_refs)}개")
                if blueprint_refs:
                    print(f"      📘 블루프린트: {len(blueprint_refs)}개")
                if mesh_refs:
                    print(f"      🧊 메시: {len(mesh_refs)}개")
                if texture_refs:
                    print(f"      🖼️ 텍스처: {len(texture_refs)}개")
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
    
    if len(selected_assets) > 0:
        print(f"   📈 평균 참조 수: {total_references_found/len(selected_assets):.1f}개/애셋")
    
    if total_references_found == 0:
        print("\n💡 팁:")
        print("   - 텍스처나 머티리얼을 선택해보세요 (더 많은 참조 관계가 있을 수 있습니다)")
        print("   - 사용 중인 애셋을 선택해보세요")
        print("   - Blueprint에서 사용되는 애셋을 선택해보세요")
    
    return total_references_found > 0


def analyze_soft_object_path():
    """
    SoftObjectPath의 다양한 기능 테스트
    """
    print("🔍 SoftObjectPath 분석 테스트...")
    print("=" * 60)
    
    selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    
    if not selected_assets:
        print("❌ 선택된 애셋이 없습니다.")
        return
    
    for i, asset in enumerate(selected_assets, 1):
        try:
            asset_path = asset.get_path_name()
            asset_name = asset.get_name()
            
            print(f"🎯 [{i}/{len(selected_assets)}] SoftObjectPath 분석: {asset_name}")
            
            # SoftObjectPath 생성
            soft_path = unreal.SoftObjectPath(asset_path)
            
            # SoftObjectPath를 문자열로 변환하는 올바른 방법
            path_string = asset_path  # 원본 경로 사용
            print(f"   📁 전체 경로: {path_string}")
            
            # 패키지 경로와 애셋 이름 분리
            if '.' in path_string:
                package_path, asset_name_from_path = path_string.rsplit('.', 1)
                print(f"   📂 패키지 경로: {package_path}")
                print(f"   📝 애셋 이름: {asset_name_from_path}")
            else:
                print(f"   📄 전체 경로가 애셋 경로입니다")
            
            # SoftObjectPath가 올바르게 생성되었는지 확인
            print(f"   🔗 SoftObjectPath 타입: {type(soft_path)}")
            
            # 유효성 검사
            try:
                is_valid = soft_path.is_valid()
                print(f"   ✅ 유효한 경로: {is_valid}")
            except AttributeError:
                print(f"   ✅ SoftObjectPath 객체가 생성되었습니다")
            
            # SoftObjectPath 비교 테스트
            soft_path2 = unreal.SoftObjectPath(asset_path)
            are_equal = (str(soft_path) == str(soft_path2))
            print(f"   🔄 경로 비교: {are_equal}")
            
            print()
            try:
                # AssetData로 변환 시도
                asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
                asset_data = asset_registry.get_asset_by_object_path(soft_path)
                
                if asset_data and asset_data.is_valid():
                    print(f"   📊 AssetData 변환: 성공")
                    print(f"      - 패키지명: {asset_data.package_name}")
                    print(f"      - 애셋 클래스: {asset_data.asset_class}")
                else:
                    print(f"   📊 AssetData 변환: 실패")
                    
            except Exception as e:
                print(f"   📊 AssetData 변환 오류: {str(e)}")
            
            print()
            
        except Exception as e:
            print(f"   ❌ SoftObjectPath 분석 오류: {str(e)}")
            print()


def run():
    """기본 실행 함수 - find_soft_references_to_object 테스트"""
    print("🔍 find_soft_references_to_object 함수 테스트")
    print("=" * 60)
    
    # SoftObjectPath 분석부터 시작
    analyze_soft_object_path()
    
    print("\n" + "=" * 60)
    
    # Soft Reference 검색 테스트
    test_find_soft_references()


def quick_test():
    """빠른 테스트"""
    test_find_soft_references()


def help_menu():
    """도움말"""
    print("📋 find_soft_references_to_object 테스트 도구")
    print("=" * 60)
    print()
    print("🔍 주요 함수들:")
    print("   test_find_soft_references()    - Soft Reference 검색 테스트")
    print("   analyze_soft_object_path()     - SoftObjectPath 분석")
    print("   run()                          - 전체 테스트 실행")
    print("   quick_test()                   - 빠른 테스트")
    print()
    print("📋 사용법:")
    print("   1. Content Browser에서 애셋 선택")
    print("   2. Python 콘솔에서 실행:")
    print("      exec(open('d:/GitHub/MaidCat/MaidCat/Content/Python/tool/copier.py').read())")
    print("      run()")
    print()
    print("💡 팁:")
    print("   - 텍스처, 머티리얼, 메시 등을 선택하면 더 많은 참조를 찾을 수 있습니다")
    print("   - Blueprint에서 사용되는 애셋들을 선택해보세요")