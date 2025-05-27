import json
import os
import shutil
import sysconfig
from pathlib import Path

from django.test import TestCase, override_settings
from django.test.utils import captured_stderr
from django.conf import settings
from arches.app.utils.frontend_configuration_utils import (
    generate_frontend_configuration,
)


# these tests can be run from the command line via
# python manage.py test tests.utils.test_settings_utils --settings="tests.test_settings"


class TestFrontendConfigurationGeneration(TestCase):
    """
    Test the generation of frontend configuration files.
    """

    @override_settings(
        APP_ROOT=str(Path(settings.ROOT_DIR) / "app"),
        PUBLIC_SERVER_ADDRESS="http://localhost:8000",
        STATIC_URL="/static/",
        WEBPACK_DEVELOPMENT_SERVER_PORT=8080,
    )
    def test_generate_frontend_configuration_core_arches(self):
        """
        Test frontend configuration generation when running core arches directly.
        """
        config_dir = os.path.realpath(
            Path(settings.ROOT_DIR).parent / "frontend_configuration"
        )
        if not os.path.exists(config_dir):
            os.mkdir(config_dir)
            self.addCleanup(shutil.rmtree, config_dir)

        generate_frontend_configuration()

        # Check content of first file
        expected_settings_data = {
            "_comment": "This is a generated file. Do not edit directly.",
            "APP_RELATIVE_PATH": "arches/app",
            "APP_ROOT": settings.APP_ROOT,
            "ARCHES_APPLICATIONS": [],
            "ARCHES_APPLICATIONS_PATHS": {},
            "SITE_PACKAGES_DIRECTORY": sysconfig.get_path("purelib"),
            "PUBLIC_SERVER_ADDRESS": "http://localhost:8000",
            "ROOT_DIR": settings.ROOT_DIR,
            "STATIC_URL": "/static/",
            "WEBPACK_DEVELOPMENT_SERVER_PORT": 8080,
        }

        # Use maxDiff=None to see the full diff if the test fails
        self.maxDiff = None

        # get the json from the webpack-metadata.json file
        with open(Path(config_dir) / "webpack-metadata.json", "r") as file:
            settings_data = json.load(file)
            self.assertEqual(settings_data, expected_settings_data)
            # Check the first call to json.dump has our expected structure

            # Check the SITE_PACKAGES_DIRECTORY is a valid path
            site_packages_path = settings_data["SITE_PACKAGES_DIRECTORY"]
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
                            "..",
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
                    "*": ["../node_modules/*"],
                }
            },
        }

        # get the json from the tsconfig-paths.json file
        with open(Path(config_dir) / "tsconfig-paths.json", "r") as file:
            tsconfig_data = json.load(file)
            self.assertEqual(tsconfig_data, expected_tsconfig_data)

    def test_generate_frontend_configuration_error_handling(self):
        """
        Test error handling in frontend configuration generation.
        """
        # Force an exception by removing a required setting
        with (
            captured_stderr() as stderr,
            self.settings(APP_ROOT=None),
            self.assertRaises(Exception),
        ):
            generate_frontend_configuration()

            # Check that the error message is printed to stderr
            self.assertIn("not 'NoneType'", stderr.getvalue())
