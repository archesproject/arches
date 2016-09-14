# initially from 
# https://github.com/Victory/django-travis-saucelabs/blob/master/mysite/saucetests/tests.py
import os
import sys

from tests import test_settings
from selenium import webdriver
from django.test import LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from tests.ui.pages.login_page import LoginPage
from tests.ui.pages.graph_page import GraphPage


if test_settings.RUN_LOCAL:
    browsers = test_settings.LOCAL_BROWSERS
else:
    from sauceclient import SauceClient
    sauce = SauceClient(test_settings.SAUCE_USERNAME, test_settings.SAUCE_ACCESS_KEY)
    browsers = test_settings.REMOTE_BROWSERS

def on_platforms(platforms, local):
    if local:
        def decorator(base_class):
            module = sys.modules[base_class.__module__].__dict__
            for i, platform in enumerate(platforms):
                d = dict(base_class.__dict__)
                d['browser'] = platform
                name = "%s_%s" % (base_class.__name__, i + 1)
                module[name] = type(name, (base_class,), d)
            pass
        return decorator

    def decorator(base_class):
        module = sys.modules[base_class.__module__].__dict__
        for i, platform in enumerate(platforms):
            d = dict(base_class.__dict__)
            d['desired_capabilities'] = platform
            name = "%s_%s" % (base_class.__name__, i + 1)
            module[name] = type(name, (base_class,), d)
    return decorator


@on_platforms(browsers, test_settings.RUN_LOCAL)
class UITest(StaticLiveServerTestCase):
    """
    Runs a test using travis-ci and saucelabs

    """

    #serialized_rollback = True

    def _fixture_teardown(self):
        pass

    def setUp(self):
        if test_settings.RUN_LOCAL:
            self.setUpLocal()
        else:
            self.setUpSauce()

    def tearDown(self):
        if test_settings.RUN_LOCAL:
            self.tearDownLocal()
        else:
            self.tearDownSauce()

    def setUpSauce(self):
        self.desired_capabilities['name'] = self.id()
        self.desired_capabilities['tunnel-identifier'] = os.environ['TRAVIS_JOB_NUMBER']
        self.desired_capabilities['build'] = os.environ['TRAVIS_BUILD_NUMBER']
        self.desired_capabilities['tags'] = [os.environ['TRAVIS_PYTHON_VERSION'], 'CI']

        print self.desired_capabilities

        sauce_url = "http://%s:%s@ondemand.saucelabs.com:80/wd/hub"
        self.driver = webdriver.Remote(
            desired_capabilities=self.desired_capabilities,
            command_executor=sauce_url % (test_settings.SAUCE_USERNAME, test_settings.SAUCE_ACCESS_KEY)
        )
        self.driver.implicitly_wait(5)

    def setUpLocal(self):
        self.driver = getattr(webdriver, self.browser)()
        self.driver.implicitly_wait(3)

    def tearDownLocal(self):
        self.driver.quit()

    def tearDownSauce(self):
        print("\nLink to your job: \n "
              "https://saucelabs.com/jobs/%s \n" % self.driver.session_id)
        try:
            if sys.exc_info() == (None, None, None):
                sauce.jobs.update_job(self.driver.session_id, passed=True)
            else:
                sauce.jobs.update_job(self.driver.session_id, passed=False)
        finally:
            self.driver.quit()

    def test_login(self):
        page = LoginPage(self.driver, self.live_server_url)
        page.login('admin', 'admin')

        self.assertEqual(self.driver.current_url, self.live_server_url + '/index.htm')

    def test_make_graph(self):
        page = LoginPage(self.driver, self.live_server_url)
        page.login('admin', 'admin')

        page = GraphPage(self.driver, self.live_server_url)
        graph_id = page.add_new_graph()
        
        self.assertEqual(self.driver.current_url, '%s/graph/%s/settings' % (self.live_server_url, graph_id))
