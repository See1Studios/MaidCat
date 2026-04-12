# setup_python.py 성능 분석 및 최적화 방안

## 현재 상태
- 실행 시간: **약 700ms**
- 주요 병목: PyCharm 설정 디렉토리 검색 및 파일 I/O

## 성능 병목 원인

### 1. PyCharm 설정 디렉토리 검색 (300-400ms 예상)
```python
def get_pycharm_config_dir():
    # 6개 이상의 디렉토리를 순차적으로 확인
    config_dirs = [
        "PyCharm2024.3", "PyCharm2024.2", "PyCharm2024.1",
        "PyCharm2023.3", "PyCharmCE2024.3", "PyCharmCE2024.2"
    ]
    for config_dir in config_dirs:
        if config_dir.exists():  # 느린 I/O 작업
            return config_dir
```

### 2. 파일 I/O 작업 (200-300ms)
- VSCode settings.json 읽기/쓰기
- PyCharm XML 파일들 생성 (misc.xml, modules.xml, workspace.xml, .iml)
- JSON/XML 파싱

### 3. 경로 계산 (50-100ms)
- `Path.resolve()` - 심볼릭 링크 해석
- 여러 Python 경로 검증

## 최적화 방안

### 즉시 적용 가능 (High Impact)

#### 1. PyCharm 설정 캐싱
```python
# 전역 캐시 변수
_pycharm_config_cache = None

def get_pycharm_config_dir():
    global _pycharm_config_cache
    if _pycharm_config_cache is not None:
        return _pycharm_config_cache
    
    # ... 기존 로직
    _pycharm_config_cache = found_dir
    return found_dir
```

#### 2. Lazy 초기화
```python
def setup_all(skip_pycharm=False):
    """
    skip_pycharm=True 시 PyCharm 설정 건너뛰기
    대부분 사용자는 VSCode만 사용
    """
    update_project_settings()  # VSCode만
    
    if not skip_pycharm:
        setup_pycharm_python_interpreter()
```

#### 3. 조건부 실행
```python
def setup_python_smart():
    """필요한 것만 업데이트"""
    # VSCode settings.json이 최신이면 건너뛰기
    if is_settings_up_to_date():
        print("   ⏭️  설정이 최신 상태입니다.")
        return
    
    # 실제 업데이트 필요한 경우만 실행
    update_project_settings()
```

### 중장기 최적화

#### 4. 병렬 처리
```python
import concurrent.futures

def setup_all_parallel():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        vscode_future = executor.submit(update_project_settings)
        pycharm_future = executor.submit(setup_pycharm_python_interpreter)
        
        vscode_future.result()
        pycharm_future.result()
```

#### 5. 증분 업데이트
- 변경된 설정만 업데이트
- 타임스탬프 기반 캐시 무효화

## 권장 적용 순서

1. **즉시**: `skip_pycharm` 옵션 추가 (VSCode 전용 사용자용)
2. **단기**: PyCharm 디렉토리 캐싱
3. **중기**: 조건부 실행 (설정 변경 감지)
4. **장기**: 필요시 병렬 처리

## 예상 효과

| 최적화 | 예상 시간 절감 | 난이도 |
|--------|----------------|--------|
| skip_pycharm 옵션 | 300-400ms | ⭐ 쉬움 |
| 디렉토리 캐싱 | 200-300ms | ⭐ 쉬움 |
| 조건부 실행 | 500-600ms | ⭐⭐ 보통 |
| 병렬 처리 | 200-300ms | ⭐⭐⭐ 어려움 |

**최대 절감 가능 시간**: 700ms → **100-200ms** (70-85% 개선)
