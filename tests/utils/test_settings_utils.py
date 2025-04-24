import json
import os
from pathlib import Path
from unittest import mock
from django.test import TestCase, override_settings
from django.conf import settings
from arches.settings_utils import generate_frontend_configuration


# these tests can be run from the command line via
# python manage.py test tests.utils.test_settings_utils --settings="tests.test_settings"


class TestFrontendConfigurationGeneration(TestCase):
    """
    Test the generation of frontend configuration files.
    """

    @mock.patch("arches.settings_utils.open")
    @mock.patch("arches.settings_utils.json.dump")
    @mock.patch("arches.settings_utils.list_arches_app_names")
    @mock.patch("arches.settings_utils.list_arches_app_paths")
    @mock.patch("arches.settings_utils.os.path.realpath")
    def test_generate_frontend_configuration_core_arches(
        self, mock_realpath, mock_app_paths, mock_app_names, mock_json_dump, mock_open
    ):
        """
        Test frontend configuration generation when running core arches directly.
        """
        # Mock settings
        mock_settings = mock.MagicMock()
        mock_settings.APP_ROOT = "/arches/app"
        mock_settings.ROOT_DIR = "/arches"
        mock_settings.PUBLIC_SERVER_ADDRESS = "http://localhost:8000"
        mock_settings.STATIC_URL = "/static/"
        mock_settings.WEBPACK_DEVELOPMENT_SERVER_PORT = 8080  # Add this missing setting

        # Mock path responses
        mock_realpath.side_effect = lambda path: path

        # App names and paths mocks
        mock_app_names.return_value = ["arches", "test_app"]
        mock_app_paths.return_value = ["/arches/path", "/test/app/path"]

        # Execute with mocked settings
        with mock.patch("arches.settings_utils.settings", mock_settings):
            generate_frontend_configuration()

        # Check file paths
        mock_open.assert_any_call(
            "/arches/../.frontend-configuration-settings.json", "w"
        )
        mock_open.assert_any_call("/arches/../.tsconfig-paths.json", "w")

        # Check content of first file
        expected_settings_data = {
            "_comment": "This is a generated file. Do not edit directly.",
            "APP_ROOT": "/arches/app",
            "ARCHES_APPLICATIONS": ["arches", "test_app"],
            "ARCHES_APPLICATIONS_PATHS": {
                "arches": "/arches/path",
                "test_app": "/test/app/path",
            },
            "SITE_PACKAGES_DIRECTORY": mock.ANY,  # We can't easily mock this
            "PUBLIC_SERVER_ADDRESS": "http://localhost:8000",
            "ROOT_DIR": "/arches",
            "STATIC_URL": "/static/",
            "WEBPACK_DEVELOPMENT_SERVER_PORT": 8080,
        }

        # Use maxDiff=None to see the full diff if the test fails
        self.maxDiff = None

        # Check the first call to json.dump has our expected data
        args, _ = mock_json_dump.call_args_list[0]
        self.assertEqual(args[0], expected_settings_data)

        # Check the SITE_PACKAGES_DIRECTORY is a valid path
        site_packages_path = args[0]["SITE_PACKAGES_DIRECTORY"]
        self.assertTrue(
            os.path.exists(site_packages_path),
            f"Expected SITE_PACKAGES_DIRECTORY to be a valid path, but got {site_packages_path}",
        )

        # Check that the directory contains typical Python packages
        common_packages = ["pip", "django"]
        found_packages = [
            pkg
            for pkg in common_packages
            if os.path.exists(os.path.join(site_packages_path, pkg))
        ]
        self.assertTrue(
            len(found_packages) > 0,
            f"Expected {site_packages_path} to contain common Python packages but found none of {common_packages}",
        )

        # Check that it has .dist-info or .egg-info directories (typical for installed packages)
        dist_info_files = [
            f
            for f in os.listdir(site_packages_path)
            if f.endswith((".dist-info", ".egg-info"))
        ]
        self.assertTrue(
            len(dist_info_files) > 0,
            f"Expected {site_packages_path} to contain .dist-info or .egg-info directories",
        )

        # Check the second call to json.dump has our expected structure
        expected_tsconfig_data = {
            "_comment": "This is a generated file. Do not edit directly.",
            "compilerOptions": {
                "paths": {
                    "@/arches/*": [
                        os.path.join(
                            ".",
                            os.path.relpath(
                                "/arches",
                                os.path.join("/arches", ".."),
                            ),
                            "app",
                            "src",
                            "arches",
                            "*",
                        )
                    ],
                    "@/test_app/*": [
                        os.path.join(
                            ".",
                            os.path.relpath(
                                "/test/app/path",
                                os.path.join("/arches", ".."),
                            ),
                            "*",
                        )
                    ],
                    "*": ["./node_modules/*"],
                }
            },
        }
        # Check the second call to json.dump has our expected structure
        args, _ = mock_json_dump.call_args_list[1]
        self.assertEqual(
            set(args[0]["_comment"]), set(expected_tsconfig_data["_comment"])
        )
        self.assertEqual(
            set(args[0]["compilerOptions"]["paths"].keys()),
            {"@/arches/*", "@/test_app/*", "*"},
        )

    @mock.patch("arches.settings_utils.sys.stderr.write")
    def test_generate_frontend_configuration_error_handling(self, mock_stderr_write):
        """
        Test error handling in frontend configuration generation.
        """
        # Force an exception by removing a required setting
        with mock.patch("arches.settings_utils.settings") as mock_settings:
            delattr(mock_settings, "APP_ROOT")

            # This should raise an AttributeError
            with self.assertRaises(Exception):
                generate_frontend_configuration()

            # Verify error was written to stderr
            mock_stderr_write.assert_called()
