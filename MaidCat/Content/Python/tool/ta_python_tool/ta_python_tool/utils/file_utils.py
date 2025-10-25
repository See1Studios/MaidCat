#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Utilities
파일 관련 유틸리티 함수들
"""

import os
import stat
from typing import Tuple


def is_file_writable(file_path: str) -> bool:
    """
    파일이 쓰기 가능한지 확인
    
    Args:
        file_path: 확인할 파일 경로
        
    Returns:
        bool: 쓰기 가능 여부
    """
    try:
        if not os.path.exists(file_path):
            return True  # 새 파일은 쓰기 가능
        
        # 파일 권한 확인
        file_stat = os.stat(file_path)
        return bool(file_stat.st_mode & stat.S_IWRITE)
    except (OSError, IOError):
        return False


def ensure_file_writable(file_path: str) -> Tuple[bool, str]:
    """
    파일을 쓰기 가능한 상태로 만들기
    
    Args:
        file_path: 파일 경로
        
    Returns:
        Tuple[bool, str]: (성공 여부, 상태 메시지)
    """
    try:
        # 파일이 없으면 쓰기 가능
        if not os.path.exists(file_path):
            return True, "새 파일 생성 가능"
        
        # 이미 쓰기 가능하면 OK
        if is_file_writable(file_path):
            return True, "파일이 이미 쓰기 가능"
        
        # 읽기 전용 파일이면 권한 변경 시도
        try:
            os.chmod(file_path, stat.S_IWRITE | stat.S_IREAD)
            if is_file_writable(file_path):
                return True, "파일 권한이 변경됨"
            else:
                return False, "권한 변경 후에도 쓰기 불가"
        except OSError as e:
            return False, f"권한 변경 실패: {str(e)}"
            
    except Exception as e:
        return False, f"예상치 못한 오류: {str(e)}"


def get_relative_path(absolute_path: str, base_path: str) -> str:
    """
    절대 경로를 기준 경로 기반 상대 경로로 변환
    
    Args:
        absolute_path: 절대 경로
        base_path: 기준 경로
        
    Returns:
        str: 상대 경로
    """
    try:
        # 절대 경로를 상대 경로로 변환
        relative_path = os.path.relpath(absolute_path, base_path)
        
        # 백슬래시를 슬래시로 변환 (JSON에서 사용)
        relative_path = relative_path.replace('\\', '/')
        
        # ../ 로 시작하지 않으면 추가
        if not relative_path.startswith('../'):
            relative_path = '../' + relative_path
        
        return relative_path
        
    except Exception:
        # 실패하면 파일명만 반환
        return '../Python/' + os.path.basename(absolute_path)


def format_file_path(file_path: str, max_length: int = 80) -> str:
    """
    긴 파일 경로를 적절히 줄여서 표시
    
    Args:
        file_path: 파일 경로
        max_length: 최대 길이
        
    Returns:
        str: 포맷된 파일 경로
    """
    if not file_path or len(file_path) <= max_length:
        return f"파일: {file_path}" if file_path else "파일: 없음"
    
    # 경로가 너무 길면 중간을 생략
    filename = os.path.basename(file_path)
    dirname = os.path.dirname(file_path)
    
    # 파일명을 포함한 최소 필요 길이 계산
    min_needed = len("파일: ") + len(filename) + len("...\\")
    
    if min_needed >= max_length:
        # 파일명만 표시
        return f"파일: ...\\{filename}"
    
    # 디렉토리 부분에서 사용할 수 있는 길이
    available_for_dir = max_length - len("파일: ") - len(filename) - len("...\\")
    
    if len(dirname) <= available_for_dir:
        return f"파일: {file_path}"
    
    # 디렉토리의 앞부분만 표시
    truncated_dir = dirname[:available_for_dir]
    return f"파일: {truncated_dir}...\\{filename}"


def find_unreal_project_root(start_path: str, max_levels: int = 10) -> str:
    """
    .uproject 파일을 찾아서 언리얼 프로젝트 루트 디렉토리를 찾습니다.
    
    Args:
        start_path: 시작 경로
        max_levels: 최대 탐색 레벨
        
    Returns:
        str: 언리얼 프로젝트 루트 경로 (찾지 못하면 빈 문자열)
    """
    current_path = os.path.abspath(start_path)
    
    for _ in range(max_levels):
        try:
            items = os.listdir(current_path)
            has_uproject = any(item.endswith('.uproject') for item in items)
            
            if has_uproject:
                return current_path
        except (OSError, PermissionError):
            pass
        
        parent_path = os.path.dirname(current_path)
        if current_path == parent_path:  # 루트 디렉토리에 도달
            break
        current_path = parent_path
    
    return ""


def find_tapython_config_path(start_path: str) -> str:
    """
    TAPython MenuConfig.json 파일의 경로를 찾습니다.
    
    Args:
        start_path: 시작 경로
        
    Returns:
        str: MenuConfig.json 파일 경로 (찾지 못하면 빈 문자열)
    """
    project_root = find_unreal_project_root(start_path)
    if not project_root:
        return ""
    
    config_path = os.path.join(project_root, "TA", "TAPython", "UI", "MenuConfig.json")
    return config_path if os.path.exists(config_path) else config_path  # 존재하지 않더라도 경로는 반환