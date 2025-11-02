# ============================================================================
# init_unreal.py - MaidCat 플러그인 핵심 초기화 스크립트
# ============================================================================
"""
MaidCat 플러그인 시작 시 실행되는 핵심 초기화 스크립트
핵심 기능만 담당:
- Python 경로 설정 (sys.path)
- 기본 환경 확인
- 다른 모듈들이 실행될 수 있는 기반 마련

사용법:
    MaidCatInitializer.initialize()  # 핵심 초기화
    MaidCatInitializer.install_dependencies()  # 의존성 설치
    MaidCatInitializer.setup_dev_environment()  # 개발환경 설정
"""

import sys
import unreal
from pathlib import Path
import time


class MaidCatInitializer:
    """MaidCat 플러그인 초기화 관리 클래스"""
    
    @staticmethod
    def get_plugin_path() -> Path:
        """플러그인 경로 반환"""
        current_file = Path(__file__)
        # init_unreal.py -> Python -> Content -> MaidCat (플러그인 루트)
        return current_file.parent.parent.parent
    
    @staticmethod
    def add_to_sys_path(path_str: str, description: str = ""):
        """sys.path에 경로 추가 (중복 방지)"""
        normalized_path = str(Path(path_str))
        
        if normalized_path not in sys.path:
            sys.path.append(normalized_path)
            print(f"✅ sys.path 추가: {normalized_path}")
            if description:
                print(f"   ({description})")
            return True
        return False
    
    @staticmethod
    def setup_python_paths():
        """플러그인 및 프로젝트 Python 경로 설정"""
        plugin_path = MaidCatInitializer.get_plugin_path()
        project_path = Path(unreal.Paths.project_dir())
        
        print("\n📂 Python 경로 설정 중...")
        
        # 필요할 수 있는 추가 경로들만 체크
        additional_paths = [
            (project_path / "TA" / "TAPython" / "Python", "프로젝트 TA Python"),
            (project_path / "TA" / "TAPython" / "Lib" / "site-packages", "프로젝트 TA 라이브러리"),
        ]
        
        added_count = 0
        for path, description in additional_paths:
            if path.exists():
                if MaidCatInitializer.add_to_sys_path(str(path), description):
                    added_count += 1
        
        if added_count > 0:
            print(f"{added_count}개 경로 추가됨")
        else:
            print(f"모든 필요한 경로가 이미 설정됨")
    
    @staticmethod
    def check_basic_environment():
        """기본 환경 상태 확인"""
        print("\n🔍 기본 환경 확인 중...")
        
        # Unreal Engine 버전 확인
        try:
            engine_version = unreal.SystemLibrary.get_engine_version()
            print(f"   ✅ Unreal Engine 버전: {engine_version}")
        except Exception as e:
            print(f"   ⚠️  엔진 버전 확인 실패: {e}")
        
        # Python 버전 확인
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        print(f"   ✅ Python 버전: {python_version}")
        
        # 플러그인 경로 확인
        plugin_path = MaidCatInitializer.get_plugin_path()
        if plugin_path.exists():
            print(f"   ✅ 플러그인 경로: {plugin_path}")
        else:
            print(f"   ❌ 플러그인 경로 찾을 수 없음: {plugin_path}")
        
        # sys.path 상태 출력 (간소화 버전)
        unique_paths = list(dict.fromkeys(str(Path(p)) for p in sys.path if p))
        sorted_paths = sorted(unique_paths, key=str.lower)
        
        print(f"\n📋 현재 sys.path 상태 ({len(sorted_paths)}개 고유 경로):")
        for i, path in enumerate(sorted_paths, 1):
            print(f"   {i:2d}. {path}")
    
    @staticmethod
    def run_startup_modules():
        """startup 폴더의 모듈들 자동 실행 (성능 모니터링 포함)"""
        print("\n🚀 startup 모듈들 실행 중...")
        
        startup_path = MaidCatInitializer.get_plugin_path() / "Content" / "Python" / "startup"
        if not startup_path.exists():
            print("   ⚠️  startup 폴더를 찾을 수 없습니다")
            return
        
        # startup 폴더의 Python 파일들 찾기
        startup_files = list(startup_path.glob("*.py"))
        
        # 제외할 파일들 (테스트나 특수 목적)
        exclude_files = {
            "test_context_menu.py",  # 테스트 파일
            "setup_python.py",      # 별도로 호출되는 설정 파일
            "__init__.py"           # 초기화 파일
        }
        
        executed_count = 0
        failed_count = 0
        total_start_time = time.time()
        execution_times = []
        
        for py_file in startup_files:
            file_name = py_file.name
            
            if file_name in exclude_files:
                print(f"   ⏭️  건너뜀: {file_name} (제외 목록)")
                continue
            
            module_start_time = time.time()
            
            try:
                # 모듈명에서 .py 제거
                module_name = f"startup.{file_name[:-3]}"
                
                # 모듈 import 및 실행
                import importlib
                module = importlib.import_module(module_name)
                
                # main 함수가 있으면 실행
                if hasattr(module, 'main'):
                    main_start_time = time.time()
                    module.main()
                    main_end_time = time.time()
                    main_duration = (main_end_time - main_start_time) * 1000
                    
                    module_end_time = time.time()
                    total_duration = (module_end_time - module_start_time) * 1000
                    
                    print(f"   ✅ {file_name}: main() 실행됨 ({main_duration:.1f}ms, 총 {total_duration:.1f}ms)")
                    execution_times.append((file_name, total_duration))
                else:
                    module_end_time = time.time()
                    total_duration = (module_end_time - module_start_time) * 1000
                    
                    print(f"   💡 {file_name}: import됨 ({total_duration:.1f}ms, main 함수 없음)")
                    execution_times.append((file_name, total_duration))
                
                executed_count += 1
                
            except Exception as e:
                module_end_time = time.time()
                total_duration = (module_end_time - module_start_time) * 1000
                
                print(f"   ❌ {file_name}: 실행 실패 ({total_duration:.1f}ms) - {e}")
                failed_count += 1
        
        total_end_time = time.time()
        total_execution_time = (total_end_time - total_start_time) * 1000
        
        # 실행 결과 및 성능 요약
        print(f"   📊 실행 결과: ✅ {executed_count}개 성공, ❌ {failed_count}개 실패")
        print(f"   ⏱️  총 실행 시간: {total_execution_time:.1f}ms")
        
        # 성능 경고 (100ms 이상 걸리는 모듈)
        slow_modules = [(name, duration) for name, duration in execution_times if duration > 100]
        if slow_modules:
            print(f"   ⚠️  느린 모듈 ({len(slow_modules)}개):")
            for name, duration in sorted(slow_modules, key=lambda x: x[1], reverse=True):
                print(f"      🐌 {name}: {duration:.1f}ms")
        
        # 가장 빠른/느린 모듈 표시
        if execution_times:
            fastest = min(execution_times, key=lambda x: x[1])
            slowest = max(execution_times, key=lambda x: x[1])
            print(f"   🚀 가장 빠름: {fastest[0]} ({fastest[1]:.1f}ms)")
            print(f"   🐌 가장 느림: {slowest[0]} ({slowest[1]:.1f}ms)")
    
    @staticmethod
    def initialize():
        """핵심 초기화 - 필수 기능만 실행"""
        print("\n🐱 MaidCat Plugin 핵심 초기화 시작...")
        
        try:
            # Python 경로 설정 (필수)
            MaidCatInitializer.setup_python_paths()
            
            # 기본 환경 확인
            MaidCatInitializer.check_basic_environment()
            
            # startup 모듈들 자동 실행
            MaidCatInitializer.run_startup_modules()
            
            print("\n✅ MaidCat 플러그인 핵심 초기화 완료!")
            print("💡 추가 기능:")
            print("   📦 의존성 설치: `MaidCatInitializer.install_dependencies()`")
            print("   🔧 개발환경 설정: `MaidCatInitializer.setup_dev_environment()`")
            
        except Exception as e:
            print(f"\n❌ 플러그인 초기화 실패: {e}")
            import traceback
            traceback.print_exc()
    
    @staticmethod
    def install_dependencies():
        """의존성 설치"""
        try:
            from tool.dependencies_installer import install_dependencies
            install_dependencies()
        except Exception as e:
            print(f"❌ 의존성 설치 실패: {e}")
    
    @staticmethod
    def setup_dev_environment(mode: str = "all"):
        """개발 환경 설정
        
        Args:
            mode: 설정 모드 - "all", "vscode", "pycharm"
        """
        try:
            from startup.setup_python import main
            main(mode)
        except Exception as e:
            print(f"❌ 개발 환경 설정 실패: {e}")

# ============================================================================
# 메인 실행 - 엔트리 포인트
# ============================================================================

if __name__ == "__main__":
    # MaidCat 플러그인 핵심 초기화 실행
    MaidCatInitializer.initialize()