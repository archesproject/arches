from django.db.models import Exists, OuterRef

from arches.app.datatypes import datatypes
from arches.app.models.models import Node, TileModel


class GeojsonFeatureCollectionDataType(datatypes.GeojsonFeatureCollectionDataType):
    def after_update_all(self, tile=None):
        nodes_exist_subquery = Node.objects.filter(
            nodegroup_id=OuterRef("nodegroup_id"),
            datatype="geojson-feature-collection",
        )
        tiles = TileModel.objects.filter(
            resourceinstance=tile.resourceinstance_id
        ).filter(Exists(nodes_exist_subquery))
        for tile in tiles:
            super().after_update_all(tile)
