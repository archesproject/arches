import importlib
from unittest.mock import patch

from django.test import TestCase, override_settings


@override_settings(ROOT_DIR="/arches")
class TestGenerateTsconfigPaths(TestCase):
    def setUp(self):
        self.tsconfig_paths_module = importlib.import_module(
            "arches.app.utils.frontend_configuration_utils.generate_tsconfig_paths"
        )
        self.generate_tsconfig_paths_function = (
            self.tsconfig_paths_module.generate_tsconfig_paths
        )

    def test_generate_tsconfig_paths_with_two_arches_applications_returns_expected_result(
        self,
    ):
        base_path_value = "/arches"
        arches_application_names = ["app_one", "app_two"]
        arches_application_paths = ["/arches_apps/app_one", "/arches_apps/app_two"]

        with (
            patch.object(
                self.tsconfig_paths_module,
                "get_base_path",
                return_value=base_path_value,
            ),
            patch.object(
                self.tsconfig_paths_module,
                "list_arches_app_names",
                return_value=arches_application_names,
            ),
            patch.object(
                self.tsconfig_paths_module,
                "list_arches_app_paths",
                return_value=arches_application_paths,
            ),
        ):

            result = self.generate_tsconfig_paths_function()

        expected = {
            "_comment": "This is a generated file. Do not edit directly.",
            "compilerOptions": {
                "paths": {
                    "@/arches/*": ["../arches/app/src/arches/*"],
                    "@/app_one/*": ["../arches_apps/app_one/src/app_one/*"],
                    "@/app_two/*": ["../arches_apps/app_two/src/app_two/*"],
                    "*": ["../node_modules/*"],
                }
            },
        }
        self.assertEqual(result, expected)

    def test_generate_tsconfig_paths_with_no_arches_applications_returns_core_and_wildcard_only(
        self,
    ):
        base_path_value = "/arches"

        with (
            patch.object(
                self.tsconfig_paths_module,
                "get_base_path",
                return_value=base_path_value,
            ),
            patch.object(
                self.tsconfig_paths_module, "list_arches_app_names", return_value=[]
            ),
            patch.object(
                self.tsconfig_paths_module, "list_arches_app_paths", return_value=[]
            ),
        ):

            result = self.generate_tsconfig_paths_function()

        self.assertIn("_comment", result)
        self.assertIn("compilerOptions", result)
        paths_mapping = result["compilerOptions"]["paths"]
        self.assertEqual(paths_mapping["@/arches/*"], ["../arches/app/src/arches/*"])
        self.assertEqual(
            sorted(k for k in paths_mapping.keys() if k not in {"@/arches/*", "*"}), []
        )
        self.assertEqual(paths_mapping["*"], ["../node_modules/*"])

    def test_generate_tsconfig_paths_raises_error_when_application_names_and_paths_do_not_match(
        self,
    ):
        base_path_value = "/arches"

        with (
            patch.object(
                self.tsconfig_paths_module,
                "get_base_path",
                return_value=base_path_value,
            ),
            patch.object(
                self.tsconfig_paths_module,
                "list_arches_app_names",
                return_value=["one", "two"],
            ),
            patch.object(
                self.tsconfig_paths_module,
                "list_arches_app_paths",
                return_value=["/arches_apps/one"],
            ),
        ):

            with self.assertRaises(ValueError):
                self.generate_tsconfig_paths_function()

    def test_generate_tsconfig_paths_when_root_directory_differs_from_base_path(self):
        base_path_value = "/project/arches"
        arches_application_names = ["alpha"]
        arches_application_paths = ["/project/apps/alpha"]

        with override_settings(ROOT_DIR="/project"):
            with (
                patch.object(
                    self.tsconfig_paths_module,
                    "get_base_path",
                    return_value=base_path_value,
                ),
                patch.object(
                    self.tsconfig_paths_module,
                    "list_arches_app_names",
                    return_value=arches_application_names,
                ),
                patch.object(
                    self.tsconfig_paths_module,
                    "list_arches_app_paths",
                    return_value=arches_application_paths,
                ),
            ):

                result = self.generate_tsconfig_paths_function()

        paths_mapping = result["compilerOptions"]["paths"]
        self.assertEqual(paths_mapping["@/arches/*"], [".././app/src/arches/*"])
        self.assertEqual(paths_mapping["@/alpha/*"], ["../apps/alpha/src/alpha/*"])
        self.assertEqual(paths_mapping["*"], ["../node_modules/*"])
