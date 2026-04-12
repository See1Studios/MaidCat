"""
Unreal Engine BlueprintFileUtilsBPLibrary Python Wrapper

이 모듈은 Unreal Engine의 BlueprintFileUtilsBPLibrary 함수들에 대한 
Python wrapper를 제공합니다. 파일 시스템 작업을 더 쉽고 안전하게 
수행할 수 있도록 도와줍니다.

주요 기능:
- 파일/디렉토리 생성, 삭제, 복사, 이동
- 파일 존재 여부 확인
- 파일 내용 읽기/쓰기
- 파일/디렉토리 검색
- 파일 크기 확인

사용 예제:
    import util.file as file_utils
    
    # 파일 작업
    file_utils.copy_file("C:/source.txt", "C:/dest.txt")
    file_utils.write_string_to_file("C:/test.txt", "Hello World!")
    content = file_utils.read_file_to_string("C:/test.txt")
    
    # 디렉토리 작업
    file_utils.create_directory("C:/MyProject/Data")
    files = file_utils.find_files("C:/MyProject", ".txt", recursive=True)
    
    # 클래스 사용
    utils = file_utils.FileUtils()
    if utils.file_exists("C:/important.dat"):
        size = utils.get_file_size("C:/important.dat")
        print(f"파일 크기: {size} bytes")

Author: MaidCat Team
Version: 1.0.0
"""

import unreal
import os
from typing import List, Optional


