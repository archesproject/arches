import re
from base_page import BasePage, script_returns_true
from page_locators import GraphPageLocators as locators
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from arches.urls import uuid_regex

class GraphPage(BasePage):
    """
    class to initialize the graph manager page

    """

    base_url = '/graph'

    def add_new_graph(self, graph_type="New Branch"):
        self.driver.get(self.live_server_url + self.base_url)
        # self.driver.implicitly_wait(10)
        wait = WebDriverWait(self.driver, 20)
        wait.until(
            EC.invisibility_of_element_located(locators.LOADING_MASK)
        )
        self.driver.find_element(*locators.ADD_BUTTON).click()
        wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, graph_type))
        ).click()

        graph_config_locators = [
            locators.STATUS_TAB,
            locators.ACTIVE_STATUS_BUTTON,
            locators.SAVE_EDITS_BUTTON
            ]

        for locator in graph_config_locators:
            wait.until(
                EC.element_to_be_clickable(locator)
            ).click()

        graph_id = None
        try:
            graph_id = wait.until(
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
        #re.compile(uuid_regex).findall(self.driver.current_url)
