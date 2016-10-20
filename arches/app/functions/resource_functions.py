from arches.app.models import models

def get_primary_name_from_nodes(resource, config):
    # eventally use sort order
    config['nodegroupid'] = ''
    config['string_template'] = '{some_nodeid} ({some_other_nodeid})'
    #tile = models.Tile.objects.filter(nodegroup_id=config['nodegroupid'])[0]
    #config['string_template'] % ()
    return 'this is an example primary name'
