import unreal

# 실제 Unreal Python에서 렌더링 관련 API 확인
print("=== Rendering API 테스트 ===")

# 1. KismetRenderingLibrary 존재 확인
try:
    kismet_lib = unreal.KismetRenderingLibrary
    print(f"✅ KismetRenderingLibrary 존재: {type(kismet_lib)}")
    
    # 주요 메서드들만 확인
    key_methods = ['create_render_target2d', 'draw_material_to_render_target', 
                   'begin_draw_canvas_to_render_target', 'end_draw_canvas_to_render_target']
    
    for method_name in key_methods:
        if hasattr(kismet_lib, method_name):
            method = getattr(kismet_lib, method_name)
            print(f"  - {method_name}: {type(method)}")
        else:
            print(f"  - {method_name}: 없음")
            
except AttributeError as e:
    print(f"❌ KismetRenderingLibrary가 존재하지 않음: {e}")

# 2. 직접 unreal 모듈에서 함수 확인
direct_functions = ['create_render_target2d', 'draw_material_to_render_target', 
                   'begin_draw_canvas_to_render_target']

print("\n=== unreal 모듈 직접 함수 확인 ===")
for func_name in direct_functions:
    try:
        func = getattr(unreal, func_name)
        print(f"✅ unreal.{func_name}: {type(func)}")
    except AttributeError:
        print(f"❌ unreal.{func_name}: 없음")

# 3. TextureRenderTarget2D 클래스 및 팩토리 확인
print("\n=== TextureRenderTarget2D 확인 ===")
try:
    rt_class = unreal.TextureRenderTarget2D
    print(f"✅ TextureRenderTarget2D: {rt_class}")
    
    # 팩토리 클래스 확인
    try:
        factory_class = unreal.TextureRenderTarget2DFactoryNew
        print(f"✅ TextureRenderTarget2DFactoryNew: {factory_class}")
    except AttributeError:
        print("❌ TextureRenderTarget2DFactoryNew: 없음")
        
except AttributeError:
    print("❌ TextureRenderTarget2D 클래스를 찾을 수 없음")

# 4. EditorAssetLibrary를 통한 애셋 생성 방법 확인
print("\n=== EditorAssetLibrary 확인 ===")
try:
    editor_lib = unreal.EditorAssetLibrary
    if hasattr(editor_lib, 'create_asset'):
        print("✅ EditorAssetLibrary.create_asset 존재")
    else:
        print("❌ EditorAssetLibrary.create_asset 없음")
except AttributeError:
    print("❌ EditorAssetLibrary 없음")

print("\n=== 테스트 완료 ===")