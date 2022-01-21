from bpy.props import PointerProperty
from asset_browser_utilities.filter.main import AssetFilterSettings
from asset_browser_utilities.library.prop import LibraryExportSettings, LibraryType


class FilterOperator:
    asset_filter_settings: PointerProperty(type=AssetFilterSettings)


class LibraryOperator:
    library_settings: PointerProperty(type=LibraryExportSettings)


class FilterLibraryOperator(FilterOperator, LibraryOperator):
    def _invoke(self, context, remove_backup=True, filter_assets=False):
        self.library_settings.init(remove_backup=remove_backup)
        if self.library_settings.library_type == LibraryType.FileOrFolder.value:
            self.asset_filter_settings.init(filter_selection=False, filter_assets=filter_assets)
            context.window_manager.fileselect_add(self)
            return {"RUNNING_MODAL"}
        else:
            self.asset_filter_settings.init(filter_selection=True, filter_assets=filter_assets)
            return context.window_manager.invoke_props_dialog(self)
