from bpy.types import PropertyGroup
from bpy.props import PointerProperty

from asset_browser_utilities.core.filter.type import FilterTypes, get_object_types, get_types
from asset_browser_utilities.core.filter.name import FilterName
from asset_browser_utilities.core.filter.selection import FilterSelection
from asset_browser_utilities.core.filter.container import AssetContainer
from asset_browser_utilities.core.filter.catalog import FilterCatalog
from asset_browser_utilities.core.filter.asset import FilterAssets
from asset_browser_utilities.core.tool import copy_simple_property_group
from asset_browser_utilities.core.cache.tool import get_from_cache
from asset_browser_utilities.core.library.prop import LibraryExportSettings, LibraryType


class AssetFilterSettings(PropertyGroup):
    filter_types: PointerProperty(type=FilterTypes)
    filter_name: PointerProperty(type=FilterName)
    filter_selection: PointerProperty(type=FilterSelection)
    filter_catalog: PointerProperty(type=FilterCatalog)
    filter_assets: PointerProperty(type=FilterAssets)

    def init_asset_filter_settings(
        self,
        filter_selection=False,
        filter_assets=False,
        filter_assets_optional=False,
        filter_selection_allow_view_3d=True,
        filter_selection_allow_asset_browser=True,
        filter_types=True,
    ):
        self.filter_selection.init(
            allow=filter_selection and get_from_cache(LibraryExportSettings).source == LibraryType.FileCurrent.value,
            allow_view_3d=filter_selection_allow_view_3d,
            allow_asset_browser=filter_selection_allow_asset_browser,
        )
        self.filter_assets.allow = filter_assets
        self.filter_assets.optional = filter_assets_optional
        self.filter_catalog.allow = filter_assets
        self.filter_types.allow = filter_types

    def get_objects_that_satisfy_filters(self):
        data_containers = (
            list(self.filter_types.types) if self.filter_types.types_global_filter else [t[0] for t in get_types()]
        )
        object_types = (
            list(self.filter_types.types_object)
            if (self.filter_types.types_object_filter and self.filter_types.types_global_filter)
            else [t[0] for t in get_object_types()]
        )
        asset_container = AssetContainer(data_containers, object_types)
        if self.filter_assets.active:
            asset_container.filter_assets()
            if self.filter_catalog.active:
                asset_container.filter_by_catalog(self.filter_catalog.catalog_uuid)
        if self.filter_name.active:
            asset_container.filter_by_name(
                self.filter_name.method,
                self.filter_name.value,
                self.filter_name.case_sensitive,
            )
        asset_container.filter_by_selection(self.filter_selection)
        return list(asset_container.all_assets)

    def draw(self, layout, context):
        box = layout.box()
        if self.filter_assets.allow:
            self.filter_assets.draw(box)
        if self.filter_assets.active:
            self.filter_selection.draw(box)
            if self.filter_types.allow:
                self.filter_types.draw(box)
            self.filter_name.draw(box, name_override="Assets")
            if self.filter_catalog.allow:
                self.filter_catalog.draw(box, context)

    def copy_from(self, other):
        # Other is the source, self is the target
        copy_simple_property_group(other, self)
        copy_simple_property_group(other.filter_assets, self.filter_assets)
        copy_simple_property_group(other.filter_types, self.filter_types)
        copy_simple_property_group(other.filter_name, self.filter_name)
        copy_simple_property_group(other.filter_selection, self.filter_selection)
        copy_simple_property_group(other.filter_catalog, self.filter_catalog)
