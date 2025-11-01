
import unreal
import webbrowser

# =============================================================================
# 문서 URL 자동 열기 기능
# =============================================================================

def open_docs(type_name):
    """해당 타입의 Epic Games 문서를 브라우저에서 열기"""
    base_url = "https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/"
    doc_url = f"{base_url}{type_name}"
    webbrowser.open(doc_url)

# =============================================================================
# 모든 언리얼 타입들 (알파벳 순으로 정렬)
# =============================================================================

def Actor():
    """기본 Actor 생성"""
    obj = unreal.Actor()
    open_docs("Actor")
    return obj

def ActorComponent():
    """ActorComponent 생성"""
    obj = unreal.ActorComponent()
    open_docs("ActorComponent")
    return obj

def ActorIterator():
    """ActorIterator 클래스 정보"""
    obj = unreal.ActorIterator
    open_docs("ActorIterator")
    return obj

def Anchors():
    """Anchors 구조체"""
    obj = unreal.Anchors()
    open_docs("Anchors")
    return obj

def AnimBlueprint():
    """AnimBlueprint 생성"""
    obj = unreal.AnimBlueprint()
    open_docs("AnimBlueprint")
    return obj

def AnimInstance():
    """AnimInstance 생성"""
    obj = unreal.AnimInstance()
    open_docs("AnimInstance")
    return obj

def AnimMontage():
    """AnimMontage 생성"""
    obj = unreal.AnimMontage()
    open_docs("AnimMontage")
    return obj

def AnimNotifyEvent():
    """AnimNotifyEvent 구조체"""
    obj = unreal.AnimNotifyEvent()
    open_docs("AnimNotifyEvent")
    return obj

def AnimSequence():
    """AnimSequence 생성"""
    obj = unreal.AnimSequence()
    open_docs("AnimSequence")
    return obj

def Array():
    """Array 클래스 정보"""
    obj = unreal.Array
    open_docs("Array")
    return obj

def AssetData():
    """AssetData 구조체"""
    obj = unreal.AssetData()
    open_docs("AssetData")
    return obj

def AssetImportData():
    """AssetImportData 생성"""
    obj = unreal.AssetImportData()
    open_docs("AssetImportData")
    return obj

def AssetRegistry():
    """AssetRegistry 서브시스템"""
    obj = unreal.AssetRegistryHelpers.get_asset_registry()
    open_docs("AssetRegistry")
    return obj

def AudioComponent():
    """AudioComponent 생성"""
    obj = unreal.AudioComponent()
    open_docs("AudioComponent")
    return obj

def BehaviorTree():
    """BehaviorTree 생성"""
    obj = unreal.BehaviorTree()
    open_docs("BehaviorTree")
    return obj

def BehaviorTreeComponent():
    """BehaviorTreeComponent 생성"""
    obj = unreal.BehaviorTreeComponent()
    open_docs("BehaviorTreeComponent")
    return obj

# Blackboard는 존재하지 않음 - 삭제됨

def BlackboardComponent():
    """BlackboardComponent 생성"""
    obj = unreal.BlackboardComponent()
    open_docs("BlackboardComponent")
    return obj

def Blueprint():
    """Blueprint 생성"""
    obj = unreal.Blueprint()
    open_docs("Blueprint")
    return obj

def BlueprintGeneratedClass():
    """BlueprintGeneratedClass 생성"""
    obj = unreal.BlueprintGeneratedClass()
    open_docs("BlueprintGeneratedClass")
    return obj

def BoneReference():
    """BoneReference 구조체"""
    obj = unreal.BoneReference()
    open_docs("BoneReference")
    return obj

def Box():
    """Box 구조체"""
    obj = unreal.Box()
    open_docs("Box")
    return obj

def CameraActor():
    """CameraActor 생성"""
    obj = unreal.CameraActor()
    open_docs("CameraActor")
    return obj

def CameraComponent():
    """CameraComponent 생성"""
    obj = unreal.CameraComponent()
    open_docs("CameraComponent")
    return obj

