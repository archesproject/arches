# initially from 
# https://github.com/Victory/django-travis-saucelabs/blob/master/mysite/saucetests/tests.py
import os
import sys

from tests import test_settings
from selenium import webdriver
from django.test import LiveServerTestCase

RUN_LOCAL = test_settings.RUN_TESTS_LOCAL

if RUN_LOCAL:
    # could add Chrome, PhantomJS etc... here
    browsers = ['Firefox']
else:
    from sauceclient import SauceClient
    USERNAME = os.environ.get('SAUCE_USERNAME')
    ACCESS_KEY = os.environ.get('SAUCE_ACCESS_KEY')
    sauce = SauceClient(USERNAME, ACCESS_KEY)

    browsers = [
        {"platform": "Windows 8.1",
         "browserName": "internet explorer",
         "version": "11"},
        {"platform": "Mac OS X 10.9",
         "browserName": "chrome",
         "version": "44"},
        {"platform": "Linux",
         "browserName": "firefox",
         "version": "43"}
    ]


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


@on_platforms(browsers, RUN_LOCAL)
class LoginTest(LiveServerTestCase):
    """
    Runs a test using travis-ci and saucelabs

    """

    def setUp(self):
        if RUN_LOCAL:
            self.setUpLocal()
        else:
            self.setUpSauce()

    def tearDown(self):
        if RUN_LOCAL:
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
            command_executor=sauce_url % (USERNAME, ACCESS_KEY)
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
        self.driver.get(self.live_server_url)
        login_link = self.driver.find_element_by_id("auth-link")
        login_link.click()
        username_input = self.driver.find_element_by_name("username")
        password_input = self.driver.find_element_by_name("password")
        username_input.send_keys('admin')
        password_input.send_keys('admin')
        submit_button = self.driver.find_element_by_xpath("//button[@type='submit']")
        submit_button.click()

        self.assertEqual(self.driver.current_url, self.live_server_url + '/graph/')