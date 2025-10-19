"""
Python Context Menu 테스트 및 사용 예제
"""

import unreal


def test_context_menu_setup():
    """컨텍스트 메뉴 설정 테스트"""
    print("\n" + "="*60)
    print("Python Context Menu 테스트")
    print("="*60)
    
    # 1. 모듈 로드
    try:
        import startup.init_context as ctx
        import importlib
        importlib.reload(ctx)
        print("✅ init_context 모듈 로드 성공")
    except Exception as e:
        print(f"❌ 모듈 로드 실패: {e}")
        return
    
    # 2. 컨텍스트 메뉴 설정
    try:
        ctx.setup_python_context_menu()
        print("✅ 컨텍스트 메뉴 설정 완료")
    except Exception as e:
        print(f"❌ 컨텍스트 메뉴 설정 실패: {e}")
        return
    
    print("\n사용 방법:")
    print("1. Content Browser에서 /Game/Python 폴더로 이동")
    print("2. Python 파일(.py) 또는 폴더를 우클릭")
    print("3. 'Python' 섹션의 메뉴 항목 확인")
    print("="*60 + "\n")


def test_module_reload():
    """모듈 리로드 기능 테스트"""
    print("\n" + "="*60)
    print("모듈 리로드 테스트")
    print("="*60)
    
    import importlib
    import sys
    
    # util.helper 모듈 리로드 테스트
    module_name = "util.helper"
    
    try:
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
            print(f"✅ {module_name} 리로드 성공")
        else:
            __import__(module_name)
            print(f"✅ {module_name} 로드 성공")
            
        # 테스트: helper 모듈 사용
        from util import helper as uh
        print(f"\n테스트: get_engine_version() = {uh.get_engine_version()}")
        
    except Exception as e:
        print(f"❌ 리로드 실패: {e}")
    
    print("="*60 + "\n")


def test_file_execution():
    """파일 실행 기능 테스트"""
    print("\n" + "="*60)
    print("파일 실행 테스트")
    print("="*60)
    
    import os
    
    # 테스트할 간단한 Python 코드
    test_code = """
print("Hello from executed Python file!")
import unreal
unreal.log("Unreal에서 실행됨!")
"""
    
    # 임시 테스트 파일 생성
    content_dir = unreal.Paths.project_content_dir()
    test_file = os.path.join(content_dir, "Python", "test_execution.py")
    
    try:
        # 파일 생성
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_code)
        print(f"✅ 테스트 파일 생성: {test_file}")
        
        # 파일 실행
        with open(test_file, 'r', encoding='utf-8') as f:
            code = f.read()
        
        exec(code, {'__name__': '__main__'})
        print("✅ 파일 실행 성공")
        
        # 정리
        os.remove(test_file)
        print("✅ 테스트 파일 삭제")
        
    except Exception as e:
        print(f"❌ 실행 실패: {e}")
    
    print("="*60 + "\n")


def show_selected_info():
    """현재 선택된 항목 정보 표시"""
    print("\n" + "="*60)
    print("선택된 항목 정보")
    print("="*60)
    
    # 선택된 에셋
    assets = unreal.EditorUtilityLibrary.get_selected_assets()
    if assets:
        print(f"\n📦 선택된 에셋 ({len(assets)}개):")
        for asset in assets:
            print(f"  • {asset.get_name()}")
            print(f"    경로: {asset.get_path_name()}")
    
    # 선택된 폴더
    folders = unreal.EditorUtilityLibrary.get_selected_folder_paths()
    if folders:
        print(f"\n📁 선택된 폴더 ({len(folders)}개):")
        for folder in folders:
            print(f"  • {folder}")
    
    if not assets and not folders:
        print("\n선택된 항목이 없습니다")
    
    print("="*60 + "\n")


def run_all_tests():
    """모든 테스트 실행"""
    print("\n" + "🧪 " + "="*58)
    print("Python Context Menu 전체 테스트 시작")
    print("="*60)
    
    test_context_menu_setup()
    test_module_reload()
    test_file_execution()
    show_selected_info()
    
    print("="*60)
    print("🎉 모든 테스트 완료!")
    print("="*60 + "\n")


# 간단한 메뉴
def show_menu():
    """테스트 메뉴 표시"""
    print("\n" + "="*60)
    print("Python Context Menu 테스트")
    print("="*60)
    print("\n사용 가능한 함수:")
    print("  1. test_context_menu_setup()  - 컨텍스트 메뉴 설정")
    print("  2. test_module_reload()       - 모듈 리로드 테스트")
    print("  3. test_file_execution()      - 파일 실행 테스트")
    print("  4. show_selected_info()       - 선택 정보 표시")
    print("  5. run_all_tests()            - 전체 테스트")
    print("\n예제:")
    print("  import startup.test_context_menu as test")
    print("  test.run_all_tests()")
    print("="*60 + "\n")


# 모듈 로드 시 메뉴 표시
if __name__ != "__main__":
    show_menu()
