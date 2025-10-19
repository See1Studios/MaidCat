# 🔧 Context API 리팩토링

`can_execute`와 `execute` 함수를 `EditorUtilityLibrary` 대신 **Context 객체**를 직접 사용하도록 개선했습니다.

## 📋 변경 사항

### Before (이전 방식) ❌

```python
@unreal.ufunction(override=True)
def can_execute(self, context):
    # Context를 무시하고 전역 함수 사용
    selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    selected_folders = unreal.EditorUtilityLibrary.get_selected_folder_paths()
    
    # 문제: Context와 무관하게 동작
    for asset in selected_assets:
        if "/Game/Python" in asset.get_path_name():
            return True
    return False
```

### After (현재 방식) ✅

```python
@unreal.ufunction(override=True)
def can_execute(self, context):
    # Context에서 직접 정보 가져오기
    asset_context = context.find_by_class(unreal.ContentBrowserAssetContextMenuContext)
    if asset_context:
        selected_assets = asset_context.selected_assets
        for asset in selected_assets:
            asset_path = str(asset.object_path)
            if "/Game/Python" in asset_path:
                return True
    return False
```

## 🎯 왜 개선되었나?

### 1. 정확성 ✅
```python
# Before: 전역 선택 상태 (다른 패널 포함)
selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()

# After: 해당 Context의 선택 상태만
asset_context = context.find_by_class(unreal.ContentBrowserAssetContextMenuContext)
selected_assets = asset_context.selected_assets
```

**차이점**: 
- 이전: "현재 에디터에서 선택된 모든 것"
- 현재: "이 메뉴를 연 컨텍스트에서 선택된 것만"

### 2. 성능 ⚡
```python
# 불필요한 전역 검색 없음
# Context가 이미 필요한 정보를 가지고 있음
```

### 3. 일관성 🎨
```python
# Context 객체의 목적에 맞게 사용
# Unreal Engine의 설계 의도를 따름
```

## 📊 적용된 클래스

### 1. PythonFolderContextMenu

**can_execute:**
```python
# 폴더 Context
menu_context = context.find_by_class(unreal.ContentBrowserDataMenuContext_FolderMenu)
if menu_context:
    selected_items = menu_context.selected_items
    for item in selected_items:
        virtual_path = item.get_virtual_path()

# 에셋 Context
asset_context = context.find_by_class(unreal.ContentBrowserAssetContextMenuContext)
if asset_context:
    selected_assets = asset_context.selected_assets
```

**execute:**
```python
# 동일한 패턴으로 실제 선택된 항목 가져오기
menu_context = context.find_by_class(...)
asset_context = context.find_by_class(...)
```

### 2. ReloadPythonModule

**can_execute & execute:**
```python
# Context에서 에셋 가져오기
asset_context = context.find_by_class(unreal.ContentBrowserAssetContextMenuContext)
if asset_context:
    selected_assets = asset_context.selected_assets
    for asset in selected_assets:
        asset_path = str(asset.object_path)  # ✨ object_path 사용
```

### 3. RunPythonFile

**can_execute & execute:**
```python
# 동일한 Context API 패턴
asset_context = context.find_by_class(unreal.ContentBrowserAssetContextMenuContext)
if not asset_context:
    return False  # execute에서는 early return
    
selected_assets = asset_context.selected_assets
```

## 🔑 주요 API 변경

### 에셋 경로 가져오기

```python
# Before
asset_path = asset.get_path_name()

# After
asset_path = str(asset.object_path)
```

**이유**: `ContentBrowserAssetContextMenuContext.selected_assets`는 `AssetData` 객체가 아니라 다른 타입이므로 `object_path` 속성 사용

### 폴더 경로 가져오기

```python
# Before
selected_folders = unreal.EditorUtilityLibrary.get_selected_folder_paths()

# After
menu_context = context.find_by_class(unreal.ContentBrowserDataMenuContext_FolderMenu)
selected_items = menu_context.selected_items
virtual_path = item.get_virtual_path()
```

## 💡 사용 패턴

### Pattern 1: 폴더 + 에셋 모두 지원

```python
@unreal.ufunction(override=True)
def can_execute(self, context):
    # 폴더 체크
    menu_context = context.find_by_class(unreal.ContentBrowserDataMenuContext_FolderMenu)
    if menu_context:
        for item in menu_context.selected_items:
            if "/Game/Python" in item.get_virtual_path():
                return True
    
    # 에셋 체크
    asset_context = context.find_by_class(unreal.ContentBrowserAssetContextMenuContext)
    if asset_context:
        for asset in asset_context.selected_assets:
            if "/Game/Python" in str(asset.object_path):
                return True
    
    return False
```

### Pattern 2: 에셋만 지원 (Python 파일)

```python
@unreal.ufunction(override=True)
def can_execute(self, context):
    asset_context = context.find_by_class(unreal.ContentBrowserAssetContextMenuContext)
    if asset_context:
        for asset in asset_context.selected_assets:
            asset_path = str(asset.object_path)
            if "/Game/Python" in asset_path and asset_path.endswith(".py"):
                return True
    return False
```

### Pattern 3: Execute에서 None 체크

```python
@unreal.ufunction(override=True)
def execute(self, context):
    asset_context = context.find_by_class(unreal.ContentBrowserAssetContextMenuContext)
    if not asset_context:
        return  # Early return
    
    # 안전하게 진행
    selected_assets = asset_context.selected_assets
    for asset in selected_assets:
        # 처리...
```

## 🐛 디버깅 팁

### Context 정보 확인

```python
@unreal.ufunction(override=True)
def can_execute(self, context):
    try:
        # Context 타입 확인
        unreal.log(f"Context type: {type(context)}")
        
        # 사용 가능한 Context 목록
        asset_ctx = context.find_by_class(unreal.ContentBrowserAssetContextMenuContext)
        folder_ctx = context.find_by_class(unreal.ContentBrowserDataMenuContext_FolderMenu)
        
        unreal.log(f"Asset context: {asset_ctx is not None}")
        unreal.log(f"Folder context: {folder_ctx is not None}")
        
        return True
    except Exception as e:
        unreal.log_warning(f"Debug error: {e}")
        return False
```

### 주석 처리된 디버깅 코드

```python
# 디버깅용 (필요시 주석 해제)
# unreal.log_warning(f"can_execute error: {e}")
```

## ✅ 장점 요약

| 항목 | Before | After |
|------|--------|-------|
| **정확성** | 전역 선택 | Context 선택 |
| **성능** | 불필요한 검색 | 필요한 정보만 |
| **타입 안전성** | 약함 | 강함 |
| **의도 명확성** | 불명확 | 명확 |
| **유지보수성** | 낮음 | 높음 |

## 🎊 결론

**Context API를 제대로 사용하면:**

✅ 더 정확한 메뉴 활성화 판단  
✅ 불필요한 전역 상태 조회 제거  
✅ Unreal Engine의 설계 의도에 부합  
✅ 코드의 의도가 더 명확해짐  

**Pylance 경고는 무시해도 됨** - Unreal API 타입 힌트의 한계일 뿐 런타임에서는 정상 작동합니다!

---

**업데이트일**: 2025-10-18  
**파일**: `init_context.py`  
**변경된 클래스**: `PythonFolderContextMenu`, `ReloadPythonModule`, `RunPythonFile`  
**주요 API**: `context.find_by_class()`, `asset.object_path`, `item.get_virtual_path()`
