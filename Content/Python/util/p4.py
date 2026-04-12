#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Perforce (P4) Utility Module
언리얼 엔진 프로젝트에서 Perforce 소스 컨트롤을 다루기 위한 유틸리티 모듈
"""

import os
import stat
import subprocess
import sys
import logging
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)


# ==================== 파일 권한 관련 ====================

def is_file_writable(file_path: str) -> bool:
    """
    파일이 쓰기 가능한지 확인
    
    Args:
        file_path: 확인할 파일 경로
        
    Returns:
        파일이 쓰기 가능하면 True, 아니면 False
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
        (성공 여부, 상태 메시지) 튜플
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


# ==================== Perforce 설정 관련 ====================

def get_perforce_settings_path(project_root: str) -> Optional[str]:
    """
    퍼포스 설정 파일 경로 반환
    
    Args:
        project_root: 언리얼 프로젝트 루트 경로
        
    Returns:
        퍼포스 설정 파일 경로 또는 None
    """
    if not project_root:
        return None
    
    return os.path.join(
        project_root, 
        "Saved", 
        "Config", 
        "WindowsEditor", 
        "SourceControlSettings.ini"
    )


def read_perforce_settings(settings_path: str) -> Optional[Dict[str, str]]:
    """
    퍼포스 설정 파일 읽기
    
    Args:
        settings_path: 설정 파일 경로
        
    Returns:
        퍼포스 설정 딕셔너리 또는 None
    """
    try:
        logger.info(f"퍼포스 설정 파일 경로: {settings_path}")
        
        if not os.path.exists(settings_path):
            logger.warning(f"퍼포스 설정 파일을 찾을 수 없습니다: {settings_path}")
            return None
        
        # INI 파일 파싱
        p4_settings = {}
        current_section = None
        
        with open(settings_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # 섹션 헤더
                if line.startswith('[') and line.endswith(']'):
                    current_section = line[1:-1]
                    continue
                
                # 키=값 형식
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # PerforceSourceControl 설정
                    if current_section == 'PerforceSourceControl.PerforceSourceControlSettings':
                        p4_settings[key] = value
                    
                    # SourceControl 설정 (Provider)
                    elif current_section == 'SourceControl.SourceControlSettings' and key == 'Provider':
                        p4_settings['Provider'] = value
        
        logger.info(f"퍼포스 설정 로드 완료: {p4_settings}")
        return p4_settings if p4_settings else None
        
    except Exception as e:
        logger.error(f"퍼포스 설정 읽기 오류: {e}")
        return None


# ==================== Perforce 환경 변수 및 명령 실행 ====================

def setup_p4_environment(p4_settings: Dict[str, str]) -> Dict[str, str]:
    """
    퍼포스 환경 변수 설정 (재사용 가능)
    
    Args:
        p4_settings: 퍼포스 설정 딕셔너리
        
    Returns:
        환경 변수 딕셔너리
    """
    p4_env = os.environ.copy()
    
    if 'Port' in p4_settings:
        p4_env['P4PORT'] = p4_settings['Port']
    if 'UserName' in p4_settings:
        p4_env['P4USER'] = p4_settings['UserName']
    if 'Workspace' in p4_settings:
        p4_env['P4CLIENT'] = p4_settings['Workspace']
    
    return p4_env


def run_p4_command(cmd: list, p4_settings: Dict[str, str], timeout: int = 2) -> subprocess.CompletedProcess:
    """
    퍼포스 명령 실행 (공통 로직)
    
    Args:
        cmd: 실행할 명령어 리스트
        p4_settings: 퍼포스 설정 딕셔너리
        timeout: 타임아웃 시간(초)
        
    Returns:
        subprocess.CompletedProcess 객체
    """
    p4_env = setup_p4_environment(p4_settings)
    
    result = subprocess.run(
        cmd,
        env=p4_env,
        capture_output=True,
        text=True,
        timeout=timeout,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
    )
    
    return result


# ==================== Perforce 파일 상태 확인 ====================

def check_perforce_file(file_path: str, p4_settings: Dict[str, str]) -> Tuple[bool, str]:
    """
    파일이 퍼포스 관리 중인지 체크 (빠른 체크)
    
    Args:
        file_path: 확인할 파일 경로
        p4_settings: 퍼포스 설정 딕셔너리
        
    Returns:
        (관리 여부, 상태 메시지) 튜플
    """
    try:
        if not p4_settings:
            return False, "퍼포스 설정 없음"
        
        # Provider가 Perforce인지 확인
        if p4_settings.get('Provider') != 'Perforce':
            return False, f"프로바이더: {p4_settings.get('Provider')}"
        
        # p4 fstat으로 파일 상태 확인
        cmd = ['p4', 'fstat', file_path]
        result = run_p4_command(cmd, p4_settings, timeout=2)
        
        # returncode 0이면 파일이 퍼포스에 있음
        if result.returncode == 0:
            is_readonly = 'headRev' in result.stdout
            return True, f"퍼포스 관리 중 (ReadOnly: {is_readonly})"
        else:
            return False, "퍼포스 관리 안됨"
            
    except subprocess.TimeoutExpired:
        logger.warning("p4 명령 타임아웃")
        return False, "퍼포스 체크 타임아웃"
    except FileNotFoundError:
        return False, "p4 명령어 없음"
    except Exception as e:
        logger.error(f"퍼포스 파일 체크 오류: {e}")
        return False, f"체크 오류: {str(e)}"


def get_file_status(file_path: str, p4_settings: Dict[str, str]) -> Optional[Dict[str, str]]:
    """
    퍼포스 파일의 상세 상태 정보 조회
    
    Args:
        file_path: 파일 경로
        p4_settings: 퍼포스 설정 딕셔너리
        
    Returns:
        상태 정보 딕셔너리 또는 None
    """
    try:
        cmd = ['p4', 'fstat', file_path]
        result = run_p4_command(cmd, p4_settings, timeout=3)
        
        if result.returncode == 0:
            # fstat 출력 파싱
            status_info = {}
            for line in result.stdout.splitlines():
                line = line.strip()
                if line.startswith('...'):
                    parts = line[3:].split(' ', 1)
                    if len(parts) == 2:
                        key, value = parts
                        status_info[key] = value.strip()
            return status_info
        else:
            return None
            
    except Exception as e:
        logger.error(f"퍼포스 파일 상태 조회 오류: {e}")
        return None


# ==================== Perforce 체크아웃/체크인 ====================

def perforce_checkout(file_path: str, p4_settings: Dict[str, str]) -> Tuple[bool, str]:
    """
    퍼포스에서 파일 체크아웃 (빠른 실행)
    
    Args:
        file_path: 체크아웃할 파일 경로
        p4_settings: 퍼포스 설정 딕셔너리
        
    Returns:
        (성공 여부, 메시지) 튜플
    """
    try:
        if not p4_settings:
            return False, "퍼포스 설정 없음"
        
        # p4 edit으로 체크아웃
        cmd = ['p4', 'edit', file_path]
        result = run_p4_command(cmd, p4_settings, timeout=3)
        
        if result.returncode == 0:
            return True, "체크아웃 성공"
        else:
            return False, f"체크아웃 실패: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return False, "체크아웃 타임아웃"
    except FileNotFoundError:
        return False, "p4 명령어 없음"
    except Exception as e:
        logger.error(f"퍼포스 체크아웃 오류: {e}")
        return False, f"체크아웃 오류: {str(e)}"


def perforce_revert(file_path: str, p4_settings: Dict[str, str], unchanged_only: bool = False) -> Tuple[bool, str]:
    """
    퍼포스에서 파일 되돌리기 (Revert)
    
    Args:
        file_path: 되돌릴 파일 경로
        p4_settings: 퍼포스 설정 딕셔너리
        unchanged_only: True면 변경사항 없는 파일만 되돌림
        
    Returns:
        (성공 여부, 메시지) 튜플
    """
    try:
        if not p4_settings:
            return False, "퍼포스 설정 없음"
        
        # p4 revert로 되돌리기
        cmd = ['p4', 'revert']
        if unchanged_only:
            cmd.append('-a')  # unchanged only
        cmd.append(file_path)
        
        result = run_p4_command(cmd, p4_settings, timeout=3)
        
        if result.returncode == 0:
            return True, "되돌리기 성공"
        else:
            return False, f"되돌리기 실패: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return False, "되돌리기 타임아웃"
    except FileNotFoundError:
        return False, "p4 명령어 없음"
    except Exception as e:
        logger.error(f"퍼포스 되돌리기 오류: {e}")
        return False, f"되돌리기 오류: {str(e)}"


def perforce_add(file_path: str, p4_settings: Dict[str, str]) -> Tuple[bool, str]:
    """
    퍼포스에 새 파일 추가
    
    Args:
        file_path: 추가할 파일 경로
        p4_settings: 퍼포스 설정 딕셔너리
        
    Returns:
        (성공 여부, 메시지) 튜플
    """
    try:
        if not p4_settings:
            return False, "퍼포스 설정 없음"
        
        # p4 add로 파일 추가
        cmd = ['p4', 'add', file_path]
        result = run_p4_command(cmd, p4_settings, timeout=3)
        
        if result.returncode == 0:
            return True, "추가 성공"
        else:
            return False, f"추가 실패: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return False, "추가 타임아웃"
    except FileNotFoundError:
        return False, "p4 명령어 없음"
    except Exception as e:
        logger.error(f"퍼포스 파일 추가 오류: {e}")
        return False, f"추가 오류: {str(e)}"


def perforce_delete(file_path: str, p4_settings: Dict[str, str]) -> Tuple[bool, str]:
    """
    퍼포스에서 파일 삭제 (Mark for delete)
    
    Args:
        file_path: 삭제할 파일 경로
        p4_settings: 퍼포스 설정 딕셔너리
        
    Returns:
        (성공 여부, 메시지) 튜플
    """
    try:
        if not p4_settings:
            return False, "퍼포스 설정 없음"
        
        # p4 delete로 삭제 마크
        cmd = ['p4', 'delete', file_path]
        result = run_p4_command(cmd, p4_settings, timeout=3)
        
        if result.returncode == 0:
            return True, "삭제 마크 성공"
        else:
            return False, f"삭제 실패: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return False, "삭제 타임아웃"
    except FileNotFoundError:
        return False, "p4 명령어 없음"
    except Exception as e:
        logger.error(f"퍼포스 파일 삭제 오류: {e}")
        return False, f"삭제 오류: {str(e)}"


# ==================== 통합 파일 쓰기 권한 관리 ====================

def ensure_file_writable_with_p4(file_path: str, p4_settings: Optional[Dict[str, str]] = None, 
                                   auto_checkout: bool = True) -> Tuple[bool, str]:
    """
    파일이 쓰기 가능한지 확인하고 필요시 처리 (퍼포스 연동 - 최적화)
    
    Args:
        file_path: 파일 경로
        p4_settings: 퍼포스 설정 딕셔너리 (None이면 퍼포스 체크 생략)
        auto_checkout: True면 자동으로 체크아웃 시도
        
    Returns:
        (성공 여부, 상태 메시지) 튜플
    """
    try:
        # 1. 빠른 권한 체크 먼저 (퍼포스 체크 전)
        if is_file_writable(file_path):
            logger.debug("파일이 이미 쓰기 가능 - 퍼포스 체크 생략")
            return True, "파일이 쓰기 가능"
        
        logger.info(f"파일이 ReadOnly - 퍼포스 체크 시작: {file_path}")
        
        # 2. 퍼포스 관리 중인지 체크 (ReadOnly인 경우에만)
        if p4_settings:
            is_in_perforce, p4_status = check_perforce_file(file_path, p4_settings)
            
            if is_in_perforce:
                logger.info(f"퍼포스 파일 감지 - 체크아웃 시도")
                
                if auto_checkout:
                    # 자동으로 체크아웃
                    checkout_success, checkout_msg = perforce_checkout(file_path, p4_settings)
                    
                    if checkout_success:
                        logger.info(f"퍼포스 체크아웃 성공")
                        return True, "퍼포스 체크아웃 완료"
                    else:
                        logger.warning(f"퍼포스 체크아웃 실패: {checkout_msg}")
                        return False, f"체크아웃 실패: {checkout_msg}"
                else:
                    return False, "퍼포스 파일 - 체크아웃 필요"
        
        # 3. 퍼포스가 아닌 경우 기존 로직 사용
        logger.info("퍼포스 관리 파일 아님 - 일반 권한 확인")
        success, message = ensure_file_writable(file_path)
        
        if success:
            logger.info(f"파일 쓰기 가능: {message}")
            return True, message
        else:
            logger.warning(f"파일 쓰기 불가: {message}")
            return False, message
        
    except Exception as e:
        logger.error(f"파일 쓰기 권한 확인 중 오류: {e}")
        return False, f"권한 확인 오류: {str(e)}"


# ==================== 편의 함수 ====================

def get_changelist_description(changelist: int, p4_settings: Dict[str, str]) -> Optional[str]:
    """
    체인지리스트의 설명 가져오기
    
    Args:
        changelist: 체인지리스트 번호
        p4_settings: 퍼포스 설정 딕셔너리
        
    Returns:
        체인지리스트 설명 또는 None
    """
    try:
        cmd = ['p4', 'describe', '-s', str(changelist)]
        result = run_p4_command(cmd, p4_settings, timeout=3)
        
        if result.returncode == 0:
            return result.stdout
        else:
            return None
            
    except Exception as e:
        logger.error(f"체인지리스트 설명 조회 오류: {e}")
        return None


def get_pending_changelists(p4_settings: Dict[str, str]) -> list:
    """
    사용자의 대기 중인 체인지리스트 목록 가져오기
    
    Args:
        p4_settings: 퍼포스 설정 딕셔너리
        
    Returns:
        체인지리스트 번호 리스트
    """
    try:
        user = p4_settings.get('UserName')
        if not user:
            return []
        
        cmd = ['p4', 'changes', '-s', 'pending', '-u', user]
        result = run_p4_command(cmd, p4_settings, timeout=5)
        
        if result.returncode == 0:
            changelists = []
            for line in result.stdout.splitlines():
                if line.startswith('Change'):
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            changelists.append(int(parts[1]))
                        except ValueError:
                            pass
            return changelists
        else:
            return []
            
    except Exception as e:
        logger.error(f"체인지리스트 목록 조회 오류: {e}")
        return []
