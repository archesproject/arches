import os

from django.conf import settings

from arches.settings_utils import list_arches_app_names, list_arches_app_paths
from arches.app.utils.frontend_configuration_utils.get_base_path import get_base_path


def generate_tsconfig_paths():
    base_path = get_base_path()
    root_dir_path = os.path.realpath(settings.ROOT_DIR)

    path_lookup = dict(
        zip(list_arches_app_names(), list_arches_app_paths(), strict=True)
    )

    return {
        "_comment": "This is a generated file. Do not edit directly.",
        "compilerOptions": {
            "paths": {
                "@/arches/*": [
                    os.path.join(
                        "..",
                        os.path.relpath(
                            root_dir_path,
                            os.path.join(base_path, ".."),
                        ),
                        "app",
                        "src",
                        "arches",
                        "*",
                    )
                ],
                **{
                    os.path.join("@", path_name, "*"): [
                        os.path.join(
                            "..",
                            os.path.relpath(path, os.path.join(base_path, "..")),
                            "src",
                            path_name,
                            "*",
                        )
                    ]
                    for path_name, path in path_lookup.items()
                },
                "*": ["../node_modules/*"],
            }
        },
    }
