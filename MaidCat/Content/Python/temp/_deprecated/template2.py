import unreal
#4.27
EAL = unreal.EditorAssetLibrary #ContentBrowser에서 대부분의 일반적인 기능을 수행하는 유틸리티 클래스입니다. AssetRegistryHelpers 클래스에는 더 복잡한 유틸리티가 있습니다. 
EFL = unreal.EditorFilterLibrary #개체 목록을 필터링하는 유틸리티 클래스입니다. 개체는 World Editor에 있어야 합니다.
ELL = unreal.EditorLevelLibrary #World Editor에서 대부분의 일반적인 기능을 수행하는 유틸리티 클래스입니다.
EUL = unreal.EditorUtilityLibrary #Blutilities에 에디터 유틸리티 기능 노출
SKL = unreal.EditorSkeletalMeshLibrary #SkeletalMesh를 변경 및 분석하고 SkeletalMesh 에디터의 공통 기능을 사용하는 유틸리티 클래스입니다.
SML = unreal.EditorStaticMeshLibrary #StaticMesh를 변경 및 분석하고 Mesh Editor의 공통 기능을 사용하는 유틸리티 클래스입니다. 
MEL = unreal.MaterialEditingLibrary #머티리얼 생성/편집을 위한 블루프린트 라이브러리
matLib = unreal.MaterialLibrary #머티리얼 라이브러리 파라미터 컬렉션 Get Set 및 머티리얼 인스턴스 다이내믹 생성
RL  = unreal.RenderingLibrary #Kismet Rendering Library. 렌더타겟과 관련된 기능들을 제공
strLib  = unreal.StringLibrary #문자열 처리 라이브러리
sysLib  = unreal.SystemLibrary #시스템 라이브러리
bpfuLib = unreal.BlueprintFileUtilsBPLibrary
at = unreal.AssetTools
atHelper = unreal.AssetToolsHelpers
arHelper = unreal.AssetRegistryHelpers
engineVersion = sysLib.get_engine_version()

#5.0
EAS = unreal.EditorActorSubsystem

def listAssetPaths():
    assetPaths = EAL.list_assets("/Game")
    for assetPath in assetPaths : print(assetPath)

def getSelectionContentBrowser():
    selectedAssets = EUL.get_selected_assets()
    for selectedAsset in selectedAssets: print(selectedAsset)

def getAllActors():
    actors = EAS.get_all_level_actors()
    for actor in actors : print(actor)

def getSelectedActors():
    selectedActors = EAS.get_selected_level_actors()
    for selectedActor in selectedActors :  print(selectedActor)
