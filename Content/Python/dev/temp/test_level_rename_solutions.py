"""
레벨 Rename 해결 방법 테스트

문제: rename_asset() 호출 시 대화창이 자동으로 Cancel됨
해결책: 여러 방법 시도
"""

import unreal

def solution1_rename_with_loaded_asset():
    """해결책 1: rename_loaded_asset() 사용"""
    
    unreal.log("=" * 80)
    unreal.log("🔧 해결책 1: rename_loaded_asset() 사용")
    unreal.log("=" * 80)
    
    source_level = "/Game/NewMap"
    dest_level = "/Game/RenamedMap_Solution1"
    
    # 소스 확인
    if not unreal.EditorAssetLibrary.does_asset_exist(source_level):
        unreal.log_error(f"❌ 소스 레벨 없음: {source_level}")
        return False
    
    # 레벨 로드
    unreal.log(f"📝 레벨 로드: {source_level}")
    level_asset = unreal.EditorAssetLibrary.load_asset(source_level)
    
    if not level_asset:
        unreal.log_error(f"❌ 레벨 로드 실패")
        return False
    
    unreal.log(f"✅ 레벨 로드 성공: {level_asset.get_name()}")
    
    # rename_loaded_asset 사용
    unreal.log(f"📝 rename_loaded_asset() 시도")
    unreal.log(f"   {source_level} → {dest_level}")
    
    try:
        success = unreal.EditorAssetLibrary.rename_loaded_asset(level_asset, dest_level)
        
        if success:
            unreal.log(f"✅ Rename 성공!")
            verify_rename(dest_level, source_level)
        else:
            unreal.log_error(f"❌ Rename 실패")
            
        return success
        
    except Exception as e:
        unreal.log_error(f"❌ 예외 발생: {e}")
        return False


def solution2_duplicate_and_delete():
    """해결책 2: duplicate + delete 조합"""
    
    unreal.log("\n" + "=" * 80)
    unreal.log("🔧 해결책 2: duplicate_asset() + delete_asset() 조합")
    unreal.log("=" * 80)
    
    source_level = "/Game/NewMap"
    dest_level = "/Game/RenamedMap_Solution2"
    
    # 소스 확인
    if not unreal.EditorAssetLibrary.does_asset_exist(source_level):
        unreal.log_error(f"❌ 소스 레벨 없음: {source_level}")
        return False
    
    try:
        # 1. 복제
        unreal.log(f"📝 1단계: 레벨 복제")
        duplicated = unreal.EditorAssetLibrary.duplicate_asset(source_level, dest_level)
        
        if not duplicated:
            unreal.log_error(f"❌ 복제 실패")
            return False
        
        unreal.log(f"✅ 복제 성공: {dest_level}")
        
        # 2. 원본 삭제 (사용자에게 확인 - 이 단계는 선택적)
        unreal.log(f"📝 2단계: 원본 삭제 (선택적)")
        unreal.log(f"   ⚠️ 주의: 이 방법은 rename이 아닌 copy입니다!")
        unreal.log(f"   원본을 삭제하려면 수동으로 삭제해야 합니다.")
        
        verify_rename(dest_level, source_level)
        return True
        
    except Exception as e:
        unreal.log_error(f"❌ 예외 발생: {e}")
        return False


def solution3_editor_asset_subsystem():
    """해결책 3: EditorAssetSubsystem의 rename_asset 사용"""
    
    unreal.log("\n" + "=" * 80)
    unreal.log("🔧 해결책 3: EditorAssetSubsystem.rename_asset()")
    unreal.log("=" * 80)
    
    source_level = "/Game/NewMap"
    dest_level = "/Game/RenamedMap_Solution3"
    
    # 소스 확인
    if not unreal.EditorAssetLibrary.does_asset_exist(source_level):
        unreal.log_error(f"❌ 소스 레벨 없음: {source_level}")
        return False
    
    # EditorAssetSubsystem 가져오기
    subsystem = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
    
    if not subsystem:
        unreal.log_error("❌ EditorAssetSubsystem을 가져올 수 없습니다.")
        return False
    
    unreal.log(f"📝 EditorAssetSubsystem.rename_asset() 시도")
    unreal.log(f"   {source_level} → {dest_level}")
    
    try:
        success = subsystem.rename_asset(source_level, dest_level)
        
        if success:
            unreal.log(f"✅ Rename 성공!")
            verify_rename(dest_level, source_level)
        else:
            unreal.log_error(f"❌ Rename 실패")
            
        return success
        
    except Exception as e:
        unreal.log_error(f"❌ 예외 발생: {e}")
        return False


