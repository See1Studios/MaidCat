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
        self.max_depth = 100  # 실질적으로 무제한
        
    def debug_log(self, message: str, level: int = 1):
        """디버그 로깅 (극한 성능 최적화)"""
        return  # 모든 디버그 로깅 비활성화
    
    def can_serialize(self, obj: Any) -> bool:
        """이 직렬화기가 해당 객체를 처리할 수 있는지 확인"""
        return False
    
    def serialize(self, obj: Any, name: str = "root") -> Dict[str, Any]:
        """객체를 직렬화"""
        raise NotImplementedError


# ===============================================================================
# 유틸리티 함수들
# ===============================================================================

def get_property_names_advanced(obj: Any) -> List[str]:
    """
    객체의 프로퍼티 이름을 UCLASS/USTRUCT별로 최적화된 방법으로 추출합니다.
    
    UCLASS: PythonBPLib.get_all_property_names() 사용 (get_class() 있음)
    USTRUCT: dir() + static_struct() 리플렉션 사용 (bp_lib 지원 안됨)
    
    Args:
        obj: 분석할 객체 (UCLASS 또는 USTRUCT)
        
    Returns:
        List[str]: 프로퍼티 이름 목록
    """
    property_names = []
    
    # 객체 타입 확인: UCLASS vs USTRUCT
    obj_type = type(obj).__name__
    is_uclass = hasattr(obj, 'get_class')
    is_ustruct = hasattr(obj, 'static_struct') and not is_uclass
    
    # 방법 1: PythonBPLib.get_all_property_names() - UCLASS에만 효과적
    # USTRUCT는 지원하지 않음! (get_class()가 있는 객체만 지원)
    if hasattr(obj, 'get_class'):
        try:
            import unreal
            if hasattr(unreal, 'PythonBPLib'):
                # UCLASS 객체의 클래스에 PythonBPLib 적용
                obj_class = obj.get_class()
                names = unreal.PythonBPLib.get_all_property_names(obj_class)
                if names:
                    for name in names:
                        try:
                            obj.get_editor_property(str(name))
                            property_names.append(str(name))
                        except:
                            pass
                    
                    # UCLASS에서 속성을 찾았다면 반환
                    if property_names:
                        return property_names
        except Exception:
            pass
        
        # 방법 1-2: bp_lib wrapper 시도 (UCLASS 백업)
        try:
            obj_class = obj.get_class()
            names = bp_lib.get_all_property_names(obj_class)
            if names:
                property_names.extend([str(name) for name in names])
                # bp_lib로 UCLASS 속성 발견됨
                return property_names
        except Exception:
            pass
    
    # 방법 2: dir() + 간단한 필터링 - USTRUCT 전용 (bp_lib 지원 안됨)
    # USTRUCT는 PythonBPLib가 지원하지 않으므로 dir() 사용
    if hasattr(obj, 'static_struct') and not hasattr(obj, 'get_class'):
        try:
            all_attrs = dir(obj)
            # dir() 결과에서 callable이 아닌 속성들만 추출
            for attr in all_attrs:
                # 기본적인 필터링만
                if attr.startswith('_') or len(attr) < 2:
                    continue
                
                # callable 제외
                try:
                    attr_value = getattr(obj, attr)
                    if not callable(attr_value):
                        property_names.append(attr)
                except:
                    continue
            
        except Exception:
            pass
    
    # 방법 3: 구조체의 경우 static_struct()를 통해 실제 속성 목록 가져오기
    if hasattr(obj, 'static_struct') and hasattr(obj, 'get_editor_property') and len(property_names) < 5:
        try:
            struct_class = obj.static_struct()

            # 방법 3-2: 일반적인 구조체 클래스 속성 탐색
            if not property_names:
                try:
                    # UE 구조체 클래스의 속성 정보를 가져오는 다른 방법들 시도
                    if hasattr(struct_class, 'get_struct_properties') or hasattr(struct_class, 'get_properties'):
                        for method_name in ['get_struct_properties', 'get_properties', 'get_all_properties']:
                            try:
                                method = getattr(struct_class, method_name, None)
                                if method and callable(method):
                                    props = method()
                                    if props:
                                        for prop in props:
                                            prop_name = str(prop.get_name() if hasattr(prop, 'get_name') else prop)
                                            if prop_name and not prop_name.startswith('_'):
                                                try:
                                                    obj.get_editor_property(prop_name)
                                                    property_names.append(prop_name)
                                                except:
                                                    pass
                                        break
                            except:
                                continue
                    
                    # 위 방법이 실패하면 리플렉션을 통한 속성 탐색
                    if not property_names and hasattr(unreal, 'SystemLibrary'):
                        try:
                            # USTRUCT의 경우 SystemLibrary.get_object_property_names 사용
                            # (링크 참조: C++에서 TFieldIterator<UProperty> 방식과 유사)
                            reflection_data = unreal.SystemLibrary.get_object_property_names(struct_class)
                            if reflection_data:
                                for prop_name in reflection_data:
                                    try:
                                        obj.get_editor_property(str(prop_name))
                                        property_names.append(str(prop_name))
                                    except:
                                        pass
                        except:
                            pass
                    
                    # USTRUCT 전용: 실제로는 이런 함수가 존재하지 않음!
                    # TODO: MaidCat의 PythonBPLib에 USTRUCT용 함수 추가 필요:
                    # - get_all_struct_property_names(UScriptStruct* StructClass)
                    # - C++ 구현: TFieldIterator<FProperty>(StructClass) 방식
                    if not property_names:
                        try:
                            # 방법 A: MaidCat에 USTRUCT 전용 함수 추가 (현재 존재하지 않음)
                            # BLUEPRINT 함수로 구현 필요: 
                            # UFUNCTION(BlueprintCallable) static TArray<FString> GetAllStructPropertyNames(UScriptStruct* StructClass)
                            if hasattr(unreal, 'PythonBPLib') and hasattr(unreal.PythonBPLib, 'get_all_struct_property_names'):
                                struct_props = unreal.PythonBPLib.get_all_struct_property_names(struct_class)
                                if struct_props:
                                    for prop_name in struct_props:
                                        try:
                                            obj.get_editor_property(str(prop_name))
                                            property_names.append(str(prop_name))
                                        except:
                                            pass
                            else:
                                print(f"⚠️ USTRUCT 속성 발견 함수가 없습니다: get_all_struct_property_names() 구현 필요")
                        except:
                            pass
                            
                except Exception:
                    pass
                        
        except Exception:
            pass
    
    return property_names


