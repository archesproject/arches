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

from django.conf import settings
from django.core.urlresolvers import reverse
from django_webtest import WebTest
from django.contrib.auth.models import User

# see WebTest API for more:
# http://webtest.readthedocs.org/en/latest/api.html
class Main(WebTest):
    def setUp(self):
        super(Main, self).setUp()
        self.user = User.objects.create_user('test', 'test@archesproject.org', 'password')
        self.user.save()

    def test_login(self):
        index = self.app.get('/')
        login = index.click('Login')
        login_form = login.forms['login-form']
        login_form['username'] = 'test'
        login_form['password'] = 'password'
        response = login_form.submit('submit')
        self.assertTrue(response.status_code == 302)
        response = response.follow()
        assert 'Welcome test - Logout' in response

    def tearDown(self):
        super(Main, self).tearDown()
        self.user.delete()
