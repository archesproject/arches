import uuid
from arches.app.functions.base import BaseFunction
from arches.app.models import models
from arches.app.models.tile import Tile
from arches.app.datatypes.datatypes import DataTypeFactory

class PrimaryDescriptorsMultipleFunction(BaseFunction):

    def get_primary_descriptor_from_nodes(self, resource, config):
        try:

            #NEXUS Afegim varis nodes
            elements = []
            if(isinstance(config['nodegroup_id'], list)):
                elements = config['nodegroup_id']
            else:
                elements = [config['nodegroup_id']]

            for element in elements:
                for tile in models.TileModel.objects.filter(nodegroup_id=uuid.UUID(element), sortorder=0).filter(resourceinstance_id=resource.resourceinstanceid):
                    for node in models.Node.objects.filter(nodegroup_id=uuid.UUID(element)):
                        if str(node.nodeid) in tile.data:
                            datatype_factory = DataTypeFactory()
                            datatype = datatype_factory.get_instance(node.datatype)
                            value = datatype.get_display_value(tile, node)
                            config['string_template'] = config['string_template'].replace('<%s>' % node.name, value)


        except ValueError as e:
            print e, 'invalid nodegroupid'

        return config['string_template']
