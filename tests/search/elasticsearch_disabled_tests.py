from contextlib import contextmanager

from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import CommandError
from django.http import Http404
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings

from arches.app.models.models import ResourceInstance
from arches.app.models.system_settings import settings as arches_settings
from arches.app.permissions.arches_default_deny import (
    ArchesDefaultDenyPermissionFramework,
)
from arches.app.search.null_search_engine import NullSearchEngine
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.utils.decorators import requires_elasticsearch


@contextmanager
def elasticsearch_enabled(value):
    """
    Arches reads this setting through arches.app.models.system_settings, a separate
    LazySettings instance that django's override_settings does not touch. This sets
    and restores it explicitly: mock.patch.object would delattr on exit, which
    removes the default from django's Settings object entirely.
    """
    original = arches_settings.ELASTICSEARCH_ENABLED
    arches_settings.ELASTICSEARCH_ENABLED = value
    try:
        yield
    finally:
        arches_settings.ELASTICSEARCH_ENABLED = original


class NullSearchEngineTests(SimpleTestCase):
    def setUp(self):
        self.se = NullSearchEngine(prefix="Test")

    def test_query_returns_empty_es_shaped_response(self):
        result = self.se.search(index="resources", query={"match_all": {}})
        self.assertEqual(result["hits"]["hits"], [])
        self.assertEqual(result["hits"]["total"]["value"], 0)
        self.assertIsNone(result["_scroll_id"])
        self.assertEqual(result["aggregations"], {})

    def test_mget_marks_every_id_not_found(self):
        result = self.se.search(index="resources", id=["a", "b"])
        self.assertEqual([doc["found"] for doc in result["docs"]], [False, False])

    def test_get_returns_none(self):
        self.assertIsNone(self.se.search(index="resources", id="a"))

    def test_count_is_zero(self):
        self.assertEqual(self.se.count(index="resources"), 0)

    def test_writes_are_noops(self):
        self.se.index_data(index="resources", body={"a": 1}, id="1")
        self.se.bulk_index([])
        self.se.delete(index="resources", id="1")
        self.se.refresh(index="resources")
        with self.se.BulkIndexer() as indexer:
            indexer.add(index="resources", id="1", data={})

    def test_bulk_item_uses_prefix(self):
        item = self.se.create_bulk_item(index="resources", id="1", data={})
        self.assertEqual(item["_index"], "test_resources")

    def test_snapshots_raise(self):
        with self.assertRaises(NotImplementedError):
            self.se.list_snapshots("repo")


class SearchEngineFactoryTests(SimpleTestCase):
    def test_factory_returns_null_engine_when_disabled(self):
        with elasticsearch_enabled(False):
            engine = SearchEngineFactory().create()
        self.assertIsInstance(engine, NullSearchEngine)

    def test_requires_elasticsearch_decorator_404s(self):
        @requires_elasticsearch
        def view(request):
            return "ok"

        with elasticsearch_enabled(False), self.assertRaises(Http404):
            view(RequestFactory().get("/"))

    def test_requires_elasticsearch_decorator_passes_when_enabled(self):
        @requires_elasticsearch
        def view(request):
            return "ok"

        with elasticsearch_enabled(True):
            self.assertEqual(view(RequestFactory().get("/")), "ok")

    def test_es_command_refuses_when_disabled(self):
        with elasticsearch_enabled(False), self.assertRaises(CommandError):
            call_command("es", operation="setup_indexes")


class DisabledPermissionFrameworkCheckTests(SimpleTestCase):
    def run_check(self):
        from arches.apps import check_elasticsearch_disabled_permission_framework

        return check_elasticsearch_disabled_permission_framework(None)

    @override_settings(
        ELASTICSEARCH_ENABLED=False,
        PERMISSION_FRAMEWORK="arches_default_allow.ArchesDefaultAllowPermissionFramework",
    )
    def test_default_allow_is_an_error_without_elasticsearch(self):
        errors = self.run_check()
        self.assertEqual([e.id for e in errors], ["arches.E004"])

    @override_settings(
        ELASTICSEARCH_ENABLED=False,
        PERMISSION_FRAMEWORK="arches_default_deny.ArchesDefaultDenyPermissionFramework",
    )
    def test_default_deny_is_fine_without_elasticsearch(self):
        self.assertEqual(self.run_check(), [])

    @override_settings(
        ELASTICSEARCH_ENABLED=True,
        PERMISSION_FRAMEWORK="arches_default_allow.ArchesDefaultAllowPermissionFramework",
    )
    def test_default_allow_is_fine_with_elasticsearch(self):
        self.assertEqual(self.run_check(), [])


class DefaultDenyAllowedInstancesFromDbTests(TestCase):
    """get_allowed_instances must work from the database alone."""

    def setUp(self):
        self.enterContext(elasticsearch_enabled(False))

    def test_superuser_gets_all_or_requested_subset(self):
        framework = ArchesDefaultDenyPermissionFramework()
        admin = User.objects.get(username="admin")
        all_ids = {str(pk) for pk in ResourceInstance.objects.values_list("pk", flat=True)}

        self.assertEqual(set(framework.get_allowed_instances(admin)), all_ids)
        self.assertEqual(
            framework.get_allowed_instances(admin, resources=["x"]), ["x"]
        )

    def test_user_without_permissions_gets_nothing(self):
        framework = ArchesDefaultDenyPermissionFramework()
        user = User.objects.create_user("nobody", password="x")
        self.assertEqual(framework.get_allowed_instances(user), [])
