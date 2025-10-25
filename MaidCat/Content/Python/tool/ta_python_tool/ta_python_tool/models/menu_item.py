#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Menu Item Model
메뉴 아이템 데이터 모델
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum


class MenuItemType(Enum):
    """메뉴 아이템 타입"""
    SUBMENU = "submenu"
    COMMAND = "command"
    CHAMELEON_TOOLS = "chameleonTools"


class IconType(Enum):
    """아이콘 타입"""
    NONE = "없음"
    EDITOR_STYLE = "EditorStyle"
    CHAMELEON_STYLE = "ChameleonStyle"
    IMAGE_PATH = "ImagePath"


@dataclass
class IconData:
    """아이콘 데이터"""
    icon_type: IconType = IconType.NONE
    name: str = ""
    image_path: str = ""
    
    def to_dict(self) -> Optional[Dict[str, str]]:
        """딕셔너리로 변환"""
        if self.icon_type == IconType.NONE or not self.name:
            return None
        
        if self.icon_type == IconType.EDITOR_STYLE:
            return {"style": "EditorStyle", "name": self.name}
        elif self.icon_type == IconType.CHAMELEON_STYLE:
            return {"style": "ChameleonStyle", "name": self.name}
        elif self.icon_type == IconType.IMAGE_PATH:
            return {"ImagePathInPlugin": self.name}
        
        return None
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'IconData':
        """딕셔너리에서 생성"""
        if not data:
            return cls()
        
        if "style" in data:
            style = data.get("style", "")
            name = data.get("name", "")
            if style == "EditorStyle":
                return cls(IconType.EDITOR_STYLE, name)
            elif style == "ChameleonStyle":
                return cls(IconType.CHAMELEON_STYLE, name)
        elif "ImagePathInPlugin" in data:
            path = data.get("ImagePathInPlugin", "")
            return cls(IconType.IMAGE_PATH, path)
        
        return cls()


@dataclass
class MenuItem:
    """메뉴 아이템"""
    name: str = ""
    item_type: MenuItemType = MenuItemType.COMMAND
    tooltip: str = ""
    enabled: bool = True
    icon: IconData = field(default_factory=IconData)
    
    # Command 관련
    command: str = ""
    can_execute_action: str = ""
    
    # Chameleon Tools 관련
    chameleon_tools: str = ""
    
    # Submenu 관련
    items: List['MenuItem'] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        result: Dict[str, Any] = {"name": self.name}
        
        if self.tooltip:
            result["tooltip"] = self.tooltip
        
        # 아이콘 데이터 추가
        icon_dict = self.icon.to_dict()
        if icon_dict:
            result["icon"] = icon_dict
        
        # 타입별 필드 추가
        if self.item_type == MenuItemType.SUBMENU:
            result["items"] = [item.to_dict() for item in self.items]
        
        elif self.item_type == MenuItemType.COMMAND:
            result["enabled"] = self.enabled
            if self.command:
                result["command"] = self.command
            if self.can_execute_action:
                result["canExecuteAction"] = self.can_execute_action
        
        elif self.item_type == MenuItemType.CHAMELEON_TOOLS:
            result["enabled"] = self.enabled
            if self.chameleon_tools:
                result["ChameleonTools"] = self.chameleon_tools
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MenuItem':
        """딕셔너리에서 생성"""
        item = cls()
        item.name = data.get("name", "")
        item.tooltip = data.get("tooltip", "")
        item.enabled = data.get("enabled", True)
        
        # 아이콘 데이터
        icon_data = data.get("icon", {})
        item.icon = IconData.from_dict(icon_data)
        
        # 타입 판단 및 데이터 설정
        if "items" in data:
            item.item_type = MenuItemType.SUBMENU
            item.items = [cls.from_dict(child) for child in data["items"]]
        elif "ChameleonTools" in data:
            item.item_type = MenuItemType.CHAMELEON_TOOLS
            item.chameleon_tools = data.get("ChameleonTools", "")
        else:
            item.item_type = MenuItemType.COMMAND
            item.command = data.get("command", "")
            item.can_execute_action = data.get("canExecuteAction", "")
        
        return item
    
    def get_display_info(self) -> tuple[str, str]:
        """표시용 정보 반환 (타입, 표시명)"""
        if self.item_type == MenuItemType.SUBMENU:
            return ("📁 서브메뉴", f"📁 {self.name}")
        elif self.item_type == MenuItemType.CHAMELEON_TOOLS:
            return ("🎨 카멜레온", f"🎨 {self.name}")
        elif self.item_type == MenuItemType.COMMAND:
            return ("⚡ 명령어", f"⚡ {self.name}")
        else:
            return ("📄 엔트리", f"📄 {self.name}")
    
    def find_child_by_path(self, path: List[int]) -> Optional['MenuItem']:
        """경로로 자식 아이템 찾기"""
        if not path:
            return self
        
        if not self.items or path[0] >= len(self.items):
            return None
        
        if len(path) == 1:
            return self.items[path[0]]
        
        return self.items[path[0]].find_child_by_path(path[1:])
    
    def add_child(self, child: 'MenuItem', index: Optional[int] = None):
        """자식 아이템 추가"""
        if self.item_type != MenuItemType.SUBMENU:
            return False
        
        if index is None:
            self.items.append(child)
        else:
            self.items.insert(index, child)
        
        return True
    
    def remove_child(self, index: int) -> bool:
        """자식 아이템 제거"""
        if self.item_type != MenuItemType.SUBMENU:
            return False
        
        if 0 <= index < len(self.items):
            del self.items[index]
            return True
        
        return False
    
    def move_child(self, from_index: int, to_index: int) -> bool:
        """자식 아이템 이동"""
        if self.item_type != MenuItemType.SUBMENU:
            return False
        
        if 0 <= from_index < len(self.items) and 0 <= to_index < len(self.items):
            item = self.items.pop(from_index)
            self.items.insert(to_index, item)
            return True
        
        return False