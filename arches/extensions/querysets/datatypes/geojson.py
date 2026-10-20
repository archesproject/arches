from arches.app.datatypes import datatypes
from arches.app.models.models import Node


class GeojsonFeatureCollectionDataType(datatypes.GeojsonFeatureCollectionDataType):
    def after_update_all(self, tile=None, changed_tiles=None):
        if changed_tiles is None:
            return super().after_update_all(tile)
        for tile in changed_tiles:
            if any(
                node.datatype == "geojson-feature-collection"
                for node in tile.nodegroup.node_set.all()
            ):
                super().after_update_all(tile)
