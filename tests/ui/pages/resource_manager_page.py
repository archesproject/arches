from base_page import BasePage, script_returns_true
from page_locators import ResourceManagerPageLocators as locators
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from arches.urls import uuid_regex

class ResourceManagerPage(BasePage):
    """
    class to initialize the report-manager page

    """

    def __init__(self, driver, live_server_url, graph_id):
        super(ResourceManagerPage, self).__init__(driver, live_server_url, '/resource')
        self.graph_id = graph_id

    def add_new_resource(self):
        """
        Clicks on the add new resource button and returns a new resource_id

        """

        self.open()
        resource_id = None
        add_new_resource_button = (By.XPATH, "//*[@data-arches-graphid='" + self.graph_id + "']")
        self.wait.until(
            EC.element_to_be_clickable(add_new_resource_button)
        ).click()
        try:
            resource_id = self.wait.until(
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

        return resource_id

