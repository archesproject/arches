import uuid
from arches.app.models import models
from arches.app.models.tile import Tile

def get_primary_name_from_nodes(resource, config):
    for tile in models.Tile.objects.filter(nodegroup_id=uuid.UUID(config['nodegroup_id']), sortorder=0):
        for node in models.Node.objects.filter(nodegroup_id=uuid.UUID(config['nodegroup_id'])):
            if str(node.nodeid) in tile.data:
                config['string_template'] = config['string_template'].replace('<%s>' % node.name, tile.data[str(node.nodeid)])

    return config['string_template']
