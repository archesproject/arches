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
from tests.ui.pages.node_page import NodePage
from tests.ui.pages.card_page import CardPage
from tests.ui.pages.map_widget_page import MapWidgetPage
import uuid

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

    def test_make_node(self):
        page = LoginPage(self.driver, self.live_server_url)
        page.login('admin', 'admin')
        graph_page = GraphPage(self.driver, self.live_server_url)
        graph_id = graph_page.add_new_graph()
        page = NodePage(self.driver, self.live_server_url, graph_id)
        node_ids = page.add_new_node('22000000-0000-0000-0000-000000000000', 'geojson-feature-collection')
        try:
            uuid.UUID(node_ids['node_id'])
            uuid.UUID(node_ids['nodegroup_id'])
            node_ids_are_valid = True
        except:
            node_id_is_valid = False
        self.assertTrue(node_ids_are_valid)

    def test_make_map_widget(self):
        page = LoginPage(self.driver, self.live_server_url)
        page.login('admin', 'admin')
        #Create a new branch model
        graph_page = GraphPage(self.driver, self.live_server_url)
        graph_id = graph_page.add_new_graph()
        #Add a node to it of type geojson
        branch_node_page = NodePage(self.driver, self.live_server_url, graph_id)
        node_ids = branch_node_page.add_new_node('22000000-0000-0000-0000-000000000000', 'geojson-feature-collection')
        #Create a resource model
        resource_graph_page = GraphPage(self.driver, self.live_server_url)
        resource_graph_id = resource_graph_page.add_new_graph("New Resource Model")
        #Add a the branch model created above to the
        resource_node_page = NodePage(self.driver, self.live_server_url, resource_graph_id)
        resource_node_page.add_new_node(graph_id, '', True)
        #Navigate to the card manager and click on the correspoding card for the node created above
        card_page = CardPage(self.driver, self.live_server_url, graph_id)
        card_id = card_page.select_card(node_ids)

        map_widget_page = MapWidgetPage(self.driver, self.live_server_url, 'card', card_id)
        tools_opened = map_widget_page.open_tools()

        self.assertTrue(tools_opened)
