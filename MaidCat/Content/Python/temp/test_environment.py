"""
환경 테스트 스크립트
- 언리얼 엔진 버전 확인
- Python 경로 상태 확인
- TAPython 라이브러리 확인
- 기본 API 동작 테스트
"""

import unreal
import sys
from pathlib import Path

def test_environment():
    """개발 환경 테스트"""
    
    print("=" * 70)
    print("🧪 MaidCat 환경 테스트 시작")
    print("=" * 70)
    
    # 1. 언리얼 엔진 정보
    print("\n📦 언리얼 엔진 정보:")
    try:
        engine_version = unreal.SystemLibrary.get_engine_version()
        print(f"   ✅ 엔진 버전: {engine_version}")
    except Exception as e:
        print(f"   ❌ 엔진 버전 확인 실패: {e}")
    
    # 2. Python 정보
    print("\n🐍 Python 정보:")
    print(f"   ✅ Python 버전: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print(f"   ✅ 실행 파일: {sys.executable}")
    
    # 3. 프로젝트 경로
    print("\n📁 프로젝트 경로:")
    project_dir = unreal.Paths.project_dir()
    print(f"   ✅ 프로젝트 디렉토리: {project_dir}")
    print(f"   ✅ 콘텐츠 디렉토리: {unreal.Paths.project_content_dir()}")
    
    # 4. TAPython 라이브러리 확인
    print("\n🔧 TAPython 라이브러리 확인:")
    tapython_libs = [
        "PythonBPLib",
        "PythonMaterialLib",
        "PythonDataTableLib",
        "PythonMeshLib",
        "PythonEnumLib",
        "PythonStructLib",
    ]
    
    available_libs = []
    for lib_name in tapython_libs:
        if hasattr(unreal, lib_name):
            available_libs.append(lib_name)
            print(f"   ✅ {lib_name}")
        else:
            print(f"   ❌ {lib_name} - 없음")
    
    # 5. sys.path 확인
    print("\n📋 Python 경로 (sys.path) 상태:")
    unique_paths = list(dict.fromkeys(str(Path(p)) for p in sys.path if p))
    
    # MaidCat 관련 경로 필터링
    maidcat_paths = [p for p in unique_paths if 'MaidCat' in p or 'TAPython' in p]
    print(f"   MaidCat/TAPython 관련 경로 ({len(maidcat_paths)}개):")
    for path in maidcat_paths:
        print(f"      - {path}")
    
    # 6. 간단한 API 테스트
    print("\n🧪 기본 API 테스트:")
    try:
        # 에디터 서브시스템 가져오기
        asset_subsystem = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
        print(f"   ✅ EditorAssetSubsystem 접근 성공")
        
        # 액터 서브시스템
        actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        print(f"   ✅ EditorActorSubsystem 접근 성공")
        
        # 현재 선택된 액터 수
        selected_actors = actor_subsystem.get_selected_level_actors()
        print(f"   ✅ 현재 선택된 액터: {len(selected_actors)}개")
        
    except Exception as e:
        print(f"   ❌ API 테스트 실패: {e}")
    
    # 7. TAPython 기능 테스트
    print("\n🎨 TAPython 기능 테스트:")
    try:
        if hasattr(unreal, 'PythonBPLib'):
            # 뷰포트 카메라 위치 가져오기 시도
            cam_loc = unreal.PythonBPLib.get_view_port_camera_location()
            cam_rot = unreal.PythonBPLib.get_view_port_camera_rotation()
            print(f"   ✅ 뷰포트 카메라 위치: {cam_loc}")
            print(f"   ✅ 뷰포트 카메라 회전: {cam_rot}")
        else:
            print(f"   ⚠️  PythonBPLib 없음 - TAPython 미설치")
    except Exception as e:
        print(f"   ⚠️  TAPython 기능 테스트 실패: {e}")
    
    # 결과 요약
    print("\n" + "=" * 70)
    print("📊 테스트 결과 요약:")
    print(f"   • TAPython 라이브러리: {len(available_libs)}/{len(tapython_libs)} 사용 가능")
    print(f"   • Python 경로: {len(unique_paths)}개 등록됨")
    print("=" * 70)
    
    unreal.log("✅ 환경 테스트 완료")

if __name__ == "__main__":
    test_environment()
