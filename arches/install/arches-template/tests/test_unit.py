'''
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
'''

from django.core.urlresolvers import reverse
from django.test import SimpleTestCase
from django.contrib.auth.models import User
from django.test.client import RequestFactory
from arches.app.views.main import auth
from django.contrib.sessions.middleware import SessionMiddleware

class Main(SimpleTestCase):
    def setUp(self):
        super(Main, self).setUp()
        self.user = User.objects.create_user('test', 'test@archesproject.org', 'password')
        self.user.save()

    def test_login(self):
        factory = RequestFactory()
        request = factory.post(reverse('auth'), {'username': 'test', 'password': 'password'})
        request.user = self.user
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        response = auth(request)
        self.assertTrue(response.status_code == 302)
        self.assertTrue(response.get('location') == reverse('home'))

    def tearDown(self):
        super(Main, self).tearDown()
        self.user.delete()
