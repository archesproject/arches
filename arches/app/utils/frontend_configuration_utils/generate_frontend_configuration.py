import json
import os
import sys

from arches.app.utils.frontend_configuration_utils.generate_tsconfig_paths import (
    generate_tsconfig_paths,
)
from arches.app.utils.frontend_configuration_utils.generate_urls_json import (
    generate_urls_json,
)
from arches.app.utils.frontend_configuration_utils.generate_webpack_configuration import (
    generate_webpack_configuration,
)
from arches.app.utils.frontend_configuration_utils.get_base_path import get_base_path


def _generate_frontend_configuration_directory(base_path):
    destination_dir = os.path.realpath(
        os.path.join(base_path, "..", "frontend_configuration")
    )

    os.makedirs(destination_dir, exist_ok=True)


def _generate_urls_json_file(base_path):
    destination_file_path = os.path.realpath(
        os.path.join(base_path, "..", "frontend_configuration", "urls.json")
    )

    with open(destination_file_path, "w", encoding="utf-8") as destination_file:
        json.dump(
            {
                "_comment": "This file is auto-generated. Do not edit manually.",
                **generate_urls_json(),
            },
            destination_file,
            indent=4,
        )


def _generate_webpack_configuration_file(base_path):
    destination_path = os.path.realpath(
        os.path.join(base_path, "..", "frontend_configuration", "webpack-metadata.json")
    )

    with open(destination_path, "w", encoding="utf-8") as file:
        json.dump(
            generate_webpack_configuration(),
            file,
            indent=4,
        )


def _generate_tsconfig_paths_file(base_path):
    destination_path = os.path.realpath(
        os.path.join(base_path, "..", "frontend_configuration", "tsconfig-paths.json")
    )

    with open(destination_path, "w", encoding="utf-8") as file:
        json.dump(generate_tsconfig_paths(), file, indent=4)


def generate_frontend_configuration():
    try:
        base_path = get_base_path()

        _generate_frontend_configuration_directory(base_path)
        _generate_urls_json_file(base_path)
        _generate_webpack_configuration_file(base_path)
        _generate_tsconfig_paths_file(base_path)
    except Exception as e:
        # Ensures error message is shown if error encountered
        sys.stderr.write(str(e))
        raise e
