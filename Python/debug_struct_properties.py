import unreal
from tool.ue_serializer import test_base_property_overrides

def debug_material_instance():
    # 머티리얼 인스턴스 로드
    material_instance = unreal.EditorAssetLibrary.load_asset('/Game/PostProcessTest_Inst')
    if material_instance:
        print("=== MaterialInstance BasePropertyOverrides 직접 접근 ===")
        
        # 다양한 방법으로 BasePropertyOverrides 접근 시도
        struct_obj = None
        try:
            struct_obj = getattr(material_instance, 'base_property_overrides', None)
            if struct_obj:
                print("Found: base_property_overrides")
        except:
            pass
            
        if not struct_obj:
            try:
                struct_obj = material_instance.get_editor_property('base_property_overrides')
                if struct_obj:
                    print("Found via get_editor_property: base_property_overrides")
            except:
                pass
                
        # 대문자 버전도 시도
        if not struct_obj:
            try:
                struct_obj = material_instance.get_editor_property('BasePropertyOverrides')
                if struct_obj:
                    print("Found via get_editor_property: BasePropertyOverrides")
            except Exception as e:
                print(f"Failed BasePropertyOverrides: {e}")
                
        # 모든 속성을 검사해서 BaseProperty 관련 찾기
        if not struct_obj:
            print("Searching all properties for BaseProperty related...")
            from tool.ue_serializer import get_property_names_advanced
            props = get_property_names_advanced(material_instance)
            base_props = [p for p in props if 'base' in p.lower() and 'property' in p.lower()]
            print(f"Found BaseProperty related props: {base_props}")
            
            if base_props:
                try:
                    struct_obj = material_instance.get_editor_property(base_props[0])
                    print(f"Got struct via {base_props[0]}")
                except Exception as e:
                    print(f"Failed to get {base_props[0]}: {e}")
        
        if struct_obj:
            print("=== MaterialInstanceBasePropertyOverrides 분석 ===")
            test_base_property_overrides(struct_obj)
        else:
            print("BasePropertyOverrides 구조체를 찾을 수 없습니다")
            
            # 디버깅: 모든 구조체 속성 찾기
            print("=== All struct properties ===")
            from tool.ue_serializer import get_property_names_advanced
            props = get_property_names_advanced(material_instance)
            for prop in props[:10]:  # 처음 10개만
                try:
                    value = material_instance.get_editor_property(prop)
                    print(f"{prop}: {type(value)} - {str(value)[:100]}")
                except:
                    pass
    else:
        print('Material instance not found')

if __name__ == "__main__":
    debug_material_instance()