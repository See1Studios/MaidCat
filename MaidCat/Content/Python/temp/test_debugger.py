"""
디버거 테스트 스크립트
- 브레이크포인트 설정 테스트
- 변수 검사 테스트
- 스텝 실행 테스트
"""

import unreal

def test_basic_operations():
    """기본 연산 테스트 - 브레이크포인트 설정 위치"""
    
    # 1. 간단한 변수 선언
    project_dir = unreal.Paths.project_dir()
    content_dir = unreal.Paths.project_content_dir()
    
    print(f"프로젝트 디렉토리: {project_dir}")
    print(f"콘텐츠 디렉토리: {content_dir}")
    
    # 2. 리스트 처리
    test_numbers = [1, 2, 3, 4, 5]
    squared = [n ** 2 for n in test_numbers]
    
    print(f"원본 숫자: {test_numbers}")
    print(f"제곱 결과: {squared}")
    
    # 3. 서브시스템 접근
    asset_subsystem = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    
    # 4. 액터 정보
    selected_actors = actor_subsystem.get_selected_level_actors()
    
    print(f"\n현재 선택된 액터 수: {len(selected_actors)}")
    
    for i, actor in enumerate(selected_actors):
        actor_name = actor.get_name()
        actor_class = actor.get_class().get_name()
        actor_location = actor.get_actor_location()
        
        print(f"\n액터 {i + 1}:")
        print(f"  이름: {actor_name}")
        print(f"  클래스: {actor_class}")
        print(f"  위치: {actor_location}")
    
    return len(selected_actors)


def test_loop_debugging():
    """반복문 디버깅 테스트"""
    
    print("\n반복문 테스트 시작")
    
    results = []
    for i in range(5):
        value = i * 10
        results.append(value)
        print(f"  반복 {i}: 값 = {value}")
    
    total = sum(results)
    print(f"합계: {total}")
    
    return results


def main():
    """메인 함수 - 여기에 브레이크포인트 설정"""
    
    print("=" * 70)
    print("🐛 디버거 테스트 시작")
    print("=" * 70)
    
    # 기본 연산 테스트
    actor_count = test_basic_operations()
    
    # 반복문 테스트
    loop_results = test_loop_debugging()
    
    # 결과 요약
    print("\n" + "=" * 70)
    print("📊 테스트 완료")
    print(f"  액터 수: {actor_count}")
    print(f"  반복 결과: {loop_results}")
    print("=" * 70)
    
    unreal.log("✅ 디버거 테스트 완료")


if __name__ == "__main__":
    main()
