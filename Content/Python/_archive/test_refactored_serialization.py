"""
타입별 직렬화기 구조 테스트
=========================
새로운 클래스 분리 구조의 성능과 기능을 테스트합니다.
"""

import unreal
import time
import json
from advanced_serialization import SerializationManager, UnrealObjectSerializer

def test_new_structure_performance():
    """새로운 타입별 직렬화기 구조의 성능 테스트"""
    print("🧪 새로운 타입별 직렬화기 구조 성능 테스트")
    print("=" * 50)
    
    try:
        # PostProcessSettings 객체 생성
        post_process_settings = unreal.PostProcessSettings()
        
        # 1. 새로운 SerializationManager 테스트
        print("\n📋 1. SerializationManager 테스트")
        start_time = time.time()
        
        manager = SerializationManager(debug=False, deep_analysis=True, force_full=True)
        result = manager.serialize(post_process_settings, "PostProcessSettings")
        
        end_time = time.time()
        manager_time = end_time - start_time
        
        if result and "_properties" in result:
            manager_props = len(result["_properties"])
            print(f"✅ Manager 결과: {manager_props}개 속성")
            print(f"⏱️ Manager 시간: {manager_time:.2f}초")
            
            # JSON 크기 확인
            json_str = json.dumps(result, indent=2, default=str)
            manager_size = len(json_str)
            print(f"📄 Manager JSON 크기: {manager_size:,}자")
        else:
            print("❌ Manager 실패")
            return False
        
        # 2. 레거시 UnrealObjectSerializer 테스트 (호환성 확인)
        print("\n📋 2. 레거시 UnrealObjectSerializer 테스트")
        start_time = time.time()
        
        legacy_serializer = UnrealObjectSerializer(debug=False, deep_analysis=True, force_full=True)
        legacy_result = legacy_serializer.serialize(post_process_settings, "PostProcessSettings")
        
        end_time = time.time()
        legacy_time = end_time - start_time
        
        if legacy_result and "_properties" in legacy_result:
            legacy_props = len(legacy_result["_properties"])
            print(f"✅ Legacy 결과: {legacy_props}개 속성")
            print(f"⏱️ Legacy 시간: {legacy_time:.2f}초")
            
            # JSON 크기 확인
            legacy_json_str = json.dumps(legacy_result, indent=2, default=str)
            legacy_size = len(legacy_json_str)
            print(f"📄 Legacy JSON 크기: {legacy_size:,}자")
        else:
            print("❌ Legacy 실패")
            return False
        
        # 3. 성능 비교 및 결과 분석
        print("\n📊 성능 분석")
        print("-" * 30)
        print(f"Manager 속성 수: {manager_props}")
        print(f"Legacy 속성 수: {legacy_props}")
        print(f"속성 수 일치: {'✅' if manager_props == legacy_props else '❌'}")
        print()
        print(f"Manager 시간: {manager_time:.2f}초")
        print(f"Legacy 시간: {legacy_time:.2f}초")
        if legacy_time > 0:
            speed_ratio = legacy_time / manager_time
            print(f"속도 비율: {speed_ratio:.2f}x")
        
        print()
        print(f"Manager JSON 크기: {manager_size:,}자")
        print(f"Legacy JSON 크기: {legacy_size:,}자")
        size_diff = legacy_size - manager_size
        print(f"크기 차이: {size_diff:,}자")
        
        # 4. 통계 정보
        manager_stats = manager.get_stats()
        legacy_stats = legacy_serializer.get_stats()
        
        print(f"\n📈 Manager 통계: {manager_stats}")
        print(f"📈 Legacy 통계: {legacy_stats}")
        
        # 5. 타입별 직렬화기 개별 테스트
        print(f"\n🔍 타입별 직렬화기 개별 테스트")
        test_individual_serializers(manager)
        
        return True
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_individual_serializers(manager):
    """개별 직렬화기들 테스트"""
    
    # 1. EnumSerializer 테스트
    try:
        tone_curve_enum = unreal.ToneCurve.LINEAR
        enum_result = manager.enum_serializer.serialize(tone_curve_enum, "test_enum")
        print(f"✅ EnumSerializer: {enum_result.get('_class_name', 'Unknown')}")
    except Exception as e:
        print(f"❌ EnumSerializer 실패: {e}")
    
    # 2. StructSerializer 테스트
    try:
        vector = unreal.Vector(1.0, 2.0, 3.0)
        struct_result = manager.struct_serializer.serialize(vector, "test_vector")
        print(f"✅ StructSerializer: {struct_result.get('_class_name', 'Unknown')}")
    except Exception as e:
        print(f"❌ StructSerializer 실패: {e}")
    
    # 3. ObjectSerializer 테스트
    try:
        material = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/BasicShapeMaterial")
        if material:
            obj_result = manager.object_serializer.serialize(material, "test_material")
            print(f"✅ ObjectSerializer: {obj_result.get('_class_name', 'Unknown')}")
        else:
            print("⚠️ ObjectSerializer: 테스트 머티리얼 로드 실패")
    except Exception as e:
        print(f"❌ ObjectSerializer 실패: {e}")
    
    # 4. ArraySerializer 테스트
    try:
        test_array = [1, 2, 3, 4, 5]
        array_result = manager.array_serializer.serialize(test_array, "test_array")
        print(f"✅ ArraySerializer: {array_result.get('_length', 0)}개 아이템")
    except Exception as e:
        print(f"❌ ArraySerializer 실패: {e}")

if __name__ == "__main__":
    success = test_new_structure_performance()
    print(f"\n🎯 전체 테스트 결과: {'성공' if success else '실패'}")