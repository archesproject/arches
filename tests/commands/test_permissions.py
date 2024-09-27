# these tests can be run from the command line via
# python manage.py test tests.commands.test_permissions --settings="tests.test_settings"


from django.core.management import call_command
from tests.base_test import ArchesTestCase
from django.contrib.auth.models import Group, User
from arches.app.utils.permission_backend import PermissionBackend
from arches.app.models import models


class PermissionsCommandTest(ArchesTestCase):

    def setUp(cls):
        resource_reviewer_group = Group.objects.get(name="Resource Reviewer")
        cls.user = User.objects.create_user(username="test_user")
        cls.user.groups.add(resource_reviewer_group)
        cls.etl_module = models.ETLModule.objects.all()[0]
        cls.permission_backend = PermissionBackend()

    def test_grant_perm(self):
        call_command(
            "permissions",
            permission="view",
            action="grant",
            group="Resource Reviewer",
            type="etlmodule",
        )
        has_perm = self.permission_backend.has_perm(
            self.user, "view_etlmodule", obj=self.etl_module
        )
        self.assertTrue(has_perm)

    def test_revoke_perm(self):
        call_command(
            "permissions",
            permission="view",
            action="grant",
            group="Resource Reviewer",
            type="etlmodule",
        )
        call_command(
            "permissions",
            permission="view",
            action="revoke",
            group="Resource Reviewer",
            type="etlmodule",
        )
        has_perm = self.permission_backend.has_perm(
            self.user, "view_etlmodule", obj=self.etl_module
        )
        self.assertFalse(has_perm)
