from django.utils.translation import gettext as _

from arches.app.models import models
from arches.app.models.system_settings import settings
import arches.app.utils.task_management as task_management
import arches.app.tasks as tasks


def update_resource_instance_data_based_on_graph_diff(initial_graph, updated_graph, user):
    if task_management.check_if_celery_available():
        tasks.update_resource_instance_data_based_on_graph_diff.apply_async(
            (initial_graph, updated_graph, user.pk),
        )
    else:
        raise Exception(_('Could not establish a connection with celery. Please ensure celery is running before attempting to update business data.'))
