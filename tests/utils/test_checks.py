from importlib.metadata import PackageNotFoundError
from unittest import mock

from django.apps import apps
from django.core.management import call_command
from django.core.management.base import SystemCheckError
from django.test import SimpleTestCase


# these tests can be run from the command line via
# python manage.py test tests.utils.test_checks.SystemCheckTests --settings="tests.test_settings"


def raise_package_not_found_error(name):
    raise PackageNotFoundError


class SystemCheckTests(SimpleTestCase):
    def test_compatibility(self):
        """Patch core arches to be an "arches application" so we can check
        its range of compatible arches version, which it won't have.
        """

        core_arches_appconfig = apps.get_app_config("arches")
        core_arches_appconfig.is_arches_application = True
        self.addCleanup(setattr, core_arches_appconfig, "is_arches_application", False)

        # Test something pip-installed.
        with self.assertRaisesMessage(
            SystemCheckError, "Invalid or missing arches requirement"
        ):
            call_command("check")

        # Mock having to go to the pyproject.toml
        with mock.patch("arches.apps.requires", raise_package_not_found_error):
            with self.assertRaisesMessage(
                SystemCheckError, "Invalid or missing arches requirement"
            ):
                call_command("check")

        # Mock an incompatible version requirement.
        with mock.patch("arches.apps.requires", lambda app_name: ["arches==0.0.1"]):
            with self.assertRaisesMessage(
                SystemCheckError, "Incompatible arches requirement"
            ):
                call_command("check")
