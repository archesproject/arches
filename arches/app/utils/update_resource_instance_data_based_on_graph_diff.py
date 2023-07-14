import arches.app.tasks as tasks
import arches.app.utils.task_management as task_management

from arches.app.models import models
from django.utils.translation import ugettext as _


def update_resource_instance_data_based_on_graph_diff(initial_graph, updated_graph):
    resource_instances = models.ResourceInstance.objects.filter(graph_publication_id=initial_graph['publication_id'])
    tiles = models.TileModel.objects.filter(resourceinstance__in=resource_instances)

    import pdb; pdb.set_trace()

    for resource_instance in resource_instances:
        resource_instance.graph_publication_id = updated_graph['publication_id']
        resource_instance.save()

    # if task_management.check_if_celery_available():
    #     tasks.foo.apply_async(
    #         initial_graph=initial_graph,
    #         updated_graph=updated_graph
    #     )