def Character():
    """기본 Character 생성"""
    obj = unreal.Character()
    open_docs("Character")
    return obj

def CharacterMovementComponent():
    """CharacterMovementComponent 생성"""
    obj = unreal.CharacterMovementComponent()
    open_docs("CharacterMovementComponent")
    return obj

def Class():
    """Class 정보"""
    obj = unreal.Class()
    open_docs("Class")
    return obj

def ClassIterator():
    """ClassIterator 클래스 정보"""
    obj = unreal.ClassIterator
    open_docs("ClassIterator")
    return obj

# CollisionProfile는 존재하지 않음 - 삭제됨

def CollisionResponseContainer():
    """CollisionResponseContainer 구조체"""
    obj = unreal.CollisionResponseContainer()
    open_docs("CollisionResponseContainer")
    return obj

def Color():
    """Color 구조체"""
    obj = unreal.Color()
    open_docs("Color")
    return obj

def CurveBase():
    """CurveBase 생성"""
    obj = unreal.CurveBase()
    open_docs("CurveBase")
    return obj

def CurveFloat():
    """CurveFloat 생성"""
    obj = unreal.CurveFloat()
    open_docs("CurveFloat")
    return obj

def CurveLinearColor():
    """CurveLinearColor 생성"""
    obj = unreal.CurveLinearColor()
    open_docs("CurveLinearColor")
    return obj

def CurveVector():
    """CurveVector 생성"""
    obj = unreal.CurveVector()
    open_docs("CurveVector")
    return obj

def DataAsset():
    """DataAsset 생성"""
    obj = unreal.DataAsset()
    open_docs("DataAsset")
    return obj

def DataTable():
    """DataTable 생성"""
    obj = unreal.DataTable()
    open_docs("DataTable")
    return obj

def DateTime():
    """DateTime 구조체"""
    obj = unreal.DateTime.now()
    open_docs("DateTime")
    return obj

def DelegateBase():
    """DelegateBase 생성"""
    obj = unreal.DelegateBase()
    open_docs("DelegateBase")
    return obj

# DirectionalLightActor는 존재하지 않음 - 삭제됨

def DirectionalLightComponent():
    """DirectionalLightComponent 생성"""
    obj = unreal.DirectionalLightComponent()
    open_docs("DirectionalLightComponent")
    return obj

def EditorActorSubsystem():
    """EditorActorSubsystem 가져오기"""
    obj = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    open_docs("EditorActorSubsystem")
    return obj

def EditorAssetLibrary():
    """EditorAssetLibrary 정보"""
    obj = unreal.EditorAssetLibrary()
    open_docs("EditorAssetLibrary")
    return obj

def EditorAssetSubsystem():
    """EditorAssetSubsystem 가져오기"""
    obj = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
    open_docs("EditorAssetSubsystem")
    return obj

def EditorLevelLibrary():
    """EditorLevelLibrary 정보"""
    obj = unreal.EditorLevelLibrary()
    open_docs("EditorLevelLibrary")
    return obj

def EngineSubsystem():
    """EngineSubsystem 기본"""
    obj = unreal.EngineSubsystem()
    open_docs("EngineSubsystem")
    return obj

def Enum():
    """Enum 정보"""
    obj = unreal.Enum()
    open_docs("Enum")
    return obj

def FieldPath():
    """FieldPath 구조체"""
    obj = unreal.FieldPath()
    open_docs("FieldPath")
    return obj

def FixedArray():
    """FixedArray 클래스 정보"""
    obj = unreal.FixedArray
    open_docs("FixedArray")
    return obj

def FloatRange():
    """FloatRange 구조체"""
    obj = unreal.FloatRange()
    open_docs("FloatRange")
    return obj

def FunctionDef():
    """FunctionDef 클래스 정보"""
    obj = unreal.FunctionDef
    open_docs("FunctionDef")
    return obj

def GameInstance():
    """GameInstance 생성"""
    obj = unreal.GameInstance()
    open_docs("GameInstance")
    return obj

def GameModeBase():
    """GameModeBase 클래스"""
    obj = unreal.GameModeBase.static_class()
    open_docs("GameModeBase")
    return obj

