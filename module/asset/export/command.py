from pathlib import Path

import bpy

from asset_browser_utilities.core.console.parser import ArgumentsParser
from asset_browser_utilities.core.log.logger import Logger
from asset_browser_utilities.core.file.path import open_file_if_different_from_current
from asset_browser_utilities.core.file.save import create_new_file_and_set_as_current, save_file, sanitize_filepath
from asset_browser_utilities.core.library.tool import append_asset, get_blend_data_name_from_directory
from asset_browser_utilities.module.library.link.tool import replace_asset_with_linked_one


if __name__ == "__main__":
    parser = ArgumentsParser()
    asset_names = parser.get_arg_values(arg_name="asset_names", next_arg_name="asset_types")
    asset_types = parser.get_arg_values(arg_name="asset_types", next_arg_name="asset_folders")
    asset_folders = parser.get_arg_values(arg_name="asset_folders", next_arg_name="source_file")
    source_file = parser.get_arg_value("source_file")
    filepath = parser.get_arg_value("filepath")
    folder = parser.get_arg_value("folder")
    remove_backup = parser.get_arg_value("remove_backup", bool)
    overwrite = parser.get_arg_value("overwrite", bool)
    individual_files = parser.get_arg_value("individual_files", bool)
    catalog_folders = parser.get_arg_value("catalog_folders", bool)
    link_back = parser.get_arg_value("link_back", bool)

    if link_back:
        assets_to_link_back = []
    if individual_files:
        for asset_name, directory, folders in zip(asset_names, asset_types, asset_folders):
            filepath = Path(folder)
            if folders:
                for subfolder in folders.split("/"):
                    filepath /= subfolder
            filepath /= asset_name + ".blend"
            if filepath.exists():
                open_file_if_different_from_current(str(filepath))
            else:
                filepath = create_new_file_and_set_as_current(str(filepath), should_switch_to_asset_workspace=True)
            blend_data_name = get_blend_data_name_from_directory(directory)
            append_asset(source_file, directory, asset_name, overwrite=overwrite)
            if link_back:
                assets_to_link_back.append([str(filepath), directory, asset_name])
            save_file(remove_backup=remove_backup)
            Logger.display(f"Exported Asset '{directory}/{asset_name}' to '{filepath}'")
    else:
        if Path(filepath).exists():
            open_file_if_different_from_current(filepath)
        else:
            filepath = create_new_file_and_set_as_current(filepath, should_switch_to_asset_workspace=True)
        for asset_name, directory in zip(asset_names, asset_types):
            append_asset(source_file, directory, asset_name, overwrite=overwrite)
            if link_back:
                assets_to_link_back.append(str(filepath), directory, asset_name)
            Logger.display(f"Exported Asset '{directory}/{asset_name}' to '{filepath}'")
        save_file(remove_backup=remove_backup)

    if link_back:
        open_file_if_different_from_current(str(source_file))
        for filepath, directory, asset_name in assets_to_link_back:
            blend_data_name = get_blend_data_name_from_directory(directory)
            replace_asset_with_linked_one(
                getattr(bpy.data, blend_data_name)[asset_name],
                filepath,
                directory,
                asset_name,
                create_liboverrides=True,
            )
            save_file(remove_backup=remove_backup)

    quit()
