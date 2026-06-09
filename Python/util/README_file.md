# 📁 File Utils - Unreal Engine File System Wrapper

`util/file.py`는 Unreal Engine의 `BlueprintFileUtilsBPLibrary`에 대한 Python wrapper입니다.

## 🚀 주요 기능

### 파일 작업
- ✅ 파일 복사/이동/삭제
- ✅ 파일 존재 확인
- ✅ 파일 크기 확인
- ✅ 텍스트 파일 읽기/쓰기

### 디렉토리 작업
- ✅ 디렉토리 생성/삭제
- ✅ 디렉토리 존재 확인
- ✅ 파일/디렉토리 검색

### 경로 유틸리티
- ✅ 경로 정규화
- ✅ 파일명/확장자 추출
- ✅ 경로 결합

## 📖 사용법

### 기본 사용법 (함수형)

```python
import util.file as file_utils

# 파일 작업
file_utils.copy_file("C:/source.txt", "C:/destination.txt")
file_utils.move_file("C:/old_location.txt", "C:/new_location.txt")
file_utils.delete_file("C:/unwanted.txt")

# 파일 내용 작업
file_utils.write_string_to_file("C:/log.txt", "Hello World!", append=True)
content = file_utils.read_file_to_string("C:/log.txt")
print(content)

# 디렉토리 작업
file_utils.create_directory("C:/MyProject/Data", create_tree=True)
file_utils.delete_directory("C:/TempFolder")

# 파일 검색
txt_files = file_utils.find_files("C:/MyProject", ".txt", recursive=True)
subdirs = file_utils.find_directories("C:/MyProject", recursive=False)
```

### 클래스 사용법

```python
from util.file import FileUtils

utils = FileUtils()

# 파일 존재 확인 후 작업
if utils.file_exists("C:/important.dat"):
    size = utils.get_file_size("C:/important.dat")
    print(f"파일 크기: {size:,} bytes")
    
    # 백업 생성
    backup_path = "C:/important_backup.dat"
    if utils.copy_file("C:/important.dat", backup_path):
        print("✅ 백업 생성 완료")
```

### 경로 유틸리티

```python
import util.file as file_utils

file_path = "C:/Projects/MyGame/Assets/Textures/player.png"

# 경로 분석
filename = file_utils.get_filename_with_extension(file_path)  # "player.png"
name_only = file_utils.get_filename_without_extension(file_path)  # "player"
extension = file_utils.get_file_extension(file_path)  # ".png"
directory = file_utils.get_directory_path(file_path)  # "C:/Projects/MyGame/Assets/Textures"

# 경로 결합
new_path = file_utils.combine_paths("C:/Projects", "MyGame", "NewAssets", "player2.png")
normalized = file_utils.normalize_path(new_path)  # 슬래시 정규화
```

## 🔧 고급 사용 예제

### 1. 프로젝트 파일 정리

```python
import util.file as file_utils

def cleanup_project_files(project_dir):
    """프로젝트 디렉토리에서 임시 파일들을 정리"""
    
    # 임시 파일 확장자들
    temp_extensions = [".tmp", ".log", ".cache", ".bak"]
    
    for ext in temp_extensions:
        temp_files = file_utils.find_files(project_dir, ext, recursive=True)
        for temp_file in temp_files:
            if file_utils.delete_file(temp_file):
                print(f"🗑️ 삭제됨: {temp_file}")
    
    print("✅ 프로젝트 정리 완료")

# 사용
cleanup_project_files("C:/MyUnrealProject")
```

### 2. 파일 배치 처리

```python
import util.file as file_utils

def batch_rename_files(directory, old_prefix, new_prefix):
    """특정 접두사를 가진 파일들을 일괄 이름 변경"""
    
    all_files = file_utils.find_files(directory, recursive=False)
    
    for file_path in all_files:
        filename = file_utils.get_filename_with_extension(file_path)
        
        if filename.startswith(old_prefix):
            new_filename = filename.replace(old_prefix, new_prefix, 1)
            new_path = file_utils.combine_paths(directory, new_filename)
            
            if file_utils.move_file(file_path, new_path):
                print(f"📝 이름 변경: {filename} → {new_filename}")

# 사용
batch_rename_files("C:/Assets/Textures", "old_", "new_")
```

### 3. 백업 시스템

```python
import util.file as file_utils
from datetime import datetime

def create_backup(source_dir, backup_root):
    """디렉토리 백업 생성"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = file_utils.combine_paths(backup_root, f"backup_{timestamp}")
    
    if file_utils.create_directory(backup_dir):
        print(f"📦 백업 디렉토리 생성: {backup_dir}")
        
        # 모든 파일 복사
        all_files = file_utils.find_files(source_dir, recursive=True)
        
        for file_path in all_files:
            # 상대 경로 계산
            rel_path = os.path.relpath(file_path, source_dir)
            dest_path = file_utils.combine_paths(backup_dir, rel_path)
            
            # 대상 디렉토리 생성
            dest_dir = file_utils.get_directory_path(dest_path)
            file_utils.create_directory(dest_dir)
            
            # 파일 복사
            if file_utils.copy_file(file_path, dest_path):
                print(f"📋 복사됨: {rel_path}")
        
        print("✅ 백업 완료")
        return backup_dir
    
    return None

# 사용
backup_path = create_backup("C:/MyProject/ImportantData", "C:/Backups")
```

## ⚠️ 주의사항

1. **경로 구분자**: 항상 `/`를 사용하거나 `normalize_path()` 함수를 사용하세요.
2. **권한**: 파일 작업시 적절한 읽기/쓰기 권한이 있는지 확인하세요.
3. **대용량 파일**: 매우 큰 파일의 경우 메모리 사용량을 고려하세요.
4. **에러 처리**: 모든 함수는 예외를 잡아서 False/None을 반환하므로 반환값을 확인하세요.

## 🔄 함수 대체

Unreal API가 없거나 다를 경우, 일부 함수는 Python 표준 라이브러리로 대체됩니다:

- `find_files()` → `os.walk()` 사용
- `find_directories()` → `os.walk()` 사용
- 기타 파일 작업들도 필요시 `os`, `shutil` 모듈로 대체 가능

## 📚 관련 문서

- [Unreal Engine Python API](https://docs.unrealengine.com/5.3/en-US/python-api-reference/)
- [BlueprintFileUtilsBPLibrary](https://docs.unrealengine.com/5.3/en-US/python-api-reference/class/BlueprintFileUtilsBPLibrary/)