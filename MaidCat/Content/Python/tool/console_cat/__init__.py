# ============================================================================
# console_cat - MaidCat 콘솔 명령어 도구 🐱
# ============================================================================
"""
MaidCat 플러그인의 Unreal Engine 콘솔 명령어 관련 도구 모음

구조:
1. generate_console_command_list.py: 콘솔 명령어 데이터 생성기
   - Unreal Engine의 콘솔 명령어를 추출하고 번역
   - JSON 데이터 파일 생성 (Saved/ConsoleCommandData/)

2. console_cat.py: PySide6 기반 콘솔 명령어 실행기
   - 생성된 데이터 파일을 기반으로 GUI 제공
   - 버튼 클릭으로 콘솔 명령어 실행
   - 카테고리별 정리 및 검색 기능
   - 요구사항: pip install PySide6

3. translation_dictionary.json: 명령어 번역 캐시
   - 번역된 명령어 설명 저장
   - API 호출 최소화

사용법:
1. generate_console_command_list.py 실행 → 데이터 생성
2. console_cat.py 실행 → GUI로 명령어 실행
"""

# 주요 함수들
def generate_command_data():
    """콘솔 명령어 데이터 생성"""
    try:
        from . import generate_console_command_list as generator
        generator.main()
        print("✅ 콘솔 명령어 데이터 생성 완료")
    except Exception as e:
        print(f"❌ 데이터 생성 실패: {e}")

def run_console_cat():
    """Qt 콘솔 실행기 시작"""
    try:
        from . import console_cat as cc
        cc.main()
        print("🚀 Console Cat 시작됨")
    except Exception as e:
        print(f"❌ Console Cat 시작 실패: {e}")

def get_info():
    """Console Cat 모듈 정보 반환"""
    return {
        "name": "Console Cat 🐱",
        "description": "MaidCat 콘솔 명령어 도구 모음",
        "workflow": [
            "1. generate_command_data() - 데이터 생성",
            "2. run_console_cat() - GUI 실행기 시작"
        ],
        "files": [
            "generate_console_command_list.py",
            "console_cat.py",
            "translation_dictionary.json"
        ]
    }

# 편의 함수들
setup_data = generate_command_data  # 별칭
run_gui = run_console_cat           # 별칭
run_console_runner = run_console_cat # 호환성 유지

print("Console Cat module loaded. (Cat emoji)")