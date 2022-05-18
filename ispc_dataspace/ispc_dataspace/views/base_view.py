from arches.app.views.base import BaseManagerView
from arches.app.models.tile import Tile

class BaseView(BaseManagerView):

    def get_thumbnail_url_from_images(self, resource_instance, images_nodegroup_id, thumbnail_node_id):
        images_tile = self.get_nodegroup_from_resource_instance(resource_instance, images_nodegroup_id)
        return self.get_thumbnail_url_from_images_tile(images_tile, thumbnail_node_id)
   
    def get_thumbnail_url_from_tiles(self, tiles, images_nodegroup_id, thumbnail_node_id):
        images_tile = self.get_nodegroup_from_tiles(tiles, images_nodegroup_id)
        return self.get_thumbnail_url_from_images_tile(images_tile, thumbnail_node_id)

    def get_thumbnail_url_from_images_tile(self, images_tile, thumbnail_node_id):
        if not images_tile:
                    return None

        return self.get_thumbnail_url(images_tile, thumbnail_node_id)

    def get_nodegroup_from_resource_instance(self, resource_instance, nodegroup_id):
        tiles = Tile.objects.filter(resourceinstance=resource_instance)
        return self.get_nodegroup_from_tiles(tiles, nodegroup_id)

    def get_nodegroup_from_tiles(self, tiles, nodegroup_id):
        try:
            return tiles.get(nodegroup_id=nodegroup_id)
        except Tile.DoesNotExist:
            return None

    def get_thumbnail_url(self, images_tile, thumbnail_node_id):
        try:
            thumbnail_nodes = images_tile.data.get(thumbnail_node_id)
            if thumbnail_nodes:
                thumbnail_node = thumbnail_nodes[0] or None
                return thumbnail_node['url'] or None
        except AttributeError:
            pass

        return None