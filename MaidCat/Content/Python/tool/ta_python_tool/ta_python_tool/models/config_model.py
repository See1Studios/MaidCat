#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Config Model
설정 데이터 모델
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from .menu_item import MenuItem
from ..config.constants import ALL_TOOL_MENUS, DEFAULT_CONFIG_STRUCTURE
from ..utils.file_utils import ensure_file_writable, find_tapython_config_path
from ..utils.logging_utils import get_logger

logger = get_logger()


@dataclass
class ToolMenuConfig:
    """툴 메뉴 설정"""
    has_section: bool = True
    items: List[MenuItem] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        result: Dict[str, Any] = {
            "HasSection": self.has_section,
            "items": [item.to_dict() for item in self.items]
        }
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolMenuConfig':
        """딕셔너리에서 생성"""
        config = cls()
        config.has_section = data.get("HasSection", True)
        
        items_data = data.get("items", [])
        config.items = [MenuItem.from_dict(item_data) for item_data in items_data]
        
        return config
    
    def add_item(self, item: MenuItem, index: Optional[int] = None):
        """아이템 추가"""
        if index is None:
            self.items.append(item)
        else:
            self.items.insert(index, item)
    
    def remove_item(self, index: int) -> bool:
        """아이템 제거"""
        if 0 <= index < len(self.items):
            del self.items[index]
            return True
        return False
    
    def move_item(self, from_index: int, to_index: int) -> bool:
        """아이템 이동"""
        if 0 <= from_index < len(self.items) and 0 <= to_index < len(self.items):
            item = self.items.pop(from_index)
            self.items.insert(to_index, item)
            return True
        return False


class ConfigManager:
    """설정 관리자"""
    
    def __init__(self):
        self.config_data: Dict[str, ToolMenuConfig] = {}
        self.file_path: str = ""
        self.has_unsaved_changes: bool = False
        
        # 기본 설정 파일 경로 찾기
        self.default_config_path = self._find_default_config_path()
    
    def _find_default_config_path(self) -> str:
        """기본 설정 파일 경로 찾기"""
        try:
            script_path = os.path.abspath(__file__)
            return find_tapython_config_path(script_path)
        except Exception as e:
            logger.error(f"기본 설정 파일 경로 찾기 실패: {e}")
            return ""
    
    def load_file(self, file_path: str) -> bool:
        """설정 파일 로드"""
        try:
            logger.info(f"설정 파일 로드 시작: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            # 데이터 변환
            self.config_data = {}
            for tool_menu_id, menu_data in raw_data.items():
                self.config_data[tool_menu_id] = ToolMenuConfig.from_dict(menu_data)
            
            self.file_path = file_path
            self.has_unsaved_changes = False
            
            logger.info(f"설정 파일 로드 완료: {len(self.config_data)}개 툴 메뉴")
            return True
            
        except FileNotFoundError:
            logger.error(f"파일을 찾을 수 없음: {file_path}")
            return False
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류: {e}")
            return False
        except Exception as e:
            logger.error(f"설정 파일 로드 오류: {e}")
            return False
    
    def save_file(self, file_path: Optional[str] = None) -> bool:
        """설정 파일 저장"""
        try:
            target_path = file_path or self.file_path
            if not target_path:
                logger.error("저장할 파일 경로가 없습니다")
                return False
            
            # 파일 쓰기 권한 확인
            can_write, message = ensure_file_writable(target_path)
            if not can_write:
                logger.error(f"파일 쓰기 권한 없음: {message}")
                return False
            
            # 데이터 변환
            raw_data = {}
            for tool_menu_id, menu_config in self.config_data.items():
                raw_data[tool_menu_id] = menu_config.to_dict()
            
            # 파일 저장
            with open(target_path, 'w', encoding='utf-8') as f:
                json.dump(raw_data, f, indent=4, ensure_ascii=False)
            
            if file_path:  # 새 경로로 저장한 경우
                self.file_path = file_path
            
            self.has_unsaved_changes = False
            logger.info(f"설정 파일 저장 완료: {target_path}")
            return True
            
        except Exception as e:
            logger.error(f"설정 파일 저장 오류: {e}")
            return False
    
    def create_new_config(self) -> bool:
        """새 설정 생성"""
        try:
            self.config_data = {}
            self.file_path = ""
            self.has_unsaved_changes = False
            return True
        except Exception as e:
            logger.error(f"새 설정 생성 오류: {e}")
            return False
    
    def add_tool_menu(self, tool_menu_id: str, has_section: bool = True) -> bool:
        """툴 메뉴 추가"""
        if tool_menu_id in self.config_data:
            return False
        
        self.config_data[tool_menu_id] = ToolMenuConfig(has_section=has_section)
        self.mark_as_modified()
        return True
    
    def remove_tool_menu(self, tool_menu_id: str) -> bool:
        """툴 메뉴 제거"""
        if tool_menu_id not in self.config_data:
            return False
        
        del self.config_data[tool_menu_id]
        self.mark_as_modified()
        return True
    
    def get_tool_menu(self, tool_menu_id: str) -> Optional[ToolMenuConfig]:
        """툴 메뉴 가져오기"""
        return self.config_data.get(tool_menu_id)
    
    def get_available_tool_menus(self) -> List[tuple[str, str]]:
        """사용 가능한 툴 메뉴 목록 반환"""
        available = []
        for tool_menu_id, tool_menu_name in ALL_TOOL_MENUS:
            if tool_menu_id in self.config_data:
                available.append((tool_menu_id, tool_menu_name))
        return available
    
    def get_tool_menu_display_name(self, tool_menu_id: str) -> str:
        """툴 메뉴 표시명 반환"""
        for menu_id, menu_name in ALL_TOOL_MENUS:
            if menu_id == tool_menu_id:
                return menu_name
        
        # 기본 이름이 없으면 ID를 기반으로 가독성 있는 이름 생성
        if "." in tool_menu_id:
            parts = tool_menu_id.split(".")
            return " > ".join(parts)
        else:
            return tool_menu_id
    
    def mark_as_modified(self):
        """변경사항 표시"""
        self.has_unsaved_changes = True
    
    def mark_as_saved(self):
        """저장됨 표시"""
        self.has_unsaved_changes = False
    
    def is_tapython_available(self) -> bool:
        """TAPython 플러그인 사용 가능 여부 확인"""
        return bool(self.default_config_path and os.path.exists(self.default_config_path))
    
    def create_default_config_structure(self) -> Dict[str, Any]:
        """기본 설정 구조 생성"""
        return DEFAULT_CONFIG_STRUCTURE.copy()
    
    def validate_tool_menu_data(self, tool_menu_id: str) -> ToolMenuConfig:
        """툴 메뉴 데이터 검증 및 생성"""
        if tool_menu_id not in self.config_data:
            self.config_data[tool_menu_id] = ToolMenuConfig()
        return self.config_data[tool_menu_id]