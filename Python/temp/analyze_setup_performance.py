"""
setup_python.py 성능 분석 스크립트
느린 부분을 찾아내기 위한 프로파일링
"""

import unreal
import time
from pathlib import Path

def measure_time(func_name, func):
    """함수 실행 시간 측정"""
    start = time.time()
    result = func()
    elapsed = time.time() - start
    print(f"   ⏱️  {func_name}: {elapsed:.3f}초")
    return result, elapsed

def analyze_setup_performance():
    """setup_python의 각 단계별 성능 분석"""
    print("=" * 70)
    print("🔍 setup_python.py 성능 분석")
    print("=" * 70)
    
    total_times = {}
    
    # 1. 모듈 임포트 시간 측정
    print("\n📦 모듈 임포트 시간 측정...")
    
    start = time.time()
    import tool.dev_env_setup
    import_time = time.time() - start
    total_times['모듈 임포트'] = import_time
    print(f"   ⏱️  tool.dev_env_setup 임포트: {import_time:.3f}초")
    
    # 2. 경로 수집 시간
    print("\n📁 경로 수집 시간 측정...")
    _, path_time = measure_time(
        "경로 수집",
        lambda: tool.dev_env_setup._get_paths()
    )
    total_times['경로 수집'] = path_time
    
    # 3. Python 경로 생성 시간
    print("\n🐍 Python 경로 생성 시간 측정...")
    project_path, current_plugin_path, resolved_plugin_path = tool.dev_env_setup._get_paths()
    
    _, python_paths_time = measure_time(
        "Python 경로 리스트 생성",
        lambda: tool.dev_env_setup.get_project_python_paths(current_plugin_path, project_path)
    )
    total_times['Python 경로 생성'] = python_paths_time
    
    # 4. 플러그인 검색 시간 (다른 플러그인들)
    print("\n🔌 플러그인 검색 시간 측정...")
    plugins_dir = project_path / "Plugins"
    if plugins_dir.exists():
        start = time.time()
        plugin_count = 0
        for plugin_dir in plugins_dir.iterdir():
            if plugin_dir.is_dir():
                plugin_count += 1
                plugin_python = plugin_dir / "Content" / "Python"
                _ = plugin_python.exists()  # exists() 호출
        plugin_scan_time = time.time() - start
        total_times['플러그인 스캔'] = plugin_scan_time
        print(f"   ⏱️  플러그인 스캔 ({plugin_count}개): {plugin_scan_time:.3f}초")
    
    # 5. 언리얼 Python 인터프리터 감지 시간 (레지스트리 포함)
    print("\n🔧 Python 인터프리터 감지 시간 측정...")
    _, interpreter_time = measure_time(
        "언리얼 Python 인터프리터 감지",
        lambda: tool.dev_env_setup._get_unreal_python_interpreter()
    )
    total_times['인터프리터 감지'] = interpreter_time
    
    # 6. VSCode 설정 파일 I/O 시간
    print("\n📝 VSCode 설정 파일 I/O 시간 측정...")
    vscode_settings_path = project_path / ".vscode" / "settings.json"
    
    # 읽기 시간
    _, read_time = measure_time(
        "settings.json 읽기",
        lambda: tool.dev_env_setup._load_existing_vscode_settings(vscode_settings_path)
    )
    total_times['설정 파일 읽기'] = read_time
    
    # 쓰기 시간
    python_paths = tool.dev_env_setup.get_project_python_paths(current_plugin_path, project_path)
    settings = tool.dev_env_setup._create_vscode_python_settings(python_paths, "permissive")
    
    _, write_time = measure_time(
        "settings.json 쓰기",
        lambda: tool.dev_env_setup._save_vscode_settings(vscode_settings_path, settings)
    )
    total_times['설정 파일 쓰기'] = write_time
    
    # 7. PyCharm 설정 파일 생성 시간
    print("\n🧪 PyCharm 설정 파일 생성 시간 측정...")
    
    test_dir = project_path / ".idea_test"
    _, pycharm_time = measure_time(
        "PyCharm 설정 파일 생성",
        lambda: _test_pycharm_creation(test_dir, python_paths)
    )
    total_times['PyCharm 설정 생성'] = pycharm_time
    
    # 테스트 디렉토리 삭제
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    
    # 8. Copilot 지침 복사 시간
    print("\n📋 Copilot 지침 복사 시간 측정...")
    _, copilot_time = measure_time(
        "Copilot 지침 복사",
        lambda: _test_copilot_copy()
    )
    total_times['Copilot 지침 복사'] = copilot_time
    
    # 결과 요약
    print("\n" + "=" * 70)
    print("📊 성능 분석 결과 요약")
    print("=" * 70)
    
    # 시간순으로 정렬
    sorted_times = sorted(total_times.items(), key=lambda x: x[1], reverse=True)
    
    total_time = sum(total_times.values())
    
    for i, (name, elapsed) in enumerate(sorted_times, 1):
        percentage = (elapsed / total_time * 100) if total_time > 0 else 0
        bar_length = int(percentage / 2)  # 최대 50칸
        bar = "█" * bar_length
        print(f"{i}. {name:.<30} {elapsed:>6.3f}초 ({percentage:>5.1f}%) {bar}")
    
    print("-" * 70)
    print(f"{'총 측정 시간':.<30} {total_time:>6.3f}초 (100.0%)")
    print("=" * 70)
    
    # 개선 제안
    print("\n💡 성능 개선 제안:")
    
    if total_times.get('인터프리터 감지', 0) > 0.5:
        print("   ⚠️  인터프리터 감지가 느림 → 캐싱 고려")
    
    if total_times.get('플러그인 스캔', 0) > 0.3:
        print("   ⚠️  플러그인 스캔이 느림 → 병렬 처리 또는 캐싱 고려")
    
    if total_times.get('PyCharm 설정 생성', 0) > 1.0:
        print("   ⚠️  PyCharm 설정이 느림 → 필요시에만 생성하도록 변경")
    
    if total_times.get('모듈 임포트', 0) > 0.5:
        print("   ⚠️  모듈 임포트가 느림 → 지연 로딩 고려")
    
    print("\n✅ 분석 완료!")
    return total_times


def _test_pycharm_creation(test_dir, python_paths):
    """PyCharm 설정 생성 테스트"""
    test_dir.mkdir(exist_ok=True)
    idea_dir = test_dir / ".idea"
    idea_dir.mkdir(exist_ok=True)
    
    # 실제 생성 함수들 호출
    tool.dev_env_setup._create_pycharm_misc_xml(idea_dir)
    tool.dev_env_setup._create_pycharm_modules_xml(idea_dir, test_dir)
    tool.dev_env_setup._create_pycharm_iml_file(idea_dir, test_dir, python_paths)
    tool.dev_env_setup._create_pycharm_workspace_xml(idea_dir)


def _test_copilot_copy():
    """Copilot 지침 복사 테스트"""
    import startup.setup_python
    # 복사 시도 (실패해도 무시)
    try:
        startup.setup_python.copy_copilot_instructions()
    except Exception:
        pass


if __name__ == "__main__":
    analyze_setup_performance()
