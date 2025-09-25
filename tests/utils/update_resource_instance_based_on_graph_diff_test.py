from django.test import TestCase
from unittest.mock import patch, MagicMock
from django.contrib.auth.models import User
from arches.app.utils.update_resource_instance_data_based_on_graph_diff import (
    update_resource_instance_data_based_on_graph_diff,
)


class UpdateResourceInstanceDataBasedOnGraphDiffTest(TestCase):

    @patch(
        "arches.app.utils.task_management.check_if_celery_available", return_value=True
    )
    @patch(
        "arches.app.tasks.update_resource_instance_data_based_on_graph_diff.apply_async"
    )
    def test_update_resource_instance_data_task_scheduled(
        self, mock_apply_async, mock_check_celery
    ):
        initial_graph = MagicMock()
        updated_graph = MagicMock()
        user = User.objects.create_user("testuser")

        update_resource_instance_data_based_on_graph_diff(
            initial_graph, updated_graph, user
        )

        mock_check_celery.assert_called_once()
        mock_apply_async.assert_called_once_with(
            (initial_graph, updated_graph, user.pk)
        )

    @patch(
        "arches.app.utils.task_management.check_if_celery_available", return_value=False
    )
    def test_update_resource_instance_data_celery_not_available(
        self, mock_check_celery
    ):
        initial_graph = MagicMock()
        updated_graph = MagicMock()
        user = User.objects.create_user("testuser")

        with self.assertRaises(Exception) as context:
            update_resource_instance_data_based_on_graph_diff(
                initial_graph, updated_graph, user
            )

        self.assertEqual(
            str(context.exception),
            "Celery is not available. Please check your configuration.",
        )
        mock_check_celery.assert_called_once()
