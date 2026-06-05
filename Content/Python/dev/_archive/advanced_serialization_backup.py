"""
Advanced Unreal Object Serialization System
==========================================

Unreal Engine Python API 문서를 기반으로 한 완전히 새로운 serialization 시스템입니다.

핵심 설계 원칙:
1. Unreal Engine Python API 공식 문서 기준
2. StructBase, ObjectBase, EnumBase 정확한 타입 감지
3. get_all_property_names() + PythonBPLib 활용
4. 재귀적이지만 안전한 깊이 제한

참고 문서:
- https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/StructBase
- https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/_ObjectBase  
- https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/EnumBase

작성자: MaidCat Plugin
버전: 2.0 (완전 재설계)
"""

import unreal
import json
from typing import Any, Dict, List, Optional, Union, Set
from ue import bp_lib  # MaidCat의 PythonBPLib 래퍼 사용


# ===============================================================================
# 기본 직렬화기 클래스
# ===============================================================================

class BaseSerializer:
    """모든 직렬화기의 기본 클래스"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.current_depth = 0
        self.max_depth = 15
        
    def debug_log(self, message: str, level: int = 1):
        """디버그 로깅 (극한 성능 최적화)"""
        return  # 모든 디버그 로깅 비활성화
    
    def can_serialize(self, obj: Any) -> bool:
        """이 직렬화기가 해당 객체를 처리할 수 있는지 확인"""
        return False
    
    def serialize(self, obj: Any, name: str = "root") -> Dict[str, Any]:
        """객체를 직렬화"""
        raise NotImplementedError


class EnumSerializer(BaseSerializer):
    """Enum 전용 직렬화기"""
    
    def can_serialize(self, obj: Any) -> bool:
        """Enum 객체인지 확인"""
        if hasattr(obj, '__class__') and hasattr(obj.__class__, '__name__'):
            class_name = obj.__class__.__name__
            return (hasattr(obj, 'name') and hasattr(obj, 'value')) or 'Enum' in class_name
        return False
    
    def serialize(self, obj: Any, name: str = "root") -> Dict[str, Any]:
        """Enum 객체 직렬화"""
        class_name = getattr(obj.__class__, '__name__', 'Unknown')
        enum_name = getattr(obj, 'name', None)
        enum_value = getattr(obj, 'value', None)
        
        enum_data = {
            "_unreal_type": "enum",
            "_class_name": class_name,
            "_enum_name": enum_name,
            "_enum_value": enum_value
        }
        
        # display_name 처리
        if hasattr(obj, 'display_name'):
            display_name_obj = getattr(obj, 'display_name', None)
            if display_name_obj is not None:
                if hasattr(display_name_obj, 'to_string'):
                    enum_data["_display_name"] = str(display_name_obj.to_string())
                else:
                    enum_data["_display_name"] = str(display_name_obj)
        
        return enum_data


class StructSerializer(BaseSerializer):
    """Struct 전용 직렬화기"""
    
    def can_serialize(self, obj: Any) -> bool:
        """Struct 객체인지 확인"""
        struct_indicators = [
            hasattr(obj, 'static_struct'),
            'Struct' in str(type(obj)),
            (hasattr(obj, 'get_editor_property_names') and not hasattr(obj, 'get_class'))
        ]
        return any(struct_indicators)
    
    def serialize(self, obj: Any, name: str = "root") -> Dict[str, Any]:
        """Struct 객체 직렬화"""
        class_name = getattr(obj.__class__, '__name__', 'UnknownStruct')
        
        struct_data = {
            "_unreal_type": "struct",
            "_class_name": class_name
        }
        
        # 특별한 struct 타입들 처리 (Vector, Rotator 등)
        if class_name in ['Vector', 'Vector2D', 'Rotator', 'LinearColor', 'Color']:
            if hasattr(obj, 'x') and hasattr(obj, 'y'):
                values = {'x': getattr(obj, 'x', 0), 'y': getattr(obj, 'y', 0)}
                if hasattr(obj, 'z'):
                    values['z'] = getattr(obj, 'z', 0)
                if hasattr(obj, 'w'):
                    values['w'] = getattr(obj, 'w', 0)
                struct_data["_direct_values"] = values
            elif class_name == 'Rotator' and hasattr(obj, 'pitch'):
                struct_data["_direct_values"] = {
                    'pitch': getattr(obj, 'pitch', 0),
                    'roll': getattr(obj, 'roll', 0), 
                    'yaw': getattr(obj, 'yaw', 0)
                }
            elif class_name in ['LinearColor', 'Color'] and hasattr(obj, 'r'):
                values = {
                    'r': getattr(obj, 'r', 0),
                    'g': getattr(obj, 'g', 0),
                    'b': getattr(obj, 'b', 0)
                }
                if hasattr(obj, 'a'):
                    values['a'] = getattr(obj, 'a', 1)
                struct_data["_direct_values"] = values
        
        return struct_data


class ObjectSerializer(BaseSerializer):
    """Object 전용 직렬화기"""
    
    def __init__(self, debug: bool = False):
        super().__init__(debug)
        self._object_cache = {}
        self._processed_objects = set()
    
    def can_serialize(self, obj: Any) -> bool:
        """Object 객체인지 확인"""
        try:
            if hasattr(unreal, '_ObjectBase') and isinstance(obj, unreal._ObjectBase):
                return True
        except:
            pass
        return hasattr(obj, 'get_class')
    
    def serialize(self, obj: Any, name: str = "root") -> Dict[str, Any]:
        """Object 객체 직렬화 (완전한 속성 감지)"""
        # 클래스 정보 추출 (예외 처리 최소화)
        class_name = getattr(obj.__class__, '__name__', 'Unknown')
        path_name = getattr(obj, 'get_path_name', lambda: str(obj))()
        full_name = getattr(obj, 'get_full_name', lambda: f"{class_name} {path_name}")()
        obj_name = getattr(obj, 'get_name', lambda: class_name)()
        
        # 객체 참조 중복 처리 검사 (성능 최적화)
        if path_name and path_name in self._object_cache:
            return {"_object_reference": path_name}
        
        obj_data = {
            "_unreal_type": "object",
            "_class_name": class_name,
            "_path_name": path_name,
            "_full_name": full_name,
            "_name": obj_name,
            "_properties": {}
        }
        
        # 캐시에 추가
        if path_name:
            self._object_cache[path_name] = True
        
        return obj_data


class ArraySerializer(BaseSerializer):
    """Array/List 전용 직렬화기"""
    
    def can_serialize(self, obj: Any) -> bool:
        """Array 객체인지 확인"""
        return hasattr(obj, '__len__') and hasattr(obj, '__getitem__')
    
    def serialize(self, obj: Any, name: str = "root") -> Dict[str, Any]:
        """Array 객체 직렬화"""
        array_length = getattr(obj, '__len__', lambda: 0)()
        
        return {
            "_unreal_type": "array",
            "_length": array_length,
            "_items": []  # 아이템들은 별도로 처리
        }


# ===============================================================================
# 핵심 타입 감지 시스템 (Unreal Python API 기준)
# ===============================================================================

def detect_unreal_type(obj: Any) -> str:
    """
    Unreal Engine Python API 문서를 기준으로 정확한 타입을 감지합니다.
    
    Args:
        obj: 분석할 객체
        
    Returns:
        str: 'struct', 'object', 'enum', 'basic', 'unknown' 중 하나
    """
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return 'basic'
    
    # 1. Unreal EnumBase 감지 (가장 정확한 방법)
    try:
        if hasattr(unreal, 'EnumBase') and isinstance(obj, unreal.EnumBase):
            return 'enum'
    except:
        pass
    
    # Enum fallback: name과 value 속성을 가진 객체 (더 엄격한 체크)
    if hasattr(obj, 'name') and hasattr(obj, 'value'):
        try:
            # 실제로 enum인지 확인 (정수 값과 문자열 이름)
            value = getattr(obj, 'value', None)
            name = getattr(obj, 'name', None)
            
            # 타입 이름에 Enum이나 Mode가 포함되어 있는지 확인 (추가 검증)
            type_name = type(obj).__name__
            is_likely_enum = any(keyword in type_name for keyword in ['Mode', 'Method', 'Type', 'Format', 'Enum'])
            
            if isinstance(value, int) and isinstance(name, str) and is_likely_enum:
                return 'enum'
        except:
            pass
    
    # 2. Unreal StructBase 감지 (Epic Games 공식: "Type for all Unreal exposed struct instances")
    try:
        if hasattr(unreal, 'StructBase') and isinstance(obj, unreal.StructBase):
            return 'struct'
    except:
        pass
    
    # Struct fallback methods
    struct_indicators = [
        hasattr(obj, 'static_struct'),  # Struct는 static_struct() 메서드를 가짐
        'Struct' in str(type(obj)),     # 타입 이름에 'Struct' 포함
        (hasattr(obj, 'get_editor_property_names') and not hasattr(obj, 'get_class'))  # Struct는 get_class가 없음
    ]
    
    if any(struct_indicators):
        return 'struct'
    
    # 3. Unreal _ObjectBase 감지 (Epic Games 공식: "Type for all Unreal exposed object instances")
    try:
        if hasattr(unreal, '_ObjectBase') and isinstance(obj, unreal._ObjectBase):
            return 'object'
    except:
        pass
    
    # Object fallback: get_class 메서드를 가진 객체 (Object만의 특징)
    if hasattr(obj, 'get_class'):
        return 'object'
    
    # 4. 배열/컬렉션 타입
    if hasattr(obj, '__len__') and hasattr(obj, '__iter__'):
        return 'array'
    
    return 'unknown'


def get_property_names_advanced(obj: Any) -> List[str]:
    """
    객체의 프로퍼티 이름을 다양한 방법으로 추출합니다.
    
    Args:
        obj: 분석할 객체
        
    Returns:
        List[str]: 프로퍼티 이름 목록
    """
    property_names = []
    
    # 방법 1: get_editor_property_names() - 가장 정확한 방법
    if hasattr(obj, 'get_editor_property_names'):
        try:
            names = obj.get_editor_property_names()
            property_names.extend([str(name) for name in names])
            return property_names
        except Exception as e:
            print(f"  get_editor_property_names() 실패: {e}")
    
    # 방법 2: PythonBPLib.get_all_property_names() - TAPython 확장
    if hasattr(obj, 'get_class'):
        try:
            obj_class = obj.get_class()
            names = bp_lib.get_all_property_names(obj_class)
            if names:
                property_names.extend([str(name) for name in names])
                return property_names
        except Exception as e:
            print(f"  PythonBPLib.get_all_property_names() 실패: {e}")
    
    # 방법 3: dir() + 필터링 - 최후의 수단
    try:
        all_attrs = dir(obj)
        filtered_attrs = []
        
        for attr in all_attrs:
            # private/magic 속성 제외
            if attr.startswith('_'):
                continue
            
            # Deprecated 속성들 제외
            deprecated_patterns = [
                'b_override_exposure_offset', 'b_override_eye_', 'exposure_offset', 
                'eye_adaptation_', 'eye_adaption_'
            ]
            if any(attr.startswith(pattern) for pattern in deprecated_patterns):
                continue
            
            # 메서드처럼 보이는 것들 제외
            method_patterns = [
                'get_', 'set_', 'is_', 'has_', 'can_', 'should_', 
                'execute', 'call', 'create', 'destroy', 'spawn'
            ]
            if any(pattern in attr.lower() for pattern in method_patterns):
                continue
            
            # 대문자로 시작하는 것들 제외 (클래스명일 가능성)
            if attr[0].isupper():
                continue
            
            # 실제로 속성인지 확인 (callable이 아닌 것)
            try:
                attr_value = getattr(obj, attr)
                if not callable(attr_value):
                    filtered_attrs.append(attr)
            except:
                continue
        
        property_names.extend(filtered_attrs)
        
    except Exception as e:
        print(f"  dir() 기반 속성 추출 실패: {e}")
    
    return property_names


# ===============================================================================
# 고급 Serialization 시스템
# ===============================================================================

class AdvancedUnrealSerializer:
    """
    Unreal Engine 객체를 위한 고급 serializer입니다.
    
    Features:
    - 정확한 타입 감지 (StructBase, ObjectBase, EnumBase)
    - 순환 참조 방지
    - 깊이 제한
    - PythonBPLib 활용
    - 에러 복구
    """
    
    def __init__(self, max_depth: int = 3, enable_debug: bool = True):
        self.max_depth = max_depth
        self.enable_debug = enable_debug
        self.serialized_objects: Set[id] = set()  # 순환 참조 방지
        self.current_depth = 0
        
    def debug_log(self, message: str, indent: int = 0):
        """디버그 로그 출력 (극한 성능 최적화 - 거의 모든 로깅 비활성화)"""
        # 성능을 위해 거의 모든 로깅 스킵
        return  # 모든 디버그 로깅 비활성화
    
    def serialize(self, obj: Any, name: str = "root") -> Any:
        """
        객체를 직렬화합니다.
        
        Args:
            obj: 직렬화할 객체
            name: 객체 이름 (디버깅용)
            
        Returns:
            직렬화된 데이터
        """
        # 성능 최적화: 개별 속성 로그 최소화 (주요 구조체만)
        if (name == "root" or 
            name == "root.settings" or 
            "weighted_blendables" in name.lower()):
            self.debug_log(f"🔍 직렬화 시작: {name}")
        
        # 순환 참조 확인
        obj_id = id(obj)
        if obj_id in self.serialized_objects:
            self.debug_log(f"⚠️ 순환 참조 감지: {name}")
            return f"<circular_reference:{type(obj).__name__}>"
        
            # 깊이 제한 확인 (더 유연하게 처리)
        if self.current_depth >= self.max_depth:
            # PostProcessSettings의 경우 깊이 1레벨 추가 허용
            if "PostProcessSettings" in name or "settings" in name:
                if self.current_depth >= self.max_depth + 1:
                    self.debug_log(f"⚠️ PostProcessSettings 최대 깊이 도달: {name}")
                    return f"<max_depth_reached:{type(obj).__name__}>"
            else:
                self.debug_log(f"⚠️ 최대 깊이 도달: {name}")
                return f"<max_depth_reached:{type(obj).__name__}>"
        
        try:
            # 순환 참조 추적 시작
            self.serialized_objects.add(obj_id)
            self.current_depth += 1
            
            result = self._serialize_object(obj, name)
            
            return result
            
        finally:
            # 순환 참조 추적 정리
            self.serialized_objects.discard(obj_id)
            self.current_depth -= 1
    
    def _serialize_object(self, obj: Any, name: str) -> Any:
        """내부 직렬화 로직"""
        
        # 1. 기본 타입 처리
        if obj is None or isinstance(obj, (bool, int, float, str)):
            return obj
        
        # 2. Unreal 타입 감지
        unreal_type = detect_unreal_type(obj)
        # 주요 객체만 로깅 (성능 최적화)
        if (name == "root" or name == "root.settings" or 
            "weighted_blendables" in name.lower() or 
            unreal_type == "object"):
            self.debug_log(f"📋 타입 감지: {name} -> {unreal_type} ({type(obj).__name__})", 1)
        
        if unreal_type == 'enum':
            return self._serialize_enum(obj, name)
        elif unreal_type == 'struct':
            return self._serialize_struct(obj, name)
        elif unreal_type == 'object':
            return self._serialize_object_full(obj, name)
        elif unreal_type == 'array':
            return self._serialize_array(obj, name)
        else:
            return self._serialize_fallback(obj, name)
    
    def _serialize_enum(self, enum_obj: Any, name: str) -> Dict[str, Any]:
        """Enum 직렬화 (API 문서 기준)"""
            # 기본 정보 먼저 안전하게 추출
        try:
            class_name = type(enum_obj).__name__
            enum_name = str(getattr(enum_obj, 'name', 'Unknown'))
            enum_value = int(getattr(enum_obj, 'value', 0))
            fallback_string = str(enum_obj)
            
            # 추가 메타데이터 수집
            module_name = getattr(type(enum_obj), '__module__', '')
            qualname = getattr(type(enum_obj), '__qualname__', class_name)
            
        except Exception as e:
            self.debug_log(f"❌ Enum 기본 정보 추출 실패 ({name}): {e}", 2)
            return {
                "_unreal_type": "enum",
                "_class_name": "Unknown",
                "_error_details": {
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }
            }        # 기본 enum 데이터 구성 (항상 포함)
        enum_data = {
            "_unreal_type": "enum",
            "_class_name": class_name,
            "_enum_name": enum_name,
            "_enum_value": enum_value
        }
        
        # display_name 안전 처리 (Text 객체 오류 방지)
        enum_data["_display_name"] = enum_name  # 기본값으로 설정
        
        # 안전한 display_name 추출 시도
        try:
            if hasattr(enum_obj, 'get_display_name'):
                display_obj = enum_obj.get_display_name()
                if display_obj:
                    # Text 객체 안전 처리 - 다양한 방법 시도
                    display_str = None
                    
                    # 방법 1: __str__ 메서드 사용
                    try:
                        display_str = str(display_obj)
                    except:
                        pass
                    
                    # 방법 2: get_string() 메서드 시도
                    if not display_str:
                        try:
                            if hasattr(display_obj, 'get_string'):
                                display_str = display_obj.get_string()
                        except:
                            pass
                    
                    # 방법 3: to_string() 메서드 시도 (주의깊게)
                    if not display_str:
                        try:
                            if hasattr(display_obj, 'to_string'):
                                display_str = display_obj.to_string()
                        except:
                            pass
                    
                    # 유효한 display_name이 있으면 저장
                    if display_str and display_str != enum_name and len(display_str) > 0:
                        enum_data["_display_name"] = display_str
        except Exception as e:
            self.debug_log(f"⚠️ Enum display_name 추출 실패 (무시됨): {e}", 3)
        
        # 성능 최적화: Enum 로그 비활성화
        pass  # self.debug_log(f"✅ Enum 직렬화 성공: {class_name}.{enum_name} = {enum_value}", 2)
        return enum_data
    
    def _serialize_struct(self, struct_obj: Any, name: str) -> Dict[str, Any]:
        """Struct 직렬화 (StructBase API 기준)"""
        struct_data = {
            "_unreal_type": "struct",
            "_class_name": type(struct_obj).__name__,
        }
        
        class_name = struct_data["_class_name"]
        
        # 간단한 구조체들 직접 처리 (LinearColor, Vector 등)
        if class_name in ['LinearColor', 'Color']:
            try:
                if hasattr(struct_obj, 'r') and hasattr(struct_obj, 'g') and hasattr(struct_obj, 'b'):
                    struct_data["_direct_values"] = {
                        "r": float(struct_obj.r),
                        "g": float(struct_obj.g), 
                        "b": float(struct_obj.b)
                    }
                    if hasattr(struct_obj, 'a'):
                        struct_data["_direct_values"]["a"] = float(struct_obj.a)
                    # 성능 최적화: LinearColor 로그 비활성화
                    pass  # self.debug_log(f"✅ {class_name} 직접 처리: RGBA({struct_obj.r:.3f}, {struct_obj.g:.3f}, {struct_obj.b:.3f})", 2)
                    return struct_data
            except Exception as e:
                self.debug_log(f"⚠️ {class_name} 직접 처리 실패: {e}", 2)
        
        elif class_name in ['Vector', 'Vector2D', 'Vector4']:
            try:
                if hasattr(struct_obj, 'x') and hasattr(struct_obj, 'y'):
                    struct_data["_direct_values"] = {
                        "x": float(struct_obj.x),
                        "y": float(struct_obj.y)
                    }
                    if hasattr(struct_obj, 'z'):
                        struct_data["_direct_values"]["z"] = float(struct_obj.z)
                    if hasattr(struct_obj, 'w'):
                        struct_data["_direct_values"]["w"] = float(struct_obj.w)
                    
                    coord_str = f"({struct_obj.x:.3f}, {struct_obj.y:.3f}"
                    if hasattr(struct_obj, 'z'):
                        coord_str += f", {struct_obj.z:.3f}"
                    if hasattr(struct_obj, 'w'):
                        coord_str += f", {struct_obj.w:.3f}"
                    coord_str += ")"
                    
                    # 성능 최적화: Vector 로그 비활성화
                    pass  # self.debug_log(f"✅ {class_name} 직접 처리: {coord_str}", 2)
                    return struct_data
            except Exception as e:
                self.debug_log(f"⚠️ {class_name} 직접 처리 실패: {e}", 2)
        
        # 복잡한 구조체들은 기존 방식 사용
        try:
            # 프로퍼티 개별 직렬화 (중요한 데이터만 저장)
            property_names = get_property_names_advanced(struct_obj)
            
            if property_names:
                struct_data["_properties"] = {}
                self.debug_log(f"📝 Struct 프로퍼티: {len(property_names)}개", 2)
                
                processed_props = 0
                max_props = 500 if struct_data["_class_name"] == "PostProcessSettings" else 200
                
                # 전체 처리 모드 활성화
                if len(property_names) > max_props:
                    self.debug_log(f"⚠️ 전체 {len(property_names)}개 속성 중 {max_props}개만 처리합니다.", 2)
                else:
                    max_props = len(property_names)  # 모든 속성 처리
                
                self.debug_log(f"📋 {len(property_names)}개 속성 처리 시작 (최대 {max_props}개)", 2)
                
                for prop_name in property_names[:max_props]:
                    try:
                        # Deprecated 속성들 스킵 (확장된 필터)
                        deprecated_patterns = [
                            'b_override_exposure_offset', 'b_override_eye_', 'exposure_offset', 
                            'eye_adaptation_', 'eye_adaption_', '_deprecated', 'deprecated_',
                            'b_override_light_shaft', 'light_shaft_', 'b_override_iris_',
                            'iris_', 'b_override_depth_of_field_', 'b_override_auto_exposure_'
                        ]
                        
                        # 이름 기반 필터링
                        if any(prop_name.startswith(pattern) for pattern in deprecated_patterns):
                            continue
                        
                        # 추가 필터: 너무 짧거나 숫자로 시작하는 속성
                        if len(prop_name) < 2 or prop_name[0].isdigit():
                            continue
                            
                        if hasattr(struct_obj, 'get_editor_property'):
                            prop_value = struct_obj.get_editor_property(prop_name)
                        else:
                            prop_value = getattr(struct_obj, prop_name)
                        
                        serialized_prop = self.serialize(prop_value, f"{name}.{prop_name}")
                        if serialized_prop is not None:
                            struct_data["_properties"][prop_name] = serialized_prop
                            processed_props += 1
                            
                            # 진행 상황 보고 간격 늘리기 (성능 최적화: 10 → 50)
                            if processed_props % 50 == 0:
                                self.debug_log(f"📋 진행 상황: {processed_props}/{len(property_names)} 속성 처리 완료", 2)
                            
                    except Exception as e:
                        self.debug_log(f"⚠️ 프로퍼티 직렬화 실패 ({prop_name}): {e}", 3)
                        continue
                
                self.debug_log(f"✅ Struct 속성 처리 완료: {processed_props}/{len(property_names)}", 2)
            
            # 특별한 Struct 타입들 처리
            if struct_data["_class_name"] == "WeightedBlendables":
                struct_data.update(self._serialize_weighted_blendables(struct_obj, name))
            elif struct_data["_class_name"] == "WeightedBlendable":
                struct_data.update(self._serialize_weighted_blendable(struct_obj, name))
            
        except Exception as e:
            self.debug_log(f"❌ Struct 직렬화 실패 ({name}): {e}", 2)
            # fallback string 제거됨
            struct_data["_error_details"] = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "class_name": type(struct_obj).__name__
            }
        
        return struct_data
    
    def _serialize_weighted_blendables(self, wb_obj: Any, name: str) -> Dict[str, Any]:
        """WeightedBlendables 특화 직렬화"""
        data = {}
        try:
            if hasattr(wb_obj, 'array'):
                array_length = len(wb_obj.array)
                data["_array_info"] = {
                    "length": array_length,
                    "type": "WeightedBlendable[]"
                }
                
                if array_length > 0:
                    array_items = []
                    max_items = min(50, array_length)  # 최대 50개만 저장
                    
                    for i in range(max_items):
                        try:
                            item = wb_obj.array[i]
                            serialized_item = self.serialize(item, f"{name}.array[{i}]")
                            array_items.append(serialized_item)
                        except Exception as e:
                            array_items.append({"_error": f"아이템 {i} 처리 실패: {e}"})
                    
                    data["_array_items"] = array_items
                    
                    if array_length > max_items:
                        data["_truncated"] = f"처음 {max_items}개만 저장, 총 {array_length}개"
                else:
                    data["_array_items"] = []
                    
                self.debug_log(f"✅ WeightedBlendables 배열: {data['_array_info']['length']}개 (저장: {len(data.get('_array_items', []))}개)", 3)
        except Exception as e:
            self.debug_log(f"❌ WeightedBlendables 배열 직렬화 실패: {e}", 3)
            data["_error"] = str(e)
        
        return data
    
    def _serialize_weighted_blendable(self, wb_obj: Any, name: str) -> Dict[str, Any]:
        """WeightedBlendable 특화 직렬화"""
        data = {}
        try:
            if hasattr(wb_obj, 'weight'):
                data["_weight"] = float(wb_obj.weight)
            if hasattr(wb_obj, 'object') and wb_obj.object:
                data["_object_path"] = str(wb_obj.object.get_path_name())
            self.debug_log(f"✅ WeightedBlendable: weight={data.get('_weight', 'N/A')}", 3)
        except Exception as e:
            self.debug_log(f"❌ WeightedBlendable 직렬화 실패: {e}", 3)
        
        return data
    
    def _serialize_object_full(self, obj: Any, name: str) -> Dict[str, Any]:
        """Object 완전 직렬화 (속성 포함)"""
        try:
            obj_data = {
                "_unreal_type": "object",
                "_class_name": obj.get_class().get_name() if hasattr(obj, 'get_class') else type(obj).__name__,
            }
            
            # 경로 정보 저장 (참조용)
            if hasattr(obj, 'get_path_name'):
                obj_data["_path_name"] = str(obj.get_path_name())
            
            if hasattr(obj, 'get_full_name'):
                obj_data["_full_name"] = str(obj.get_full_name())
            
            if hasattr(obj, 'get_name'):
                obj_data["_name"] = str(obj.get_name())
            
            self.debug_log(f"🏗️ Object 완전 직렬화: {obj_data.get('_name', 'Unknown')}", 2)
            
            # 속성들 직렬화 (가장 중요한 부분!)
            obj_data["_properties"] = {}
            
            # 완전한 속성 감지 (dir() 사용 - PostProcessSettings와 동일한 방법)
            if hasattr(obj, 'get_editor_property'):
                class_name = obj_data.get('_class_name', '')
                
                # dir()을 사용하여 모든 속성을 가져오기 (PostProcessSettings와 동일한 방법)
                try:
                    all_attributes = dir(obj)
                    self.debug_log(f"    📋 {class_name}: {len(all_attributes)}개 속성 전체 처리 중...", 2)
                    
                    # 내부 속성과 메서드 필터링
                    filtered_properties = []
                    for attr in all_attributes:
                        # 언더스코어로 시작하는 내부 속성 제외
                        if not attr.startswith('_'):
                            # 메서드인지 확인 (호출 가능한 객체 제외)
                            try:
                                attr_value = getattr(obj, attr)
                                if not callable(attr_value):
                                    filtered_properties.append(attr)
                            except Exception:
                                # 접근할 수 없는 속성은 get_editor_property로 시도해볼 가치가 있음
                                filtered_properties.append(attr)
                    
                    key_properties = filtered_properties
                    self.debug_log(f"    🔍 필터링 후: {len(key_properties)}개 속성 시도", 2)
                    
                    # 처음 5개와 마지막 5개 표시
                    if key_properties:
                        first_5 = key_properties[:5]
                        last_5 = key_properties[-5:]
                        self.debug_log(f"    🔍 처음 5개: {first_5}", 2)
                        self.debug_log(f"    🔍 마지막 5개: {last_5}", 2)
                        
                except Exception as e:
                    self.debug_log(f"    ⚠️ dir() 속성 감지 실패: {e}", 2)
                    # 실패시 기본 속성만 사용
                    key_properties = ["blend_mode", "shading_model", "material_domain"]
                
                # dir() 방식으로 이미 모든 속성을 가져왔으므로 추가 감지 불필요
                
                # dir() 방식으로 이미 완전한 속성 감지 완료
                
                # 알려진 문제 속성 스킵 리스트 (성능 최적화)
                skip_props = {'on_', 'exclude_for_specific_hlod_levels', 'parameter_group_data', 'physics_volume_changed_delegate'}
                
                for prop_name in key_properties:
                    # 문제 속성 스킵
                    if any(prop_name.startswith(skip) for skip in skip_props):
                        continue
                        
                    # 빠른 속성 접근 (예외 처리 제거로 대폭 성능 향상)
                    if hasattr(obj, 'get_editor_property'):
                        prop_value = obj.get_editor_property(prop_name)
                        if prop_value is not None and self.current_depth < self.max_depth:
                            serialized_prop = self._serialize_object(prop_value, f"{name}.{prop_name}")
                            obj_data["_properties"][prop_name] = serialized_prop
                            # 로깅 빈도 더 감소 (40개마다)
                            if len(obj_data["_properties"]) % 40 == 0:
                                self.debug_log(f"  📈 진행: {len(obj_data['_properties'])}개 완료", 2)
                        continue
            
            self.debug_log(f"✅ Object 완전 직렬화 완료: {len(obj_data['_properties'])}개 속성", 2)
            return obj_data
            
        except Exception as e:
            self.debug_log(f"❌ Object 완전 직렬화 실패 ({name}): {e}", 2)
            # 실패시 참조만 저장
            return self._serialize_object_ref(obj, name)
    
    def _serialize_object_ref(self, obj: Any, name: str) -> Dict[str, Any]:
        """Object 참조 직렬화 (_ObjectBase API 기준)"""
        try:
            obj_data = {
                "_unreal_type": "object",
                "_class_name": obj.get_class().get_name() if hasattr(obj, 'get_class') else type(obj).__name__,
            }
            
            # 경로 정보 저장 (가장 중요)
            if hasattr(obj, 'get_path_name'):
                obj_data["_path_name"] = str(obj.get_path_name())
            
            if hasattr(obj, 'get_full_name'):
                obj_data["_full_name"] = str(obj.get_full_name())
            
            if hasattr(obj, 'get_name'):
                obj_data["_name"] = str(obj.get_name())
            
            self.debug_log(f"✅ Object 참조: {obj_data.get('_path_name', obj_data.get('_name', 'Unknown'))}", 2)
            
            return obj_data
            
        except Exception as e:
            self.debug_log(f"❌ Object 직렬화 실패 ({name}): {e}", 2)
            return {
                "_unreal_type": "object",
                "_class_name": type(obj).__name__,
                # fallback string 제거됨
            }
    
    def _serialize_array(self, array_obj: Any, name: str) -> Dict[str, Any]:
        """배열 직렬화 - 구조화된 정보 포함"""
        try:
            array_length = len(array_obj)
            result_data = {
                "_unreal_type": "array",
                "_length": array_length,
                "_items": []
            }
            
            # 빈 배열 처리
            if array_length == 0:
                self.debug_log(f"✅ 빈 배열 직렬화: {array_length}개", 2)
                return result_data
            
            # 배열 크기에 따른 처리
            max_items = 500 if array_length > 100 else array_length
            
            for i, item in enumerate(array_obj):
                if i >= max_items:
                    result_data["_truncated"] = f"처음 {max_items}개만 저장, 총 {array_length}개"
                    break
                
                serialized_item = self.serialize(item, f"{name}[{i}]")
                result_data["_items"].append(serialized_item)
            
            self.debug_log(f"✅ 배열 직렬화: {len(result_data['_items'])}/{array_length}개 아이템", 2)
            return result_data
            
        except Exception as e:
            self.debug_log(f"❌ 배열 직렬화 실패 ({name}): {e}", 2)
            return {
                "_unreal_type": "array",
                "_error": str(e),
                # fallback string 제거됨
            }
    
    def _serialize_fallback(self, obj: Any, name: str) -> Any:
        """알 수 없는 타입의 fallback 직렬화"""
        try:
            # Vector, Color 등의 간단한 구조체들
            if hasattr(obj, 'x') and hasattr(obj, 'y'):
                data = {"x": float(obj.x), "y": float(obj.y)}
                if hasattr(obj, 'z'):
                    data["z"] = float(obj.z)
                if hasattr(obj, 'w'):
                    data["w"] = float(obj.w)
                return data
            
            if hasattr(obj, 'r') and hasattr(obj, 'g') and hasattr(obj, 'b'):
                data = {"r": float(obj.r), "g": float(obj.g), "b": float(obj.b)}
                if hasattr(obj, 'a'):
                    data["a"] = float(obj.a)
                return data
            
            # 문자열 변환 시도
            str_value = str(obj)
            if len(str_value) < 500:  # 너무 긴 문자열 방지
                return str_value
            else:
                return str_value[:500] + "..."
                
        except Exception as e:
            self.debug_log(f"❌ Fallback 직렬화 실패 ({name}): {e}", 2)
            return f"<serialization_failed: {type(obj).__name__}>"


# ===============================================================================
# 고급 Deserialization 시스템  
# ===============================================================================

class AdvancedUnrealDeserializer:
    """
    Unreal Engine 객체를 위한 고급 deserializer입니다.
    """
    
    def __init__(self, enable_debug: bool = True):
        self.enable_debug = enable_debug
    
    def debug_log(self, message: str, indent: int = 0):
        """디버그 로그 출력 (성능을 위해 비활성화)"""
        return  # 모든 디버그 로깅 비활성화
    
    def _parse_enum_string(self, enum_str: str) -> Any:
        """문자열에서 Enum 파싱 - 강화된 버전"""
        try:
            self.debug_log(f"🔍 _parse_enum_string 시도: {enum_str}", 2)
            
            if enum_str.startswith('<') and ':' in enum_str and '>' in enum_str:
                content = enum_str.strip('<>')
                parts = content.split(': ')
                if len(parts) == 2:
                    enum_part = parts[0]
                    value_part = int(parts[1])
                    
                    if '.' in enum_part:
                        class_name, enum_name = enum_part.split('.', 1)
                        self.debug_log(f"  파싱된 정보: {class_name}.{enum_name} = {value_part}", 3)
                        
                        # 방법 1: 이름으로 복원 시도
                        try:
                            enum_class = getattr(unreal, class_name)
                            restored_enum = getattr(enum_class, enum_name)
                            self.debug_log(f"  ✅ 이름으로 복원 성공: {restored_enum}", 3)
                            return restored_enum
                        except Exception as e1:
                            self.debug_log(f"  ⚠️ 이름 복원 실패: {e1}", 3)
                        
                        # 방법 2: 값으로 복원 시도
                        try:
                            enum_class = getattr(unreal, class_name)
                            for item in enum_class:
                                if int(item.value) == value_part:
                                    self.debug_log(f"  ✅ 값으로 복원 성공: {item}", 3)
                                    return item
                        except Exception as e2:
                            self.debug_log(f"  ⚠️ 값 복원 실패: {e2}", 3)
                        
                        # 방법 3: 직접 생성 시도
                        try:
                            enum_class = getattr(unreal, class_name)
                            restored_enum = enum_class(value_part)
                            self.debug_log(f"  ✅ 직접 생성 성공: {restored_enum}", 3)
                            return restored_enum
                        except Exception as e3:
                            self.debug_log(f"  ⚠️ 직접 생성 실패: {e3}", 3)
            
            self.debug_log(f"  ❌ 파싱 실패", 3)
            return None
        except Exception as e:
            self.debug_log(f"  ❌ _parse_enum_string 예외: {e}", 3)
            return None
    
    def deserialize(self, data: Any, name: str = "root") -> Any:
        """
        직렬화된 데이터를 복원합니다.
        
        Args:
            data: 직렬화된 데이터
            name: 데이터 이름 (디버깅용)
            
        Returns:
            복원된 객체
        """
        self.debug_log(f"🔄 역직렬화 시작: {name}")
        
        try:
            return self._deserialize_data(data, name)
        except Exception as e:
            self.debug_log(f"❌ 역직렬화 실패 ({name}): {e}")
            return data  # 실패시 원본 데이터 반환
    
    def _deserialize_data(self, data: Any, name: str) -> Any:
        """내부 역직렬화 로직"""
        
        # 기본 타입
        if data is None or isinstance(data, (bool, int, float, str)):
            return data
        
        # 딩셔너리 타입들
        if isinstance(data, dict):
            unreal_type = data.get("_unreal_type")
            
            if unreal_type == "enum":
                return self._deserialize_enum(data, name)
            elif unreal_type == "struct":
                return self._deserialize_struct(data, name)
            elif unreal_type == "object":
                return self._deserialize_object_ref(data, name)
            else:
                # 일반 딕셔너리나 Vector/Color 구조체들
                return self._deserialize_simple_struct(data, name)
        
        # 문자열 Enum 감지 및 복원 시도 (fallback 처리)
        elif isinstance(data, str):
            # "<EnumClass.ENUM_VALUE: value>" 형식 감지
            if data.startswith('<') and ':' in data and '>' in data:
                try:
                    # "<BlendMode.BLEND_OPAQUE: 0>" 파싱
                    content = data.strip('<>')
                    parts = content.split(': ')
                    if len(parts) == 2:
                        enum_part = parts[0]
                        value_part = int(parts[1])
                        if '.' in enum_part:
                            class_name, enum_name = enum_part.split('.', 1)
                            
                            # 3단계 복원 시도
                            try:
                                enum_class = getattr(unreal, class_name)
                                restored_enum = getattr(enum_class, enum_name)
                                self.debug_log(f"✅ 문자열에서 Enum 복원 (이름): {class_name}.{enum_name}", 1)
                                return restored_enum
                            except Exception:
                                try:
                                    enum_class = getattr(unreal, class_name)
                                    for item in enum_class:
                                        if int(item.value) == value_part:
                                            self.debug_log(f"✅ 문자열에서 Enum 복원 (값): {class_name}({value_part})", 1)
                                            return item
                                except Exception:
                                    pass
                except Exception as e:
                    self.debug_log(f"⚠️ 문자열 Enum 파싱 실패: {e}", 2)
            return data
        
        # 리스트 타입
        elif isinstance(data, list):
            return [self.deserialize(item, f"{name}[{i}]") for i, item in enumerate(data)]
        
        return data
    
    def _deserialize_enum(self, enum_data: Dict[str, Any], name: str) -> Any:
        """Enum 역직렬화"""
        try:
            class_name = enum_data.get("_class_name", "Unknown")
            enum_name = enum_data.get("_enum_name")
            enum_value = enum_data.get("_enum_value")
            
            # _enum_name이 없는 경우 fallback_string에서 파싱 시도
            if not enum_name or enum_value is None:
                fallback_str = enum_data.get("_fallback_string", "")
                if fallback_str:
                    try:
                        # 여러 형식 지원: "<BlendMode.BLEND_OPAQUE: 0>", "BlendMode.BLEND_OPAQUE", "BLEND_OPAQUE" 등
                        if '<' in fallback_str and ':' in fallback_str:
                            # "<BlendMode.BLEND_OPAQUE: 0>" 파싱
                            parts = fallback_str.strip('<>').split(': ')
                            if len(parts) == 2:
                                enum_part = parts[0]
                                value_part = int(parts[1])
                                if '.' in enum_part:
                                    parsed_class, parsed_name = enum_part.split('.', 1)
                                    class_name = parsed_class
                                    enum_name = parsed_name
                                    enum_value = value_part
                                    self.debug_log(f"📝 <Class.Name: Value> 파싱: {class_name}.{enum_name} = {enum_value}", 2)
                        elif '.' in fallback_str:
                            # "BlendMode.BLEND_OPAQUE" 파싱
                            if fallback_str.count('.') == 1:
                                parsed_class, parsed_name = fallback_str.split('.', 1)
                                class_name = parsed_class
                                enum_name = parsed_name
                                self.debug_log(f"📝 Class.Name 파싱: {class_name}.{enum_name}", 2)
                        else:
                            # "BLEND_OPAQUE" - enum_name만 있는 경우
                            if fallback_str.isupper() and '_' in fallback_str:
                                enum_name = fallback_str
                                self.debug_log(f"📝 Name 파싱: {enum_name}", 2)
                    except Exception as e:
                        self.debug_log(f"⚠️ fallback 파싱 실패: {e}", 2)
            
            # 여전히 정보가 부족하면 실패
            if not enum_name or enum_value is None:
                self.debug_log(f"❌ Enum 복원 정보 부족: name={enum_name}, value={enum_value}", 1)
                # 마지막 시도: _parse_enum_string으로 문자열 파싱
                fallback_str = enum_data.get("_fallback_string", "")
                if fallback_str:
                    parsed_enum = self._parse_enum_string(fallback_str)
                    if parsed_enum:
                        self.debug_log(f"✅ 정보 부족한 상황에서 _parse_enum_string으로 복원 성공", 1)
                        return parsed_enum
                    else:
                        self.debug_log(f"❌ _parse_enum_string 파싱 실패", 1)
                # 정말 실패하면 문자열 반환
                return fallback_str if fallback_str else str(enum_data)
            
            # 방법 1: unreal.ClassName.enum_name 방식으로 복원
            try:
                enum_class = getattr(unreal, class_name)
                restored_enum = getattr(enum_class, enum_name)
                self.debug_log(f"✅ Enum 복원 (이름): {class_name}.{enum_name}", 1)
                return restored_enum
            except AttributeError as e:
                self.debug_log(f"⚠️ Enum 클래스 또는 이름 없음: {e}", 2)
            except Exception as e:
                self.debug_log(f"⚠️ Enum 이름 복원 실패: {e}", 2)
            
            # 방법 2: 값으로 복원 시도
            try:
                enum_class = getattr(unreal, class_name)
                for item in enum_class:
                    if hasattr(item, 'value') and int(item.value) == enum_value:
                        self.debug_log(f"✅ Enum 복원 (값): {class_name}({enum_value}) -> {item.name}", 1)
                        return item
                self.debug_log(f"⚠️ 값 {enum_value}에 해당하는 Enum 항목 없음", 2)
            except Exception as e:
                self.debug_log(f"⚠️ Enum 값 복원 실패: {e}", 2)
            
            # 방법 3: 직접 생성
            try:
                enum_class = getattr(unreal, class_name)
                restored_enum = enum_class(enum_value)
                self.debug_log(f"✅ Enum 복원 (직접): {class_name}({enum_value})", 1)
                return restored_enum
            except Exception as e:
                self.debug_log(f"⚠️ Enum 직접 생성 실패: {e}", 2)
            
            # 방법 4: 다른 가능한 클래스명들 시도 (접두사 추가 등)
            if enum_value is not None:
                alternative_classes = [f"E{class_name}", f"{class_name}s", f"Unreal{class_name}"]
                for alt_class in alternative_classes:
                    try:
                        enum_class = getattr(unreal, alt_class)
                        if enum_name:
                            restored_enum = getattr(enum_class, enum_name)
                            self.debug_log(f"✅ Enum 복원 (대체 클래스): {alt_class}.{enum_name}", 1)
                            return restored_enum
                        else:
                            # 값으로 시도
                            for item in enum_class:
                                if hasattr(item, 'value') and int(item.value) == enum_value:
                                    self.debug_log(f"✅ Enum 복원 (대체+값): {alt_class}({enum_value})", 1)
                                    return item
                    except Exception:
                        continue
            
            # fallback_string에서 복원 시도
            # if "_fallback_string" in enum_data:  # 제거됨
            #     fallback_str = enum_data["_fallback_string"]
                if fallback_str.startswith('<') and ':' in fallback_str and '>' in fallback_str:
                    try:
                        enum_part = fallback_str.split(':')[0].strip('<').strip()
                        if '.' in enum_part:
                            fb_class_name, fb_enum_name = enum_part.split('.', 1)
                            enum_class = getattr(unreal, fb_class_name)
                            restored_enum = getattr(enum_class, fb_enum_name)
                            self.debug_log(f"✅ Enum fallback 복원: {fb_class_name}.{fb_enum_name}", 1)
                            return restored_enum
                    except Exception:
                        pass
            
            self.debug_log(f"⚠️ Enum 복원 실패, _parse_enum_string으로 마지막 시도: {class_name}", 1)
            # 마지막 시도: _parse_enum_string 사용
            # _fallback_string 처리 제거됨
            if False:  # 비활성화
                if False:
                    self.debug_log(f"✅ _parse_enum_string으로 복원 성공", 1)
                    return parsed_result
                else:
                    # 정말 마지막 수단으로 문자열 반환
                    self.debug_log(f"❌ 모든 Enum 복원 시도 실패, 문자열 반환", 1)
                    return str(enum_value)  # fallback string 대신 enum_value 사용
            return str(enum_data)
            
        except Exception as e:
            self.debug_log(f"❌ Enum 복원 실패 ({name}): {e}", 1)
            # 예외 발생 시에도 _parse_enum_string 시도
            # _fallback_string 처리 제거됨
            if False:  # 비활성화
                parsed_result = None
                if parsed_result:
                    self.debug_log(f"✅ 예외 상황에서 _parse_enum_string으로 복원 성공", 1)
                    return parsed_result
                return enum_data["_fallback_string"]
            return str(enum_data)
    
    def _deserialize_struct(self, struct_data: Dict[str, Any], name: str) -> Any:
        """Struct 역직렬화 (StructBase API 기준)"""
        try:
            class_name = struct_data["_class_name"]
            
            # 직접 값이 있는 경우 우선 처리 (간단한 구조체들)
            if "_direct_values" in struct_data:
                direct_vals = struct_data["_direct_values"]
                
                # LinearColor/Color 복원
                if class_name in ['LinearColor', 'Color']:
                    if "r" in direct_vals and "g" in direct_vals and "b" in direct_vals:
                        a_val = direct_vals.get("a", 1.0)
                        restored = unreal.LinearColor(direct_vals["r"], direct_vals["g"], direct_vals["b"], a_val)
                        self.debug_log(f"✅ {class_name} 직접 복원: RGBA({direct_vals['r']:.3f}, {direct_vals['g']:.3f}, {direct_vals['b']:.3f}, {a_val:.3f})", 1)
                        return restored
                
                # Vector 타입 복원
                elif class_name in ['Vector', 'Vector2D', 'Vector4']:
                    if "x" in direct_vals and "y" in direct_vals:
                        if class_name == 'Vector' and "z" in direct_vals:
                            restored = unreal.Vector(direct_vals["x"], direct_vals["y"], direct_vals["z"])
                            self.debug_log(f"✅ Vector 직접 복원: ({direct_vals['x']:.3f}, {direct_vals['y']:.3f}, {direct_vals['z']:.3f})", 1)
                            return restored
                        elif class_name == 'Vector4' and "z" in direct_vals and "w" in direct_vals:
                            restored = unreal.Vector4(direct_vals["x"], direct_vals["y"], direct_vals["z"], direct_vals["w"])
                            self.debug_log(f"✅ Vector4 직접 복원: ({direct_vals['x']:.3f}, {direct_vals['y']:.3f}, {direct_vals['z']:.3f}, {direct_vals['w']:.3f})", 1)
                            return restored
                        else:  # Vector2D
                            restored = unreal.Vector2D(direct_vals["x"], direct_vals["y"])
                            self.debug_log(f"✅ Vector2D 직접 복원: ({direct_vals['x']:.3f}, {direct_vals['y']:.3f})", 1)
                            return restored
            
            # unreal.ClassName으로 새 인스턴스 생성 (복잡한 구조체들)
            struct_class = getattr(unreal, class_name)
            new_struct = struct_class()
            
            self.debug_log(f"🏗️ Struct 생성: {class_name}", 1)
            
            # 프로퍼티별 복원 (중요한 데이터만 복원)
            if "_properties" in struct_data:
                for prop_name, prop_data in struct_data["_properties"].items():
                    try:
                        restored_value = self.deserialize(prop_data, f"{name}.{prop_name}")
                        
                        if hasattr(new_struct, 'set_editor_property'):
                            new_struct.set_editor_property(prop_name, restored_value)
                        else:
                            setattr(new_struct, prop_name, restored_value)
                            
                    except Exception as e:
                        self.debug_log(f"⚠️ 프로퍼티 복원 실패 ({prop_name}): {e}", 2)
                        continue
            
            # 특별한 Struct 타입들 처리
            if class_name == "WeightedBlendables":
                self._restore_weighted_blendables(new_struct, struct_data, name)
            elif class_name == "WeightedBlendable":
                self._restore_weighted_blendable(new_struct, struct_data, name)
            
            self.debug_log(f"✅ Struct 복원 완료: {class_name}", 1)
            return new_struct
            
        except Exception as e:
            self.debug_log(f"❌ Struct 복원 실패 ({name}): {e}", 1)
            return str(struct_data)
    
    def _restore_weighted_blendables(self, wb_struct: Any, data: Dict[str, Any], name: str):
        """WeightedBlendables 특화 복원"""
        try:
            if "_array_items" in data and hasattr(wb_struct, 'array'):
                restored_items = []
                for i, item_data in enumerate(data["_array_items"]):
                    restored_item = self.deserialize(item_data, f"{name}.array[{i}]")
                    restored_items.append(restored_item)
                
                wb_struct.array = restored_items
                self.debug_log(f"✅ WeightedBlendables 배열 복원: {len(restored_items)}개", 2)
        except Exception as e:
            self.debug_log(f"❌ WeightedBlendables 배열 복원 실패: {e}", 2)
    
    def _restore_weighted_blendable(self, wb_struct: Any, data: Dict[str, Any], name: str):
        """WeightedBlendable 특화 복원"""
        try:
            if "_weight" in data and hasattr(wb_struct, 'weight'):
                wb_struct.weight = float(data["_weight"])
            
            if "_object_path" in data and hasattr(wb_struct, 'object'):
                try:
                    loaded_obj = unreal.load_asset(data["_object_path"])
                    if loaded_obj:
                        wb_struct.object = loaded_obj
                except Exception as e:
                    self.debug_log(f"⚠️ Asset 로드 실패 ({data['_object_path']}): {e}", 3)
            
            self.debug_log(f"✅ WeightedBlendable 복원: weight={data.get('_weight', 'N/A')}", 2)
        except Exception as e:
            self.debug_log(f"❌ WeightedBlendable 복원 실패: {e}", 2)
    
    def _deserialize_object_ref(self, obj_data: Dict[str, Any], name: str) -> Any:
        """Object 참조 역직렬화"""
        try:
            # Asset 경로로 로딩 시도
            if "_path_name" in obj_data:
                loaded_obj = unreal.load_asset(obj_data["_path_name"])
                if loaded_obj:
                    self.debug_log(f"✅ Asset 로딩 성공: {obj_data['_path_name']}", 1)
                    return loaded_obj
            
            self.debug_log(f"⚠️ Object 로딩 실패, 참조 정보 반환", 1)
            return obj_data
            
        except Exception as e:
            self.debug_log(f"❌ Object 역직렬화 실패 ({name}): {e}", 1)
            return obj_data
    
    def _deserialize_simple_struct(self, data: Dict[str, Any], name: str) -> Any:
        """간단한 구조체 (Vector, Color 등) 역직렬화"""
        # Vector 타입들
        if "x" in data and "y" in data:
            if "z" in data:
                if "w" in data:
                    return unreal.Vector4(data["x"], data["y"], data["z"], data["w"])
                else:
                    return unreal.Vector(data["x"], data["y"], data["z"])
            else:
                return unreal.Vector2D(data["x"], data["y"])
        
        # Color 타입들  
        if "r" in data and "g" in data and "b" in data:
            if "a" in data:
                return unreal.LinearColor(data["r"], data["g"], data["b"], data["a"])
            else:
                return unreal.LinearColor(data["r"], data["g"], data["b"], 1.0)
        
        # 일반 딕셔너리는 그대로 반환
        return data


# ===============================================================================
# 편의 함수들
# ===============================================================================

def serialize_object_advanced(obj: Any, max_depth: int = 5, enable_debug: bool = True) -> Dict[str, Any]:
    """
    Unreal 객체를 고급 방식으로 직렬화합니다.
    
    Args:
        obj: 직렬화할 객체
        max_depth: 최대 중첩 깊이
        enable_debug: 디버그 출력 여부
        
    Returns:
        Dict[str, Any]: 직렬화된 데이터
    """
    serializer = AdvancedUnrealSerializer(max_depth=max_depth, enable_debug=enable_debug)
    
    return {
        "_metadata": {
            "serializer_version": "2.1",
            "object_type": type(obj).__name__,
            "unreal_type": detect_unreal_type(obj),
            "timestamp": "2025-11-15",
            "max_depth": max_depth,
            "debug_enabled": enable_debug,
            "object_id": id(obj),
            "module": getattr(type(obj), '__module__', 'unknown')
        },
        "_content": serializer.serialize(obj, "root")
    }


def deserialize_object_advanced(data: Dict[str, Any], enable_debug: bool = True) -> Any:
    """
    고급 방식으로 직렬화된 데이터를 복원합니다.
    
    Args:
        data: 직렬화된 데이터
        enable_debug: 디버그 출력 여부
        
    Returns:
        Any: 복원된 객체
    """
    deserializer = AdvancedUnrealDeserializer(enable_debug=enable_debug)
    
    if "_content" in data:
        return deserializer.deserialize(data["_content"], "root")
    else:
        # 구버전 호환성
        return deserializer.deserialize(data, "root")


def serialize_postprocess_settings_advanced(pp_settings: unreal.PostProcessSettings) -> Dict[str, Any]:
    """
    PostProcessSettings를 고급 방식으로 직렬화합니다.
    
    Args:
        pp_settings: 직렬화할 PostProcessSettings
        
    Returns:
        Dict[str, Any]: 직렬화된 데이터
    """
    print("🚀 고급 PostProcessSettings 직렬화 시작...")
    
    serialized_data = serialize_object_advanced(pp_settings, max_depth=2, enable_debug=True)
    
    # 메타데이터 추가
    serialized_data["_metadata"]["specialization"] = "PostProcessSettings"
    
    print(f"✅ 고급 직렬화 완료!")
    return serialized_data


def deserialize_postprocess_settings_advanced(target_settings: unreal.PostProcessSettings, data: Dict[str, Any]) -> bool:
    """
    고급 방식으로 PostProcessSettings를 복원합니다.
    
    Args:
        target_settings: 대상 PostProcessSettings
        data: 직렬화된 데이터
        
    Returns:
        bool: 성공 여부
    """
    print("🔄 고급 PostProcessSettings 역직렬화 시작...")
    
    try:
        restored_settings = deserialize_object_advanced(data, enable_debug=True)
        
        if isinstance(restored_settings, unreal.PostProcessSettings):
            # 복원된 설정을 target_settings에 복사
            # assign() 메서드 사용 (StructBase API)
            target_settings.assign(restored_settings)
            print("✅ 고급 역직렬화 완료!")
            return True
        else:
            print(f"❌ 복원된 객체가 PostProcessSettings가 아닙니다: {type(restored_settings)}")
            return False
            
    except Exception as e:
        print(f"❌ 고급 역직렬화 실패: {e}")
        return False


# ===============================================================================
# 테스트 함수들
# ===============================================================================

def test_complete_no_limits():
    """
    제한 없이 모든 속성을 완벽하게 테스트하는 함수
    
    사용법:
    from advanced_serialization import test_complete_no_limits
    test_complete_no_limits()
    """
    print("🔥 제한 없는 완벽한 Volume 직렬화 테스트")
    print("=" * 60)
    print("⚠️ 주의: 모든 속성을 처리하므로 시간이 오래 걸릴 수 있습니다.")
    
    # 선택된 액터 가져오기
    try:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            selected_actors = unreal.EditorLevelLibrary.get_selected_level_actors()
    except Exception:
        selected_actors = unreal.EditorLevelLibrary.get_selected_level_actors()
    
    if not selected_actors:
        print("⚠️ PostProcessVolume을 선택하고 다시 실행하세요.")
        return
    
    processed_count = 0
    
    for actor in selected_actors:
        if isinstance(actor, unreal.PostProcessVolume):
            processed_count += 1
            print(f"\n🎯 완벽 처리 #{processed_count}: {actor.get_name()}")
            
            import time
            start_time = time.time()
            
            # 제한 없는 직렬화기 생성
            serializer = AdvancedUnrealSerializer(max_depth=15, enable_debug=True)
            
            # 내부 제한 임시 제거
            original_method = serializer._serialize_struct
            
            def unlimited_serialize_struct(self, struct_obj, name):
                """제한 없는 Struct 직렬화"""
                struct_data = {
                    "_unreal_type": "struct", 
                    "_class_name": type(struct_obj).__name__,
                }
                
                class_name = struct_data["_class_name"]
                
                # 간단한 구조체는 그대로 처리
                if class_name in ['LinearColor', 'Color', 'Vector', 'Vector2D', 'Vector4']:
                    return original_method(struct_obj, name)
                
                try:
                    # 모든 속성 추출 (제한 없이, 중요한 데이터만)
                    property_names = get_property_names_advanced(struct_obj)
                    
                    if property_names:
                        struct_data["_properties"] = {}
                        processed_props = 0
                        
                        print(f"📋 {class_name}: {len(property_names)}개 속성 전체 처리 중...")
                        
                        # 처음 몇 개와 마지막 몇 개 속성명 출력해서 확인
                        if len(property_names) >= 10:
                            print(f"  🔍 처음 5개: {property_names[:5]}")
                            print(f"  🔍 마지막 5개: {property_names[-5:]}")
                        else:
                            print(f"  🔍 전체 속성: {property_names}")
                        
                        failed_props = []  # 실패한 속성 추적
                        skipped_props = []  # 건너뛴 속성 추적
                        
                        for prop_name in property_names:  # 제한 제거!
                            try:
                                if prop_name.startswith('_') or len(prop_name) < 2:
                                    skipped_props.append(f"{prop_name} (이름 조건)")
                                    continue
                                
                                if hasattr(struct_obj, 'get_editor_property'):
                                    prop_value = struct_obj.get_editor_property(prop_name)
                                else:
                                    prop_value = getattr(struct_obj, prop_name)
                                
                                if self.current_depth < self.max_depth - 1:
                                    serialized_prop = self.serialize(prop_value, f"{name}.{prop_name}")
                                else:
                                    serialized_prop = str(prop_value)
                                
                                # None 값도 유효한 데이터로 처리
                                struct_data["_properties"][prop_name] = serialized_prop
                                processed_props += 1
                                
                                # 진행률 표시 간격 늘리기 (성능 최적화: 50 → 100)  
                                if processed_props % 100 == 0:
                                    print(f"  📊 진행: {processed_props}개 완료")
                                        
                            except Exception as e:
                                failed_props.append((prop_name, str(e)))
                                continue
                        
                        print(f"✅ {class_name} 완료: {processed_props}/{len(property_names)}개 속성")
                        
                        # 상세한 분석 보고
                        total_found = len(property_names)
                        total_skipped = len(skipped_props)  
                        total_failed = len(failed_props)
                        total_processed = processed_props
                        
                        print(f"📊 상세 분석:")
                        print(f"  🔍 총 발견: {total_found}개")
                        print(f"  ⏭️ 건너뛴: {total_skipped}개 (이름 조건)")
                        print(f"  ❌ 실패: {total_failed}개")
                        print(f"  ✅ 성공: {total_processed}개")
                        
                        # 건너뛴 속성들 일부 보고 (이름이 _ 로 시작하거나 길이가 짧은 것들)
                        if skipped_props and len(skipped_props) <= 15:
                            print(f"⏭️ 건너뛴 속성들: {skipped_props}")
                        elif skipped_props:
                            print(f"⏭️ 건너뛴 속성 예시: {skipped_props[:10]} ... 외 {len(skipped_props) - 10}개")
                        
                        # 실패한 속성들 보고
                        if failed_props:
                            print(f"⚠️ 실패한 속성들:")
                            for prop_name, error in failed_props[:10]:  # 처음 10개만 표시
                                print(f"  ❌ {prop_name}: {error}")
                            if len(failed_props) > 10:
                                print(f"  ... 외 {len(failed_props) - 10}개 더")
                    
                    return struct_data
                    
                except Exception as e:
                    print(f"❌ {class_name} 처리 실패: {e}")
                    # 객체 문자열 표현 제거 (불필요함)
                    return struct_data
            
            # 메서드 교체
            import types
            serializer._serialize_struct = types.MethodType(unlimited_serialize_struct, serializer)
            
            try:
                # 완벽한 직렬화 실행
                print("🚀 완벽한 직렬화 시작...")
                serialized_content = serializer.serialize(actor, "root")
                
                volume_data = {
                    "_metadata": {
                        "serializer_version": "2.1-unlimited",
                        "object_type": type(actor).__name__,
                        "timestamp": "2025-11-15",
                        "max_depth": 15,
                        "unlimited_mode": True
                    },
                    "_content": serialized_content
                }
                
                end_time = time.time()
                process_time = end_time - start_time
                
                # 결과 분석
                content = volume_data.get("_content", {})
                if isinstance(content, dict):
                    properties = content.get("_properties", {})
                    settings_data = properties.get("settings", {})
                    
                    print(f"\n🏆 완벽 처리 결과:")
                    print(f"  ⏱️ 처리 시간: {process_time:.2f}초")
                    print(f"  📊 Volume 속성: {len(properties)}개")
                    
                    if isinstance(settings_data, dict):
                        settings_props = settings_data.get("_properties", {})
                        print(f"  🎨 PostProcessSettings: {len(settings_props)}개")
                        
                        # 전체 카테고리 분석
                        categories = {}
                        for prop in settings_props.keys():
                            if 'bloom' in prop.lower():
                                categories.setdefault('Bloom', []).append(prop)
                            elif 'exposure' in prop.lower():
                                categories.setdefault('Exposure', []).append(prop)
                            elif 'color' in prop.lower():
                                categories.setdefault('Color', []).append(prop)
                            elif 'depth' in prop.lower():
                                categories.setdefault('Depth', []).append(prop)
                            elif 'motion' in prop.lower():
                                categories.setdefault('Motion', []).append(prop)
                            else:
                                categories.setdefault('기타', []).append(prop)
                        
                        for cat, props in categories.items():
                            print(f"    - {cat}: {len(props)}개")
                
                # JSON 저장
                import json, os
                json_string = json.dumps(volume_data, indent=2, ensure_ascii=False, default=str)
                
                safe_name = actor.get_name().replace(':', '_').replace('/', '_')
                filename = f"unlimited_volume_{safe_name}.json"
                # 현재 Python 폴더에 저장하여 쉽게 찾을 수 있도록 함
                current_dir = os.path.dirname(os.path.abspath(__file__))
                save_path = os.path.join(current_dir, filename)
                
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(json_string)
                
                print(f"\n🎉 완벽 처리 성공!")
                print(f"💾 저장: {save_path}")
                print(f"📏 크기: {len(json_string):,} 문자")
                print(f"⏱️ 시간: {process_time:.2f}초")
                
            except Exception as e:
                print(f"❌ 완벽 처리 실패: {e}")
                import traceback
                traceback.print_exc()
    
    if processed_count == 0:
        print("⚠️ 선택된 PostProcessVolume이 없습니다.")
    else:
        print(f"\n🏆 완벽 처리 완료! 총 {processed_count}개 Volume")








