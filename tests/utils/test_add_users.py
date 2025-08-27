from importlib.metadata import PackageNotFoundError

from django.contrib.auth.models import User
from django.core.management import call_command

from tests.base_test import ArchesTestCase


# these tests can be run from the command line via
# python manage.py test tests.utils.test_checks.SystemCheckTests --settings="tests.test_settings"


def raise_package_not_found_error(name):
    raise PackageNotFoundError


class AddUserTests(ArchesTestCase):
    def test_add_test_users(self):
        """Test adding users via the management command."""
        call_command("add_users", operation="test_users", user_count=4, power_user=True)

        self.assertEqual(User.objects.filter(username__startswith="tester").count(), 4)
        self.assertTrue(User.objects.filter(username="dev").exists())

    def test_load_users_from_csv(self):
        """Test adding users via the management command from a CSV file."""
        call_command(
            "add_users",
            operation="csv_users",
            csv_file="tests/fixtures/data/csv/user_test_data/users.csv",
        )
        self.assertTrue(User.objects.filter(username="robert").exists())
        self.assertTrue(User.objects.filter(username="fred").exists())