# ===============================================================================
# 타입별 직렬화기들
# ===============================================================================

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
        """USTRUCT 객체인지 확인 (UCLASS와 구분)"""
        obj_type_str = str(type(obj))
        obj_class_name = obj.__class__.__name__
        
        # USTRUCT 구분 방법:
        # 1. static_struct() 있음 (USTRUCT 전용)
        # 2. get_class() 없음 (UCLASS와 구분)
        # 3. 'Struct' 문자열 포함
        struct_indicators = [
            hasattr(obj, 'static_struct'),  # USTRUCT만 가짐
            'Struct' in obj_type_str,
            (hasattr(obj, 'get_editor_property_names') and not hasattr(obj, 'get_class'))  # UCLASS 제외
        ]
        
        # UCLASS는 명시적으로 제외 (get_class 있으면 UCLASS)
        is_uclass = hasattr(obj, 'get_class')
        
        result = any(struct_indicators) and not is_uclass
        return result
    
    def serialize(self, obj: Any, name: str = "root") -> Dict[str, Any]:
        """Struct 객체 직렬화"""
        class_name = getattr(obj.__class__, '__name__', 'UnknownStruct')
        
        struct_data = {
            "_unreal_type": "struct",
            "_class_name": class_name,
            "_properties": {}
        }
        
        # 모든 struct에 일반적인 속성 접근 시도
        try:
            # 일반적인 속성들 자동 감지
            common_props = ['x', 'y', 'z', 'w', 'r', 'g', 'b', 'a', 'pitch', 'roll', 'yaw']
            direct_values = {}
            
            for prop in common_props:
                if hasattr(obj, prop):
                    try:
                        direct_values[prop] = getattr(obj, prop)
                    except:
                        pass
            
            if direct_values:
                struct_data["_direct_values"] = direct_values
        except:
            pass
        
        # 속성 처리 (일반적 접근법)
        try:
            print(f"🔍 StructSerializer: {class_name} 속성 탐색 시작")
            property_names = get_property_names_advanced(obj)
            print(f"🔍 StructSerializer: {len(property_names)}개 속성 발견 - {property_names}")
            
            if property_names:
                for prop_name in property_names:
                    try:
                        # 기본 필터링만
                        if len(prop_name) < 2:
                            continue
                            
                        if hasattr(obj, 'get_editor_property'):
                            prop_value = obj.get_editor_property(prop_name)
                        else:
                            prop_value = getattr(obj, prop_name)
                        
                        # 재귀 직렬화는 매니저에서 처리
                        struct_data["_properties"][prop_name] = prop_value
                            
                    except Exception:
                        continue
                
        except Exception:
            pass
        
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
        """Object 객체 직렬화 - 메인 오브젝트는 전체, 하위 오브젝트는 참조만"""
        # 클래스 정보 추출 (예외 처리 최소화)
        class_name = getattr(obj.__class__, '__name__', 'Unknown')
        path_name = getattr(obj, 'get_path_name', lambda: str(obj))()
        full_name = getattr(obj, 'get_full_name', lambda: f"{class_name} {path_name}")()
        obj_name = getattr(obj, 'get_name', lambda: class_name)()
        
        # 객체 참조 중복 처리 검사 (성능 최적화)
        if path_name and path_name in self._object_cache:
            return {"_object_reference": path_name}
        
        # 메인 오브젝트(깊이 1)만 전체 직렬화, 하위 오브젝트(깊이 2+)는 참조만
        is_asset = self.current_depth > 1
        
        if is_asset:
            # 애셋이면 참조만 저장
            return {
                "_unreal_type": "object_reference",
                "_class_name": class_name,
                "_path_name": path_name,
                "_name": obj_name
            }
        
        # 인스턴스면 전체 직렬화
        obj_data = {
            "_unreal_type": "object",
            "_class_name": class_name,
            "_path_name": path_name,
            "_full_name": full_name,
            "_name": obj_name,
            "_properties": {}
        }
        
        # 모든 속성 시도하되 간단한 필터링만 적용
        try:
            property_names = get_property_names_advanced(obj)
            
            for prop_name in property_names:  # 모든 속성
                try:
                    if hasattr(obj, 'get_editor_property'):
                        prop_value = obj.get_editor_property(prop_name)
                        if prop_value is not None:
                            obj_data["_properties"][prop_name] = prop_value
                except Exception:
                    pass
        except Exception:
            pass
        
        # 캐시에 추가
        if path_name:
            self._object_cache[path_name] = True
        
        return obj_data
    
    def _is_asset_path(self, path_name: str, class_name: str = "") -> bool:
        """경로와 클래스 이름을 보고 애셋인지 판단 - 기본적으로 전체 직렬화"""
        if not path_name:
            return False
            
        # 인스턴스 경로 패턴들 (PersistentLevel, 서브레벨 등)
        instance_patterns = [
            ':PersistentLevel.',
            ':TheWorld.',
            '.StreamingLevel',
        ]
        
        # 인스턴스 패턴이 있으면 인스턴스
        for pattern in instance_patterns:
            if pattern in path_name:
                return False
        
        # 참조만 저장해도 되는 클래스들 (용량 최적화)
        reference_only_classes = [
            'Texture2D',          # 텍스처는 참조만으로 충분
            'StaticMesh',         # 스태틱 메시는 참조만
            'SkeletalMesh',       # 스켈레탈 메시는 참조만
            'AnimSequence',       # 애니메이션 시퀀스는 참조만
            'SoundWave',          # 사운드는 참조만
            'ParticleSystem',     # 파티클 시스템은 참조만
        ]
        
        # 클래스 이름이 참조만 저장 대상이면 애셋으로 처리
        for class_type in reference_only_classes:
            if class_type in class_name:
                return True
        
        # 엔진/스크립트 클래스는 참조만 (시스템 클래스들)
        system_patterns = [
            '/Engine/',         # 엔진 애셋  
            '/Script/',         # 스크립트 클래스
        ]
        
        for pattern in system_patterns:
            if path_name.startswith(pattern):
                return True
        
        # 기본적으로 모든 /Game/ 애셋은 전체 직렬화 (일반화)
        return False