def solution4_rename_assets_with_dialog():
    """해결책 4: AssetTools.rename_assets_with_dialog() 사용 (배치 rename)"""
    
    unreal.log("\n" + "=" * 80)
    unreal.log("🔧 해결책 4: AssetTools.rename_assets_with_dialog()")
    unreal.log("=" * 80)
    
    source_level = "/Game/NewMap"
    dest_name = "RenamedMap_Solution4"  # 이름만 (경로 제외)
    dest_level = f"/Game/{dest_name}"
    
    # 소스 확인
    if not unreal.EditorAssetLibrary.does_asset_exist(source_level):
        unreal.log_error(f"❌ 소스 레벨 없음: {source_level}")
        return False
    
    # AssetTools 가져오기
    unreal.log(f"📝 AssetTools 가져오기")
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    
    if not asset_tools:
        unreal.log_error("❌ AssetTools를 가져올 수 없습니다.")
        return False
    
    unreal.log(f"   ✅ AssetTools: {asset_tools}")
    
    # AssetRenameData 생성
    unreal.log(f"\n📝 AssetRenameData 생성")
    
    # 소스 에셋 로드
    source_asset = unreal.EditorAssetLibrary.load_asset(source_level)
    if not source_asset:
        unreal.log_error(f"❌ 소스 레벨 로드 실패")
        return False
    
    # AssetRenameData 생성
    rename_data = unreal.AssetRenameData()
    rename_data.asset = source_asset
    rename_data.new_name = dest_name  # 새 이름만 (경로 제외)
    rename_data.new_package_path = "/Game"  # 새 경로
    
    unreal.log(f"   Asset: {rename_data.asset}")
    unreal.log(f"   New Name: {rename_data.new_name}")
    unreal.log(f"   New Path: {rename_data.new_package_path}")
    
    try:
        unreal.log(f"\n📝 AssetTools.rename_assets_with_dialog() 호출")
        unreal.log(f"   ⚠️ 이 메서드는 대화창을 표시합니다!")
        unreal.log(f"   💡 대화창에서 'Yes'를 클릭해주세요!")
        
        # AssetTools 사용
        result = asset_tools.rename_assets_with_dialog(
            [rename_data], 
            auto_checkout=False
        )
        
        unreal.log(f"\n📊 결과: {result}")
        
        if result == unreal.AssetRenameResult.SUCCESS:
            unreal.log(f"✅ Rename 성공!")
            verify_rename(dest_level, source_level)
            return True
        elif result == unreal.AssetRenameResult.FAILURE:
            unreal.log_error(f"❌ Rename 실패")
        elif result == unreal.AssetRenameResult.CANCELLED:
            unreal.log_warning(f"⚠️ 사용자가 취소함")
        
        return False
        
    except Exception as e:
        unreal.log_error(f"❌ 예외 발생: {e}")
        import traceback
        unreal.log_error(traceback.format_exc())
        return False


def verify_rename(new_path, old_path):
    """rename 결과 검증"""
    unreal.log(f"\n📋 검증:")
    
    if unreal.EditorAssetLibrary.does_asset_exist(new_path):
        unreal.log(f"   ✅ 새 경로에 레벨 존재: {new_path}")
    else:
        unreal.log_error(f"   ❌ 새 경로에 레벨 없음: {new_path}")
        
    if not unreal.EditorAssetLibrary.does_asset_exist(old_path):
        unreal.log(f"   ✅ 기존 경로에서 레벨 제거됨: {old_path}")
    else:
        unreal.log_warning(f"   ⚠️ 기존 경로에 레벨 여전히 존재: {old_path}")


def cleanup():
    """테스트 레벨 정리"""
    unreal.log("\n" + "=" * 80)
    unreal.log("🧹 테스트 레벨 정리")
    unreal.log("=" * 80)
    
    test_levels = [
        "/Game/RenamedMap_Solution1",
        "/Game/RenamedMap_Solution2",
        "/Game/RenamedMap_Solution3",
        "/Game/RenamedMap_Solution4",
    ]
    
    for level_path in test_levels:
        if unreal.EditorAssetLibrary.does_asset_exist(level_path):
            unreal.log(f"   삭제: {level_path}")
            unreal.EditorAssetLibrary.delete_asset(level_path)


# ============================================================================
# 메인 실행
# ============================================================================

if __name__ == "__main__":
    unreal.log("\n\n")
    unreal.log("🚀 레벨 Rename 해결책 테스트 시작")
    unreal.log("=" * 80)
    
    results = {}
    
    # 해결책 1: rename_loaded_asset
    unreal.log("\n" + "🧪" * 40)
    results["solution1"] = solution1_rename_with_loaded_asset()
    
    # 해결책 2: duplicate + delete
    unreal.log("\n" + "🧪" * 40)
    results["solution2"] = solution2_duplicate_and_delete()
    
    # 해결책 3: EditorAssetSubsystem.rename_asset
    unreal.log("\n" + "🧪" * 40)
    results["solution3"] = solution3_editor_asset_subsystem()
    
    # 해결책 4: rename_assets_with_dialog (대화창이 뜸)
    unreal.log("\n" + "🧪" * 40)
    results["solution4"] = solution4_rename_assets_with_dialog()
    
    # 결과 요약
    unreal.log("\n\n" + "=" * 80)
    unreal.log("📊 테스트 결과 요약")
    unreal.log("=" * 80)
    
    for name, result in results.items():
        status = "✅ 성공" if result else "❌ 실패"
        unreal.log(f"   {name}: {status}")
    
    # 정리 (주석 처리 - 수동으로 정리)
    # cleanup()
    
    unreal.log("\n✅ 모든 테스트 완료!")
    unreal.log("\n💡 권장 해결책:")
    unreal.log("   1. rename_loaded_asset() 사용 (가장 간단)")
    unreal.log("   2. EditorAssetSubsystem.rename_asset() 사용")
    unreal.log("   3. duplicate + 수동 삭제 (안전하지만 rename은 아님)")
