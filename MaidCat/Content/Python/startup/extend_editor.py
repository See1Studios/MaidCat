"""
Editor Extension Initialization
에디터 확장 초기화 모듈 (래퍼)
- Python 폴더 메뉴 기능 -> python_context.py
- 애셋 메뉴 기능 -> asset_context.py
"""

import unreal
from editor import mi_context
from editor import python_context
from editor import asset_context
from editor import asset_editor

def initialize():
    """에디터 확장 시스템 초기화"""
    try:
        # Python 컨텍스트 메뉴 초기화
        python_context.register()
        
        # 애셋 브라우저 컨텍스트 메뉴 초기화
        asset_context.register()

        # MI 에디터 컨텍스트 메뉴 초기화
        mi_context.register()
        
        # 애셋 에디터 컨텍스트 메뉴 초기화
        asset_editor.register()

        unreal.log("✅ 에디터 확장 시스템이 성공적으로 추가되었습니다.")
        
    except Exception as e:
        unreal.log_error(f"❌ 에디터 확장 시스템 초기화 실패: {e}")


# 스크립트 로드 시 자동 실행
initialize()
