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
from sst.actions import *
from sst.cases import SSTTestCase
from django.contrib.auth.models import User
import subprocess
import sys
import time
import os
import signal

class Main(SSTTestCase):
    def setUp(self):
        super(Main, self).setUp()
        self.user = User.objects.create_user('test', 'test@archesproject.org', 'password')
        self.user.save()
        cmd = [sys.executable,settings.PACKAGE_ROOT + '/../manage.py','runserver','8001','--settings=settings_tests']
        self.pid = subprocess.Popen(cmd, preexec_fn=os.setpgrp, stdout=open(os.devnull, 'wb'), stderr=subprocess.STDOUT).pid
        # give it a moment to start up.
        time.sleep(1)

    def test_login(self):
        set_base_url('http://localhost:8001/')
        go_to(reverse('home'))
        click_link('auth-link')
        write_textfield(get_element(name='username'), 'test')
        write_textfield(get_element(name='password'), 'password')
        click_button('login-btn')
        assert_text_contains('auth-link', 'WELCOME TEST - LOGOUT')

    def tearDown(self):
        super(Main, self).tearDown()
        self.user.delete()
        os.killpg(self.pid, signal.SIGTERM)
        time.sleep(1)
