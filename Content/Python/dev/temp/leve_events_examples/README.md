# Level Events Examples

Unreal Engine의 레벨 에디터 이벤트 델리게이트 사용 예제 모음입니다.

## 📁 파일 구성

- `level_events_sample.py` - 완전한 기능을 갖춘 샘플 클래스
- `quick_test.py` - 빠른 테스트를 위한 간단한 스크립트

## 🚀 사용법

### 1. 완전한 샘플 실행

Unreal Editor Python 콘솔에서:

```python
# 샘플 실행
exec(open('examples/level_events_sample.py').read())

# 또는 모듈로 임포트
import sys
sys.path.append('examples')
from level_events_sample import main, cleanup_sample

# 샘플 실행
sample = main()

# 종료 시 정리
cleanup_sample(sample)
```

### 2. 빠른 테스트

```python
# 빠른 테스트 실행
exec(open('examples/quick_test.py').read())

# 종료 시 정리
cleanup_quick_test()
```

## 🎯 지원하는 이벤트

| 이벤트 | 설명 | 콜백 시그니처 |
|--------|------|---------------|
| `on_map_changed` | 맵 변경 시 (빠름, 주의 필요) | `(flags: int)` |
| `on_map_opened` | 맵 열림 시 (안정적, 권장) | `(filename: str, as_template: bool)` |
| `on_camera_moved` | 카메라 이동 시 | `(location, rotation, viewport_type, view_index)` |
| `on_pre_save_world` | 월드 저장 전 | `(flags: int, world: World)` |
| `on_post_save_world` | 월드 저장 후 | `(flags: int, world: World, success: bool)` |

## 💡 주의사항

1. **`on_map_changed` vs `on_map_opened`**
   - `on_map_changed`: 일부 에디터 스크립팅에는 너무 빠름
   - `on_map_opened`: 더 안정적이며 권장됨

2. **카메라 이벤트**
   - 매우 자주 호출되므로 성능에 주의
   - 필요시 throttling 구현 권장

3. **월드 저장 이벤트**
   - `pre_save`: 검증이나 준비 작업용
   - `post_save`: 후처리나 로깅용

## 🔧 유틸리티 함수

```python
# 현재 레벨 정보 확인
get_current_level_info()

# LevelEditorSubsystem 메서드 테스트
test_level_subsystem_methods()
```

## 📚 관련 문서

- [Unreal Engine Python API](https://docs.unrealengine.com/5.3/en-US/python-api/)
- [LevelEditorSubsystem](https://docs.unrealengine.com/5.3/en-US/BlueprintAPI/Editor/LevelEditor/LevelEditorSubsystem/)
- [MaidCat Plugin Documentation](../../README.md)

## 🛠️ 개발자 노트

이 예제들은 MaidCat 플러그인의 `ue.level_sys` 모듈을 기반으로 작성되었습니다. 
직접 Unreal API를 사용하려면 다음과 같이 할 수 있습니다:

```python
# 직접 API 사용
subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
subsystem.on_map_opened.add_callable(your_callback)
```

하지만 `level_sys` 모듈을 사용하면 더 안전하고 편리합니다.