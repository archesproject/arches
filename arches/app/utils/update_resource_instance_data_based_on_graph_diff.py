from django.utils.translation import ugettext as _

from arches.app.models import models
from arches.app.models.system_settings import settings
import arches.app.utils.task_management as task_management
import arches.app.tasks as tasks


def update_resource_instance_data_based_on_graph_diff(initial_graph, updated_graph):
    resource_instances = models.ResourceInstance.objects.filter(graph_publication_id=initial_graph['publication_id'])

    initial_nodegroup_ids_to_cardinality = {}
    for initial_nodegroup in initial_graph['nodegroups']:
        initial_nodegroup_ids_to_cardinality[initial_nodegroup['nodegroupid']] = initial_nodegroup['cardinality']

    updated_nodegroup_ids_to_node_ids = {}
    for updated_node in updated_graph['nodes']:
        if not updated_nodegroup_ids_to_node_ids.get(updated_node['nodegroup_id']):
            updated_nodegroup_ids_to_node_ids[updated_node['nodegroup_id']] = []

        updated_nodegroup_ids_to_node_ids[updated_node['nodegroup_id']].append(updated_node['nodeid'])

    initial_node_ids_to_default_values = {}
    for initial_widget in initial_graph['widgets']:
        initial_node_ids_to_default_values[initial_widget['node_id']] = initial_widget['config']['defaultValue']

    updated_node_ids_to_default_values = {}
    for updated_widget in updated_graph['widgets']:
        updated_node_ids_to_default_values[updated_widget['node_id']] = updated_widget['config']['defaultValue']

    # delete extra tiles on nodegroup cardinality change
    for updated_nodegroup in updated_graph['nodegroups']:
        if updated_nodegroup['cardinality'] == '1' and initial_nodegroup_ids_to_cardinality.get(updated_nodegroup['nodegroupid']) == 'n':
            for tile in models.TileModel.objects.filter(nodegroup_id=updated_nodegroup['nodegroupid']):
                if tile.sortorder != 0:
                    tile.delete()

    # add/remove nodes and change default values
    for tile in models.TileModel.objects.filter(resourceinstance__in=resource_instances):
        updated_node_ids = updated_nodegroup_ids_to_node_ids[str(tile.nodegroup_id)]
        
        # delete nodes not in updated graph
        for node_id in list(tile.data.keys()):
            if node_id not in updated_node_ids:
                del tile.data[node_id]

        # add nodes that only exist in updated graph
        # or update nodes default value if changed
        for node_id in updated_node_ids:
            if (
                node_id not in tile.data.keys()  # node added to tile
                or tile.data[node_id] == initial_node_ids_to_default_values.get(node_id)  # default value change
            ):
                tile.data[node_id] = updated_node_ids_to_default_values.get(node_id)
                    
        tile.save()


    for resource_instance in resource_instances:
        resource_instance.graph_publication_id = updated_graph['publication_id']
        resource_instance.save()

    # if task_management.check_if_celery_available():
    #     tasks.foo.apply_async(
    #         initial_graph=initial_graph,
    #         updated_graph=updated_graph
    #     )
