# -*- coding: utf-8 -*-
"""
BlueprintFileUtilsBPLibrary 래퍼 모듈

이 모듈은 언리얼 엔진의 BlueprintFileUtilsBPLibrary에 대한 Python 래퍼를 제공합니다.
파일 및 디렉토리 작업을 위한 편리한 함수들을 포함합니다.

사용법:
    from ue.file_util import copy_file, delete_file, make_directory
    
    # 파일 복사
    success = copy_file("C:/dest/file.txt", "C:/src/file.txt")
    
    # 파일 존재 확인
    if file_exists("C:/my/file.txt"):
        print("파일이 존재합니다")
    
    # 디렉토리에서 모든 PNG 파일 찾기
    png_files = find_files("C:/textures", ".png")
    
    # 재귀적으로 모든 파일 찾기
    all_files = find_recursive("C:/project", "*.*", find_files=True)

작성자: MaidCat
"""

from typing import List, Optional
import unreal


def copy_file(dest_filename: str, src_filename: str, replace: bool = True, 
              even_if_read_only: bool = False) -> bool:
    """
    파일을 소스에서 목적지로 복사합니다.
    
    Args:
        dest_filename: 목적지 파일 경로
        src_filename: 소스 파일 경로
        replace: 기존 파일을 교체할지 여부
        even_if_read_only: 읽기 전용 파일도 복사할지 여부
        
    Returns:
        복사가 성공하면 True, 실패하면 False
    """
    return unreal.BlueprintFileUtilsBPLibrary.copy_file(
        dest_filename, src_filename, replace, even_if_read_only
    )


def move_file(dest_filename: str, src_filename: str, replace: bool = True,
              even_if_read_only: bool = False) -> bool:
    """
    파일을 소스에서 목적지로 이동합니다.
    
    Args:
        dest_filename: 목적지 파일 경로
        src_filename: 소스 파일 경로  
        replace: 기존 파일을 교체할지 여부
        even_if_read_only: 읽기 전용 파일도 이동할지 여부
        
    Returns:
        이동이 성공하면 True, 실패하면 False
    """
    return unreal.BlueprintFileUtilsBPLibrary.move_file(
        dest_filename, src_filename, replace, even_if_read_only
    )


def delete_file(filename: str, must_exist: bool = False,
                even_if_read_only: bool = False) -> bool:
    """
    파일을 삭제합니다.
    
    Args:
        filename: 삭제할 파일 경로
        must_exist: True이면 파일이 존재해야 하며, 없으면 작업 실패
        even_if_read_only: 읽기 전용 파일도 삭제할지 여부
        
    Returns:
        삭제가 성공하면 True, 실패하면 False
    """
    return unreal.BlueprintFileUtilsBPLibrary.delete_file(
        filename, must_exist, even_if_read_only
    )


def file_exists(filename: str) -> bool:
    """
    파일이 존재하는지 확인합니다.
    
    Args:
        filename: 확인할 파일 경로
        
    Returns:
        파일이 존재하면 True, 없으면 False
    """
    return unreal.BlueprintFileUtilsBPLibrary.file_exists(filename)


def directory_exists(directory: str) -> bool:
    """
    디렉토리가 존재하는지 확인합니다.
    
    Args:
        directory: 확인할 디렉토리 경로
        
    Returns:
        디렉토리가 존재하면 True, 없으면 False
    """
    return unreal.BlueprintFileUtilsBPLibrary.directory_exists(directory)


def make_directory(path: str, create_tree: bool = False) -> bool:
    """
    디렉토리를 생성합니다.
    
    Args:
        path: 생성할 디렉토리 경로
        create_tree: True이면 필요시 전체 디렉토리 트리를 생성
        
    Returns:
        디렉토리가 생성되면 True, 실패하면 False
    """
    return unreal.BlueprintFileUtilsBPLibrary.make_directory(path, create_tree)


def delete_directory(directory: str, must_exist: bool = False,
                    delete_recursively: bool = False) -> bool:
    """
    디렉토리와 선택적으로 그 내용을 삭제합니다.
    
    Args:
        directory: 삭제할 디렉토리 경로
        must_exist: True이면 디렉토리가 존재해야 하며, 없으면 작업 실패
        delete_recursively: True이면 하위 디렉토리도 함께 삭제
        
    Returns:
        삭제가 성공하면 True, 실패하면 False
    """
    return unreal.BlueprintFileUtilsBPLibrary.delete_directory(
        directory, must_exist, delete_recursively
    )


