"""
Advanced Copy 테스트 스크립트
"""

import sys
import os

# MaidCat Python 경로 추가
maidcat_path = r"d:\GitHub\MaidCat\MaidCat\Content\Python"
if maidcat_path not in sys.path:
    sys.path.insert(0, maidcat_path)

# copier 모듈 임포트
try:
    from tool import copier
    print("✅ copier 모듈 로드 성공")
    
    # advanced 모드로 테스트
    print("\n🚀 Advanced Copy 테스트 시작...")
    print("1. 간단한 애셋을 Unreal Engine에서 선택하세요")
    print("2. 아래 코드를 Unreal Engine Python Console에서 실행하세요:")
    print("\nUnreal Engine Python Console 코드:")
    print("="*60)
    print("import sys")
    print(f"sys.path.append(r'{maidcat_path}')")
    print("from tool import copier")
    print("copier.run('/Game/AdvancedCopyTest', 'advanced')")
    print("="*60)
    
except Exception as e:
    print(f"❌ 모듈 로드 실패: {e}")