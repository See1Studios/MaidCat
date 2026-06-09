# TAPython DetailPanelCustomization 가이드

## 개요

TAPython v1.2.3의 실험적 기능인 DetailPanelCustomization을 사용하여 언리얼 에디터의 디테일 패널에 커스텀 UI를 추가하는 방법입니다.

⚠️ **주의**: 이 기능은 실험적(Experimental)이며 공식 문서화되지 않았습니다.

## 핵심 발견사항

### 1. API 사용법
```python
import unreal

# Object 인스턴스 가져오기 (Class 아님!)
actor = unreal.EditorLevelLibrary.get_selected_level_actors()[0]

# 상대 경로로 JSON 지정 (Content 디렉토리 기준)
json_path = "PPPreset/PPPreset.json"

# 등록
result = unreal.ChameleonData.add_detail_customization(actor, json_path)
print(f"등록 결과: {result}")
```

### 2. 필수 요구사항

#### ✅ Object Instance 사용
- **올바름**: `actor` (실제 인스턴스)
- **잘못됨**: `unreal.PostProcessVolume` (클래스)

#### ✅ 상대 경로 사용
- **올바름**: `"PPPreset/PPPreset.json"` (Content 기준)
- **잘못됨**: `"D:/Projects/.../PPPreset.json"` (절대 경로)
- **잘못됨**: `"../UI/PPPreset.json"` (TAPython/UI 기준)

#### ✅ InitPyCmd 필수
JSON 파일에 반드시 `InitPyCmd` 필드 포함 필요:
```json
{
    "InitPyCmd": "import unreal; unreal.log('초기화 완료!')",
    "Root": { ... }
}
```

#### ✅ "Root" 구조 사용
- **올바름**: `"Root": { "SVerticalBox": {...} }`
- **잘못됨**: `"Body": { "type": "SVerticalBox", ... }`

### 3. Component vs Actor

TAPython은 Component 중심으로 설계되었으나, Actor도 작동합니다:
- **경고 발생**: `Warning: Comp is not an UActorComponent`
- **실제 동작**: 정상 작동 (자동 처리됨)
- **권장**: `CameraComponent`, `StaticMeshComponent` 등 Component 사용

## 설정 방법

### 1. config.ini 설정

`TA/TAPython/Config/config.ini`:
```ini
[DetailPanelCustomization]
IsDetailCustomizationEnabled=True
IsForceAddDetailCustomization=True
IsReusingWidget=True
ClassName=PostProcessVolume
ClassName=CameraComponent
ClassName=StaticMeshComponent

[Advanced]
LogCreateWidget=True
```

⚠️ 엔진 재시작 필요!

### 2. 폴더 구조 생성

```
TA/TAPython/Python/
└── PPPreset/
    ├── __init__.py           # 빈 파일
    ├── PPPreset.py           # Python 로직
    └── PPPreset.json         # UI 정의
```

### 3. JSON 파일 작성

`PPPreset.json`:
```json
{
    "TabLabel": "Post Process Preset",
    "InitTabSize": [300, 150],
    "InitTabPosition": [100, 100],
    "InitPyCmd": "import unreal; unreal.log('🔥 DetailCustomization InitPyCmd 실행됨!')",
    "Root": {
        "SVerticalBox": {
            "Slots": [
                {
                    "STextBlock": {
                        "Text": "Post Process Preset",
                        "Justification": "Center"
                    }
                },
                {
                    "SButton": {
                        "Text": "Save Preset",
                        "HAlign": "Center",
                        "OnClick": "unreal.log('✅ Save Preset 클릭!')"
                    }
                },
                {
                    "SButton": {
                        "Text": "Load Preset",
                        "HAlign": "Center",
                        "OnClick": "unreal.log('✅ Load Preset 클릭!')"
                    }
                }
            ]
        }
    }
}
```

### 4. Python 로직 (선택사항)

`PPPreset.py`:
```python
import unreal

class PPDetailWidget:
    def __init__(self, json_path):
        self.json_path = json_path
        unreal.log(f"✅ PPDetailWidget 초기화: {json_path}")
    
    def on_save_clicked(self):
        unreal.log("💾 Save Preset 실행")
        # TODO: 실제 저장 로직
    
    def on_load_clicked(self):
        unreal.log("📂 Load Preset 실행")
        # TODO: 실제 로드 로직
```

## 등록 스크립트

### 방법 1: 선택된 액터에 등록

```python
import unreal

def register_detail_customization():
    # 선택된 액터 가져오기
    actors = unreal.EditorLevelLibrary.get_selected_level_actors()
    if not actors:
        unreal.log_error("액터를 선택해주세요!")
        return False
    
    actor = actors[0]
    json_path = "PPPreset/PPPreset.json"
    
    # 등록
    result = unreal.ChameleonData.add_detail_customization(actor, json_path)
    if result:
        unreal.log(f"✅ 등록 성공: {actor.get_name()}")
    else:
        unreal.log_error(f"❌ 등록 실패: {actor.get_name()}")
    
    return result

# 실행
register_detail_customization()
```

