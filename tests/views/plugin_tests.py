from django.test import TestCase

# these tests can be run from the command line via
# python manage.py test tests.views.plugin_tests --settings="tests.test_settings"


class PluginViewTests(TestCase):
    def test_post_auth_redirect_preserves_full_path(self):
        response = self.client.get("/plugins/bulk-data-manager/full-path")
        self.assertRedirects(
            response, "/auth/?next=/plugins/bulk-data-manager/full-path"
        )
