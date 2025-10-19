import os
import unreal

class UINames:
    """
    에디터 UI 컨텍스트 이름(FName)을 모아놓은 클래스입니다.
    사용법: from editor_contexts import Contexts
    예시: Contexts.LEVEL_EDITOR_TOOLBAR
    """

    # ----------------------------------------------------------------------
    # 레벨 에디터 (Level Editor)
    # ----------------------------------------------------------------------
    LEVEL_EDITOR_MAIN_MENU = "LevelEditor.MainMenu"
    LEVEL_EDITOR_MAIN_MENU_TOOLS = "LevelEditor.MainMenu.Tools"
    LEVEL_EDITOR_TOOLBAR = "LevelEditor.LevelEditorToolBar"
    LEVEL_EDITOR_ASSETS_TOOLBAR = "LevelEditor.LevelEditorToolBar.AssetsToolBar"
    LEVEL_EDITOR_ACTOR_CONTEXT_MENU = "LevelEditor.ActorContextMenu"
    LEVEL_EDITOR_VIEWPORT_CONTEXT_MENU = "LevelEditor.ViewportContextMenu"

    # ----------------------------------------------------------------------
    # 콘텐츠 브라우저 (Content Browser)
    # ----------------------------------------------------------------------
    CONTENT_BROWSER_TOOLBAR = "ContentBrowser.ToolBar"
    CONTENT_BROWSER_ADD_MENU = "ContentBrowser.AddContextMenu"
    CONTENT_BROWSER_FOLDER_CONTEXT_MENU = "ContentBrowser.FolderContextMenu"
    CONTENT_BROWSER_ASSET_CONTEXT_MENU = "ContentBrowser.AssetContextMenu"
    # 특정 애셋 타입 컨텍스트 메뉴
    CONTENT_BROWSER_ASSET_BLUEPRINT = "ContentBrowser.AssetContextMenu.Blueprint"
    CONTENT_BROWSER_ASSET_STATIC_MESH = "ContentBrowser.AssetContextMenu.StaticMesh"
    CONTENT_BROWSER_ASSET_SKELETAL_MESH = "ContentBrowser.AssetContextMenu.SkeletalMesh"
    CONTENT_BROWSER_ASSET_MATERIAL = "ContentBrowser.AssetContextMenu.Material"
    CONTENT_BROWSER_ASSET_TEXTURE = "ContentBrowser.AssetContextMenu.Texture"
    
    # ----------------------------------------------------------------------
    # 블루프린트 에디터 (Blueprint Editor)
    # ----------------------------------------------------------------------
    BLUEPRINT_EDITOR_TOOLBAR = "BlueprintEditor.ToolBar"
    BLUEPRINT_EDITOR_COMPONENTS_TOOLBAR = "BlueprintEditor.ComponentsToolbar"
    BLUEPRINT_EDITOR_GRAPH_CONTEXT_MENU = "BlueprintEditor.GraphContextMenu"
    BLUEPRINT_EDITOR_FUNCTIONS_CONTEXT_MENU = "BlueprintEditor.FunctionsContextMenu"
    BLUEPRINT_EDITOR_VARIABLES_CONTEXT_MENU = "BlueprintEditor.VariablesContextMenu"
    BLUEPRINT_EDITOR_GRAPH_NODE_MENU = "K2Node.NodeMenu" # 노드 추가 메뉴

    # ----------------------------------------------------------------------
    # 기타 에디터 (Others)
    # ----------------------------------------------------------------------
    STATIC_MESH_EDITOR_TOOLBAR = "StaticMeshEditor.ToolBar"
    SKELETAL_MESH_EDITOR_TOOLBAR = "SkeletalMeshEditor.ToolBar"
    SKELETAL_MESH_EDITOR_SKELETON_TREE_MENU = "SkeletalMeshEditor.SkeletonTree.ContextMenu"
    MATERIAL_EDITOR_TOOLBAR = "MaterialEditor.ToolBar"
    MATERIAL_EDITOR_GRAPH_MENU = "MaterialGraph.Menu"

def get_selected_asset():
    """
    Get selected assets in content browser

    :return: [unreal.Object].
    """
    return unreal.EditorUtilityLibrary.get_selected_assets()


def get_asset(path):
    """
    Get asset of a Unreal path

    :param path: str. relative Unreal path
    :return: unreal.Object
    """
    return unreal.EditorAssetLibrary.find_asset_data(path).get_asset()


def get_assets_from_folder(folder):
    """
    Get certain types of assets from a directory

    :param folder: str. search directory
    :return: [unreal.Object].
    """
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    asset_datas = asset_registry.get_assets_by_path(folder)

    return [asset_data.get_asset() for asset_data in asset_datas]


def filter_assets(assets, typ):
    """
    Filter to get certain type of Unreal asset

    :param assets: [unreal.Object]. list of assets to filter
    :param typ: unreal.Class. asset type to filter
    :return: [unreal.Object].
    """
    return [asset for asset in assets if isinstance(asset, typ)]


def create_folder(root, name):
    """
    Create a Unreal sub folder

    :param root: str. directory root
    :param name: str. Unreal folder name
    :return: bool. whether the creation is successful
    """
    path = os.path.join(root, name)
    if not unreal.EditorAssetLibrary.make_directory(path):
        return None

    return path


def get_actor(label):
    """
    Get actor from label in the current level/world

    this can't get all actors:
    `actors = unreal.EditorActorSubsystem().get_all_level_actors()`

    :param label: str. display label (different from actor name)
    :return: unreal.Actor
    """
    actors = unreal.GameplayStatics.get_all_actors_of_class(
        unreal.EditorLevelLibrary.get_editor_world(),
        unreal.Actor)

    matches = [actor for actor in actors if label == actor.get_actor_label()]
    if not matches:
        return None
    else:
        return matches[0]