def GameplayStatics():
    """GameplayStatics 라이브러리"""
    obj = unreal.GameplayStatics()
    open_docs("GameplayStatics")
    return obj

def Guid():
    """Guid 구조체"""
    obj = unreal.Guid.new_guid()
    open_docs("Guid")
    return obj

def HitResult():
    """HitResult 구조체"""
    obj = unreal.HitResult()
    open_docs("HitResult")
    return obj

# InputActionKey, InputAxisKey는 존재하지 않으므로 삭제됨

def InputChord():
    """InputChord 구조체"""
    obj = unreal.InputChord()
    open_docs("InputChord")
    return obj

def InputComponent():
    """InputComponent 생성"""
    obj = unreal.InputComponent()
    open_docs("InputComponent")
    return obj

def IntPoint():
    """IntPoint 구조체"""
    obj = unreal.IntPoint()
    open_docs("IntPoint")
    return obj

def IntVector():
    """IntVector 구조체"""
    obj = unreal.IntVector()
    open_docs("IntVector")
    return obj

def Key():
    """Key 구조체"""
    obj = unreal.Key()
    open_docs("Key")
    return obj

# KismetLibrary 클래스들은 Unreal 모듈에 존재하지 않음 - 삭제됨

def Level():
    """현재 레벨 정보"""
    obj = unreal.EditorLevelLibrary.get_editor_world().get_current_level()
    open_docs("Level")
    return obj

def LevelSequence():
    """LevelSequence 생성"""
    obj = unreal.LevelSequence()
    open_docs("LevelSequence")
    return obj

def LightComponent():
    """LightComponent 기본"""
    obj = unreal.LightComponent()
    open_docs("LightComponent")
    return obj

def LinearColor():
    """LinearColor 구조체"""
    obj = unreal.LinearColor()
    open_docs("LinearColor")
    return obj

def Map():
    """Map 클래스 정보"""
    obj = unreal.Map
    open_docs("Map")
    return obj

def Margin():
    """Margin 구조체"""
    obj = unreal.Margin()
    open_docs("Margin")
    return obj

def Material():
    """Material 생성"""
    obj = unreal.Material()
    open_docs("Material")
    return obj

def MaterialInstance():
    """MaterialInstance 생성"""
    obj = unreal.MaterialInstance()
    open_docs("MaterialInstance")
    return obj

def MaterialInstanceConstant():
    """MaterialInstanceConstant 생성"""
    obj = unreal.MaterialInstanceConstant()
    open_docs("MaterialInstanceConstant")
    return obj

def MaterialInstanceDynamic():
    """MaterialInstanceDynamic 생성"""
    obj = unreal.MaterialInstanceDynamic()
    open_docs("MaterialInstanceDynamic")
    return obj

def MaterialInterface():
    """기본 Material 로드"""
    obj = unreal.load_asset("/Engine/EngineMaterials/DefaultMaterial")
    return obj
    open_docs("MaterialInterface")
    return obj

def MaterialParameterCollection():
    """MaterialParameterCollection 생성"""
    obj = unreal.MaterialParameterCollection()
    open_docs("MaterialParameterCollection")
    return obj

def MaterialParameterInfo():
    """MaterialParameterInfo 구조체"""
    obj = unreal.MaterialParameterInfo()
    open_docs("MaterialParameterInfo")
    return obj

def Matrix():
    """Matrix 구조체"""
    obj = unreal.Matrix.make_identity()
    open_docs("Matrix")
    return obj

def MovieScene():
    """MovieScene 생성"""
    obj = unreal.MovieScene()
    open_docs("MovieScene")
    return obj

def MulticastDelegateBase():
    """MulticastDelegateBase 생성"""
    obj = unreal.MulticastDelegateBase()
    open_docs("MulticastDelegateBase")
    return obj

def Name():
    """Name 구조체"""
    obj = unreal.Name()
    open_docs("Name")
    return obj

