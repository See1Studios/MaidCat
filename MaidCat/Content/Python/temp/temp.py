# cspell:ignore testscript testmodule testfunction staticmesh
import unreal
import importlib
import inspect
import util.material as mat_util
import util.staticmesh as sm_util
import util.project as pr_util
import util.helper as uh

# importlib.reload(mat_util)
# importlib.reload(mat_util)
# importlib.reload(sm_util)
importlib.reload(uh)

# 월드 컨텍스트 가져오기 (새로운 방법)
world = uh.get_editor_world()

# Material Parameter Collection 로드
collection = uh.load_asset("/Game/TestCollection")

# 파라미터 값 가져오기
testVector = uh.ML.get_vector_parameter_value(world, collection, unreal.Name("TestVector"))
print(testVector)
# #mat_util.find_heavy_materials(threshold=600)
# # sm_util.find_uv_channel_count(threshold=3, path_to_find="/Game/")
# # pr_util.remove_empty_folders(unreal.Paths.project_content_dir(), remove_root=True)

# mat_util.find_two_sided()

# allModules = inspect.getmembers(mat_util, inspect.ismodule)
# for m in allModules:
#     print(m)
# allFunctions = inspect.getmembers(mat_util, inspect.isfunction)
# for f in allFunctions:
#     print(f)
