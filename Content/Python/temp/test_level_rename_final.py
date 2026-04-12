"""
레벨 Rename 최종 해결책

핵심 문제: 
- rename_asset() 호출 시 대화창이 뜨지만 자동으로 Cancel됨
- Python에서는 대화창 응답을 제어할 수 없음

최종 해결책:
1. 레벨을 먼저 닫기 (현재 열려있으면 rename 불가)
2. 소스 컨트롤 비활성화 또는 체크아웃
3. 실제 동작하는 rename 방법 사용
"""

import unreal

def close_current_level():
    """현재 열려있는 레벨 닫기"""
    unreal.log("📝 현재 레벨 닫기 시도...")
    
    try:
        # 새 빈 레벨 생성하여 현재 레벨 언로드
        temp_level = "/Game/Temp_EmptyLevel"
        
        # 임시 레벨이 있으면 삭제
        if unreal.EditorAssetLibrary.does_asset_exist(temp_level):
            unreal.EditorAssetLibrary.delete_asset(temp_level)
        
        # 새 레벨 생성
        success = unreal.EditorLevelLibrary.new_level(temp_level)
        
        if success:
            unreal.log("   ✅ 임시 레벨 생성 및 전환 완료")
            return True
        else:
            unreal.log_warning("   ⚠️ 임시 레벨 생성 실패")
            return False
            
    except Exception as e:
        unreal.log_error(f"   ❌ 레벨 닫기 실패: {e}")
        return False


def rename_level_method1_with_close():
    """해결책 1: 레벨 닫고 rename"""
    
    unreal.log("=" * 80)
    unreal.log("🔧 해결책 1: 레벨을 먼저 닫고 rename")
    unreal.log("=" * 80)
    
    source_level = "/Game/NewMap"
    dest_level = "/Game/RenamedMap_Method1"
    
    # 1. 소스 확인
    if not unreal.EditorAssetLibrary.does_asset_exist(source_level):
        unreal.log_error(f"❌ 소스 레벨 없음: {source_level}")
        return False
    
    # 2. 현재 레벨 닫기
    unreal.log("\n1️⃣ 현재 열려있는 레벨 닫기")
    close_current_level()
    
    # 3. Rename 시도
    unreal.log(f"\n2️⃣ Rename 시도: {source_level} → {dest_level}")
    
    try:
        success = unreal.EditorAssetLibrary.rename_asset(source_level, dest_level)
        
        if success:
            unreal.log(f"✅ Rename 성공!")
            
            # 결과 확인
            if unreal.EditorAssetLibrary.does_asset_exist(dest_level):
                unreal.log(f"   ✅ 새 경로에 레벨 존재")
            if not unreal.EditorAssetLibrary.does_asset_exist(source_level):
                unreal.log(f"   ✅ 기존 경로에서 제거됨")
        else:
            unreal.log_error(f"❌ Rename 실패")
            
        return success
        
    except Exception as e:
        unreal.log_error(f"❌ 예외 발생: {e}")
        return False


def rename_level_method2_directory():
    """해결책 2: rename_directory() 사용"""
    
    unreal.log("\n" + "=" * 80)
    unreal.log("🔧 해결책 2: 폴더로 이동 후 rename_directory()")
    unreal.log("=" * 80)
    
    source_level = "/Game/NewMap"
    
    # 1. 임시 폴더로 이동
    temp_folder = "/Game/TempRenameFolder"
    dest_in_temp = f"{temp_folder}/NewMap"
    final_dest = "/Game/RenamedMap_Method2"
    
    try:
        # 1-1. 임시 폴더 생성
        unreal.log(f"\n1️⃣ 임시 폴더 생성: {temp_folder}")
        unreal.EditorAssetLibrary.make_directory(temp_folder)
        
        # 1-2. 레벨을 임시 폴더로 이동
        unreal.log(f"\n2️⃣ 레벨을 임시 폴더로 이동")
        close_current_level()
        
        success = unreal.EditorAssetLibrary.rename_asset(source_level, dest_in_temp)
        
        if not success:
            unreal.log_error("❌ 임시 폴더로 이동 실패")
            return False
            
        unreal.log(f"   ✅ 임시 폴더로 이동 성공")
        
        # 1-3. 다시 원래 위치로 새 이름으로 이동
        unreal.log(f"\n3️⃣ 새 이름으로 원래 위치로 이동")
        success = unreal.EditorAssetLibrary.rename_asset(dest_in_temp, final_dest)
        
        if success:
            unreal.log(f"✅ Rename 성공!")
            
            # 임시 폴더 삭제
            unreal.EditorAssetLibrary.delete_directory(temp_folder)
        else:
            unreal.log_error(f"❌ Rename 실패")
            
        return success
        
    except Exception as e:
        unreal.log_error(f"❌ 예외 발생: {e}")
        return False


