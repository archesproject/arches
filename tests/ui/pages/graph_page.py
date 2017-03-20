import os
from tests import test_settings
from base_page import BasePage, script_returns_true
from page_locators import GraphPageLocators as locators
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from arches.urls import uuid_regex

class GraphPage(BasePage):
    """
    class to initialize the graph manager page

    """

    def __init__(self, driver, live_server_url):
        super(GraphPage, self).__init__(driver, live_server_url, '/graph/')

    def add_new_graph(self, graph_type="New Branch"):
        self.open()
        self.driver.find_element(*locators.ADD_BUTTON).click()
        self.wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, graph_type))
        ).click()

        graph_config_locators = [
            locators.STATUS_TAB,
            locators.ACTIVE_STATUS_BUTTON,
            locators.SAVE_EDITS_BUTTON
        ]

        for locator in graph_config_locators:
            self.wait.until(
                EC.element_to_be_clickable(locator)
            ).click()

        graph_id = None
        try:
            graph_id = self.wait.until(
                script_returns_true('''
                    try{
                        var matches = window.location.pathname.match(/(''' + uuid_regex + ''')/i);
                        if (matches && matches.length === 2){
                            return matches[1];
                        }else{
                            return false;
                        }
                    }catch(err){
                        return false;
                    }
                ''')
            )
        except:
            pass

        return graph_id

    # def import_arches_json(self):
    #     self.driver.find_element(*locators.ADD_BUTTON).click()
    #     file_input = self.driver.find_element(*locators.IMPORT_GRAPH_BUTTON)

    #     path_to_file = os.path.join(test_settings.TEST_ROOT, 'fixtures', 'resource_graphs', 'Cardinality Test Model.json')
    #     file_input.send_keys(path_to_file)

    #     management.call_command('packages', operation='import_graphs', source='tests/fixtures/resource_graphs/archesv4_resource.json')
