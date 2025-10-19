"""
When we want to get a certain asset/file or a folder in Unreal editor, we also
want to get all the latest dependencies of that asset/file or folder.

This commonly happens if we want to transfer/migrate files from two Unreal project/branch
that lives in separate version control system.
"""

import logging
import unreal
import filecmp
import os
import shutil
import util.reference
import util.path

logger = logging.getLogger(__name__)

def migrate(file_paths, source_string, target_string):
    """
    Migrate list of files from source locations to target folders
    Since the source files to move all share the same file root and is meant to be
    moved to a new root, therefore we only need a source and target string replacement

    Example:
    Moving content files from r'C:/Desktop/UnrealProject' to r'D:/UnrealProject'

    :param file_paths: [str]. list of file paths, make sure it's normalized
    :param source_string: str. name of the shared file root for the source files
    :param target_string: str. name of the new target file root for migration
    :return: [str]. list of the file paths in target folders
    """
    target_files = list()

    for asset_path in file_paths:
        # conform target folder location
        dir_name = os.path.dirname(asset_path)
        target_dir = dir_name.replace(source_string, target_string)

        logging.info('moving %s to %s', asset_path, target_dir)
        copy_file(asset_path, target_dir)
        target_files.append(os.path.join(target_dir, os.path.basename(asset_path)))

    return target_files


def flatten_list(lst):
    """
    Flatten nested (multi-level) list to a list with one level

    :param lst: list.
    :return: list. list flattened
    """
    flattened_list = list()
    for element in lst:
        if isinstance(element, list):
            flattened_list.extend(flatten_list(element))
        else:
            flattened_list.append(element)

    return flattened_list


def copy_file(src_file, dst_folder, do_diff=False, force=True):
    
    """
    Copy the file from one place to the other

    :param src_file: str. source file full path
    :param dst_folder: str. destination folder full path
    :param do_diff: bool. whether to do file comparison
                    if the file content are the same, the copy operation will be skipped
    :param force: bool. whether to overwrite target file if one already exists
    :return: bool. whether the copy is successful
    """
    if not os.path.isfile(src_file):
        logger.warning('%s not located', src_file)
        return False

    if not os.path.isdir(dst_folder):
        os.makedirs(dst_folder)

    base_name = os.path.basename(src_file)
    target_file = os.path.join(dst_folder, base_name)
    if os.path.exists(target_file):
        # file already already exists we can choose to overwrite
        if not force:
            return False

        if do_diff and filecmp.cmp(src_file, target_file):
            return False

    shutil.copy(src_file, dst_folder)
    return True

def get_dependencies_from_folder(u_folder_path):
    """
    Get all the downstream dependencies from an Unreal root folder path

    :param u_folder_path: str. Unreal folder path to look for dependencies
    :return: [str]. unique list of Unreal asset dependencies in system path
    """
    dependency_sys_paths = list()

    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    asset_datas = asset_registry.get_assets_by_path(u_folder_path)

    asset_package_paths = [asset_data.get_asset().get_outer().get_path_name()
                           for asset_data in asset_datas]

    for asset_package_path in asset_package_paths:
        dependency_sys_paths.extend(get_dependencies_from_package(asset_package_path))

    seen = set()
    # make it unique
    return [x for x in dependency_sys_paths if x not in seen and not seen.add(x)]


def get_dependencies_from_package(u_package_path):
    """
    Get all the downstream dependencies from an Unreal root asset/package path

    :param u_package_path: str. Unreal package path to look for dependencies
                           we want the outer object path of an asset
                           e.g. ('/Game/Rig/Test' instead of '/Game/Rig/Test.Test')
    :return: [str]. unique list of Unreal asset dependencies in system path
    """
    dependency_sys_paths = list()

    u_reg = unreal.AssetRegistryHelpers.get_asset_registry()

    # soft object reference asset may not exist which will cause issues
    u_options = unreal.AssetRegistryDependencyOptions(
        include_soft_package_references=False,
        include_hard_package_references=True,
        include_searchable_names=False,
        include_soft_management_references=False,
        include_hard_management_references=False
    )

    dependencies = reference.get_dependencies_as_list(
        u_reg,
        u_options,
        u_package_path
    )
    dependencies = util.flatten_list(dependencies)
    for dependency in dependencies:
        # this converts package path to asset full path which determines
        # if it is a folder or a file on disk
        asset = unreal.EditorAssetLibrary.find_asset_data(dependency).get_asset()
        if asset:
            u_path = asset.get_path_name()
            sys_path = path.to_sys_path(u_path)
            dependency_sys_paths.append(sys_path)
        else:
            # throw out error here
            logger.error("File doesn't exist on disk: %s", u_package_path)

    return dependency_sys_paths


if __name__ == '__main__':
    pass
