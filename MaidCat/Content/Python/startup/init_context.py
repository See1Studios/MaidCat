"""
Context Menu Initialization
컨텍스트 메뉴 초기화 모듈 (래퍼)
- Python 폴더 메뉴 기능 -> python_context.py
- 애셋 메뉴 기능 -> asset_context.py
"""

import unreal
from editor import python_context
from editor import asset_context


def initialize():
    """컨텍스트 메뉴 시스템 초기화"""
    try:
        # Python 컨텍스트 메뉴 초기화
        python_context.initialize()
        
        # 애셋 컨텍스트 메뉴 초기화
        asset_context.initialize()
        
        unreal.log("✅ Context menu system initialized successfully")
        
    except Exception as e:
        unreal.log_error(f"❌ Failed to initialize context menu system: {e}")


# 스크립트 로드 시 자동 실행
initialize()
