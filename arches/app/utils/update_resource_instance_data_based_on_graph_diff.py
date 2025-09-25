import arches.app.utils.task_management as task_management
import arches.app.tasks as tasks


def update_resource_instance_data_based_on_graph_diff(
    initial_graph, updated_graph, user
):
    if task_management.check_if_celery_available():
        tasks.update_resource_instance_data_based_on_graph_diff.apply_async(
            (initial_graph, updated_graph, user.pk),
        )
    else:
        raise task_management.CeleryNotAvailableError()
