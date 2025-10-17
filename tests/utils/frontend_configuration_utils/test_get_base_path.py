from django.test import TestCase, override_settings
from arches.app.utils.frontend_configuration_utils.get_base_path import get_base_path


class TestGetBasePath(TestCase):
    @override_settings(APP_ROOT="/arches/app", ROOT_DIR="/arches")
    def test_returns_root_dir_when_app_root_is_direct_child_of_root_dir(self):
        result = get_base_path()
        self.assertEqual(result, "/arches")

    @override_settings(APP_ROOT="/srv/arches_instance/app", ROOT_DIR="/arches")
    def test_returns_app_root_when_app_root_is_not_child_of_root_dir(self):
        result = get_base_path()
        self.assertEqual(result, "/srv/arches_instance/app")

    @override_settings(APP_ROOT="/arches/app/", ROOT_DIR="/arches/")
    def test_trailing_slashes_are_ignored(self):
        result = get_base_path()
        self.assertEqual(result, "/arches")
