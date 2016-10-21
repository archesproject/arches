import uuid, re
from arches.app.models import models
from arches.app.models.tile import Tile

def get_primary_name_from_nodes(resource, config):
    # eventally use sort order
    #uuid_regex = '(?P<nodeid>[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})'
    # x = {}
    # for match in re.findall(uuid_regex, config['string_template']):
    #     x[match] = ''

    for tile in models.Tile.objects.filter(nodegroup_id=uuid.UUID(config['nodegroup_id'])):
        t = Tile(tile)
        t.get_node_display_values()
        for nodeid, nodevalue in t.data.iteritems():
            #x[nodeid] = nodevalue
            print nodevalue
            config['string_template'] = config['string_template'].replace('{%s}' % nodeid, nodevalue)

    return config['string_template']
