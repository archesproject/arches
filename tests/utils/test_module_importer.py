from django.test import TestCase, override_settings

from arches.app.const import ExtensionType
from arches.app.utils.module_importer import get_directories
from tests.base_test import sync_overridden_test_settings_to_arches

# these tests can be run from the command line via
# python manage.py test tests.utils.test_module_importer --settings="tests.test_settings"

class ModuleImporterTests(TestCase):
    @override_settings(
        APP_NAME="hiphop",
        ARCHES_APPLICATIONS=["arches_for_music", "arches_for_dance"],
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
        self.assertEqual(function_dirs, [
            "arches.app.functions",
            "arches_for_music.functions",
            "arches_for_music.pkg.extensions.functions",
            "arches_for_dance.functions",
            "arches_for_dance.pkg.extensions.functions",
            "hiphop.functions",
        ])

    @override_settings(
        APP_NAME="hiphop",
        ARCHES_APPLICATIONS=["arches_for_music", "arches_for_dance"],
        SEARCH_COMPONENT_LOCATIONS=[
            # Same, but poorly ordered.
            "hiphop.search_components",
            "arches_for_music.search_components",
            "arches.app.search.components",
        ]
    )
    def test_arches_application_extension_explicit_poorly_ordered(self):
        with sync_overridden_test_settings_to_arches():
            search_dirs = get_directories(ExtensionType.SEARCH_COMPONENTS)
        self.assertEqual(search_dirs, [
            "arches.app.search.components",
            "arches_for_music.search_components",
            "arches_for_music.pkg.extensions.search_components",
            "arches_for_dance.search_components",
            "arches_for_dance.pkg.extensions.search_components",
            "hiphop.search_components",
        ])

    @override_settings(
        APP_NAME="hiphop",
        ARCHES_APPLICATIONS=["arches_for_music", "arches_for_dance"],
        ETL_MODULE_LOCATIONS=[
            # App not given.
            "arches.app.etl_modules",
        ]
    )
    def test_arches_application_extension_implicit(self):
        with sync_overridden_test_settings_to_arches():
            etl_modules = get_directories(ExtensionType.ETL_MODULES)
        self.assertEqual(etl_modules, [
            "arches.app.etl_modules",
            "arches_for_music.etl_modules",
            "arches_for_music.pkg.extensions.etl_modules",
            "arches_for_dance.etl_modules",
            "arches_for_dance.pkg.extensions.etl_modules",
        ])

    @override_settings(
        APP_NAME="hiphop",
        ARCHES_APPLICATIONS=["arches_for_music", "arches_for_dance"],
        DATATYPE_LOCATIONS=[],  # Nothing given.
    )
    def test_arches_application_extension_core_arches_implicit(self):
        with sync_overridden_test_settings_to_arches():
            datatypes = get_directories(ExtensionType.DATATYPES)
        self.assertEqual(datatypes, [
            "arches.app.datatypes",
            "arches_for_music.datatypes",
            "arches_for_music.pkg.extensions.datatypes",
            "arches_for_dance.datatypes",
            "arches_for_dance.pkg.extensions.datatypes",
        ])