### 방법 2: 특정 타입의 모든 액터에 등록

```python
import unreal

def register_all_postprocess_volumes():
    # 모든 PostProcessVolume 가져오기
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    pp_volumes = [a for a in actors if isinstance(a, unreal.PostProcessVolume)]
    
    json_path = "PPPreset/PPPreset.json"
    success_count = 0
    
    for volume in pp_volumes:
        result = unreal.ChameleonData.add_detail_customization(volume, json_path)
        if result:
            success_count += 1
            unreal.log(f"✅ 등록: {volume.get_name()}")
    
    unreal.log(f"총 {success_count}/{len(pp_volumes)}개 등록 완료")
    return success_count

# 실행
register_all_postprocess_volumes()
```

## 유용한 API

### 등록된 커스터마이제이션 확인

```python
import unreal

# 모든 등록 정보 로그 출력
unreal.ChameleonData.log_all_saved_detail_customization()

# 등록 가능한 클래스 목록 (296개)
classes = unreal.ChameleonData.get_detail_panel_customized_class_names()
print(f"등록 가능한 클래스: {len(classes)}개")
for cls in classes[:10]:  # 처음 10개만
    print(f"  - {cls}")
```

### 커스터마이제이션 제거

```python
import unreal

# 모든 커스터마이제이션 제거
unreal.ChameleonData.clear_detail_customization()
unreal.log("🧹 모든 커스터마이제이션 제거 완료")
```

### 커스터마이즈된 객체 가져오기

```python
import unreal

# UniqueID로 객체 가져오기 (로그에서 확인 가능)
unique_id = 54867  # 예시
obj = unreal.ChameleonData.get_customized_object(unique_id)
if obj:
    unreal.log(f"✅ 객체 발견: {obj}")
else:
    unreal.log_warning(f"⚠️ UniqueID {unique_id} 객체 없음")
```

## UniqueID 활용

### UniqueID란?

TAPython이 각 DetailPanelCustomization에 할당하는 **고유 식별자**입니다.
- 로그에서 `SetDetailCustomizationWidget call. UniqueID: 54867` 형태로 확인
- 객체 또는 ChameleonData 인스턴스를 조회하는 데 사용

### UniqueID 확인 방법

#### 방법 1: 액터 선택 시 로그 확인
```python
# 1. 에디터에서 커스터마이징된 액터 선택
# 2. 출력 로그 창에서 "UniqueID:" 검색
# 예: PythonTA: SetDetailCustomizationWidget call. UniqueID: 54867, type: PostProcessVolume
```

#### 방법 2: 등록된 목록 확인
```python
import unreal

# 모든 등록 정보 출력 (UniqueID는 로그에만 표시됨)
unreal.ChameleonData.log_all_saved_detail_customization()
# 출력 예:
# Customization 1: /Temp/Untitled_2.Untitled_2:PersistentLevel.PostProcessVolume_1 -> PPPreset/PPPreset.json
```

#### 방법 3: 로그 파일 직접 확인
```bash
# Saved/Logs/*.log 파일 열기
# "UniqueID:" 검색
```

### UniqueID로 객체 조회

```python
import unreal

def get_object_info(unique_id):
    """UniqueID로 커스터마이징된 객체 정보 조회"""
    obj = unreal.ChameleonData.get_customized_object(unique_id)
    
    if obj:
        unreal.log(f"✅ 객체 발견!")
        unreal.log(f"   타입: {obj.get_class().get_name()}")
        unreal.log(f"   이름: {obj.get_name()}")
        unreal.log(f"   경로: {obj.get_path_name()}")
        return obj
    else:
        unreal.log_warning(f"⚠️ UniqueID {unique_id} 객체 없음")
        return None

# 사용 예
get_object_info(54867)
```

### UniqueID로 ChameleonData 조회

ChameleonData를 통해 위젯을 **동적으로 제어**할 수 있습니다:

```python
import unreal

# ChameleonData 가져오기
json_path = "PPPreset/PPPreset.json"
unique_id = 54867

data = unreal.PythonBPLib.get_chameleon_data(json_path, unique_id)

if data:
    # 위젯 제어 (JSON에 aka_name 필요)
    data.set_text("status_text", "✅ 프리셋 로드 완료!")
    data.set_enabled("save_button", False)
    data.set_combo_box_items("preset_combo", ["Day", "Night", "Sunset"])
```

### 동적 UI 제어를 위한 JSON 설정

ChameleonData로 제어하려면 JSON에 `aka_name` 추가:

```json
{
    "Root": {
        "SVerticalBox": {
            "Slots": [
                {
                    "STextBlock": {
                        "aka_name": "status_text",
                        "Text": "Ready"
                    }
                },
                {
                    "SButton": {
                        "aka_name": "save_button",
                        "Text": "Save",
                        "OnClick": "..."
                    }
                },
                {
                    "SComboBox": {
                        "aka_name": "preset_combo"
                    }
                }
            ]
        }
    }
}
```

### 완전한 워크플로우 예제

