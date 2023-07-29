from django.utils.translation import ugettext as _

from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models import models
from arches.app.models.system_settings import settings
import arches.app.utils.task_management as task_management
import arches.app.tasks as tasks


def update_resource_instance_data_based_on_graph_diff(initial_graph, updated_graph):
    resource_instances = models.ResourceInstance.objects.filter(graph_publication_id=initial_graph['publication_id'])

    initial_node_ids_to_nodegroup_ids = {}
    for initial_node in initial_graph['nodes']:
        initial_node_ids_to_nodegroup_ids[initial_node['nodeid']] = initial_node['nodegroup_id']

    moved_nodes = {}  # node_id: {'from': nodegroup_id, 'to': nodegroup_id}
    updated_nodegroup_ids_to_node_ids = {}
    for updated_node in updated_graph['nodes']:
        if not updated_nodegroup_ids_to_node_ids.get(updated_node['nodegroup_id']):
            updated_nodegroup_ids_to_node_ids[updated_node['nodegroup_id']] = []

        updated_nodegroup_ids_to_node_ids[updated_node['nodegroup_id']].append(updated_node['nodeid'])

        initial_nodegroup_id = initial_node_ids_to_nodegroup_ids.get(updated_node['nodeid'])
        if initial_nodegroup_id is not None and initial_nodegroup_id != updated_node['nodegroup_id']:
            moved_nodes[updated_node['nodeid']] = {'from': initial_nodegroup_id, 'to': updated_node['nodegroup_id']}

    updated_node_ids_to_datatypes = {}
    for updated_node in updated_graph['nodes']:
        updated_node_ids_to_datatypes[updated_node['nodeid']] = updated_node['datatype']

    initial_node_ids_to_default_values = {}
    for initial_widget in initial_graph['widgets']:
        initial_node_ids_to_default_values[initial_widget['node_id']] = initial_widget['config']['defaultValue']

    updated_node_ids_to_default_values = {}
    for updated_widget in updated_graph['widgets']:
        updated_node_ids_to_default_values[updated_widget['node_id']] = updated_widget['config']['defaultValue']

    datatype_factory = DataTypeFactory()

    # first, explicity move nodes between nodegroups
    for resource_instance in resource_instances:
        for key, value in moved_nodes.items():
            from_tile = models.TileModel.objects.get(nodegroup_id=value['from'], resource_instance=resource_instance)
            to_tile = models.TileModel.objects.get(nodegroup_id=value['to'], resource_instance=resource_instance)

            to_tile.tiledata[key] = from_tile.tiledata[key]
            del from_tile.tiledata[key]

            from_tile.save()
            to_tile.save()

    # then, add/remove nodes and change default values
    for tile in models.TileModel.objects.filter(resourceinstance__in=resource_instances):
        updated_node_ids = updated_nodegroup_ids_to_node_ids[str(tile.nodegroup_id)]
        
        # delete nodes not in updated graph
        for node_id in tile.data.keys():
            if node_id not in updated_node_ids:
                del tile.data[node_id]

        # add nodes that only exist in updated graph
        # or update nodes default value if changed
        for node_id in updated_node_ids:
            if node_id not in tile.data.keys():
                value = updated_node_ids_to_default_values.get(node_id)

                # if not value:
                    # datatype_instance = datatype_factory.get_instance(updated_node_ids_to_datatypes[node_id])
                    # value = datatype_instance.transform_value_for_tile(None)  #TODO: cbyrd need to create new datatype method for empty value generation

                tile.data['node_id'] = value
                    
            elif tile.data[node_id] == initial_node_ids_to_default_values.get(node_id):
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
