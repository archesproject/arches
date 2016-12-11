import uuid
from arches.app.functions.base import BaseFunction
from arches.app.models import models
from arches.app.models.tile import Tile

class RequiredNodesFunction(BaseFunction):
    def get(self, resource, config):
        return self.get_required_nodes(resource, config)

    def get_required_nodes(self, resource, config):
        for tile in models.Tile.objects.filter(nodegroup_id=uuid.UUID(config['nodegroup_id']), sortorder=0):
            for node in models.Node.objects.filter(nodegroup_id=uuid.UUID(config['nodegroup_id'])):
                if str(node.nodeid) in tile.data:
                    config['string_template'] = config['string_template'].replace('<%s>' % node.name, tile.data[str(node.nodeid)])

        return config['string_template']
