import uuid
from arches.app.functions.base import BaseFunction
from arches.app.models import models
from arches.app.models.tile import Tile

class PrimaryNameFunction(BaseFunction):
    def get(self, resource, config):
        return self.get_primary_name_from_nodes(resource, config)

    def get_primary_name_from_nodes(self, resource, config):
        for tile in models.TileModel.objects.filter(nodegroup_id=uuid.UUID(config['nodegroup_id']), sortorder=0).filter(resourceinstance__resourceinstanceid=resource.resourceinstanceid):
            for node in models.Node.objects.filter(nodegroup_id=uuid.UUID(config['nodegroup_id'])):
                if str(node.nodeid) in tile.data:
                    value = tile.data[str(node.nodeid)]
                    if value:
                        concept_values = []
                        if node.datatype == 'concept':
                            print tile.data[str(node.nodeid)]
                            concept_values = models.Value.objects.filter(valueid=uuid.UUID(tile.data[str(node.nodeid)]))
                        if len(concept_values) == 1:
                            value = concept_values[0].value
                        config['string_template'] = config['string_template'].replace('<%s>' % node.name, value)

        return config['string_template']