class ArraySerializer(BaseSerializer):
    """Array/List 전용 직렬화기"""
    
    def can_serialize(self, obj: Any) -> bool:
        """Array 객체인지 확인"""
        return hasattr(obj, '__len__') and hasattr(obj, '__getitem__')
    
    def serialize(self, obj: Any, name: str = "root") -> Dict[str, Any]:
        """Array 객체 직렬화"""
        array_length = getattr(obj, '__len__', lambda: 0)()
        
        array_data = {
            "_unreal_type": "array",
            "_length": array_length,
            "_items": []
        }
        
        # 배열 크기 제한 (무한 중첩 방지)
        max_items = min(array_length, 10)  # 최대 10개 항목만
        
        for i in range(max_items):
            try:
                item = obj[i]
                array_data["_items"].append(item)  # 매니저에서 재귀 직렬화
            except Exception:
                array_data["_items"].append(None)
        
        if max_items < array_length:
            array_data["_truncated"] = f"처음 {max_items}개만 저장, 총 {array_length}개"
        
        return array_data


# ===============================================================================
# 복원(Deserialization) 관리자
# ===============================================================================

class DeserializationManager:
    """직렬화된 데이터를 Unreal 객체로 복원"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self._loaded_objects = {}  # 객체 캐시
    
    def deserialize(self, data: Any) -> Any:
        """직렬화된 데이터를 객체로 복원"""
        if not isinstance(data, dict):
            return data
        
        unreal_type = data.get("_unreal_type")
        
        if unreal_type == "object":
            return self._deserialize_object(data)
        elif unreal_type == "struct":
            return self._deserialize_struct(data)
        elif unreal_type == "enum":
            return self._deserialize_enum(data)
        elif unreal_type == "array":
            return self._deserialize_array(data)
        else:
            return data
    
    def _deserialize_object(self, data: Dict[str, Any]) -> Any:
        """Object 복원: 경로로 애셋 로드"""
        path_name = data.get("_path_name")
        
        # 객체 참조인 경우
        if "_object_reference" in data:
            ref_path = data["_object_reference"]
            if ref_path in self._loaded_objects:
                return self._loaded_objects[ref_path]
            path_name = ref_path
        
        # 애셋 로드 (Object는 링크만 저장했으므로 단순 로드)
        if path_name:
            try:
                obj = unreal.EditorAssetLibrary.load_asset(path_name)
                if obj:
                    self._loaded_objects[path_name] = obj
                    return obj
            except Exception:
                pass
        
        # 로드 실패시 링크 정보만 반환
        return {
            "_unreal_type": "object_link",
            "_class_name": data.get("_class_name"),
            "_path_name": path_name,
            "_name": data.get("_name"),
            "note": f"애셋 로드 실패: {path_name}"
        }
    
    def _deserialize_struct(self, data: Dict[str, Any]) -> Any:
        """Struct 복원: 동적 인스턴스 생성"""
        class_name = data.get("_class_name")
        direct_values = data.get("_direct_values", {})
        
        # 동적 구조체 생성 시도
        if direct_values and class_name and hasattr(unreal, class_name):
            try:
                unreal_class = getattr(unreal, class_name)
                # 생성자 인수 개수에 따라 동적 호출
                values = list(direct_values.values())
                if len(values) <= 4:  # 대부분의 기본 구조체는 4개 이하
                    return unreal_class(*values[:len(values)])
            except Exception:
                pass
        
        # 복원 실패시 데이터 형태로 반환
        return {
            "_unreal_type": "struct_data",
            "_class_name": class_name,
            "_direct_values": direct_values,
            "_properties": data.get("_properties", {}),
            "note": f"구조체 복원 실패: {class_name}"
        }
    
    def _deserialize_enum(self, data: Dict[str, Any]) -> Any:
        """Enum 복원"""
        # 간단히 딕셔너리로 반환 (enum 복원은 복잡함)
        return {
            "class_name": data.get("_class_name"),
            "enum_name": data.get("_enum_name"),
            "enum_value": data.get("_enum_value")
        }
    
    def _deserialize_array(self, data: Dict[str, Any]) -> List[Any]:
        """Array 복원"""
        items = data.get("_items", [])
        return [self.deserialize(item) for item in items]


# ===============================================================================
# 메인 직렬화 관리자
# ===============================================================================

class SerializationManager:
    """타입별 직렬화기들을 관리하는 메인 클래스"""
    
    def __init__(self, debug: bool = False, deep_analysis: bool = False, force_full: bool = False):
        """타입별 직렬화기들을 관리하는 메인 매니저"""
        self.debug = debug
        self.deep_analysis = deep_analysis
        self.force_full = force_full
        self.current_depth = 0
        self.max_depth = 100  # 실질적으로 무제한
        
        # 타입별 직렬화기들 초기화
        self.enum_serializer = EnumSerializer(debug)
        self.struct_serializer = StructSerializer(debug)
        self.object_serializer = ObjectSerializer(debug)
        self.array_serializer = ArraySerializer(debug)
        
        # 성능 통계
        self._stats = {
            'processed_objects': 0,
            'skipped_objects': 0,
            'total_properties': 0,
            'failed_properties': 0
        }
    
    def debug_log(self, message: str, level: int = 1):
        """디버그 로깅 (극한 성능 최적화)"""
        return  # 모든 디버그 로깅 비활성화
    
    def serialize(self, obj: Any, name: str = "root") -> Optional[Dict[str, Any]]:
        """메인 직렬화 진입점 - 적절한 타입별 직렬화기에 위임"""
        if obj is None:
            return None
            
        self.current_depth += 1
        if self.current_depth > self.max_depth:
            self.current_depth -= 1
            return None
            
        try:
            # 타입별 직렬화기 선택
            obj_type = type(obj).__name__
            

            
            if self.enum_serializer.can_serialize(obj):

                result = self.enum_serializer.serialize(obj, name)
            elif self.struct_serializer.can_serialize(obj):

                result = self.struct_serializer.serialize(obj, name)
                # 속성들을 재귀적으로 직렬화
                if "_properties" in result:
                    for prop_name, prop_value in result["_properties"].items():
                        result["_properties"][prop_name] = self.serialize(prop_value, f"{name}.{prop_name}")
            elif self.object_serializer.can_serialize(obj):

                # ObjectSerializer에 현재 깊이 전달
                self.object_serializer.current_depth = self.current_depth
                result = self.object_serializer.serialize(obj, name)
                
                # Object의 속성들 재귀 직렬화 (경로 기반 판단)
                if "_properties" in result:
                    for prop_name, prop_value in result["_properties"].items():
                        # 모든 속성을 재귀적으로 직렬화 (ObjectSerializer가 알아서 판단)
                        result["_properties"][prop_name] = self.serialize(prop_value, f"{name}.{prop_name}")
            elif self.array_serializer.can_serialize(obj):

                result = self.array_serializer.serialize(obj, name)
                # 배열 아이템들을 재귀적으로 직렬화
                if "_items" in result:
                    for i, item in enumerate(result["_items"]):
                        result["_items"][i] = self.serialize(item, f"{name}[{i}]")
            else:

                result = self._serialize_primitive(obj)
            
            self._stats['processed_objects'] += 1
            return result
            
        finally:
            self.current_depth -= 1
    
    def _serialize_primitive(self, obj: Any) -> Any:
        """원시 타입 직렬화"""
        if obj is None:
            return None
        elif isinstance(obj, (bool, int, float, str)):
            return obj
        elif hasattr(obj, '__iter__') and not isinstance(obj, str):
            try:
                return [self.serialize(item, f"item_{i}") for i, item in enumerate(obj)]
            except:
                return str(obj)
        else:
            return str(obj)
    
    def get_stats(self) -> Dict[str, int]:
        """성능 통계 반환"""
        return self._stats.copy()
    
    def reset_stats(self):
        """통계 초기화"""
        for key in self._stats:
            self._stats[key] = 0





# ===============================================================================
# 테스트 함수들
# ===============================================================================

def test_selected_object():
    """
    현재 선택된 객체로 완벽한 직렬화 테스트 (백업 파일 기반)
    
    사용법:
    - 에디터에서 객체(액터/에셋) 선택 후 실행
    - PostProcessVolume 권장 (가장 복잡한 테스트)
    """
    print("🔥 선택된 객체 완벽 직렬화 테스트")
    print("=" * 50)
    
    # 선택된 객체 가져오기 (deprecation 경고 억제)
    selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    
    try:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            selected_actors = unreal.EditorLevelLibrary.get_selected_level_actors()
    except:
        selected_actors = []
    
    target_objects = []
    
    if selected_assets:
        target_objects.extend([(obj, f"에셋: {obj.get_name()}") for obj in selected_assets])
    
    if selected_actors:
        target_objects.extend([(obj, f"액터: {obj.get_name()}") for obj in selected_actors])
    
    if not target_objects:
        print("⚠️ 객체를 선택하고 다시 실행하세요.")
        print("💡 권장: PostProcessVolume (가장 완벽한 테스트)")
        return False
    
    processed_count = 0
    
    for target_object, obj_description in target_objects:
        processed_count += 1
        print(f"\n🎯 처리 #{processed_count}: {obj_description}")
        print(f"📋 객체 타입: {type(target_object).__name__}")
        
        import time
        start_time = time.time()
        
        try:
            # deprecation 경고 억제하면서 직렬화
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                
                manager = SerializationManager(debug=False, deep_analysis=True, force_full=True)
                result = manager.serialize(target_object, "selected_object")
            
            end_time = time.time()
            process_time = end_time - start_time
            
            if result:
                # 결과 분석
                result_type = result.get("_unreal_type", "unknown")
                
                print(f"✅ {result_type.upper()} 직렬화 성공!")
                
                properties = {}
                
                if result_type == "object":
                    print(f"  🔗 Object 링크 정보:")
                    print(f"    - 클래스: {result.get('_class_name', 'Unknown')}")
                    print(f"    - 경로: {result.get('_path_name', 'Unknown')}")
                    print(f"    - 이름: {result.get('_name', 'Unknown')}")
                elif "_properties" in result:
                    properties = result["_properties"]
                    print(f"  📊 Struct 속성 수: {len(properties)}개")
                    
                    # 주요 속성들 확인 (Struct만)
                    prop_names = list(properties.keys())
                    if len(prop_names) > 0:
                        print(f"  🔍 Struct 속성들: {prop_names}")  # 모든 속성 표시
                
                # 하위 객체 분석 (일반적 접근)
                if properties:
                    struct_count = 0
                    largest_struct = None
                    largest_count = 0
                    
                    for prop_name, prop_value in properties.items():
                        if isinstance(prop_value, dict) and prop_value.get("_unreal_type") == "struct":
                            struct_count += 1
                            struct_props = prop_value.get("_properties", {})
                            if len(struct_props) > largest_count:
                                largest_count = len(struct_props)
                                largest_struct = prop_name
                    
                    if struct_count > 0:
                        print(f"  📦 하위 구조체: {struct_count}개")
                        if largest_struct:
                            print(f"  🏆 최대 구조체: {largest_struct} ({largest_count}개 속성)")
                
                elif result_type == "struct" and "_properties" in result:
                    prop_count = len(result["_properties"])
                    print(f"  📊 구조체 속성: {prop_count}개")
                
                elif result_type == "enum":
                    enum_name = result.get("_enum_name", "Unknown")
                    enum_value = result.get("_enum_value", "Unknown")
                    print(f"  🔢 Enum: {enum_name} = {enum_value}")
                
                print(f"  ⏱️ 처리 시간: {process_time:.2f}초")
                print(f"  📊 처리 통계: {manager.get_stats()}")
                
                # JSON 크기 확인
                json_str = json.dumps(result, indent=2, default=str, ensure_ascii=False)
                json_size = len(json_str)
                print(f"  📄 JSON 크기: {json_size:,}자")
                
                # 결과 자동 파일 저장 (Object 링크로 인해 크기 감소)
                if json_size > 1000:
                    import os
                    safe_name = obj_description.replace(':', '_').replace('/', '_').replace(' ', '_')
                    filename = f"serialization_result_{safe_name}.json"
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    save_path = os.path.join(current_dir, filename)
                    
                    try:
                        with open(save_path, 'w', encoding='utf-8') as f:
                            f.write(json_str)
                        print(f"  💾 자동 저장 완료: {filename}")
                        print(f"  📁 경로: {save_path}")
                    except Exception as e:
                        print(f"  ❌ 저장 실패: {e}")
                else:
                    print(f"  💾 크기가 작아서 파일 저장 생략")
                
            else:
                print("❌ 직렬화 실패: 결과가 비어있음")
                
        except Exception as e:
            print(f"❌ 처리 실패: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n🏆 테스트 완료! 총 {processed_count}개 객체 처리")
    return processed_count > 0


def test_postprocess_settings():
    """PostProcessSettings 전용 테스트 (단축 함수)"""
    print("🎨 PostProcessSettings 전용 테스트")
    
    import time
    start_time = time.time()
    
    try:
        settings = unreal.PostProcessSettings()
        
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            manager = SerializationManager(debug=False)
            result = manager.serialize(settings, "pps_test")
        
        end_time = time.time()
        
        if result and "_properties" in result:
            prop_count = len(result["_properties"])
            print(f"✅ 성공: {prop_count}개 속성 처리")
            print(f"⏱️ 시간: {end_time - start_time:.2f}초")
            
            json_str = json.dumps(result, indent=2, default=str)
            print(f"📄 크기: {len(json_str):,}자")
            return True
        else:
            print("❌ 실패")
            return False
            
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False


def test_vector():
    """Vector 테스트 (단축 함수)"""
    print("📐 Vector 테스트")
    
    try:
        vector = unreal.Vector(1.0, 2.0, 3.0)
        manager = SerializationManager(debug=False)
        result = manager.serialize(vector, "vector_test")
        
        if result:
            print(f"✅ Vector 직렬화 성공")
            print(f"📋 타입: {result.get('_unreal_type')}")
            print(f"📊 클래스: {result.get('_class_name')}")
            if "_direct_values" in result:
                values = result["_direct_values"]
                print(f"🎯 값: x={values.get('x')}, y={values.get('y')}, z={values.get('z')}")
            return True
        else:
            print("❌ 실패")
            return False
            
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False


def test_selected_asset():
    """선택된 애셋 전용 직렬화 테스트"""
    print("🎯 선택된 애셋 직렬화 테스트")
    print("=" * 40)
    
    # 선택된 애셋 가져오기
    selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    
    if not selected_assets:
        print("⚠️ 애셋을 선택하고 다시 실행하세요.")
        print("💡 권장: Material, Mesh, Texture 등")
        return False
    
    processed_count = 0
    
    for i, asset in enumerate(selected_assets):
        processed_count += 1
        asset_name = asset.get_name()
        asset_class = asset.__class__.__name__
        asset_path = asset.get_path_name()
        
        print(f"\n🎯 처리 #{i+1}: 애셋: {asset_name}")
        print(f"📋 애셋 타입: {asset_class}")
        print(f"📁 경로: {asset_path}")
        
        import time
        start_time = time.time()
        
        try:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                
                manager = SerializationManager(debug=False)
                result = manager.serialize(asset, f"asset_{asset_name}")
            
            end_time = time.time()
            process_time = end_time - start_time
            
            if result:
                result_type = result.get("_unreal_type", "unknown")
                
                print(f"✅ {result_type.upper()} 직렬화 성공!")
                print(f"  🔗 애셋 정보:")
                print(f"    - 클래스: {result.get('_class_name', 'Unknown')}")
                print(f"    - 경로: {result.get('_path_name', 'Unknown')}")
                print(f"    - 이름: {result.get('_name', 'Unknown')}")
                
                # 애셋은 보통 object_reference로 처리되므로 속성 수 확인
                if "_properties" in result:
                    prop_count = len(result["_properties"])
                    print(f"  📊 속성 수: {prop_count}개")
                    
                    if prop_count > 0:
                        prop_names = list(result["_properties"].keys())
                        print(f"  🔍 주요 속성: {prop_names[:10]}")  # 처음 10개만
                
                print(f"  ⏱️ 처리 시간: {process_time:.2f}초")
                print(f"  📊 처리 통계: {manager.get_stats()}")
                
                # JSON 크기 확인 및 저장
                json_str = json.dumps(result, indent=2, default=str, ensure_ascii=False)
                json_size = len(json_str)
                print(f"  📄 JSON 크기: {json_size:,}자")
                
                # 자동 저장 (애셋은 참조만 저장되므로 크기가 작을 수 있음)
                import os
                safe_name = asset_name.replace('/', '_').replace(' ', '_').replace(':', '_')
                filename = f"serialization_result_애셋_{safe_name}.json"
                current_dir = os.path.dirname(os.path.abspath(__file__))
                full_path = os.path.join(current_dir, filename)
                
                try:
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(json_str)
                    print(f"  💾 저장 완료: {filename}")
                    print(f"  📁 경로: {full_path}")
                    
                except Exception as e:
                    print(f"  ❌ 저장 실패: {e}")
                
            else:
                print("❌ 직렬화 실패")
                
        except Exception as e:
            print(f"❌ 처리 실패: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n🏆 테스트 완료! 총 {processed_count}개 애셋 처리")
    return processed_count > 0


def test_material():
    """기본 머티리얼 테스트 (단축 함수)"""
    print("🎭 머티리얼 테스트")
    
    try:
        material = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/BasicShapeMaterial")
        if not material:
            print("❌ 기본 머티리얼 로드 실패")
            return False
        
        manager = SerializationManager(debug=False)
        result = manager.serialize(material, "material_test")
        
        if result and "_properties" in result:
            prop_count = len(result["_properties"])
            print(f"✅ 머티리얼 직렬화 성공: {prop_count}개 속성")
            print(f"📋 이름: {result.get('_name')}")
            print(f"🎯 클래스: {result.get('_class_name')}")
            return True
        else:
            print("❌ 실패")
            return False
            
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False


def test_deserialization():
    """복원 테스트 (직렬화 + 복원)"""
    print("🔄 직렬화 + 복원 테스트")
    
    try:
        # 1. Vector 테스트
        print("\n📐 Vector 복원 테스트:")
        original_vector = unreal.Vector(10.5, 20.3, 30.7)
        
        serializer = SerializationManager()
        serialized = serializer.serialize(original_vector)
        
        deserializer = DeserializationManager()
        restored_vector = deserializer.deserialize(serialized)
        
        print(f"  원본: {original_vector}")
        print(f"  복원: {restored_vector}")
        
        # 2. LinearColor 테스트  
        print("\n🎨 LinearColor 복원 테스트:")
        original_color = unreal.LinearColor(0.8, 0.2, 0.5, 1.0)
        
        serialized = serializer.serialize(original_color)
        restored_color = deserializer.deserialize(serialized)
        
        print(f"  원본: {original_color}")
        print(f"  복원: {restored_color}")
        
        # 3. 간단한 JSON 저장 결과를 로드해서 복원 테스트
        print("\n💾 저장된 JSON 복원 테스트:")
        import os
        json_files = [f for f in os.listdir(".") if f.startswith("serialization_result_") and f.endswith(".json")]
        
        if json_files:
            latest_file = json_files[-1]  # 가장 최근 파일
            print(f"  📁 로드할 파일: {latest_file}")
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            
            # Object 복원 시도
            if saved_data.get("_unreal_type") == "object":
                restored_object = deserializer.deserialize(saved_data)
                print(f"  ✅ Object 복원 시도: {type(restored_object)}")
                if hasattr(restored_object, 'get_name'):
                    print(f"  📋 복원된 객체명: {restored_object.get_name()}")
        
        return True
        
    except Exception as e:
        print(f"❌ 복원 테스트 실패: {e}")
        return False


def test_base_property_overrides(base_overrides=None):
    """BasePropertyOverrides 구조체 분석"""
    print("🔍 BasePropertyOverrides 구조체 분석")
    
    if base_overrides is None:
        # 선택된 머티리얼 인스턴스 가져오기
        selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
        
        if not selected_assets:
            print("❌ 머티리얼 인스턴스를 선택해주세요")
            return
        
        asset = selected_assets[0]
        if not isinstance(asset, unreal.MaterialInstanceConstant):
            print("❌ MaterialInstanceConstant를 선택해주세요")
            return
        
        print(f"📋 선택된 에셋: {asset.get_name()}")
        
        # BasePropertyOverrides 가져오기
        try:
            base_overrides = asset.get_editor_property("base_property_overrides")
        except:
            try:
                base_overrides = asset.get_editor_property("BasePropertyOverrides")
            except Exception as e:
                print(f"❌ BasePropertyOverrides 가져오기 실패: {e}")
                return
    
    try:
        print(f"✅ BasePropertyOverrides 타입: {type(base_overrides)}")
        print(f"📋 클래스명: {base_overrides.__class__.__name__}")
        
        # dir() 결과 확인
        print("\n🔍 dir() 결과:")
        all_attrs = dir(base_overrides)
        print(f"  전체 속성 개수: {len(all_attrs)}")
        
        # 모든 속성 보기 (언더스코어 포함)
        print("  모든 속성들:")
        for i, attr in enumerate(all_attrs):
            if i < 20:  # 처음 20개만
                print(f"    {attr}")
            elif i == 20:
                print("    ... (더 많음)")
                break
        
        # 언더스코어 없는 속성들
        print("  언더스코어 없는 속성들:")
        non_underscore_attrs = [attr for attr in all_attrs if not attr.startswith('_')]
        print(f"    개수: {len(non_underscore_attrs)}")
        
        for attr in non_underscore_attrs:
            try:
                value = getattr(base_overrides, attr)
                is_callable = callable(value)
                print(f"    {attr}: {'(함수)' if is_callable else value} ({type(value)})")
            except Exception as e:
                print(f"    {attr}: 접근 실패 - {e}")
        
        # bp_lib로 속성 확인 (있다면)
        if bp_lib and hasattr(base_overrides, 'static_struct'):
            print("\n🔍 bp_lib로 속성 확인:")
            try:
                struct_class = base_overrides.static_struct()
                names = bp_lib.get_all_property_names(struct_class)
                if names:
                    for name in names:
                        try:
                            prop_value = base_overrides.get_editor_property(str(name))
                            print(f"  {name}: {prop_value} ({type(prop_value)})")
                        except Exception as e:
                            print(f"  {name}: 접근 실패 - {e}")
                else:
                    print("  bp_lib에서 속성을 찾지 못했습니다")
            except Exception as e:
                print(f"  bp_lib 테스트 실패: {e}")
        
        # 수동으로 알려진 속성들 확인
        print("\n🔍 알려진 속성들 확인:")
        known_props = [
            'override_base_color',
            'override_metallic',  
            'override_specular',
            'override_roughness',
            'override_emissive_color',
            'override_opacity',
            'override_opacity_mask',
            'override_normal',
            'override_world_position_offset',
            'override_subsurface_color',
            'override_clearcoat',
            'override_clearcoat_roughness',
            'override_ambient_occlusion',
            'override_refraction',
            'override_customized_u_vs',
            'override_pixel_depth_offset',
            'override_shading_model'
        ]
        
        for prop in known_props:
            try:
                if hasattr(base_overrides, prop):
                    value = getattr(base_overrides, prop)
                    print(f"  {prop}: {value}")
                elif hasattr(base_overrides, 'get_editor_property'):
                    value = base_overrides.get_editor_property(prop)
                    print(f"  {prop}: {value}")
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"❌ BasePropertyOverrides 접근 실패: {e}")


if __name__ == "__main__":
    print("🚀 UE Serializer 로드 완료")
    print("📋 사용 가능한 함수들:")
    print("  - test_selected_object(): 선택된 객체(액터+애셋) 테스트")  
    print("  - test_selected_asset(): 선택된 애셋만 테스트")
    print("  - test_postprocess_settings(): PostProcessSettings 테스트")
    print("  - test_vector(): Vector 테스트")
    print("  - test_material(): 기본 머티리얼 테스트")
    print("  - test_deserialization(): 직렬화+복원 테스트")
    print("  - test_base_property_overrides(): BasePropertyOverrides 구조체 분석")
    
    # 기본 테스트 실행
    # test_selected_object()