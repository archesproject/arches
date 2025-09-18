from django.utils import timezone
from tests.base_test import ArchesTestCase

from arches.app.models.graph import Graph
from arches.app.models.models import GraphXPublishedGraph, Language


class GraphXPublishedGraphTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.graph = Graph.objects.create_graph(name="Publication Lookup Tests")
        cls.link = GraphXPublishedGraph.objects.create(
            graph=cls.graph,
            notes="test link",
            published_time=timezone.now(),
        )

        cls.lang_en, _ = Language.objects.get_or_create(
            code="en", defaults={"name": "English"}
        )
        cls.lang_en_us, _ = Language.objects.get_or_create(
            code="en-US", defaults={"name": "English (US)"}
        )
        cls.lang_es, _ = Language.objects.get_or_create(
            code="es", defaults={"name": "Spanish"}
        )
        cls.lang_es_mx, _ = Language.objects.get_or_create(
            code="es-MX", defaults={"name": "Spanish (MX)"}
        )
        cls.lang_fr, _ = Language.objects.get_or_create(
            code="fr", defaults={"name": "French"}
        )

    def test_exact_match_is_case_and_separator_insensitive(self):
        publication_en_us = self.link.publishedgraph_set.create(
            language=self.lang_en_us
        )

        with self.assertNumQueries(1):
            result_one = self.link.find_publication_in_language("en_us")
        self.assertEqual(result_one.pk, publication_en_us.pk)

        with self.assertNumQueries(0):
            result_two = self.link.find_publication_in_language("EN-us")
        self.assertEqual(result_two.pk, publication_en_us.pk)

    def test_falls_back_to_primary_language_when_region_not_found(self):
        publication_en = self.link.publishedgraph_set.create(language=self.lang_en)

        with self.assertNumQueries(2):
            result = self.link.find_publication_in_language("en-US")
        self.assertEqual(result.pk, publication_en.pk)

        with self.assertNumQueries(0):
            cached = self.link.find_publication_in_language("en-us")
        self.assertEqual(cached.pk, publication_en.pk)

    def test_returns_none_and_caches_none_when_no_match_any_level(self):
        with self.assertNumQueries(2):
            result_one = self.link.find_publication_in_language("fr-CA")
        self.assertIsNone(result_one)

        with self.assertNumQueries(0):
            result_two = self.link.find_publication_in_language("fr_ca")
        self.assertIsNone(result_two)

    def test_cache_invalidation_via_refresh_from_db(self):
        publication_en = self.link.publishedgraph_set.create(language=self.lang_en)

        with self.assertNumQueries(2):
            first = self.link.find_publication_in_language("en-US")
        self.assertEqual(first.pk, publication_en.pk)

        publication_en_us_new = self.link.publishedgraph_set.create(
            language=self.lang_en_us
        )

        with self.assertNumQueries(0):
            still_cached = self.link.find_publication_in_language("en_us")
        self.assertEqual(still_cached.pk, publication_en.pk)

        self.link.refresh_from_db()

        with self.assertNumQueries(1):
            after_refresh = self.link.find_publication_in_language("en-US")
        self.assertEqual(after_refresh.pk, publication_en_us_new.pk)

    def test_different_languages_are_cached_separately(self):
        publication_es = self.link.publishedgraph_set.create(language=self.lang_es)
        publication_es_mx = self.link.publishedgraph_set.create(
            language=self.lang_es_mx
        )

        with self.assertNumQueries(1):
            result_es = self.link.find_publication_in_language("es")
        self.assertEqual(result_es.pk, publication_es.pk)

        with self.assertNumQueries(1):
            result_es_mx = self.link.find_publication_in_language("es-MX")
        self.assertEqual(result_es_mx.pk, publication_es_mx.pk)

        with self.assertNumQueries(0):
            cached_es = self.link.find_publication_in_language("ES")
        self.assertEqual(cached_es.pk, publication_es.pk)

        with self.assertNumQueries(0):
            cached_es_mx = self.link.find_publication_in_language("es_mx")
        self.assertEqual(cached_es_mx.pk, publication_es_mx.pk)
