import os
import sysconfig
import importlib
from unittest.mock import patch

from django.test import TestCase, override_settings


@override_settings(
    APP_ROOT="/arches/app",
    ROOT_DIR="/arches",
    STATIC_URL="/static/",
    WEBPACK_DEVELOPMENT_SERVER_PORT=9000,
)
class TestGenerateWebpackConfiguration(TestCase):
    def setUp(self):
        self.webpack_configuration_module = importlib.import_module(
            "arches.app.utils.frontend_configuration_utils.generate_webpack_configuration"
        )
        self.generate_webpack_configuration_function = (
            self.webpack_configuration_module.generate_webpack_configuration
        )

        self.application_root_path = "/arches/app"
        self.root_directory_path = "/arches"
        self.static_url_value = "/static/"
        self.development_server_port = 9000

    def test_generate_webpack_configuration_returns_expected_payload_with_two_apps(
        self,
    ):
        arches_application_names = ["app_one", "app_two"]
        arches_application_paths = ["/arches_apps/app_one", "/arches_apps/app_two"]

        with (
            patch.object(
                self.webpack_configuration_module,
                "list_arches_app_names",
                return_value=arches_application_names,
            ),
            patch.object(
                self.webpack_configuration_module,
                "list_arches_app_paths",
                return_value=arches_application_paths,
            ),
        ):
            result = self.generate_webpack_configuration_function()

        expected_app_root_realpath = os.path.realpath(self.application_root_path)
        expected_root_dir_realpath = os.path.realpath(self.root_directory_path)
        expected_app_relative_path = os.path.relpath(expected_app_root_realpath)

        self.assertIn("_comment", result)
        self.assertEqual(
            result["_comment"], "This is a generated file. Do not edit directly."
        )
        self.assertEqual(result["APP_ROOT"], expected_app_root_realpath)
        self.assertEqual(result["ROOT_DIR"], expected_root_dir_realpath)
        self.assertEqual(result["APP_RELATIVE_PATH"], expected_app_relative_path)
        self.assertEqual(result["ARCHES_APPLICATIONS"], arches_application_names)
        self.assertEqual(
            result["ARCHES_APPLICATIONS_PATHS"],
            {"app_one": "/arches_apps/app_one", "app_two": "/arches_apps/app_two"},
        )
        self.assertEqual(result["STATIC_URL"], self.static_url_value)
        self.assertEqual(
            result["WEBPACK_DEVELOPMENT_SERVER_PORT"], self.development_server_port
        )
        self.assertEqual(
            result["SITE_PACKAGES_DIRECTORY"], sysconfig.get_path("purelib")
        )

    def test_generate_webpack_configuration_with_no_apps_returns_empty_mapping(self):
        with (
            patch.object(
                self.webpack_configuration_module,
                "list_arches_app_names",
                return_value=[],
            ),
            patch.object(
                self.webpack_configuration_module,
                "list_arches_app_paths",
                return_value=[],
            ),
        ):
            result = self.generate_webpack_configuration_function()

        self.assertEqual(result["ARCHES_APPLICATIONS"], [])
        self.assertEqual(result["ARCHES_APPLICATIONS_PATHS"], {})

    def test_generate_webpack_configuration_raises_when_app_names_and_paths_lengths_mismatch(
        self,
    ):
        with (
            patch.object(
                self.webpack_configuration_module,
                "list_arches_app_names",
                return_value=["one", "two"],
            ),
            patch.object(
                self.webpack_configuration_module,
                "list_arches_app_paths",
                return_value=["/arches_apps/one"],
            ),
        ):
            with self.assertRaises(ValueError):
                self.generate_webpack_configuration_function()

    def test_generate_webpack_configuration_site_packages_directory_is_an_existing_path(
        self,
    ):
        with (
            patch.object(
                self.webpack_configuration_module,
                "list_arches_app_names",
                return_value=[],
            ),
            patch.object(
                self.webpack_configuration_module,
                "list_arches_app_paths",
                return_value=[],
            ),
        ):
            result = self.generate_webpack_configuration_function()

        site_packages_directory = result["SITE_PACKAGES_DIRECTORY"]
        self.assertIsInstance(site_packages_directory, str)
        self.assertTrue(
            os.path.exists(site_packages_directory),
            f"Expected existing path, got {site_packages_directory}",
        )

    def test_single_test_can_override_baseline_settings_locally(self):
        with override_settings(STATIC_URL="/static-dev/"):
            with (
                patch.object(
                    self.webpack_configuration_module,
                    "list_arches_app_names",
                    return_value=[],
                ),
                patch.object(
                    self.webpack_configuration_module,
                    "list_arches_app_paths",
                    return_value=[],
                ),
            ):
                result = self.generate_webpack_configuration_function()
        self.assertEqual(result["STATIC_URL"], "/static-dev/")
