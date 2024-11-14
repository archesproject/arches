from importlib.metadata import PackageNotFoundError
from unittest import mock

from django.apps import apps
from django.core.checks import Tags
from django.core.management import call_command
from django.core.management.base import SystemCheckError
from django.test import SimpleTestCase, override_settings


# these tests can be run from the command line via
# python manage.py test tests.utils.test_checks.SystemCheckTests --settings="tests.test_settings"


def raise_package_not_found_error(name):
    raise PackageNotFoundError


class SystemCheckTests(SimpleTestCase):
    @override_settings(DEBUG=False)
    def test_compatibility(self):
        """Patch core arches to be an "arches application" so we can check
        its range of compatible arches version, which it won't have.
        """

        core_arches_appconfig = apps.get_app_config("arches")
        core_arches_appconfig.is_arches_application = True
        self.addCleanup(setattr, core_arches_appconfig, "is_arches_application", False)

        # Test something pip-installed.
        with self.assertRaisesMessage(
            SystemCheckError,
            "Arches requirement is invalid, missing, or given by a URL.",
        ):
            call_command("check", tag=[Tags.compatibility])

        # Mock having to go to the pyproject.toml
        with mock.patch("arches.apps.requires", raise_package_not_found_error):
            with self.assertRaisesMessage(
                SystemCheckError,
                "Arches requirement is invalid, missing, or given by a URL.",
            ):
                call_command("check", tag=[Tags.compatibility])

        # Mock an incompatible version requirement.
        with mock.patch(
            "arches.apps.requires",
            lambda app_name: ["arches-for-x==0.0.1", "arches==1.0.1"],
        ):
            with self.assertRaisesMessage(SystemCheckError, "arches==1.0.1"):
                call_command("check", tag=[Tags.compatibility])
