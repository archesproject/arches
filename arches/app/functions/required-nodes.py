import uuid
from django.core.exceptions import ValidationError
from arches.app.functions.base import BaseFunction
from arches.app.models import models
from arches.app.models.tile import Tile

class RequiredNodesFunction(BaseFunction):

    def __init__(self, config=None):
        self.config = config

    def save(self, resource, config):
        return self.get_required_nodes(resource, self.config)

    def get_required_nodes(self, tile, config):
        missing_nodes = []
        for required_node in config['required_nodes']:
            if tile['data'][required_node] in ['', None]:
                missing_nodes.append(required_node)

        if missing_nodes != []:
            raise ValidationError('You must complete all required fields before this card can be saved', (',').join(missing_nodes))

        return tile
