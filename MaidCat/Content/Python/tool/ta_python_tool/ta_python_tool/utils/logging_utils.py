#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logging Utilities
로깅 설정 및 관리 유틸리티
"""

import logging
import os
from typing import Optional, Tuple

from ..config.constants import LOG_FILE_NAME, LOG_LEVEL_CONSOLE, LOG_LEVEL_FILE, LOG_FORMAT

# 중복 초기화 방지
_logger_initialized = False
_logger_instance: Optional[logging.Logger] = None
_file_handler_instance: Optional[logging.FileHandler] = None


def setup_logging() -> Tuple[logging.Logger, Optional[logging.FileHandler]]:
    """
    로깅 설정 함수
    
    Returns:
        Tuple[logging.Logger, Optional[logging.FileHandler]]: 로거와 파일 핸들러
    """
    global _logger_initialized, _logger_instance, _file_handler_instance
    
    if _logger_initialized and _logger_instance:
        return _logger_instance, _file_handler_instance
    
    # 기존 핸들러 정리
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)
    
    # 새로운 로거 설정 (propagate 방지)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.ERROR)  # WARNING에서 ERROR로 변경하여 로그 출력 최소화
    logger.propagate = False  # 부모 로거로 전파 방지
    
    # 기존 핸들러 제거
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, LOG_LEVEL_CONSOLE))
    
    # 파일 핸들러 (스크립트 디렉토리에 저장)
    file_handler = None
    try:
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        log_file = os.path.join(script_dir, LOG_FILE_NAME)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, LOG_LEVEL_FILE))
        _file_handler_instance = file_handler
    except Exception:
        # 파일 생성 실패시 콘솔만 사용
        file_handler = None
        _file_handler_instance = None
    
    # 포맷터 설정
    formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(formatter)
    if file_handler:
        file_handler.setFormatter(formatter)
    
    # 핸들러 추가
    logger.addHandler(console_handler)
    if file_handler:
        logger.addHandler(file_handler)
    
    _logger_initialized = True
    _logger_instance = logger
    
    return logger, file_handler


def get_logger() -> logging.Logger:
    """로거 인스턴스를 반환합니다."""
    if not _logger_initialized or _logger_instance is None:
        logger, _ = setup_logging()
        return logger
    return _logger_instance


def cleanup_logging():
    """로깅 리소스를 정리합니다."""
    global _logger_initialized, _logger_instance, _file_handler_instance
    
    try:
        if _file_handler_instance:
            _file_handler_instance.close()
            if _logger_instance:
                _logger_instance.removeHandler(_file_handler_instance)
        
        _logger_initialized = False
        _logger_instance = None
        _file_handler_instance = None
    except Exception as e:
        print(f"로깅 리소스 정리 중 오류: {e}")