def find_files(directory: str, file_extension: str = "") -> Optional[List[str]]:
    """
    선택적 확장자 필터로 디렉토리 내 모든 파일을 찾습니다.
    
    Args:
        directory: 검색할 디렉토리의 절대 경로
        file_extension: 확장자 필터 (예: ".txt" 또는 "txt"). 
                       빈 문자열이면 모든 파일을 찾습니다.
                       
    Returns:
        찾은 파일 경로 목록, 없으면 None
    """
    result = unreal.BlueprintFileUtilsBPLibrary.find_files(directory, file_extension)
    return list(result) if result else None


def find_recursive(start_directory: str, wildcard: str = "",
                  find_files: bool = True, find_directories: bool = False) -> Optional[List[str]]:
    """
    선택적 와일드카드 필터로 파일 및/또는 디렉토리를 재귀적으로 찾습니다.
    
    Args:
        start_directory: 검색을 시작할 절대 경로
        wildcard: 와일드카드 패턴 (예: "*.png", "*images*")
        find_files: 결과에 파일을 포함할지 여부
        find_directories: 결과에 디렉토리를 포함할지 여부
        
    Returns:
        찾은 경로 목록, 없으면 None
    """
    result = unreal.BlueprintFileUtilsBPLibrary.find_recursive(
        start_directory, wildcard, find_files, find_directories
    )
    return list(result) if result else None


def get_user_directory() -> str:
    """
    사용자 디렉토리를 가져옵니다 (플랫폼별).
    
    Returns:
        사용자 디렉토리 경로 (예: Documents 폴더 또는 홈 디렉토리)
    """
    return unreal.BlueprintFileUtilsBPLibrary.get_user_directory()


# 일반적인 작업을 위한 편의 함수들
def ensure_directory(path: str) -> bool:
    """
    디렉토리가 존재하는지 확인하고, 필요시 생성합니다.
    
    Args:
        path: 존재를 확인할 디렉토리 경로
        
    Returns:
        디렉토리가 존재하거나 생성되면 True, 실패하면 False
    """
    if directory_exists(path):
        return True
    return make_directory(path, create_tree=True)


def safe_delete_file(filename: str) -> bool:
    """
    파일을 안전하게 삭제합니다 (존재할 때만).
    
    Args:
        filename: 삭제할 파일 경로
        
    Returns:
        파일이 삭제되었거나 존재하지 않으면 True, 삭제 실패하면 False
    """
    if not file_exists(filename):
        return True
    return delete_file(filename, must_exist=False, even_if_read_only=True)


def backup_file(filename: str, backup_suffix: str = ".bak") -> bool:
    """
    파일의 백업 복사본을 생성합니다.
    
    Args:
        filename: 백업할 파일 경로
        backup_suffix: 백업 파일명에 추가할 접미사
        
    Returns:
        백업이 생성되면 True, 실패하면 False
    """
    if not file_exists(filename):
        return False
    
    backup_filename = filename + backup_suffix
    return copy_file(backup_filename, filename, replace=True)


def find_files_by_extension(directory: str, extensions: List[str]) -> List[str]:
    """
    여러 확장자로 파일을 찾습니다.
    
    Args:
        directory: 검색할 디렉토리
        extensions: 찾을 확장자 목록 (예: [".txt", ".log"])
        
    Returns:
        지정된 확장자 중 하나를 가진 모든 파일 목록
    """
    all_files = []
    for ext in extensions:
        files = find_files(directory, ext)
        if files:
            all_files.extend(files)
    return all_files


def get_directory_size(directory: str) -> int:
    """
    디렉토리 내 총 파일 개수를 가져옵니다 (재귀적).
    
    Args:
        directory: 파일을 세어볼 디렉토리
        
    Returns:
        재귀적으로 찾은 파일 개수
    """
    files = find_recursive(directory, "", find_files=True, find_directories=False)
    return len(files) if files else 0


def get_file_count_recursive(directory: str) -> int:
    """
    디렉토리 내 파일 개수를 재귀적으로 세어줍니다.
    
    Args:
        directory: 세어볼 디렉토리 경로
        
    Returns:
        찾은 파일의 총 개수
    """
    return get_directory_size(directory)


