import uuid

from django.conf import settings
from django.test import TestCase

from arches.app.models.graph import Graph
from arches.app.models.models import (
    EditLog,
    ResourceInstance,
    ResourceInstanceLifecycle,
)
from arches.app.utils.transaction import reverse_edit_log_entries

# these tests can be run from the command line via
# python manage.py test tests.utils.test_transactions --settings="tests.test_settings"


class TestTransactions(TestCase):
    def test_reverse_edit_log_entries_errors_if_publication_differs(self):
        transaction_id = uuid.uuid4()
        graph = Graph.objects.create_graph()
        lifecycle = ResourceInstanceLifecycle.objects.get(
            pk=settings.DEFAULT_RESOURCE_INSTANCE_LIFECYCLE_ID
        )
        state = lifecycle.resource_instance_lifecycle_states.first()
        resource = ResourceInstance.objects.create(
            graph=graph,
            graph_publication=graph.publication,
            resource_instance_lifecycle_state=state,
        )
        EditLog.objects.create(
            transactionid=str(transaction_id), resourceinstanceid=str(resource.pk)
        )

        graph.publish()

        with self.assertRaises(RuntimeError):
            reverse_edit_log_entries(transaction_id=transaction_id)
