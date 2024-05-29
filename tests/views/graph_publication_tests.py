from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client
from unittest.mock import patch, MagicMock
from arches.app.models.graph import Graph

class GraphPublicationViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser')
        self.client.force_login(self.user)
        self.graph = Graph.new()
        self.graph.save()

    @patch('arches.app.views.graph.update_resource_instance_data_based_on_graph_diff')
    @patch('arches.app.models.graph.Graph.get_published_graph')
    @patch('arches.app.models.graph.Graph.update_from_editable_future_graph')
    @patch('arches.app.models.graph.Graph.publish')
    def test_publish_graph_updating_resource_instance_data(self, mock_publish, mock_update, mock_get_published_graph, mock_update_resource_instance_data):
        mock_get_published_graph.return_value = MagicMock(serialized_graph='serialized_graph')
        self.graph.source_identifier_id = None
        self.graph.save()

        url = reverse('publish_graph', args=[self.graph.pk])
        data = {
            "notes": "Some notes",
            "shouldUpdateResourceInstanceData": True
        }
        response = self.client.post(url, data, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        mock_update.assert_called_once()
        mock_publish.assert_called_once_with(notes='Some notes', user=self.user)
        mock_get_published_graph.assert_called()
        mock_update_resource_instance_data.assert_called_once()

    @patch('arches.app.views.graph.update_resource_instance_data_based_on_graph_diff')
    @patch('arches.app.models.graph.Graph.get_published_graph')
    @patch('arches.app.models.graph.Graph.update_from_editable_future_graph')
    @patch('arches.app.models.graph.Graph.publish')
    def test_publish_graph_without_updating_resource_instance_data(self, mock_publish, mock_update, mock_get_published_graph, mock_update_resource_instance_data):
        mock_get_published_graph.return_value = MagicMock(serialized_graph='serialized_graph')
        self.graph.source_identifier_id = None
        self.graph.save()

        url = reverse('publish_graph', args=[self.graph.pk])
        data = {
            "notes": "Some notes",
            "shouldUpdateResourceInstanceData": False
        }
        response = self.client.post(url, data, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        mock_update.assert_called_once()
        mock_publish.assert_called_once_with(notes='Some notes', user=self.user)
        mock_get_published_graph.assert_not_called()
        mock_update_resource_instance_data.assert_not_called()

    @patch('arches.app.views.graph.update_resource_instance_data_based_on_graph_diff')
    @patch('arches.app.models.graph.Graph.get_published_graph')
    @patch('arches.app.models.graph.Graph.update_from_editable_future_graph')
    @patch('arches.app.models.graph.Graph.publish')
    @patch('arches.app.views.graph.logger')
    def test_publish_graph_exception(self, mock_logger, mock_publish, mock_update, mock_get_published_graph, mock_update_resource_instance_data):
        mock_get_published_graph.side_effect = Exception('Test exception')
        self.graph.source_identifier_id = None
        self.graph.save()

        url = reverse('publish_graph', args=[self.graph.pk])
        data = {
            "notes": "Some notes",
            "shouldUpdateResourceInstanceData": True
        }
        response = self.client.post(url, data, content_type='application/json')

        self.assertEqual(response.status_code, 500)
        mock_logger.exception.assert_called_once()
        self.assertDictEqual(
            response.json(), 
            {
                'message': 'Please contact your administrator if issue persists', 
                'status': 'false', 
                'success': False, 
                'title': 'Unable to process publication'
            }
        )

    @patch('arches.app.models.graph.Graph.revert')
    def test_revert_graph(self, mock_revert):
        self.graph.source_identifier_id = None
        self.graph.save()

        url = reverse('revert_graph', args=[self.graph.pk])
        response = self.client.post(url, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        mock_revert.assert_called_once()
        self.assertEqual(response.json()['message'], "The graph has been reverted. Please click the OK button to reload the page.")

    @patch('arches.app.models.graph.Graph.revert')
    @patch('arches.app.views.graph.logger')
    def test_revert_graph_exception(self, mock_logger, mock_revert):
        mock_revert.side_effect = Exception('Test exception')
        self.graph.source_identifier_id = None
        self.graph.save()

        url = reverse('revert_graph', args=[self.graph.pk])
        response = self.client.post(url, content_type='application/json')

        self.assertEqual(response.status_code, 500)
        mock_logger.exception.assert_called_once()
        self.assertDictEqual(
            response.json(), 
            {
                'message': 'Please contact your administrator if issue persists', 
                'status': 'false', 
                'success': False, 
                'title': 'Unable to process publication'
            }
        )

    @patch('arches.app.models.graph.Graph.update_published_graphs')
    def test_update_published_graphs(self, mock_update_published_graphs, ):
        self.graph.source_identifier_id = None
        self.graph.save()

        url = reverse('update_published_graphs', args=[self.graph.pk])
        data = {
            "notes": "Some notes"
        }
        response = self.client.post(url, data, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        mock_update_published_graphs.assert_called_once_with(notes='Some notes', user=self.user)
        self.assertEqual(response.json()['message'], "The published graphs have been successfully updated.")

    @patch('arches.app.models.graph.Graph.update_published_graphs')
    @patch('arches.app.views.graph.logger')
    def test_update_published_graphs_exception(self, mock_logger, mock_update_published_graphs):
        mock_update_published_graphs.side_effect = Exception('Test exception')
        self.graph.source_identifier_id = None
        self.graph.save()

        url = reverse('update_published_graphs', args=[self.graph.pk])
        data = {
            "notes": "Some notes"
        }
        response = self.client.post(url, data, content_type='application/json')

        self.assertEqual(response.status_code, 500)
        mock_logger.exception.assert_called_once()
        self.assertDictEqual(
            response.json(), 
            {
                'message': 'Please contact your administrator if issue persists', 
                'status': 'false', 
                'success': False, 
                'title': 'Unable to update published graphs'
            }
        )

    @patch('arches.app.models.graph.Graph.restore_state_from_serialized_graph')
    @patch('arches.app.models.models.PublishedGraph.objects.get')
    def test_restore_state_from_serialized_graph(self, mock_get_published_graph, mock_restore_state):
        mock_get_published_graph.return_value = MagicMock(serialized_graph='serialized_graph')
        self.graph.source_identifier_id = None
        self.graph.save()

        url = reverse('restore_state_from_serialized_graph', args=[self.graph.pk])
        response = self.client.post(url, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        mock_get_published_graph.assert_called_once()
        mock_restore_state.assert_called_once_with('serialized_graph')
        self.assertEqual(response.json()['message'], "The graph has been successfully restored.")

    @patch('arches.app.models.graph.Graph.restore_state_from_serialized_graph')
    @patch('arches.app.models.models.PublishedGraph.objects.get')
    @patch('arches.app.views.graph.logger')
    def test_restore_state_from_serialized_graph_exception(self, mock_logger, mock_get_published_graph, mock_restore_state):
        mock_get_published_graph.side_effect = Exception('Test exception')
        self.graph.source_identifier_id = None
        self.graph.save()

        url = reverse('restore_state_from_serialized_graph', args=[self.graph.pk])
        response = self.client.post(url, content_type='application/json')

        self.assertEqual(response.status_code, 500)
        mock_logger.exception.assert_called_once()
        self.assertDictEqual(
            response.json(), 
            {
                'message': 'Please contact your administrator if issue persists', 
                'status': 'false', 
                'success': False, 
                'title': 'Unable to restore state from serialized graph'
            }
        )