import inspect
from unittest import mock

from django.test import TestCase, override_settings

from arches.app.const import ExtensionType
from arches.app.utils.module_importer import get_directories, get_class_from_modulename
from tests.base_test import sync_overridden_test_settings_to_arches

# these tests can be run from the command line via
# python manage.py test tests.utils.test_module_importer --settings="tests.test_settings"


def patched_arches_applications():
    return ["arches_for_music", "arches_for_dance"]


@mock.patch(
    "arches.app.utils.module_importer.list_arches_app_names",
    patched_arches_applications,
)
class GetDirectoriesTests(TestCase):
    @override_settings(
        APP_NAME="hiphop",
        FUNCTION_LOCATIONS=[
            "arches.app.functions",
            # Include an example where one of the installed apps is explicitly given
            "arches_for_music.pkg.extensions.functions",
            "hiphop.functions",
        ],
    )
    def test_arches_application_extension_explicit(self):
        with sync_overridden_test_settings_to_arches():
            function_dirs = get_directories(ExtensionType.FUNCTIONS)
        self.assertEqual(
            function_dirs,
            [
                "arches_for_music.functions",
                "arches_for_music.pkg.extensions.functions",
                "arches_for_dance.functions",
                "arches_for_dance.pkg.extensions.functions",
                "hiphop.functions",
                "arches.app.functions",
            ],
        )

    @override_settings(
        APP_NAME="hiphop",
        SEARCH_COMPONENT_LOCATIONS=[
            # Same, but poorly ordered.
            "hiphop.search_components",
            "arches_for_music.search_components",
            "arches.app.search.components",
        ],
    )
    def test_arches_application_extension_explicit_poorly_ordered(self):
        with sync_overridden_test_settings_to_arches():
            search_dirs = get_directories(ExtensionType.SEARCH_COMPONENTS)
        self.assertEqual(
            search_dirs,
            [
                "arches_for_music.search_components",
                "arches_for_music.pkg.extensions.search_components",
                "arches_for_dance.search_components",
                "arches_for_dance.pkg.extensions.search_components",
                "hiphop.search_components",
                "arches.app.search.components",
            ],
        )

    @override_settings(
        APP_NAME="hiphop",
        ETL_MODULE_LOCATIONS=[
            # App not given.
            "arches.app.etl_modules",
        ],
    )
    def test_arches_application_extension_implicit(self):
        with sync_overridden_test_settings_to_arches():
            etl_modules = get_directories(ExtensionType.ETL_MODULES)
        self.assertEqual(
            etl_modules,
            [
                "arches_for_music.etl_modules",
                "arches_for_music.pkg.extensions.etl_modules",
                "arches_for_dance.etl_modules",
                "arches_for_dance.pkg.extensions.etl_modules",
                "arches.app.etl_modules",
            ],
        )

    @override_settings(
        APP_NAME="hiphop",
        DATATYPE_LOCATIONS=[],  # Nothing given.
    )
    def test_arches_application_extension_core_arches_implicit(self):
        with sync_overridden_test_settings_to_arches():
            datatypes = get_directories(ExtensionType.DATATYPES)
        self.assertEqual(
            datatypes,
            [
                "arches_for_music.datatypes",
                "arches_for_music.pkg.extensions.datatypes",
                "arches_for_dance.datatypes",
                "arches_for_dance.pkg.extensions.datatypes",
                "arches.app.datatypes",
            ],
        )


class GetClassFromModuleNameTests(TestCase):
    @override_settings(DATATYPE_LOCATIONS=["nonexistent_module"])
    def test_nonexistent_module(self):
        with sync_overridden_test_settings_to_arches():
            with self.assertRaises(ModuleNotFoundError):
                get_class_from_modulename(
                    "nonexistent_module",
                    "BaseDataType",
                    ExtensionType.DATATYPES,
                )

    @override_settings(DATATYPE_LOCATIONS=["tests.fixtures.datatypes"])
    def test_module_without_url_datatype(self):
        with sync_overridden_test_settings_to_arches():
            result = get_class_from_modulename(
                "url",
                "URLDataType",
                ExtensionType.DATATYPES,
            )
            self.assertTrue(inspect.isclass(result))
