import sys
import types

from django.http import HttpResponse
from django.test import TestCase, override_settings
from django.urls import clear_url_caches, include, path, re_path
from django.conf.urls.i18n import i18n_patterns
from django.views import View

from arches.app.utils.frontend_configuration_utils.generate_urls_json import (
    generate_urls_json,
)


@override_settings(STATIC_URL="/static/", MEDIA_URL="/media/")
class TestGenerateUrlsJson(TestCase):
    def setUp(self):
        class UpdatePublishedGraphView(View):
            def get(self, request, *args, **kwargs):
                return HttpResponse("ok")

        class TileserverView(View):
            def get(self, request, *args, **kwargs):
                return HttpResponse("ok")

        class WeirdRegexView(View):
            def get(self, request, *args, **kwargs):
                return HttpResponse("ok")

        class MiscellaneousView(View):
            def get(self, request, *args, **kwargs):
                return HttpResponse("ok")

        class AdminLikeView(View):
            def get(self, request, *args, **kwargs):
                return HttpResponse("ok")

        UpdatePublishedGraphView.__module__ = "arches.graph"
        TileserverView.__module__ = "arches.map"
        WeirdRegexView.__module__ = "arches.weird"
        MiscellaneousView.__module__ = "misc_app.views"
        AdminLikeView.__module__ = "project_admin.views"

        arches_core_patterns = [
            re_path(
                r"^graph/(?P<graphid>[0-9a-f\-]+)/update_published_graph$",
                UpdatePublishedGraphView.as_view(),
                name="update_published_graph",
            ),
            re_path(r"^tileserver/(?P<path>.*)$", TileserverView.as_view()),
            re_path(
                r"^weird/(?P<slug>[a-z0-9_-]+)/(?:optional)/(?P<identifier>[0-9]+)/[abc]$",
                WeirdRegexView.as_view(),
                name="weird_regex",
            ),
        ]

        misc_app_patterns = [
            re_path(r"^misc/(?P<number>[0-9]+)$", MiscellaneousView.as_view()),
        ]

        root_with_i18n_patterns = i18n_patterns(
            path("", include(arches_core_patterns)),
            path("", include(arches_core_patterns)),
            path(
                "",
                include(
                    (arches_core_patterns, "arches_core"), namespace="arches_querysets"
                ),
            ),
            path("", include(misc_app_patterns)),
            path("admin/model/<str:object_id>", AdminLikeView.as_view()),
        )

        root_plain_patterns = [
            path("", include(arches_core_patterns)),
            path("admin/logs/<str:object_id>", AdminLikeView.as_view()),
        ]

        self.root_with_i18n_module = types.ModuleType("testproject.urls")
        self.root_with_i18n_module.urlpatterns = root_with_i18n_patterns
        sys.modules[self.root_with_i18n_module.__name__] = self.root_with_i18n_module

        self.root_plain_module = types.ModuleType("plainproject.urls")
        self.root_plain_module.urlpatterns = root_plain_patterns
        sys.modules[self.root_plain_module.__name__] = self.root_plain_module

        self._registered_modules = [
            self.root_with_i18n_module.__name__,
            self.root_plain_module.__name__,
        ]
        clear_url_caches()

    def tearDown(self):
        clear_url_caches()
        for name in self._registered_modules:
            sys.modules.pop(name, None)

    def test_with_i18n_routes_and_namespacing(self):
        with override_settings(ROOT_URLCONF=self.root_with_i18n_module.__name__):
            clear_url_caches()
            urls_by_name = generate_urls_json()

        self.assertIn("arches:update_published_graph", urls_by_name)
        entry = urls_by_name["arches:update_published_graph"][0]
        self.assertEqual(
            entry["url"], "/{language_code}/graph/{graphid}/update_published_graph"
        )
        self.assertEqual(entry["params"], ["language_code", "graphid"])

        self.assertNotIn("arches_querysets:update_published_graph", urls_by_name)

        self.assertIn("arches:tileserver", urls_by_name)
        tiles = urls_by_name["arches:tileserver"][0]
        self.assertEqual(tiles["url"], "/{language_code}/tileserver/{path}")
        self.assertEqual(tiles["params"], ["language_code", "path"])

        self.assertIn("misc_app:misc", urls_by_name)
        misc = urls_by_name["misc_app:misc"][0]
        self.assertEqual(misc["url"], "/{language_code}/misc/{number}")
        self.assertEqual(misc["params"], ["language_code", "number"])

        self.assertIn("arches:weird_regex", urls_by_name)
        weird = urls_by_name["arches:weird_regex"][0]
        self.assertEqual(weird["url"], "/{language_code}/weird/{slug}/{identifier}")
        self.assertEqual(weird["params"], ["language_code", "slug", "identifier"])

        self.assertIn("admin", urls_by_name)
        self.assertEqual(
            urls_by_name["admin"],
            [
                {
                    "url": "/{language_code}/admin/{url}",
                    "params": ["language_code", "url"],
                }
            ],
        )

        self.assertEqual(
            urls_by_name["testproject:static_url"], [{"url": "/static/", "params": []}]
        )
        self.assertEqual(
            urls_by_name["testproject:media_url"], [{"url": "/media/", "params": []}]
        )

    def test_without_i18n_routes(self):
        with override_settings(ROOT_URLCONF=self.root_plain_module.__name__):
            clear_url_caches()
            urls_by_name = generate_urls_json()

        self.assertIn("admin", urls_by_name)
        self.assertEqual(
            urls_by_name["admin"], [{"url": "/admin/{url}", "params": ["url"]}]
        )
        self.assertIn("plainproject:static_url", urls_by_name)
        self.assertIn("plainproject:media_url", urls_by_name)

    def test_deduplicates_across_multiple_includes(self):
        with override_settings(ROOT_URLCONF=self.root_with_i18n_module.__name__):
            clear_url_caches()
            urls_by_name = generate_urls_json()

        self.assertEqual(len(urls_by_name["arches:update_published_graph"]), 1)

    def test_path_converters(self):
        class AlphaDetailView(View):
            def get(self, request, *args, **kwargs):
                return HttpResponse("ok")

        AlphaDetailView.__module__ = "alpha_app.views"

        alpha_patterns = [
            path(
                "alpha/<uuid:item_id>/<slug:slug>/detail",
                AlphaDetailView.as_view(),
                name="alpha_detail",
            ),
        ]
        alpha_root_patterns = i18n_patterns(path("", include(alpha_patterns)))

        alpha_root_module = types.ModuleType("testproject_alpha.urls")
        alpha_root_module.urlpatterns = alpha_root_patterns
        sys.modules[alpha_root_module.__name__] = alpha_root_module
        self._registered_modules.append(alpha_root_module.__name__)
        clear_url_caches()

        with override_settings(ROOT_URLCONF=alpha_root_module.__name__):
            clear_url_caches()
            urls_by_name = generate_urls_json()

        alpha_entry = urls_by_name["alpha_app:alpha_detail"][0]
        self.assertEqual(
            alpha_entry["url"], "/{language_code}/alpha/{item_id}/{slug}/detail"
        )
        self.assertEqual(alpha_entry["params"], ["language_code", "item_id", "slug"])

    def test_force_script_name_with_i18n(self):
        with override_settings(
            ROOT_URLCONF=self.root_with_i18n_module.__name__, FORCE_SCRIPT_NAME="/proxy"
        ):
            clear_url_caches()
            urls_by_name = generate_urls_json()

        self.assertEqual(
            urls_by_name["arches:update_published_graph"][0]["url"],
            "/proxy/{language_code}/graph/{graphid}/update_published_graph",
        )
        self.assertEqual(
            urls_by_name["arches:tileserver"][0]["url"],
            "/proxy/{language_code}/tileserver/{path}",
        )
        self.assertEqual(
            urls_by_name["misc_app:misc"][0]["url"],
            "/proxy/{language_code}/misc/{number}",
        )
        self.assertEqual(
            urls_by_name["arches:weird_regex"][0]["url"],
            "/proxy/{language_code}/weird/{slug}/{identifier}",
        )
        self.assertEqual(
            urls_by_name["admin"],
            [
                {
                    "url": "/{language_code}/admin/{url}",
                    "params": ["language_code", "url"],
                }
            ],
        )
        self.assertEqual(
            urls_by_name["testproject:static_url"], [{"url": "/static/", "params": []}]
        )
        self.assertEqual(
            urls_by_name["testproject:media_url"], [{"url": "/media/", "params": []}]
        )

    def test_force_script_name_without_i18n(self):
        from arches.app.utils.frontend_configuration_utils.generate_urls_json import (
            generate_urls_json,
        )

        with override_settings(
            ROOT_URLCONF=self.root_plain_module.__name__, FORCE_SCRIPT_NAME="/proxy/"
        ):
            clear_url_caches()
            urls_by_name = generate_urls_json()

        self.assertEqual(
            urls_by_name["admin"], [{"url": "/admin/{url}", "params": ["url"]}]
        )
        self.assertIn("plainproject:static_url", urls_by_name)
        self.assertIn("plainproject:media_url", urls_by_name)
