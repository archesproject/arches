import importlib
import json
import os
import tempfile
from unittest.mock import patch

from django.test import TestCase
from django.test.utils import captured_stderr


class TestGenerateFrontendConfiguration(TestCase):
    def setUp(self):
        self.module = importlib.import_module(
            "arches.app.utils.frontend_configuration_utils.generate_frontend_configuration"
        )
        self.run_generate = self.module.generate_frontend_configuration

        self.urls_payload = {
            "arches:update_published_graph": [
                {
                    "url": "/graph/{graphid}/update_published_graph",
                    "params": ["graphid"],
                }
            ]
        }
        self.webpack_payload = {"a": 1, "b": 2}
        self.tsconfig_payload = {
            "compilerOptions": {"paths": {"*": ["../node_modules/*"]}}
        }

    @patch(
        "arches.app.utils.frontend_configuration_utils.generate_frontend_configuration.get_base_path"
    )
    @patch(
        "arches.app.utils.frontend_configuration_utils.generate_frontend_configuration.generate_urls_json"
    )
    @patch(
        "arches.app.utils.frontend_configuration_utils.generate_frontend_configuration.generate_webpack_configuration"
    )
    @patch(
        "arches.app.utils.frontend_configuration_utils.generate_frontend_configuration.generate_tsconfig_paths"
    )
    def test_writes_all_expected_files_with_expected_payloads(
        self,
        generate_tsconfig_paths_mock,
        generate_webpack_configuration_mock,
        generate_urls_json_mock,
        get_base_path_mock,
    ):
        generate_urls_json_mock.return_value = self.urls_payload
        generate_webpack_configuration_mock.return_value = self.webpack_payload
        generate_tsconfig_paths_mock.return_value = self.tsconfig_payload

        with tempfile.TemporaryDirectory() as temporary_directory_path:
            base_path_value = os.path.join(temporary_directory_path, "arches")
            get_base_path_mock.return_value = base_path_value

            self.run_generate()

            destination_directory_path = os.path.realpath(
                os.path.join(base_path_value, "..", "frontend_configuration")
            )
            urls_file_path = os.path.join(destination_directory_path, "urls.json")
            webpack_file_path = os.path.join(
                destination_directory_path, "webpack-metadata.json"
            )
            tsconfig_file_path = os.path.join(
                destination_directory_path, "tsconfig-paths.json"
            )

            self.assertTrue(os.path.isdir(destination_directory_path))
            self.assertTrue(os.path.isfile(urls_file_path))
            self.assertTrue(os.path.isfile(webpack_file_path))
            self.assertTrue(os.path.isfile(tsconfig_file_path))

            with open(urls_file_path, "r", encoding="utf-8") as file_handle:
                urls_data = json.load(file_handle)
            self.assertIn("_comment", urls_data)
            self.assertIn("arches:update_published_graph", urls_data)
            self.assertEqual(
                urls_data["arches:update_published_graph"],
                self.urls_payload["arches:update_published_graph"],
            )

            with open(webpack_file_path, "r", encoding="utf-8") as file_handle:
                webpack_data = json.load(file_handle)
            self.assertEqual(webpack_data, self.webpack_payload)

            with open(tsconfig_file_path, "r", encoding="utf-8") as file_handle:
                tsconfig_data = json.load(file_handle)
            self.assertEqual(tsconfig_data, self.tsconfig_payload)

    @patch(
        "arches.app.utils.frontend_configuration_utils.generate_frontend_configuration.get_base_path"
    )
    @patch(
        "arches.app.utils.frontend_configuration_utils.generate_frontend_configuration._generate_frontend_configuration_directory"
    )
    @patch(
        "arches.app.utils.frontend_configuration_utils.generate_frontend_configuration._generate_urls_json_file"
    )
    @patch(
        "arches.app.utils.frontend_configuration_utils.generate_frontend_configuration._generate_webpack_configuration_file"
    )
    @patch(
        "arches.app.utils.frontend_configuration_utils.generate_frontend_configuration._generate_tsconfig_paths_file"
    )
    def test_calls_helpers_in_sequence(
        self,
        generate_tsconfig_paths_file_mock,
        generate_webpack_configuration_file_mock,
        generate_urls_json_file_mock,
        generate_frontend_configuration_directory_mock,
        get_base_path_mock,
    ):
        call_sequence = []

        def record(label):
            call_sequence.append(label)

        get_base_path_mock.return_value = "arches"
        generate_frontend_configuration_directory_mock.side_effect = (
            lambda base: record("directory")
        )
        generate_urls_json_file_mock.side_effect = lambda base: record("urls")
        generate_webpack_configuration_file_mock.side_effect = lambda base: record(
            "webpack"
        )
        generate_tsconfig_paths_file_mock.side_effect = lambda base: record("tsconfig")

        self.run_generate()

        self.assertEqual(call_sequence, ["directory", "urls", "webpack", "tsconfig"])

    @patch(
        "arches.app.utils.frontend_configuration_utils.generate_frontend_configuration.get_base_path"
    )
    def test_reraises_and_logs_when_get_base_path_fails(self, get_base_path_mock):
        get_base_path_mock.side_effect = RuntimeError("explode")
        with captured_stderr() as captured_stream, self.assertRaises(RuntimeError):
            self.run_generate()
        self.assertIn("explode", captured_stream.getvalue())

    @patch(
        "arches.app.utils.frontend_configuration_utils.generate_frontend_configuration.get_base_path"
    )
    @patch(
        "arches.app.utils.frontend_configuration_utils.generate_frontend_configuration._generate_frontend_configuration_directory"
    )
    @patch(
        "arches.app.utils.frontend_configuration_utils.generate_frontend_configuration._generate_urls_json_file"
    )
    def test_reraises_and_logs_when_first_helper_fails(
        self,
        generate_urls_json_file_mock,
        generate_frontend_configuration_directory_mock,
        get_base_path_mock,
    ):
        with tempfile.TemporaryDirectory() as temporary_directory_path:
            base_path_value = os.path.join(temporary_directory_path, "arches")
            get_base_path_mock.return_value = base_path_value
            generate_frontend_configuration_directory_mock.return_value = None
            generate_urls_json_file_mock.side_effect = ValueError("urls failed")

            with captured_stderr() as captured_stream, self.assertRaises(ValueError):
                self.run_generate()

        self.assertIn("urls failed", captured_stream.getvalue())
