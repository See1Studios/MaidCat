# MaidCat 프로젝트 지침

Use context7 for up-to-date documentation and examples.

## Dev Environment

This plugin is developed standalone but runs inside a host Unreal Engine project via symbolic link.
When debugging, testing, or executing commands, check `dev.local.json` (gitignored, project root) for the current host project context:

```json
{
  "host_project_dir": "D:\\UnrealProjects\\See1Unreal",
  "uproject_file":    "D:\\UnrealProjects\\See1Unreal\\See1Unreal.uproject",
  "engine_version":   "5.4"
}
```

- `dev.local.json` is generated automatically by `CreatePluginLink.ps1` when the symlink is created.
- If the file is missing, ask the user to run `InstallAsLink.bat` first.
- Logs are at `{host_project_dir}/Saved/Logs/`
- Unreal Python stub file: `{host_project_dir}/Intermediate/PythonStub/unreal.py`
  Always verify API against this file before writing any `unreal.*` code.

## General Principles

**Think Before Coding**: Never guess. Always verify against official API docs or the `unreal.py` stub file before writing code. For editor-only properties, check the `__doc__` strings in the stub — they do not appear in `dir()`. For large changes, ask first instead of proceeding unilaterally.

**Simplicity First**: Implement the minimum code that solves the stated problem. Do not add speculative features, unnecessary abstractions, unrequested flexibility, or excessive error handling.

**Surgical Changes**: Touch only the code necessary for the task. Do not improve adjacent code, refactor working functionality, or remove code you did not make unused yourself.

**Goal-Driven Execution**: Translate instructions into verifiable goals with clear success criteria, then execute until those criteria are met.

## Python 코드베이스 구조

Python 코드베이스의 루트는 `MaidCat/Content/Python/` 폴더입니다.

**중요**: 이 워크스페이스는 플러그인 개발 환경이며, 실제 실행 시에는 `{Project}/Plugins/MaidCat/` 경로에서 동작합니다.

### 의존성:
이 프로젝트는 **TAPython** 플러그인에 의존합니다.
- TAPython은 Python으로 네이티브 Slate UI를 만들 수 있게 해주는 언리얼 엔진 플러그인입니다
- 43+ 위젯 타입 지원, JSON 기반 UI 정의, 200+ 에디터 인터페이스 제공
- 문서: https://www.tacolor.xyz/tapython/welcome_to_tapython.html
- GitHub: https://github.com/cgerchenhp/UE_TAPython_Plugin_Release

