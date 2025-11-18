"""
__pycache__ 삭제 타이밍 테스트
"""

import os
import sys
import time
from pathlib import Path

def check_pycache_exists(folder_path):
    """__pycache__ 폴더 존재 여부 확인"""
    pycache_path = Path(folder_path) / "__pycache__"
    exists = pycache_path.exists()
    
    if exists:
        files = list(pycache_path.glob("*.pyc"))
        print(f"  📁 __pycache__ 존재: {len(files)}개 .pyc 파일")
        for f in files[:3]:  # 처음 3개만 표시
            print(f"    - {f.name}")
    else:
        print(f"  ✅ __pycache__ 없음")
    
    return exists

def test_import_creates_pycache():
    """import가 __pycache__를 재생성하는지 테스트"""
    print("=" * 70)
    print("🧪 __pycache__ 재생성 테스트")
    print("=" * 70)
    
    # editor 폴더 경로
    editor_path = Path(__file__).parent.parent / "editor"
    
    print(f"\n📂 테스트 경로: {editor_path}")
    
    # 1. 현재 상태 확인
    print("\n1️⃣ 현재 상태:")
    check_pycache_exists(editor_path)
    
    # 2. __pycache__ 삭제
    print("\n2️⃣ __pycache__ 삭제 시도...")
    pycache_path = editor_path / "__pycache__"
    if pycache_path.exists():
        import shutil
        shutil.rmtree(pycache_path, ignore_errors=True)
        time.sleep(0.1)
        print("  🗑️  삭제 완료")
    
    # 3. 삭제 확인
    print("\n3️⃣ 삭제 후 상태:")
    exists_after_delete = check_pycache_exists(editor_path)
    
    # 4. 모듈 import 시도
    print("\n4️⃣ 모듈 import 시도...")
    try:
        import importlib
        if 'editor.python_context' in sys.modules:
            print("  🔄 기존 모듈 리로드")
            importlib.reload(sys.modules['editor.python_context'])
        else:
            print("  📦 새로 import")
            import editor.python_context
    except Exception as e:
        print(f"  ❌ Import 실패: {e}")
    
    # 5. import 후 상태 확인
    print("\n5️⃣ import 후 상태:")
    exists_after_import = check_pycache_exists(editor_path)
    
    # 결과 분석
    print("\n" + "=" * 70)
    print("📊 결과 분석")
    print("=" * 70)
    
    if not exists_after_delete and exists_after_import:
        print("✅ 확인: Python이 import 시 __pycache__를 자동 재생성합니다!")
        print("💡 결론: __pycache__ 삭제는 의미가 없을 수 있습니다.")
    elif exists_after_delete:
        print("⚠️  삭제가 실패했습니다 (파일이 사용 중)")
    else:
        print("❓ __pycache__가 재생성되지 않음 (예상 밖)")

if __name__ == "__main__":
    test_import_creates_pycache()