def clean_empty_directories(root_directory: str) -> int:
    """
    빈 디렉토리들을 정리합니다 (재귀적).
    
    Args:
        root_directory: 정리를 시작할 루트 디렉토리
        
    Returns:
        삭제된 디렉토리 개수
    """
    if not directory_exists(root_directory):
        return 0
    
    # 모든 디렉토리를 찾음
    directories = find_recursive(root_directory, "", find_files=False, find_directories=True)
    if not directories:
        return 0
    
    deleted_count = 0
    # 깊은 디렉토리부터 삭제 (역순으로 정렬)
    directories.sort(reverse=True)
    
    for directory in directories:
        # 디렉토리가 비어있는지 확인 (파일과 하위 디렉토리 모두 확인)
        files = find_files(directory)
        subdirs = find_recursive(directory, "", find_files=False, find_directories=True)
        
        # 현재 디렉토리 자체는 제외하고 하위 디렉토리만 확인
        subdirs = [d for d in subdirs if d != directory] if subdirs else []
        
        if not files and not subdirs:
            if delete_directory(directory, must_exist=False, delete_recursively=False):
                deleted_count += 1
    
    return deleted_count


def get_file_size_mb(directory: str) -> float:
    """
    디렉토리 내 모든 파일의 대략적인 크기를 MB 단위로 추정합니다.
    (실제 파일 크기가 아닌 파일 개수 기반 추정치)
    
    Args:
        directory: 크기를 계산할 디렉토리
        
    Returns:
        추정된 크기 (MB 단위). 파일당 평균 1MB로 가정
    """
    file_count = get_file_count_recursive(directory)
    # 파일당 평균 1MB로 추정 (실제 파일 크기 API가 없으므로)
    return float(file_count)


def copy_directory_contents(source_dir: str, dest_dir: str, 
                           file_extension: str = "") -> int:
    """
    디렉토리의 모든 파일을 다른 디렉토리로 복사합니다.
    
    Args:
        source_dir: 소스 디렉토리
        dest_dir: 목적지 디렉토리
        file_extension: 특정 확장자 파일만 복사 (빈 문자열이면 모든 파일)
        
    Returns:
        복사된 파일 개수
    """
    if not directory_exists(source_dir):
        return 0
    
    # 목적지 디렉토리 생성
    ensure_directory(dest_dir)
    
    # 파일 목록 가져오기
    files = find_files(source_dir, file_extension)
    if not files:
        return 0
    
    copied_count = 0
    for file_path in files:
        # 파일명만 추출
        file_name = file_path.split("/")[-1] if "/" in file_path else file_path.split("\\")[-1]
        dest_file = dest_dir + "/" + file_name
        
        if copy_file(dest_file, file_path, replace=True):
            copied_count += 1
    
    return copied_count


def get_file_extension(filename: str) -> str:
    """
    파일명에서 확장자를 추출합니다.
    
    Args:
        filename: 파일명 또는 경로
        
    Returns:
        확장자 (점 포함, 예: ".txt"). 확장자가 없으면 빈 문자열
    """
    if "." not in filename:
        return ""
    
    # 경로에서 파일명만 추출
    file_name = filename.split("/")[-1] if "/" in filename else filename.split("\\")[-1]
    
    # 마지막 점 이후의 부분이 확장자
    parts = file_name.split(".")
    if len(parts) < 2:
        return ""
    
    return "." + parts[-1]


def change_file_extension(filename: str, new_extension: str) -> str:
    """
    파일명의 확장자를 변경합니다.
    
    Args:
        filename: 원본 파일명 또는 경로
        new_extension: 새로운 확장자 (점 포함 또는 미포함 모두 가능)
        
    Returns:
        새로운 확장자를 가진 파일명
    """
    # 새 확장자가 점으로 시작하지 않으면 추가
    if new_extension and not new_extension.startswith("."):
        new_extension = "." + new_extension
    
    # 기존 확장자 제거
    if "." in filename:
        # 경로와 파일명 분리
        if "/" in filename:
            path_parts = filename.rsplit("/", 1)
            path = path_parts[0] + "/"
            file_name = path_parts[1]
        elif "\\" in filename:
            path_parts = filename.rsplit("\\", 1)
            path = path_parts[0] + "\\"
            file_name = path_parts[1]
        else:
            path = ""
            file_name = filename
        
        # 파일명에서 확장자 제거
        name_parts = file_name.split(".")
        if len(name_parts) > 1:
            base_name = ".".join(name_parts[:-1])
        else:
            base_name = file_name
        
        return path + base_name + new_extension
    else:
        return filename + new_extension