class FileUtils:
    """
    Unreal BlueprintFileUtilsBPLibrary의 Python wrapper 클래스
    파일 시스템 작업을 위한 편리한 인터페이스 제공
    """
    
    @staticmethod
    def copy_file(source_path: str, destination_path: str, overwrite: bool = True) -> bool:
        """
        파일을 복사합니다.
        
        Args:
            source_path (str): 원본 파일 경로
            destination_path (str): 대상 파일 경로
            overwrite (bool): 덮어쓰기 허용 여부
            
        Returns:
            bool: 성공 여부
        """
        try:
            return unreal.BlueprintFileUtilsBPLibrary.copy_file(source_path, destination_path, overwrite)
        except Exception as e:
            print(f"❌ 파일 복사 실패: {e}")
            return False
    
    @staticmethod
    def move_file(source_path: str, destination_path: str, overwrite: bool = True) -> bool:
        """
        파일을 이동합니다.
        
        Args:
            source_path (str): 원본 파일 경로
            destination_path (str): 대상 파일 경로
            overwrite (bool): 덮어쓰기 허용 여부
            
        Returns:
            bool: 성공 여부
        """
        try:
            return unreal.BlueprintFileUtilsBPLibrary.move_file(source_path, destination_path, overwrite)
        except Exception as e:
            print(f"❌ 파일 이동 실패: {e}")
            return False
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """
        파일을 삭제합니다.
        
        Args:
            file_path (str): 삭제할 파일 경로
            
        Returns:
            bool: 성공 여부
        """
        try:
            return unreal.BlueprintFileUtilsBPLibrary.delete_file(file_path)
        except Exception as e:
            print(f"❌ 파일 삭제 실패: {e}")
            return False
    
    @staticmethod
    def file_exists(file_path: str) -> bool:
        """
        파일이 존재하는지 확인합니다.
        
        Args:
            file_path (str): 확인할 파일 경로
            
        Returns:
            bool: 파일 존재 여부
        """
        try:
            return unreal.BlueprintFileUtilsBPLibrary.file_exists(file_path)
        except Exception as e:
            print(f"❌ 파일 존재 확인 실패: {e}")
            return False
    
    @staticmethod
    def directory_exists(directory_path: str) -> bool:
        """
        디렉토리가 존재하는지 확인합니다.
        
        Args:
            directory_path (str): 확인할 디렉토리 경로
            
        Returns:
            bool: 디렉토리 존재 여부
        """
        try:
            return unreal.BlueprintFileUtilsBPLibrary.directory_exists(directory_path)
        except Exception as e:
            print(f"❌ 디렉토리 존재 확인 실패: {e}")
            return False
    
    @staticmethod
    def create_directory(directory_path: str, create_tree: bool = True) -> bool:
        """
        디렉토리를 생성합니다.
        
        Args:
            directory_path (str): 생성할 디렉토리 경로
            create_tree (bool): 상위 디렉토리도 함께 생성할지 여부
            
        Returns:
            bool: 성공 여부
        """
        try:
            return unreal.BlueprintFileUtilsBPLibrary.create_directory(directory_path, create_tree)
        except Exception as e:
            print(f"❌ 디렉토리 생성 실패: {e}")
            return False
    
    @staticmethod
    def delete_directory(directory_path: str, must_exist: bool = False) -> bool:
        """
        디렉토리를 삭제합니다.
        
        Args:
            directory_path (str): 삭제할 디렉토리 경로
            must_exist (bool): 디렉토리가 반드시 존재해야 하는지 여부
            
        Returns:
            bool: 성공 여부
        """
        try:
            return unreal.BlueprintFileUtilsBPLibrary.delete_directory(directory_path, must_exist)
        except Exception as e:
            print(f"❌ 디렉토리 삭제 실패: {e}")
            return False
    
    @staticmethod
    def find_files(directory: str, file_extension: str = "", recursive: bool = True) -> List[str]:
        """
        디렉토리에서 파일들을 찾습니다.
        
        Args:
            directory (str): 검색할 디렉토리 경로
            file_extension (str): 찾을 파일 확장자 (예: ".txt", ".py")
            recursive (bool): 하위 디렉토리도 검색할지 여부
            
        Returns:
            List[str]: 찾은 파일들의 경로 리스트
        """
        try:
            # Unreal API 시그니처에 따라 조정 필요
            return unreal.BlueprintFileUtilsBPLibrary.find_files_in_directory(directory, file_extension, recursive)
        except AttributeError:
            # 대안 방법 또는 Python 기본 라이브러리 사용
            print(f"⚠️ find_files_in_directory 함수를 찾을 수 없습니다. Python os.walk 사용")
            return FileUtils._find_files_fallback(directory, file_extension, recursive)
        except Exception as e:
            print(f"❌ 파일 찾기 실패: {e}")
            return []
    
    @staticmethod
    def find_directories(directory: str, recursive: bool = True) -> List[str]:
        """
        디렉토리에서 하위 디렉토리들을 찾습니다.
        
        Args:
            directory (str): 검색할 디렉토리 경로
            recursive (bool): 하위 디렉토리도 검색할지 여부
            
        Returns:
            List[str]: 찾은 디렉토리들의 경로 리스트
        """
        try:
            # Unreal API 시그니처에 따라 조정 필요
            return unreal.BlueprintFileUtilsBPLibrary.find_directories_in_directory(directory, recursive)
        except AttributeError:
            # 대안 방법 또는 Python 기본 라이브러리 사용
            print(f"⚠️ find_directories_in_directory 함수를 찾을 수 없습니다. Python os.walk 사용")
            return FileUtils._find_directories_fallback(directory, recursive)
        except Exception as e:
            print(f"❌ 디렉토리 찾기 실패: {e}")
            return []
    
    @staticmethod
    def _find_files_fallback(directory: str, file_extension: str = "", recursive: bool = True) -> List[str]:
        """Python 기본 라이브러리를 사용한 파일 찾기 대안"""
        found_files = []
        if not os.path.exists(directory):
            return found_files
            
        if recursive:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if not file_extension or file.endswith(file_extension):
                        found_files.append(os.path.join(root, file))
        else:
            try:
                for item in os.listdir(directory):
                    item_path = os.path.join(directory, item)
                    if os.path.isfile(item_path):
                        if not file_extension or item.endswith(file_extension):
                            found_files.append(item_path)
            except OSError:
                pass
                
        return found_files
    
    @staticmethod
    def _find_directories_fallback(directory: str, recursive: bool = True) -> List[str]:
        """Python 기본 라이브러리를 사용한 디렉토리 찾기 대안"""
        found_dirs = []
        if not os.path.exists(directory):
            return found_dirs
            
        if recursive:
            for root, dirs, files in os.walk(directory):
                for dir_name in dirs:
                    found_dirs.append(os.path.join(root, dir_name))
        else:
            try:
                for item in os.listdir(directory):
                    item_path = os.path.join(directory, item)
                    if os.path.isdir(item_path):
                        found_dirs.append(item_path)
            except OSError:
                pass
                
        return found_dirs
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """
        파일 크기를 가져옵니다.
        
        Args:
            file_path (str): 파일 경로
            
        Returns:
            int: 파일 크기 (바이트)
        """
        try:
            return unreal.BlueprintFileUtilsBPLibrary.get_file_size(file_path)
        except Exception as e:
            print(f"❌ 파일 크기 확인 실패: {e}")
            return -1
    
    @staticmethod
    def read_file_to_string(file_path: str) -> Optional[str]:
        """
        파일을 읽어서 문자열로 반환합니다.
        
        Args:
            file_path (str): 읽을 파일 경로
            
        Returns:
            Optional[str]: 파일 내용 (실패시 None)
        """
        try:
            return unreal.BlueprintFileUtilsBPLibrary.read_file_to_string(file_path)
        except Exception as e:
            print(f"❌ 파일 읽기 실패: {e}")
            return None
    
    @staticmethod
    def write_string_to_file(file_path: str, content: str, append: bool = False) -> bool:
        """
        문자열을 파일에 씁니다.
        
        Args:
            file_path (str): 쓸 파일 경로
            content (str): 쓸 내용
            append (bool): 추가 모드 여부 (False면 덮어쓰기)
            
        Returns:
            bool: 성공 여부
        """
        try:
            return unreal.BlueprintFileUtilsBPLibrary.write_string_to_file(file_path, content, append)
        except Exception as e:
            print(f"❌ 파일 쓰기 실패: {e}")
            return False