def NiagaraComponent():
    """NiagaraComponent 생성"""
    obj = unreal.NiagaraComponent()
    open_docs("NiagaraComponent")
    return obj

def NiagaraSystem():
    """NiagaraSystem 생성"""
    obj = unreal.NiagaraSystem()
    open_docs("NiagaraSystem")
    return obj

def Object():
    """Object 기본 클래스"""
    obj = unreal.Object()
    open_docs("Object")
    return obj

def ObjectIterator():
    """ObjectIterator 생성"""
    obj = unreal.ObjectIterator()
    open_docs("ObjectIterator")
    return obj

def Package():
    """Package 정보"""
    obj = unreal.Package()
    open_docs("Package")
    return obj

def ParticleSystem():
    """ParticleSystem 생성"""
    obj = unreal.ParticleSystem()
    open_docs("ParticleSystem")
    return obj

def ParticleSystemComponent():
    """ParticleSystemComponent 생성"""
    obj = unreal.ParticleSystemComponent()
    open_docs("ParticleSystemComponent")
    return obj

def Pawn():
    """기본 Pawn 생성"""
    obj = unreal.Pawn()
    open_docs("Pawn")
    return obj

def PhysicsAsset():
    """PhysicsAsset 생성"""
    obj = unreal.PhysicsAsset()
    open_docs("PhysicsAsset")
    return obj

def Plane():
    """Plane 구조체"""
    obj = unreal.Plane()
    open_docs("Plane")
    return obj

def PlayerController():
    """PlayerController 생성"""
    obj = unreal.PlayerController()
    open_docs("PlayerController")
    return obj

def PlayerInput():
    """PlayerInput 생성"""
    obj = unreal.PlayerInput()
    open_docs("PlayerInput")
    return obj

def PointLightComponent():
    """PointLightComponent 생성"""
    obj = unreal.PointLightComponent()
    open_docs("PointLightComponent")
    return obj

def PostProcessComponent():
    """PostProcessComponent 생성"""
    obj = unreal.PostProcessComponent()
    open_docs("PostProcessComponent")
    return obj

def PostProcessSettings():
    """PostProcessSettings 구조체"""
    obj = unreal.PostProcessSettings()
    open_docs("PostProcessSettings")
    return obj

def PrimaryAssetId():
    """PrimaryAssetId 구조체"""
    obj = unreal.PrimaryAssetId()
    open_docs("PrimaryAssetId")
    return obj

def PrimitiveComponent():
    """PrimitiveComponent 생성"""
    obj = unreal.PrimitiveComponent()
    open_docs("PrimitiveComponent")
    return obj

def PropertyDef():
    """PropertyDef 클래스 정보"""
    obj = unreal.PropertyDef
    open_docs("PropertyDef")
    return obj

def PythonObjectHandle():
    """PythonObjectHandle 생성"""
    obj = unreal.PythonObjectHandle()
    open_docs("PythonObjectHandle")
    return obj

def Quat():
    """Quat(Quaternion) 구조체"""
    obj = unreal.Quat()
    open_docs("Quat")
    return obj

# RenderTransform는 존재하지 않음 - 삭제됨

# RigidBodyState는 존재하지 않음 - 삭제됨

def Rotator():
    """Rotator 구조체"""
    obj = unreal.Rotator()
    open_docs("Rotator")
    return obj

def ScalarParameterValue():
    """ScalarParameterValue 구조체"""
    obj = unreal.ScalarParameterValue()
    open_docs("ScalarParameterValue")
    return obj

def SceneComponent():
    """SceneComponent 생성"""
    obj = unreal.SceneComponent()
    open_docs("SceneComponent")
    return obj

def ScopedEditorTransaction():
    """ScopedEditorTransaction 생성"""
    obj = unreal.ScopedEditorTransaction("")
    return obj
    open_docs("ScopedEditorTransaction")
    return obj

def ScopedSlowTask():
    """ScopedSlowTask 생성"""
    obj = unreal.ScopedSlowTask(1.0, "Test Task")
    return obj
    open_docs("ScopedSlowTask")
    return obj

