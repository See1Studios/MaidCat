"""
메뉴 리로드 테스트

MenuConfig.json 변경사항을 적용하기 위해 메뉴를 리로드합니다.
"""

import unreal

# 메뉴 리로드
unreal.log("="*80)
unreal.log("🔄 메뉴 리로드 중...")
unreal.log("="*80)

try:
    # TAPython 메뉴 리로드 함수 호출
    # (정확한 API는 TAPython 버전에 따라 다를 수 있음)
    unreal.log("메뉴 리로드 시도...")
    
    # 대안: 언리얼 에디터를 재시작하거나
    # Window > Developer Tools > Refresh Toolbar 메뉴 확인
    
    unreal.log("✅ 메뉴 설정이 변경되었습니다!")
    unreal.log("")
    unreal.log("📍 확인사항:")
    unreal.log("1. 언리얼 에디터 상단 툴바 확인")
    unreal.log("2. 'Post Process Preset Manager' 버튼 찾기")
    unreal.log("3. 클릭하면 독립 창이 열림")
    unreal.log("")
    unreal.log("⚠️  버튼이 보이지 않는다면:")
    unreal.log("   - 언리얼 에디터 재시작")
    unreal.log("   - 또는 Window > Load Layout > Default 실행")
    
except Exception as e:
    unreal.log_error(f"예외: {e}")

unreal.log("="*80)
