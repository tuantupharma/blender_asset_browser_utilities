import os
import os.path
from pathlib import Path

import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.types import Operator
from bpy.props import StringProperty, PointerProperty

from asset_browser_utilities.core.ui.message import message_box
from asset_browser_utilities.core.operator.helper import FilterLibraryOperator
from asset_browser_utilities.console.builder import CommandBuilder
from asset_browser_utilities.file.path import is_this_current_file
from asset_browser_utilities.file.save import create_new_file_and_set_as_current, save_file, save_if_possible_and_necessary
from asset_browser_utilities.library.helper import get_blend_library_name, append_asset, item_exists
from .prop import ExportProperties

class BatchExecute:
    def __init__(
        self, asset_names, asset_types, source_file, target_filepath, remove_backup, overwrite, individual_files
    ):
        self.asset_names = asset_names
        self.asset_types = asset_types
        self.current_asset_name = ""
        self.current_asset_type = ""

        self.source_file = Path(str(source_file))
        self.filepath = target_filepath
        self.target_folder = Path(self.filepath).parent

        self.remove_backup = remove_backup
        self.overwrite = overwrite
        self.individual_files = individual_files

    def execute(self):
        if self.individual_files:
            self.execute_next()
        else:
            self.execute_all()

    def execute_all(self):
        self.open_or_create_file(self.filepath)
        bpy.app.timers.register(self.append_all_assets_and_save_file, first_interval=0.1)

    def execute_next(self):
        if self.current_asset_name == "":
            if not self.asset_names:
                message_box(message="Work completed !")
                return
            self.current_asset_name = self.asset_names.pop(0)
            self.current_asset_type = self.asset_types.pop(0)
        new_filepath = self.target_folder / (self.current_asset_name + ".blend")
        self.open_or_create_file(new_filepath)

        bpy.app.timers.register(self.append_asset_and_save_file_and_execute_next, first_interval=0.1)

    def open_or_create_file(self, filepath=None):
        if filepath is None:
            filepath = self.filepath
        if os.path.isfile(filepath):
            bpy.ops.wm.open_mainfile(filepath=str(filepath))
        else:
            create_new_file_and_set_as_current(str(filepath))

    def append_all_assets_and_save_file(self):
        for name, _type in zip(self.asset_names, self.asset_types):
            self.current_asset_name = name
            self.current_asset_type = _type
            if not self.overwrite and item_exists(name, _type):
                continue
            self.append_asset()
        save_file(remove_backup=self.remove_backup)

    def append_asset_and_save_file_and_execute_next(self):
        if self.overwrite or not item_exists(self.current_asset_name, self.current_asset_type):
            self.append_asset()
            save_file(remove_backup=self.remove_backup)
        self.current_asset_name = ""
        self.current_asset_type = ""
        self.execute_next()

    def append_asset(self):
        append_asset(str(self.source_file), self.current_asset_type, self.current_asset_name)


class ASSET_OT_batch_export(Operator, ExportHelper, FilterLibraryOperator):
    "Export Assets"
    bl_idname = "asset.batch_export"
    bl_label = "Export Assets"

    filter_glob: StringProperty(
        default="*.blend",
        options={"HIDDEN"},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    filename_ext = ".blend"

    operator_settings: PointerProperty(type=ExportProperties)

    def invoke(self, context, event):
        self.asset_filter_settings.init(filter_selection=True, filter_assets=True)
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        if is_this_current_file(self.filepath):
            return {"FINISHED"}
        self.populate_asset_and_asset_names()
        if self.operator_settings.open_in_new_blender_instance:
            self.execute_in_new_blender_instance()
        else:
            self.execute_in_this_instance()
        return {"FINISHED"}

    def populate_asset_and_asset_names(self):
        assets = self.asset_filter_settings.get_objects_that_satisfy_filters()
        self.asset_names = [a.name for a in assets]
        self.asset_types = [get_blend_library_name(a) for a in assets]

    def execute_in_new_blender_instance(self):
        caller = CommandBuilder(Path(os.path.realpath(__file__)))
        for name in self.asset_names:
            caller.add_arg_value("asset_names", name)
        for _type in self.asset_types:
            caller.add_arg_value("asset_types", _type)
        caller.add_arg_value("source_file", bpy.data.filepath)
        caller.add_arg_value("filepath", self.filepath)
        caller.add_arg_value("remove_backup", self.library_settings.remove_backup)
        caller.add_arg_value("overwrite", self.operator_settings.overwrite)
        caller.add_arg_value("individual_files", self.operator_settings.individual_files)
        caller.call()

    def execute_in_this_instance(self):
        save_if_possible_and_necessary()
        operator_logic = BatchExecute(
            self.asset_names,
            self.asset_types,
            bpy.data.filepath,
            self.filepath,
            self.library_settings.remove_backup,
            self.operator_settings.overwrite,
            self.operator_settings.individual_files,
        )
        operator_logic.execute()

    def draw(self, context):
        layout = self.layout
        self.operator_settings.draw(layout)
        self.asset_filter_settings.draw(layout)
