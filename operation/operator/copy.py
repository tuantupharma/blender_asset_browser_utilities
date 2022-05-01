from asset_browser_utilities.preview.tool import can_preview_be_generated
from bpy.types import Operator, PropertyGroup
from bpy.props import PointerProperty, BoolProperty

from asset_browser_utilities.core.operator.tool import BatchExecute, BatchFolderOperator
from asset_browser_utilities.custom_property.tool import copy_prop, get_prop


class BatchExecuteOverride(BatchExecute):
    def __init__(self, operator, context):
        self.active_asset = context.active_file.local_id
        super().__init__(operator, context)

    def do_on_asset(self, asset):
        if asset == self.active_asset:
            return
        asset_data_source = self.active_asset.asset_data
        asset_data_target = asset.asset_data
        if self.tags:
            tags_source = asset_data_target.tags
            for tag in asset_data_source.tags:
                tags_source.new(name=tag.name, skip_if_exists=True)
        if self.custom_properties:
            for prop_name in asset_data_source.keys():
                copy_prop(asset_data_source, asset_data_target, prop_name)
        if self.preview and can_preview_be_generated(asset):
            source_preview = self.active_asset.preview
            if source_preview is not None:
                asset_preview = asset.preview
                if asset_preview is None:
                    asset.asset_generate_preview()
                if asset_preview is not None:
                    asset_preview.image_pixels.foreach_set(source_preview.image_pixels)
        if self.catalog:
            asset_data_target.catalog_id = asset_data_source.catalog_id
        if self.author:
            asset_data_target.author = asset_data_source.author
        if self.description:
            asset_data_target.description = asset_data_source.description

        super().do_on_asset(asset)


class OperatorProperties(PropertyGroup):
    tags: BoolProperty(name="Tags")
    custom_properties: BoolProperty(name="Custom Properties")
    preview: BoolProperty(name="Preview")
    catalog: BoolProperty(name="Catalog")
    author: BoolProperty(name="Author")
    description: BoolProperty(name="Description")

    def draw(self, layout):
        box = layout.box()
        box.label(text="Copy These Properties From Active Asset")
        box.prop(self, "tags", icon="BOOKMARKS")
        box.prop(self, "custom_properties", icon="PROPERTIES")
        box.prop(self, "preview", icon="SEQ_PREVIEW")
        box.prop(self, "catalog", icon="OUTLINER_COLLECTION")
        box.prop(self, "author", icon="USER")
        box.prop(self, "description", icon="FILE_TEXT")


class ASSET_OT_copy_from_active(Operator, BatchFolderOperator):
    bl_idname = "abu.copy_from_active"
    bl_label = "Copy From Active"

    operator_settings: PointerProperty(type=OperatorProperties)
    logic_class = BatchExecuteOverride

    def invoke(self, context, event):
        return self._invoke(context, filter_assets=True)