from django.test import TestCase
from unittest.mock import patch, MagicMock

from arches.app.models.system_settings import settings
from arches.extensions.controlled_lists.search_indexes.reference_index import (
    ReferenceIndex,
)


class ReferenceIndexTests(TestCase):
    def setUp(self):
        self.reference_index = ReferenceIndex(index_name=settings.REFERENCES_INDEX_NAME)

    @patch(
        "arches.extensions.controlled_lists.search_indexes.reference_index.SearchEngineInstance"
    )
    @patch("arches.extensions.controlled_lists.search_indexes.reference_index.Query")
    def test_get_term_results(self, mock_search_engine, mock_query):
        mock_results = {
            "aggregations": {
                "label_agg": {
                    "buckets": [
                        {
                            "key": "label1",
                            "list_name_agg": {
                                "buckets": [
                                    {
                                        "key": "list1",
                                        "item_agg": {"buckets": [{"key": "item1"}]},
                                    }
                                ]
                            },
                        }
                    ]
                }
            }
        }
        mock_query.search.return_value = mock_results
        mock_search_engine.return_value = mock_query

        term_results = ReferenceIndex.search_terms("search_string", lang="en")

        self.assertEqual(len(term_results), 1)
        self.assertEqual(term_results[0]["text"], "label1")
        self.assertEqual(term_results[0]["context_label"], "list1")
        self.assertEqual(term_results[0]["value"], "item1")

    def test_get_documents_to_index(self):
        resourceinstance = MagicMock()
        tiles = MagicMock()
        documents, _ = self.reference_index.get_documents_to_index(
            resourceinstance, tiles
        )
        self.assertIsNone(documents)
