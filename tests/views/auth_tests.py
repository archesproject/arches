"""
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import base64
from tests.base_test import ArchesTestCase, OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET, CREATE_TOKEN_SQL
from django.db import connection
from django.urls import reverse
from django.contrib.auth.models import User, Group, AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from django.test.client import Client
from arches.app.views.auth import LoginView
from arches.app.views.concept import RDMView
from arches.app.utils.middleware import SetAnonymousUser

# these tests can be run from the command line via
# python manage.py test tests/views/auth_tests.py --pattern="*.py" --settings="tests.test_settings"


class AuthTests(ArchesTestCase):
    @classmethod
    def setUpClass(cls):
        cls.factory = RequestFactory()
        cls.client = Client()
        cls.user = User.objects.create_user("test", "test@archesproject.org", "password")

        rdm_admin_group = Group.objects.get(name="RDM Administrator")
        cls.user.groups.add(rdm_admin_group)
        cls.anonymous_user = User.objects.get(username="anonymous")

        cls.token = "abc"
        cls.oauth_client_id = OAUTH_CLIENT_ID
        cls.oauth_client_secret = OAUTH_CLIENT_SECRET

        sql_str = CREATE_TOKEN_SQL.format(token=cls.token, user_id=cls.user.pk)
        cursor = connection.cursor()
        cursor.execute(sql_str)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def test_login(self):
        """
        Test that a user can login and is redirected to the home page

        """

        request = self.factory.post(reverse("auth"), {"username": "test", "password": "password"})
        request.user = self.user
        apply_middleware(request)
        view = LoginView.as_view()
        response = view(request)

        self.assertTrue(response.status_code == 302)
        self.assertTrue(response.get("location") == reverse("home"))

    def test_login_w_email(self):
        """
        Test that a user can login with their email address and is redirected to the home page

        """

        request = self.factory.post(reverse("auth"), {"username": "test@archesproject.org", "password": "password"})
        request.user = self.user
        apply_middleware(request)
        view = LoginView.as_view()
        response = view(request)

        self.assertTrue(response.status_code == 302)
        self.assertTrue(response.get("location") == reverse("home"))

    def test_invalid_credentials(self):
        """
        Test that a user can't login with invalid credentials

        """

        request = self.factory.post(reverse("auth"), {"username": "wrong", "password": "wrong"})
        request.user = self.user
        apply_middleware(request)
        view = LoginView.as_view()
        response = view(request)

        self.assertTrue(response.status_code == 401)

    def test_logout(self):
        """
        Test that a user can logout

        """

        view = LoginView.as_view()

        request = self.factory.post(reverse("auth"), {"username": "test", "password": "password"})
        request.user = self.user
        apply_middleware(request)
        response = view(request)

        request = self.factory.get(reverse("auth"), {"logout": "true"})
        request.user = self.user
        apply_middleware(request)
        response = view(request)

        self.assertTrue(response.status_code == 302)
        self.assertTrue(response.get("location") == reverse("auth"))

    def test_get_oauth_token(self):
        key = "{0}:{1}".format(self.oauth_client_id, self.oauth_client_secret)
        client = Client(HTTP_AUTHORIZATION="Basic %s" % base64.b64encode(key.encode("UTF-8")).decode("UTF-8"))

        # make sure we can POST to the authorize endpoint and get back the proper form
        # response = client.post(reverse('auth'), {'username': 'test', 'password': 'password', 'next': 'oauth2:authorize'})
        # response = client.get(reverse('oauth2:authorize'), {
        #     'client_id': self.oauth_client_id,
        #     'state': 'random_state_string',
        #     'response_type': 'code'
        # }, follow=True)
        # form = response.context['form']
        # data = form.cleaned_data
        # self.assertTrue(response.status_code == 200)
        # self.assertTrue(data['client_id']  == self.oauth_client_id)

        # response = self.client.post(reverse('oauth2:token'), {
        #     'grant_type': 'password',
        #     'username': 'test',
        #     'password': 'password',
        #     'scope': 'read write',
        # })

        response = client.post(
            reverse("oauth2:token"), {"grant_type": "client_credentials", "scope": "read write", "client_id": self.oauth_client_id}
        )

        # print response
        # {"access_token": "ZzVGlb8SLLeCOaogtyhRpBoFbKcuqI", "token_type": "Bearer", "expires_in": 36000, "scope": "read write"}
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json()["token_type"] == "Bearer")

    def test_use_oauth_token_for_access_to_privileged_page(self):
        """
        Test that we can use a valid OAuth Token to gain access to a page that requires a logged in user

        """

        response = self.client.get(reverse("rdm", args=[""]))
        self.assertTrue(response.status_code == 302)
        self.assertTrue(response.get("location").split("?")[0] == reverse("auth"))
        self.assertTrue(response.get("location").split("?")[0] != reverse("rdm", args=[""]))

        response = self.client.get(reverse("rdm", args=[""]), HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertTrue(response.status_code == 200)

    def test_set_anonymous_user_middleware(self):
        """
        Test to check that any anonymous request to the system gets the anonymous user set on the
        request as opposed to the built-in AnonymousUser supplied by django

        """

        request = self.factory.get(reverse("home"))
        request.user = AnonymousUser()
        set_anonymous_user(request)

        self.assertTrue(request.user.username == "anonymous")
        self.assertTrue(request.user != AnonymousUser())

    def test_nonauth_user_access_to_RDM(self):
        """
        Test to check that a non-authenticated user can't access the RDM page, or POST data to the url

        """

        request = self.factory.get(reverse("rdm", args=[""]))
        request.user = AnonymousUser()
        apply_middleware(request)
        view = RDMView.as_view()
        response = view(request)

        self.assertTrue(response.status_code == 302)
        self.assertTrue(response.get("location").split("?")[0] == reverse("auth"))

        # test get a concept
        request = self.factory.get(reverse("rdm", kwargs={"conceptid": "00000000-0000-0000-0000-000000000001"}))
        request.user = AnonymousUser()
        apply_middleware(request)
        view = RDMView.as_view()
        response = view(request)

        self.assertTrue(response.status_code == 302)
        self.assertTrue(response.get("location").split("?")[0] == reverse("auth"))

        # test update a concept
        concept = {
            "id": "00000000-0000-0000-0000-000000000001",
            "legacyoid": "ARCHES",
            "nodetype": "ConceptScheme",
            "values": [],
            "subconcepts": [
                {
                    "values": [
                        {"value": "test label", "language": "en-US", "category": "label", "type": "prefLabel", "id": "", "conceptid": ""},
                        {"value": "", "language": "en-US", "category": "note", "type": "scopeNote", "id": "", "conceptid": ""},
                    ],
                    "relationshiptype": "hasTopConcept",
                    "nodetype": "Concept",
                    "id": "",
                    "legacyoid": "",
                    "subconcepts": [],
                    "parentconcepts": [],
                    "relatedconcepts": [],
                }
            ],
        }

        request = self.factory.post(reverse("rdm", kwargs={"conceptid": "00000000-0000-0000-0000-000000000001"}), concept)
        request.user = AnonymousUser()
        apply_middleware(request)
        view = RDMView.as_view()
        response = view(request)

        self.assertTrue(response.status_code == 302)
        self.assertTrue(response.get("location").split("?")[0] == reverse("auth"))


def apply_middleware(request):
    save_session(request)
    set_anonymous_user(request)


def save_session(request):
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()


def set_anonymous_user(request):
    set_anon_middleware = SetAnonymousUser()
    set_anon_middleware.process_request(request)


def strip_response_location(response):
    return response.get("location").replace("http://testserver", "").split("?")[0]