**TAPython 추가 라이브러리** ([PythonLib API](https://www.tacolor.xyz/tapython/pythonlib_api.html)):
- TAPython은 200+ 에디터 Python 인터페이스를 제공하며, `unreal.py` 스텁 파일에 통합되어 있음
- `unreal.PythonBPLib` - 에디터 인터페이스 모음 (상호작용/뷰포트/애셋 등, 103개 함수)
- `unreal.PythonMaterialLib` - 머티리얼 편집 인터페이스 (34개 함수)
- `unreal.PythonDataTableLib` - DataTable 편집 (19개 함수)
- `unreal.PythonMeshLib` - 메시/스켈레탈메시/프로시저럴메시 (15개 함수)
- `unreal.PythonEnumLib` - 사용자 정의 Enum (12개 함수)
- `unreal.PythonStructLib` - 사용자 정의 Struct (14개 함수)
- `unreal.PythonLandscapeLib` - 랜드스케이프 머티리얼 (12개 함수)
- `unreal.PythonPhysicsAssetLib` - 피직스 애셋 (38개 함수)
- `unreal.PythonTextureLib` - Texture2D/RenderTarget2D (3개 함수)
- `unreal.PythonControlRigLib` - ControlRig 인터페이스
- `unreal.PythonLevelLib` - 레벨 에디터 인터페이스
- `unreal.PythonTestLib` - 테스팅 인터페이스

**TAPython 폴더 구조** (`{host_project_dir}/TA/TAPython/`):
- `Python/`: TAPython 설치 시 자동 생성되는 예제 코드 (읽기 전용 참고용)
  - `Example/`, `ChameleonGallery/`, `ChameleonSketch/`, `QueryTools/` 등 예제 포함
  - `QueryTools/`는 객체 상세 조회, 속성 비교, 참조/의존성 질의 예제를 제공함 (`ObjectDetailViewer.py`, `queryTools.py`)
  - 각 예제는 `.py` + `.json` 쌍으로 구성됨
  - **중요**: 이 폴더는 참고용이며, 실제 도구는 `MaidCat/Content/Python/` 에 작성
- `Lib/site-packages/`: pip로 설치된 패키지 저장 폴더
- `Config/`: TAPython 설정 파일
- `UI/`: TAPython UI 정의 파일 (JSON)

### 플러그인 진입점 (Entry Point):
- **`init_unreal.py`**: 언리얼 엔진 에디터 시작 시 자동 실행되는 초기화 스크립트
  - Python 경로 설정 (`sys.path`)
  - 기본 환경 확인 (엔진 버전, Python 버전, 플러그인 경로)
  - `startup/` 폴더의 모듈들 자동 실행
  - 핵심 초기화: `MaidCatInitializer.initialize()`
  - 의존성 설치: `MaidCatInitializer.install_dependencies()`
  - 개발환경 설정: `MaidCatInitializer.setup_dev_environment()`

### 주요 Python 모듈 구조:

- **`tool/`**: 메인 도구 모듈
  - `console_cat/`: 콘솔 관련 도구
  - `dependencies_installer/`: 의존성 설치 도구
  - `migrator.py`, `mi_migrator.py`: 마이그레이션 도구
  - `copier.py`, `replacer.py`: 복사 및 교체 도구
  - `package_manager.py`: 패키지 관리
  - `ta_python_tool.py`: TA Python 도구

- **`ue/`**: 언리얼 엔진 API 래퍼 및 유틸리티
  - `asset_*.py`: 애셋 관련 라이브러리들
  - `level_*.py`: 레벨 관련 라이브러리들
  - `mat_lib.py`, `mesh_lib.py`, `tex_lib.py`: 머티리얼, 메시, 텍스처 라이브러리
  - `bp_lib.py`: 블루프린트 라이브러리
  - `util_*.py`: 범용 유틸리티들

- **`util/`**: 범용 유틸리티 모듈
  - `editor.py`, `editor_utility_widget.py`: 에디터 유틸리티
  - `material.py`, `static_mesh.py`: 애셋별 유틸리티
  - `file.py`, `path.py`: 파일 및 경로 유틸리티
  - `render/`, `cinematic/`: 렌더링 및 시네마틱 유틸리티

- **`ui/`**: 사용자 인터페이스 모듈
  - `name_window.py`: 이름 입력 다이얼로그
  - `helper.py`: UI 헬퍼 함수들

- **기타 모듈**:
  - `startup/`: 시작 스크립트
  - `editor/`: 에디터 확장 관련 스크립트
  - `validator/`: 검증 도구
  - `chameleon/`: Chameleon 도구 관련 기능 (TAPython UI 시스템)
  - `temp/`: 임시 테스트 코드 (Git 추적 제외)

### Chameleon 데이터 API:

**Chameleon**은 TAPython의 핵심 UI 시스템으로, JSON 기반 Slate 위젯과 Python 코드 간 통신 채널입니다.

- **주요 개념**:
  - JSON 파일로 UI 정의 (Slate 위젯 43+개 지원)
  - `ChameleonData` 객체를 통한 위젯 제어
  - `aka_name`으로 위젯 식별 및 접근
  - Python 코드로 위젯 내용 동적 수정 가능

- **자주 사용하는 API**:
  - **텍스트**: `set_text()`, `get_text()`, `set_text_read_only()`
  - **이미지**: `set_image_from_path()`, `set_image_data()`, `set_image_data_from_texture2d()`
  - **가시성**: `set_visibility()`, `set_collapsed()`, `get_visibility()`
  - **리스트뷰**: `set_list_view_items()`, `get_list_view_items()`, `set_list_view_selections()`
  - **콤보박스**: `set_combo_box_items()`, `get_combo_box_selected_item()`
  - **체크박스**: `set_is_checked()`, `get_is_checked()`
  - **값**: `set_int_value()`, `get_float_value()`, `set_progress_bar_percent()`
  - **색상**: `set_color_and_opacity()`, `set_button_color_and_opacity()`
  - **동적 UI**: `set_content_from_json()`, `append_slot_from_json()`, `remove_widget_at()`
  - **윈도우 제어**: `launch_chameleon_tool()`, `request_close()`, `set_chameleon_window_size()`

- **참고 문서**: 
  - [TAPython 공식 문서](https://www.tacolor.xyz/tapython/welcome_to_tapython.html)
  - [Chameleon Data API](https://www.tacolor.xyz/pages/ChameleonDataAPI.html)
  - UI 구성 예제 우선 참고: `{host_project_dir}/TA/TAPython/Python/ChameleonGallery/` (예: `{project}TA\TAPython\Python\ChameleonGallery`)
  - 객체 introspection, 속성 비교, 참조/의존성 조회 예제 참고: `{host_project_dir}/TA/TAPython/Python/QueryTools/` (예: `{project}TA\TAPython\Python\QueryTools`)

- **Chameleon 도구 작성 위치**:
  - 실제 도구는 반드시 **`MaidCat/Content/Python/`** 아래에 작성
  - UI 예제 참고: `MaidCat/Content/Python/ui/` — `.py` + `.json` 쌍 구조 확인
  - TAPython 설치 예제(`{host_project_dir}/TA/TAPython/Python/`)는 참고용으로만 활용



### Python 코딩 가이드라인:

1. **모듈 임포트 순서**: 
   - 표준 라이브러리 → `unreal` → 로컬 모듈 순서
   
2. **언리얼 API 사용**: 
   - 코드 작성 시 원본 `unreal` 모듈 함수 직접 사용 선호
   - `ue/` 모듈의 래핑 함수들은 참고용으로만 활용 (수동 코딩 시 단축용)

3. **임시 테스트 코드**:
   - 임시 테스트/실험 코드는 반드시 `temp/` 폴더에 작성
   - `temp/` 폴더는 `.gitignore`에 포함되어 커밋되지 않음
   - 테스트 후 필요한 코드는 적절한 모듈로 이동

4. **의존성 관리**: 
   - `requirements.txt`에 정의된 패키지 사용 (`unreal-qt`)
   - 새로운 패키지 필요 시 requirements.txt 업데이트

5. **에러 처리**: 
   - `unreal.log_*` 함수들을 사용한 로깅
   - 적절한 예외 처리와 사용자 친화적 메시지

6. **타입 안전성과 API 검증**:
   - 코드 작성 전 항상 `unreal.py` 스텁 파일에서 클래스와 함수명 확인
   - Pylance를 통한 타입 체크 활용하여 API 사용법 검증
   - IntelliSense 자동완성을 통해 올바른 매개변수와 반환 타입 확인

7. **Python 실행 환경**:
   - 언리얼 엔진 Python은 일반적인 방법으로 실행 불가
   - **Unreal Engine Python 확장 필수**: 
     - 확장 ID: `nilssoderman.ue-python`
     - GitHub Copilot이 `run_vscode_command` 도구로 직접 실행 가능
   - **주요 명령어**:
     - `ue-python.execute` - Python 코드 실행 (Ctrl+Enter)
     - `ue-python.attach` - 디버거 연결
     - `ue-python.setupCodeCompletion` - 코드 자동완성 설정
     - `ue-python.openDocumentation` - API 문서 열기
     - `ue-python.reloadModules` - 모듈 리로드
   - **사용 전 필수 설정**:
     - 언리얼 엔진에서 Remote Execution 활성화 필요
     - 편집 → 프로젝트 설정 → Plugins → Python → Enable Remote Execution 체크

8. **언리얼 객체 구조**:
   - **베이스 클래스**: `unreal._ObjectBase`, `unreal.StructBase`, `unreal.EnumBase`
   - **에디터 프로퍼티**: `get_editor_property()` / `set_editor_property()` 사용
     - **중요**: `editor_property`는 `dir()`에 나타나지 않음 - 스텁 파일 참조 필수
   - **참고**: [Python API Reference](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/)

9. **Python-언리얼 타입 변환**:
   - **자동 변환**: `list`→Array, `str`→Text/Name, `dict`→Map, `tuple`→Vector
   - **주의**: Python 코드에서는 명시적 변환 권장 (`unreal.Name()`, `unreal.Vector()` 등)

10. **실행 및 디버깅**:
   - **자동 실행 및 로그 분석**:
     - Copilot이 `run_vscode_command(commandId: "ue-python.execute")` 호출하여 자동 실행
     - 실행 후 `Saved/Logs/See1Unreal.log` 파일에서 결과 자동 분석
     - PowerShell을 통해 로그 필터링 및 파싱 (Python, 에러, 경고 메시지 추출)
   - **로그 확인 방법**:
     - 프로젝트 로그: `{ProjectRoot}/Saved/Logs/See1Unreal.log`
     - Python 메시지는 `LogPython:` 태그로 필터링
     - 실행 결과는 타임스탬프와 함께 기록됨
   - **디버깅 도구**:
     - `unreal.log()` - 정보 메시지 (LogPython 카테고리)
     - `unreal.log_warning()` - 경고 메시지
     - `unreal.log_error()` - 에러 메시지
     - `unreal.log_flush()` - 로그 즉시 디스크에 기록
   - **VS Code 디버거 사용**:
     - `ue-python.attach` 명령으로 디버거 연결
     - 코드에 브레이크포인트 설정 (라인 왼쪽 클릭)
     - **중요**: Copilot은 디버거 상태를 인지할 수 없음
       - 브레이크포인트에서 멈춰있어도 로그에는 나타나지 않음
       - 디버깅 중 변수 값, 콜스택 등은 VS Code UI에서만 확인 가능
       - 사용자가 직접 F5(계속), F10(단계 넘기기), F11(한 단계씩 코드 실행) 등으로 제어
     - 디버거 컨트롤: F5(계속), F10(Step Over), F11(Step Into), Shift+F11(Step Out)
     - 변수 검사: 디버그 패널의 Variables 섹션, Watch 표현식, Debug Console 활용
   - **에러 분석**:
     - 로그에서 타입 불일치, API 사용법 오류 등 자동 파악
     - 스텁 파일(`Intermediate/PythonStub/unreal.py`)과 비교하여 정확한 API 확인
     - 복잡한 로직은 디버거로 단계별 실행하며 변수 상태 확인 권장

11. **플러그인 실행 경로**:
   - 개발 시: `d:\\GitHub\\MaidCat\\MaidCat\\Content\\Python\\`
   - 실제 실행 시: `{ProjectRoot}/Plugins/MaidCat/Content/Python/`
   - 플러그인은 상대 경로 기반으로 동작
   - 절대 경로 사용 금지, `unreal.Paths` API를 통한 경로 해석 필수
   - 주요 경로 API: `unreal.Paths.project_dir()`, `unreal.Paths.project_content_dir()` 등

12. **언리얼 엔진 주요 API**:
   
   **참고 문서**: [Unreal Python API Reference](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/)
   
   - **Core System**:
     - [`unreal.SystemLibrary`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/SystemLibrary) - 트레이싱, 오버랩, 디버그 드로잉, 타이머
     - [`unreal.GameplayStatics`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/GameplayStatics) - 게임플레이 유틸리티 (스폰, 오디오, 파티클 등)
     - [`unreal.KismetMathLibrary`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/KismetMathLibrary) - 수학 연산 (벡터, 회전, 변환 등)
     - [`unreal.KismetStringLibrary`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/KismetStringLibrary) - 문자열 처리
   
   - **Editor Asset Management**:
     - [`unreal.EditorAssetLibrary`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/EditorAssetLibrary) - 애셋 로드/저장/삭제/리네임
     - [`unreal.EditorAssetSubsystem`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/EditorAssetSubsystem) - 애셋 편집 서브시스템 (중복, 병합, 메타데이터)
     - [`unreal.AssetRegistry`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/AssetRegistry) - 애셋 레지스트리 (검색/쿼리/필터링)
     - [`unreal.AssetRegistryHelpers`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/AssetRegistryHelpers) - AssetData 유틸리티 (검증, 변환, 정렬, 태그 조회 등) 및 AssetRegistry 인스턴스 가져오기
     - [`unreal.AssetTools`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/AssetTools) - 애셋 도구 (Import/Export/생성)
     - [`unreal.AssetToolsHelpers`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/AssetToolsHelpers) - AssetTools 인스턴스 가져오기 (`get_asset_tools()`)
     - **중요**: 애셋 작업 시 [`AssetData`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/AssetData) 우선 사용 권장
       - 메모리 효율적 (실제 애셋을 로드하지 않음)
       - 주요 속성: `package_name`, `package_path`, `asset_name`, `asset_class_path`
       - 주요 메서드: `is_valid()`, `is_asset_loaded()`, `get_asset()`, `get_tag_value()`, `to_soft_object_path()`
   
   - **Editor Level & Actor**:
     - [`unreal.EditorLevelLibrary`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/EditorLevelLibrary) - 레벨/월드 관리 (액터 스폰, 선택, 삭제)
     - [`unreal.EditorActorSubsystem`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/EditorActorSubsystem) - 액터 선택/복제/삭제/정렬
     - [`unreal.EditorFilterLibrary`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/EditorFilterLibrary) - 액터 필터링 (타입, 클래스, 레이어별)
     - [`unreal.LevelEditorSubsystem`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/LevelEditorSubsystem) - 레벨 에디터 뷰포트/설정
   
   - **Editor Mesh Editing**:
     - [`unreal.EditorStaticMeshLibrary`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/EditorStaticMeshLibrary) - 스태틱 메시 편집 (LOD, UV, 콜리전)
     - [`unreal.EditorSkeletalMeshLibrary`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/EditorSkeletalMeshLibrary) - 스켈레탈 메시 편집 (본, LOD, 모프타겟)
     - [`unreal.GeometryScriptLibrary_MeshBasicEditFunctions`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/GeometryScript_MeshBasicEditFunctions) - 동적 메시 편집
   
   - **Material & Texture**:
     - [`unreal.MaterialEditingLibrary`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/MaterialEditingLibrary) - 머티리얼 노드 생성/연결/편집
     - [`unreal.MaterialLibrary`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/KismetMaterialLibrary) - 머티리얼 파라미터 설정/가져오기
     - [`unreal.EditorTextureLibrary`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/EditorTextureLibrary) - 텍스처 편집
   
   - **Rendering & Capture**:
     - [`unreal.KismetRenderingLibrary`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/KismetRenderingLibrary) - 렌더타겟, 캡처, 스크린샷
     - [`unreal.AutomationLibrary`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/AutomationLibrary) - 자동화 스크린샷/비교
   
   - **Editor UI & Utility**:
     - [`unreal.EditorUtilityLibrary`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/EditorUtilityLibrary) - 위젯 블루프린트, 선택, 다이얼로그
     - [`unreal.EditorUtilitySubsystem`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/EditorUtilitySubsystem) - 유틸리티 위젯 실행/탭 관리
     - [`unreal.EditorDialogLibrary`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/EditorDialogLibrary) - 에디터 다이얼로그 (메시지, 입력, 파일 선택)
   
   - **Editor Menu Extension** (에디터 메뉴/툴바 확장):
     - [`unreal.ToolMenus`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/ToolMenus) - 메뉴 시스템 메인 인터페이스
     - [`unreal.ToolMenu`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/ToolMenu) - 메뉴 정의
     - [`unreal.ToolMenuSection`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/ToolMenuSection) - 메뉴 섹션
     - [`unreal.ToolMenuEntry`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/ToolMenuEntry) - 메뉴 항목
     - [`unreal.ToolMenuContext`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/ToolMenuContext) - 메뉴 컨텍스트
     - [`unreal.ToolMenuEntryScriptData`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/ToolMenuEntryScriptData) - 메뉴 항목 스크립트 데이터
     - [`unreal.ToolMenuEntryScriptDataAdvanced`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/ToolMenuEntryScriptDataAdvanced) - 고급 스크립트 데이터
     - [`unreal.ToolMenuInsert`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/ToolMenuInsert) - 메뉴 삽입 위치
     - [`unreal.ToolMenuOwner`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/ToolMenuOwner) - 메뉴 소유자
     - [`unreal.ToolMenuProfile`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/ToolMenuProfile) - 메뉴 프로필
     - [`unreal.ToolMenuStringCommand`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/ToolMenuStringCommand) - 문자열 커맨드
   
   - **File & Path**:
     - [`unreal.Paths`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/Paths) - 경로 유틸리티 (프로젝트, 콘텐츠, 플러그인 경로)
     - [`unreal.BlueprintFileUtilsBPLibrary`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/BlueprintFileUtilsBPLibrary) - 파일 시스템 (읽기/쓰기/복사/삭제)
   
   - **Animation**:
     - [`unreal.AnimationLibrary`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/AnimationLibrary) - 애니메이션 시퀀스 편집
     - [`unreal.AnimationBlueprintLibrary`](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/AnimationBlueprintLibrary) - 애님 블루프린트 편집
   
   - **Subsystem Access**:
     - `unreal.get_editor_subsystem(SubsystemClass)` - 에디터 서브시스템 가져오기
     - `unreal.get_engine_subsystem(SubsystemClass)` - 엔진 서브시스템 가져오기
     - 예: `unreal.get_editor_subsystem(unreal.EditorActorSubsystem)`
   
   - **중요**: ue/ 모듈의 래핑 함수들은 참고용으로만 활용 (수동 코딩 시 단축용)
   - **중요**: 코드 작성 시 항상 공식 API 문서에서 정확한 클래스명과 메서드 확인