def SelectedActorIterator():
    """SelectedActorIterator 클래스 정보"""
    obj = unreal.SelectedActorIterator
    open_docs("SelectedActorIterator")
    return obj

def SelectionSet():
    """현재 선택된 액터들"""
    obj = unreal.EditorLevelLibrary.get_selected_level_actors()
    open_docs("Array")
    return obj  # SelectionSet는 Array를 리턴

def Set():
    """Set 클래스 정보"""
    obj = unreal.Set
    open_docs("Set")
    return obj

def SkeletalMesh():
    """SkeletalMesh 생성"""
    obj = unreal.SkeletalMesh()
    open_docs("SkeletalMesh")
    return obj

def SkeletalMeshActor():
    """SkeletalMeshActor 생성"""
    obj = unreal.SkeletalMeshActor()
    open_docs("SkeletalMeshActor")
    return obj

def SkeletalMeshComponent():
    """SkeletalMeshComponent 생성"""
    obj = unreal.SkeletalMeshComponent()
    open_docs("SkeletalMeshComponent")
    return obj

def Skeleton():
    """Skeleton 생성"""
    obj = unreal.Skeleton()
    open_docs("Skeleton")
    return obj

def SoundAttenuation():
    """SoundAttenuation 생성"""
    obj = unreal.SoundAttenuation()
    open_docs("SoundAttenuation")
    return obj

def SoundBase():
    """SoundBase 생성"""
    obj = unreal.SoundBase()
    open_docs("SoundBase")
    return obj

def SoundCue():
    """SoundCue 생성"""
    obj = unreal.SoundCue()
    open_docs("SoundCue")
    return obj

def SoundWave():
    """SoundWave 생성"""
    obj = unreal.SoundWave()
    open_docs("SoundWave")
    return obj

def Sphere():
    """Sphere 구조체"""
    obj = unreal.Sphere()
    open_docs("Sphere")
    return obj

def SplineComponent():
    """SplineComponent 생성"""
    obj = unreal.SplineComponent()
    open_docs("SplineComponent")
    return obj

def SpotLightComponent():
    """SpotLightComponent 생성"""
    obj = unreal.SpotLightComponent()
    open_docs("SpotLightComponent")
    return obj

def StaticMesh():
    """StaticMesh 생성"""
    obj = unreal.StaticMesh()
    open_docs("StaticMesh")
    return obj

def StaticMeshActor():
    """StaticMeshActor 생성"""
    obj = unreal.StaticMeshActor()
    open_docs("StaticMeshActor")
    return obj

def StaticMeshComponent():
    """StaticMeshComponent 생성"""
    obj = unreal.StaticMeshComponent()
    open_docs("StaticMeshComponent")
    return obj

def Struct():
    """Struct 정보"""
    obj = unreal.Struct()
    open_docs("Struct")
    return obj

def StructBase():
    """StructBase 생성"""
    obj = unreal.StructBase()
    open_docs("StructBase")
    return obj

def StructIterator():
    """StructIterator 클래스 정보"""
    obj = unreal.StructIterator
    open_docs("StructIterator")
    return obj

# SubsystemBlueprintLibrary는 존재하지 않음 - 삭제됨

def Text():
    """Text 구조체"""
    obj = unreal.Text()
    open_docs("Text")
    return obj

def Texture():
    """Texture 기본"""
    obj = unreal.Texture()
    open_docs("Texture")
    return obj

def Texture2D():
    """Texture2D 생성"""
    obj = unreal.Texture2D()
    open_docs("Texture2D")
    return obj

def TextureParameterValue():
    """TextureParameterValue 구조체"""
    obj = unreal.TextureParameterValue()
    open_docs("TextureParameterValue")
    return obj

def TextureRenderTarget():
    """TextureRenderTarget 생성"""
    obj = unreal.TextureRenderTarget()
    open_docs("TextureRenderTarget")
    return obj

def TextureRenderTarget2D():
    """TextureRenderTarget2D 생성"""
    obj = unreal.TextureRenderTarget2D()
    open_docs("TextureRenderTarget2D")
    return obj