```python
import unreal

# 1단계: 액터 등록
actor = unreal.EditorLevelLibrary.get_selected_level_actors()[0]
json_path = "PPPreset/PPPreset.json"
result = unreal.ChameleonData.add_detail_customization(actor, json_path)

if result:
    unreal.log("✅ 등록 성공!")
    
    # 2단계: 등록된 목록 확인
    unreal.ChameleonData.log_all_saved_detail_customization()
    
    # 3단계: 에디터에서 액터 선택하여 UniqueID 확인
    # 로그에서 "UniqueID: 54867" 확인
    
    # 4단계: ChameleonData로 위젯 제어
    unique_id = 54867  # 로그에서 확인한 값
    data = unreal.PythonBPLib.get_chameleon_data(json_path, unique_id)
    
    if data:
        # 동적으로 UI 업데이트
        data.set_text("status", "커스터마이징 활성화됨!")
```

### 제한사항

- **Actor → UniqueID 직접 조회 불가**: TAPython API는 객체로부터 UniqueID를 직접 조회하는 방법을 제공하지 않음
- **로그 파싱 필요**: UniqueID를 얻으려면 로그 파일을 파싱하거나 액터 선택 시 로그를 확인해야 함
- **재시작 시 변경**: 엔진 재시작 시 UniqueID가 변경될 수 있음 (객체 경로로 관리 권장)

## 디버깅

### 로그 확인

`Saved/Logs/See1Unreal.log` (또는 프로젝트명.log):
```
PythonTA: Get Customization Json From Pool, Path PPPreset/PPPreset.json.
PythonTA: SetDetailCustomizationWidget call. UniqueID: 54867, type: PostProcessVolume
PythonTA: InitPyCmd: import unreal; unreal.log('🔥 DetailCustomization InitPyCmd 실행됨!')
LogPython: 🔥 DetailCustomization InitPyCmd 실행됨!
```

### 자주 발생하는 에러

#### ❌ "Json File can't find: InitPyCmd"
**원인**: JSON에 InitPyCmd 필드 없음  
**해결**: InitPyCmd 추가

#### ❌ "Both Object And Pool Failed"
**원인**: 절대 경로 사용 또는 파일 없음  
**해결**: 상대 경로로 변경, 파일 경로 확인

#### ❌ "File: for customize details not exists"
**원인**: 잘못된 경로  
**해결**: Content 디렉토리 기준 상대 경로로 수정

#### ⚠️ "Warning: Comp is not an UActorComponent"
**원인**: Actor에 등록 (Component 아님)  
**해결**: 무시 가능 (자동 처리됨) 또는 Component 사용

## 경로 해석 규칙

TAPython은 다음과 같이 경로를 해석합니다:

```
입력: "PPPreset/PPPreset.json"
실제 경로: TA/TAPython/Python/PPPreset/PPPreset.json
```

**구조**:
```
TA/TAPython/
├── Python/              ← Python 코드 루트
│   └── PPPreset/        ← 패키지 폴더
│       ├── __init__.py
│       ├── PPPreset.py
│       └── PPPreset.json
└── UI/                  ← 일반 Chameleon Tools (standalone)
```

## 제한사항

1. **실험적 기능** - 공식 지원 없음, 향후 변경 가능
2. **문서 부족** - 공식 문서 없음 (개발자도 권장하지 않음)
3. **엔진 재시작 필요** - config.ini 변경 시
4. **Component 중심** - Actor 사용 시 경고 발생 (작동은 함)
5. **경로 제약** - Content 디렉토리 기준 상대 경로만 가능

## 참고 자료

- **TAPython 공식 문서**: https://www.tacolor.xyz/tapython/
- **Chameleon Data API**: https://www.tacolor.xyz/pages/ChameleonDataAPI.html
- **GitHub**: https://github.com/cgerchenhp/UE_TAPython_Plugin_Release

## 샘플 코드 위치

**경로**: `Plugins/MaidCat/Content/Python/sample/detail_customization_samples/`

이 폴더의 모든 샘플 코드는 **실제 동작이 검증**되었습니다.

### Python 샘플
- `sample_detail_simple.py` - 간단한 등록 예제 (입문용)
- `sample_detail_batch.py` - 일괄 등록 예제 (PostProcessVolume, CameraComponent)
- `sample_detail_advanced.py` - 고급 기능 (검증, 상태 확인, 조건부 등록)
- `sample_detail_uniqueid.py` - **UniqueID 활용** (객체 조회, 동적 UI 제어)
- `test_detail_customization.py` - 종합 테스트 스크립트

### JSON 템플릿
- `TEMPLATE_DetailCustomization.json` - 기본 템플릿 (주석 포함)
- `SAMPLE_Advanced_UI.json` - 고급 UI 예제 (복잡한 레이아웃)

**JSON 파일 위치**: `TA/TAPython/Python/PPPreset/`

## 버전 정보

- **TAPython**: v1.2.3
- **Unreal Engine**: 5.x
- **최초 작성**: 2025년 11월 22일
- **UniqueID 가이드 추가**: 2025년 11월 23일