def rename_level_method3_file_system():
    """해결책 3: 파일 시스템에서 직접 rename (고급)"""
    
    unreal.log("\n" + "=" * 80)
    unreal.log("🔧 해결책 3: 파일 시스템 직접 조작 (실험적)")
    unreal.log("=" * 80)
    
    import os
    import shutil
    
    source_level = "/Game/NewMap"
    dest_level = "/Game/RenamedMap_Method3"
    
    try:
        # 1. 프로젝트 경로 가져오기
        project_dir = unreal.Paths.project_content_dir()
        unreal.log(f"📂 프로젝트 Content 경로: {project_dir}")
        
        # 2. 실제 파일 경로 변환
        source_file = os.path.join(project_dir, "NewMap.umap")
        dest_file = os.path.join(project_dir, "RenamedMap_Method3.umap")
        
        unreal.log(f"\n파일 경로:")
        unreal.log(f"   Source: {source_file}")
        unreal.log(f"   Dest: {dest_file}")
        
        # 3. 파일 존재 확인
        if not os.path.exists(source_file):
            unreal.log_error(f"❌ 소스 파일 없음: {source_file}")
            return False
        
        # 4. 현재 레벨 닫기
        unreal.log(f"\n1️⃣ 현재 레벨 닫기")
        close_current_level()
        
        # 5. 파일 이동
        unreal.log(f"\n2️⃣ 파일 시스템에서 파일 이동")
        
        # umap 파일 이동
        shutil.move(source_file, dest_file)
        unreal.log(f"   ✅ .umap 파일 이동 완료")
        
        # umap_BuiltData 파일도 이동 (있으면)
        source_buildata = source_file.replace(".umap", "_BuiltData.uasset")
        dest_buildata = dest_file.replace(".umap", "_BuiltData.uasset")
        
        if os.path.exists(source_buildata):
            shutil.move(source_buildata, dest_buildata)
            unreal.log(f"   ✅ _BuiltData 파일 이동 완료")
        
        # 6. Asset Registry 리프레시
        unreal.log(f"\n3️⃣ Asset Registry 리프레시")
        asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
        
        # 경로를 디스크 경로로 변환
        scan_paths = [project_dir]
        asset_registry.scan_paths_synchronous(scan_paths, True)
        
        unreal.log(f"   ✅ Asset Registry 리프레시 완료")
        
        # 7. 결과 확인
        unreal.log(f"\n4️⃣ 결과 확인")
        if unreal.EditorAssetLibrary.does_asset_exist(dest_level):
            unreal.log(f"   ✅ 새 에셋 등록됨: {dest_level}")
            return True
        else:
            unreal.log_error(f"   ❌ 새 에셋이 등록되지 않음")
            return False
            
    except Exception as e:
        unreal.log_error(f"❌ 예외 발생: {e}")
        import traceback
        unreal.log_error(traceback.format_exc())
        return False


def cleanup():
    """테스트 레벨 정리"""
    unreal.log("\n" + "=" * 80)
    unreal.log("🧹 테스트 레벨 정리")
    unreal.log("=" * 80)
    
    test_items = [
        "/Game/RenamedMap_Method1",
        "/Game/RenamedMap_Method2",
        "/Game/RenamedMap_Method3",
        "/Game/Temp_EmptyLevel",
        "/Game/TempRenameFolder",
    ]
    
    for item in test_items:
        try:
            # 폴더인지 파일인지 확인
            if unreal.EditorAssetLibrary.does_directory_exist(item):
                unreal.log(f"   삭제 (폴더): {item}")
                unreal.EditorAssetLibrary.delete_directory(item)
            elif unreal.EditorAssetLibrary.does_asset_exist(item):
                unreal.log(f"   삭제 (에셋): {item}")
                unreal.EditorAssetLibrary.delete_asset(item)
        except:
            pass


# ============================================================================
# 메인 실행
# ============================================================================

if __name__ == "__main__":
    unreal.log("\n\n")
    unreal.log("🚀 레벨 Rename 최종 해결책 테스트")
    unreal.log("=" * 80)
    
    results = {}
    
    # 방법 1: 레벨 닫고 rename
    unreal.log("\n" + "🧪" * 40)
    results["method1"] = rename_level_method1_with_close()
    
    # 방법 2: 폴더 이동 활용 (주석 처리 - method1이 성공하면 불필요)
    # unreal.log("\n" + "🧪" * 40)
    # results["method2"] = rename_level_method2_directory()
    
    # 방법 3: 파일 시스템 직접 조작 (주석 처리 - 위험함)
    # unreal.log("\n" + "🧪" * 40)
    # results["method3"] = rename_level_method3_file_system()
    
    # 결과 요약
    unreal.log("\n\n" + "=" * 80)
    unreal.log("📊 테스트 결과 요약")
    unreal.log("=" * 80)
    
    for name, result in results.items():
        status = "✅ 성공" if result else "❌ 실패"
        unreal.log(f"   {name}: {status}")
    
    unreal.log("\n💡 결론:")
    unreal.log("   Python에서 레벨 rename 시 대화창이 자동 Cancel되는 문제는")
    unreal.log("   언리얼 엔진의 내부 정책으로, 완전한 우회는 어렵습니다.")
    unreal.log("")
    unreal.log("   권장 해결책:")
    unreal.log("   1. duplicate_asset() + 수동 삭제")
    unreal.log("   2. C++ 플러그인으로 구현")
    unreal.log("   3. 에디터 UI에서 수동 rename")
    
    # 정리 (주석 처리)
    # cleanup()