def TimelineComponent():
    """TimelineComponent 생성"""
    obj = unreal.TimelineComponent()
    open_docs("TimelineComponent")
    return obj

def Timespan():
    """Timespan 구조체"""
    obj = unreal.Timespan()
    open_docs("Timespan")
    return obj

def Transform():
    """Transform 구조체"""
    obj = unreal.Transform()
    open_docs("Transform")
    return obj

def TypeIterator():
    """TypeIterator 클래스 정보"""
    obj = unreal.TypeIterator
    open_docs("TypeIterator")
    return obj

def UserDefinedStruct():
    """UserDefinedStruct 생성"""
    obj = unreal.UserDefinedStruct()
    open_docs("UserDefinedStruct")
    return obj

def UserWidget():
    """UserWidget 생성"""
    obj = unreal.UserWidget()
    open_docs("UserWidget")
    return obj

def ValueDef():
    """ValueDef 클래스 정보"""
    obj = unreal.ValueDef
    open_docs("ValueDef")
    return obj

def Vector():
    """Vector 구조체"""
    obj = unreal.Vector()
    open_docs("Vector")
    return obj

def Vector2D():
    """Vector2D 구조체"""
    obj = unreal.Vector2D()
    open_docs("Vector2D")
    return obj

def Vector4():
    """Vector4 구조체"""
    obj = unreal.Vector4()
    open_docs("Vector4")
    return obj

def VectorParameterValue():
    """VectorParameterValue 구조체"""
    obj = unreal.VectorParameterValue()
    open_docs("VectorParameterValue")
    return obj

def Widget():
    """Widget 기본 클래스"""
    obj = unreal.Widget()
    open_docs("Widget")
    return obj

def WidgetBlueprint():
    """WidgetBlueprint 생성"""
    obj = unreal.WidgetBlueprint()
    open_docs("WidgetBlueprint")
    return obj

def WidgetComponent():
    """WidgetComponent 생성"""
    obj = unreal.WidgetComponent()
    open_docs("WidgetComponent")
    return obj

def World():
    """현재 월드 정보"""
    obj = unreal.EditorLevelLibrary.get_editor_world()
    open_docs("World")
    return obj

def WorldSettings():
    """WorldSettings 생성"""
    obj = unreal.WorldSettings()
    open_docs("WorldSettings")
    return obj

# =============================================================================
# 복합 구조체 - 모든 복잡한 타입들 포함
# =============================================================================

def ComplexUnrealTypes():
    """모든 복잡한 언리얼 타입들을 포함하는 구조체"""
    return {
        "actor": unreal.Actor(),
        "actor_component": unreal.ActorComponent(),
        "anim_sequence": unreal.AnimSequence(),
        "audio_component": unreal.AudioComponent(),
        "behavior_tree": unreal.BehaviorTree(),
        "blueprint": unreal.Blueprint(),
        "bone_reference": unreal.BoneReference(),
        "camera_component": unreal.CameraComponent(),
        "character": unreal.Character(),
        "collision_response": unreal.CollisionResponseContainer(),
        "curve_float": unreal.CurveFloat(),
        "data_table": unreal.DataTable(),
        "directional_light": unreal.DirectionalLightComponent(),
        "hit_result": unreal.HitResult(),
        "material": unreal.Material(),
        "material_parameter_info": unreal.MaterialParameterInfo(),
        "niagara_component": unreal.NiagaraComponent(),
        "particle_component": unreal.ParticleSystemComponent(),
        "pawn": unreal.Pawn(),
        "post_process_settings": unreal.PostProcessSettings(),
        "skeletal_mesh_component": unreal.SkeletalMeshComponent(),
        "sound_wave": unreal.SoundWave(),
        "static_mesh_component": unreal.StaticMeshComponent(),
        "texture_2d": unreal.Texture2D(),
        "user_widget": unreal.UserWidget(),
        "widget_component": unreal.WidgetComponent(),
        "current_world": unreal.EditorLevelLibrary.get_editor_world(),
        "editor_subsystem": unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    }