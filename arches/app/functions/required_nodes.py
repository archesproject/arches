import uuid
from django.core.exceptions import ValidationError
from arches.app.functions.base import BaseFunction
from arches.app.models import models
from arches.app.models.tile import Tile
import json

class RequiredNodesFunction(BaseFunction):

    def save(self, resource, config):
        message = 'You must complete all required fields before this card can be saved. The following fields are required:'
        return self.check_for_required_nodes(resource, self.config, message)

    def on_import(self, resource):
        message = 'The following nodes require values - '
        return self.check_for_required_nodes(resource, self.config, message, True)

    def check_for_required_nodes(self, tile, config, message, return_id=False):
        missing_nodes = []
        required_node_groups = json.loads(config['required_nodes'])
        required_nodes = required_node_groups[self.nodegroup_id]
        for required_node in required_nodes:
            try:
                tile_data = tile.data
            except AttributeError as e:
                tile_data = tile['data']

            if tile_data[required_node] in ['', None]:
                result = models.Node.objects.get(pk=required_node).name
                if return_id == True:
                    result = '{0}: {1}'.format(result, required_node)
                missing_nodes.append(result)

        if missing_nodes != []:
            raise ValidationError(message, (', ').join(missing_nodes))

        return tile
