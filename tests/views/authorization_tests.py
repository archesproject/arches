import json
import time
from urllib.parse import urlencode
from unittest.mock import patch

from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.http import HttpResponse
from django.test.client import Client
from django.urls import reverse

from arches.app.models import models
from arches.app.models.system_settings import settings
from arches.app.utils.arches_crypto import AESCipher
from arches.app.utils.betterJSONSerializer import JSONSerializer
from tests.base_test import ArchesTestCase
from tests.utils.permission_test_utils import add_users

# these tests can be run from the command line via
# python manage.py test tests.views.authorization_tests --settings="tests.test_settings"


class GraphPublicationAuthorizationTests(ArchesTestCase):
    graph_fixtures = ["Data_Type_Model"]
    graphid = "330802c5-95bd-11e8-b7ac-acde48001122"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        User.objects.create_user("noperms", "noperms@test.com", "Test12345!")

    def test_anonymous_cannot_unpublish(self):
        url = reverse("unpublish_graph", kwargs={"graphid": self.graphid})
        with patch("arches.app.views.graph.Graph.unpublish") as unpublish:
            response = Client().post(url)
        self.assertIn(response.status_code, (302, 401, 403))
        unpublish.assert_not_called()

    def test_user_without_graph_editor_group_cannot_publish(self):
        client = Client()
        client.login(username="noperms", password="Test12345!")
        url = reverse("publish_graph", kwargs={"graphid": self.graphid})
        with patch("arches.app.views.graph.Graph.publish") as publish:
            response = client.post(url)
        self.assertIn(response.status_code, (302, 401, 403))
        publish.assert_not_called()

    def test_graph_editor_can_unpublish(self):
        client = Client()
        client.login(username="admin", password="admin")
        url = reverse("unpublish_graph", kwargs={"graphid": self.graphid})
        with patch("arches.app.views.graph.Graph.unpublish") as unpublish:
            response = client.post(url, "{}", content_type="application/json")
        self.assertEqual(response.status_code, 200)
        unpublish.assert_called_once()


class ConceptValueAuthorizationTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        User.objects.create_user("noperms", "noperms@test.com", "Test12345!")

    def setUp(self):
        concept = models.Concept.objects.create(nodetype_id="Concept")
        self.value = models.Value.objects.create(
            concept=concept,
            valuetype_id="prefLabel",
            value="test label",
            language_id="en",
        )

    def delete_value(self, client):
        return client.delete(
            reverse("concept_value"),
            json.dumps({"id": str(self.value.pk)}),
            content_type="application/json",
        )

    def test_anonymous_cannot_delete_value(self):
        response = self.delete_value(Client())
        self.assertIn(response.status_code, (302, 401, 403))
        self.assertTrue(models.Value.objects.filter(pk=self.value.pk).exists())

    def test_user_without_rdm_group_cannot_delete_value(self):
        client = Client()
        client.login(username="noperms", password="Test12345!")
        response = self.delete_value(client)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(models.Value.objects.filter(pk=self.value.pk).exists())

    def test_rdm_administrator_can_delete_value(self):
        client = Client()
        client.login(username="admin", password="admin")
        response = self.delete_value(client)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(models.Value.objects.filter(pk=self.value.pk).exists())

    def test_value_remains_readable_by_anonymous(self):
        response = Client().get(reverse("concept_value"), {"valueid": self.value.pk})
        self.assertEqual(response.status_code, 200)


class TwoFactorSettingsAuthorizationTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.victim = User.objects.create_user("victim", "victim@test.com", "Test12345!")
        cls.other = User.objects.create_user("other", "other@test.com", "Test12345!")
        for user in (cls.victim, cls.other):
            models.UserProfile.objects.get_or_create(user=user)

    def setUp(self):
        render_patch = patch(
            "arches.app.views.auth.render",
            side_effect=lambda request, template, context: HttpResponse(
                json.dumps({"link": context.get("link")})
            ),
        )
        self.render = render_patch.start()
        self.addCleanup(render_patch.stop)
        self.url = reverse("two-factor-authentication-settings")
        self.profile = models.UserProfile.objects.get(user=self.victim)
        self.profile.encrypted_mfa_hash = "existing"
        self.profile.save()

    def make_link(self, user, age_seconds=0):
        data = JSONSerializer().serialize(
            {"ts": int(time.time()) - age_seconds, "user": user}
        )
        return AESCipher(settings.SECRET_KEY).encrypt(data).decode()

    def test_post_with_user_id_only_is_rejected(self):
        response = Client().post(
            self.url,
            {"user-id": self.victim.pk, "generate-manual-key-button": "1"},
        )
        self.assertEqual(response.status_code, 403)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.encrypted_mfa_hash, "existing")

    def test_post_with_invalid_link_is_rejected(self):
        response = Client().post(
            self.url, {"link": "garbage", "delete-mfa-hash-button": "1"}
        )
        self.assertEqual(response.status_code, 403)

    def test_post_with_expired_link_is_rejected(self):
        link = self.make_link(self.victim, age_seconds=16 * 60)
        response = Client().post(
            self.url, {"link": link, "generate-manual-key-button": "1"}
        )
        self.assertEqual(response.status_code, 403)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.encrypted_mfa_hash, "existing")

    def test_get_with_expired_link_is_rejected(self):
        link = self.make_link(self.victim, age_seconds=16 * 60)
        response = Client().get(self.url, {"link": link})
        self.assertEqual(response.status_code, 403)

    def test_post_with_valid_link_acts_on_link_user_not_user_id(self):
        link = self.make_link(self.victim)
        response = Client().post(
            self.url,
            {
                "link": link,
                "user-id": self.other.pk,
                "generate-manual-key-button": "1",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertNotEqual(self.profile.encrypted_mfa_hash, "existing")
        other_profile = models.UserProfile.objects.get(user=self.other)
        self.assertFalse(other_profile.encrypted_mfa_hash)

    def test_valid_link_get_renders_form_carrying_link(self):
        link = self.make_link(self.victim)
        response = Client().get(self.url, {"link": link})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["link"], link)

    def test_valid_link_post_logs_out_only_link_user(self):
        victim_client, other_client = Client(), Client()
        victim_client.login(username="victim", password="Test12345!")
        other_client.login(username="other", password="Test12345!")
        before = Session.objects.count()
        Client().post(
            self.url,
            {"link": self.make_link(self.victim), "delete-mfa-hash-button": "1"},
        )
        self.assertEqual(Session.objects.count(), before - 1)


class RelatedResourcesAuthorizationTests(ArchesTestCase):
    graph_fixtures = ["Data_Type_Model"]
    graphid = "330802c5-95bd-11e8-b7ac-acde48001122"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        add_users()

    def setUp(self):
        self.root = models.ResourceInstance.objects.create(graph_id=self.graphid)
        self.target = models.ResourceInstance.objects.create(graph_id=self.graphid)
        self.unrelated_a = models.ResourceInstance.objects.create(graph_id=self.graphid)
        self.unrelated_b = models.ResourceInstance.objects.create(graph_id=self.graphid)
        self.rr = models.ResourceXResource.objects.create(
            resourceinstanceidfrom=self.root,
            resourceinstanceidto=self.target,
            relationshiptype="http://www.w3.org/2004/02/skos/core#related",
        )
        self.foreign_rr = models.ResourceXResource.objects.create(
            resourceinstanceidfrom=self.unrelated_a,
            resourceinstanceidto=self.unrelated_b,
            relationshiptype="http://www.w3.org/2004/02/skos/core#related",
        )
        self.client = Client()
        self.client.login(username="ben", password="Test12345!")

    def delete(self, relationship_ids, root=None, url_id=None):
        url = reverse("related_resources", kwargs={"resourceid": url_id or ""})
        query = urlencode(
            {
                "resourcexids[]": [str(i) for i in relationship_ids],
                "root_resourceinstanceid": str(root or self.root.pk),
            },
            doseq=True,
        )
        return self.client.delete(f"{url}?{query}")

    def update(self, relationship_ids, root=None, url_id=None):
        url = reverse("related_resources", kwargs={"resourceid": url_id or ""})
        return self.client.post(
            url,
            {
                "relationship_properties[relationshiptype]": "http://www.w3.org/2004/02/skos/core#broader",
                "relationship_properties[datestarted]": "",
                "relationship_properties[dateended]": "",
                "relationship_properties[notes]": "changed",
                "root_resourceinstanceid": str(root or self.root.pk),
                "relationship_ids[]": [str(i) for i in relationship_ids],
            },
        )

    def test_delete_without_edit_permission_is_denied(self):
        with patch("arches.app.views.resource.user_can_edit_resource") as can_edit:
            can_edit.return_value = False
            response = self.delete([self.rr.pk])
        self.assertEqual(response.status_code, 403)
        self.assertTrue(models.ResourceXResource.objects.filter(pk=self.rr.pk).exists())

    def test_update_without_edit_permission_is_denied(self):
        with patch("arches.app.views.resource.user_can_edit_resource") as can_edit:
            can_edit.return_value = False
            response = self.update([self.rr.pk])
        self.assertEqual(response.status_code, 403)
        self.rr.refresh_from_db()
        self.assertNotEqual(self.rr.notes, "changed")

    def test_create_without_edit_permission_is_denied(self):
        url = reverse("related_resources", kwargs={"resourceid": ""})
        with patch("arches.app.views.resource.user_can_edit_resource") as can_edit:
            can_edit.return_value = False
            response = self.client.post(
                url,
                {
                    "relationship_properties[relationshiptype]": "x",
                    "relationship_properties[datestarted]": "",
                    "relationship_properties[dateended]": "",
                    "relationship_properties[notes]": "",
                    "root_resourceinstanceid": str(self.root.pk),
                    "instances_to_relate[]": [str(self.unrelated_a.pk)],
                },
            )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            models.ResourceXResource.objects.filter(
                resourceinstanceidfrom=self.root
            ).count(),
            1,
        )

    def test_relationship_not_involving_root_is_denied(self):
        response = self.delete([self.foreign_rr.pk])
        self.assertEqual(response.status_code, 403)
        response = self.update([self.foreign_rr.pk])
        self.assertEqual(response.status_code, 403)
        self.foreign_rr.refresh_from_db()
        self.assertNotEqual(self.foreign_rr.notes, "changed")

    def test_missing_or_mismatched_root_is_denied(self):
        url = reverse("related_resources", kwargs={"resourceid": ""})
        response = self.client.delete(f"{url}?resourcexids[]={self.rr.pk}")
        self.assertEqual(response.status_code, 403)
        response = self.delete([self.rr.pk], url_id=str(self.unrelated_a.pk))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(models.ResourceXResource.objects.filter(pk=self.rr.pk).exists())

    def test_anonymous_cannot_delete(self):
        url = reverse("related_resources", kwargs={"resourceid": ""})
        response = Client().delete(
            f"{url}?resourcexids[]={self.rr.pk}&root_resourceinstanceid={self.root.pk}"
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(models.ResourceXResource.objects.filter(pk=self.rr.pk).exists())

    def test_editor_can_delete_own_relationship(self):
        response = self.delete([self.rr.pk])
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            models.ResourceXResource.objects.filter(pk=self.rr.pk).exists()
        )

    def test_editor_can_update_own_relationship(self):
        response = self.update([self.rr.pk], url_id=str(self.root.pk))
        self.assertEqual(response.status_code, 200)
        self.rr.refresh_from_db()
        self.assertEqual(self.rr.notes, "changed")