# 편의 함수들 (모듈 레벨)
def copy_file(source: str, destination: str, overwrite: bool = True) -> bool:
    """파일 복사 편의 함수"""
    return FileUtils.copy_file(source, destination, overwrite)

def move_file(source: str, destination: str, overwrite: bool = True) -> bool:
    """파일 이동 편의 함수"""
    return FileUtils.move_file(source, destination, overwrite)

def delete_file(file_path: str) -> bool:
    """파일 삭제 편의 함수"""
    return FileUtils.delete_file(file_path)

def file_exists(file_path: str) -> bool:
    """파일 존재 확인 편의 함수"""
    return FileUtils.file_exists(file_path)

def directory_exists(directory_path: str) -> bool:
    """디렉토리 존재 확인 편의 함수"""
    return FileUtils.directory_exists(directory_path)

def create_directory(directory_path: str, create_tree: bool = True) -> bool:
    """디렉토리 생성 편의 함수"""
    return FileUtils.create_directory(directory_path, create_tree)

def delete_directory(directory_path: str, must_exist: bool = False) -> bool:
    """디렉토리 삭제 편의 함수"""
    return FileUtils.delete_directory(directory_path, must_exist)

def find_files(directory: str, file_extension: str = "", recursive: bool = True) -> List[str]:
    """파일 찾기 편의 함수"""
    return FileUtils.find_files(directory, file_extension, recursive)

def find_directories(directory: str, recursive: bool = True) -> List[str]:
    """디렉토리 찾기 편의 함수"""
    return FileUtils.find_directories(directory, recursive)

def get_file_size(file_path: str) -> int:
    """파일 크기 확인 편의 함수"""
    return FileUtils.get_file_size(file_path)

def read_file_to_string(file_path: str) -> Optional[str]:
    """파일 읽기 편의 함수"""
    return FileUtils.read_file_to_string(file_path)

def write_string_to_file(file_path: str, content: str, append: bool = False) -> bool:
    """파일 쓰기 편의 함수"""
    return FileUtils.write_string_to_file(file_path, content, append)


# 추가 유틸리티 함수들
def get_file_extension(file_path: str) -> str:
    """파일 확장자 추출"""
    return os.path.splitext(file_path)[1]

def get_filename_without_extension(file_path: str) -> str:
    """확장자 없는 파일명 추출"""
    return os.path.splitext(os.path.basename(file_path))[0]

def get_filename_with_extension(file_path: str) -> str:
    """확장자 포함 파일명 추출"""
    return os.path.basename(file_path)

def get_directory_path(file_path: str) -> str:
    """파일의 디렉토리 경로 추출"""
    return os.path.dirname(file_path)

def normalize_path(path: str) -> str:
    """경로 정규화"""
    return os.path.normpath(path).replace('\\', '/')

def combine_paths(*paths) -> str:
    """경로들을 안전하게 결합"""
    return normalize_path(os.path.join(*paths))


if __name__ == "__main__":
    # 사용 예제
    print("=== File Utils 사용 예제 ===")
    
    # 테스트 디렉토리 경로
    test_dir = "C:/Temp/TestFiles"
    test_file = combine_paths(test_dir, "test.txt")
    
    # 디렉토리 생성
    if create_directory(test_dir):
        print(f"✅ 디렉토리 생성 성공: {test_dir}")
    
    # 파일 생성
    if write_string_to_file(test_file, "Hello, Unreal File Utils!"):
        print(f"✅ 파일 생성 성공: {test_file}")
    
    # 파일 존재 확인
    if file_exists(test_file):
        print(f"✅ 파일 존재 확인: {test_file}")
    
    # 파일 읽기
    content = read_file_to_string(test_file)
    if content:
        print(f"✅ 파일 내용: {content}")
    
    # 파일 크기 확인
    size = get_file_size(test_file)
    print(f"📏 파일 크기: {size} bytes")
    
    # 파일 목록
    files = find_files(test_dir, ".txt")
    print(f"📁 텍스트 파일들: {files}")