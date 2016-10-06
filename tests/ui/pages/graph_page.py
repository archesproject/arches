import re
from base_page import BasePage, script_returns_true
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from arches.urls import uuid_regex

class GraphPage(BasePage):
    """
    class to initialize the graph manager page

    """

    base_url = '/graph'

    def add_new_graph(self):
        self.driver.get(self.live_server_url + self.base_url)
        self.driver.find_element_by_xpath("//button[@type='button']").click()
        wait = WebDriverWait(self.driver, 20)
        element = wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "New Branch"))
        )
        element.click()

        graph_id = None
        try:
            graph_id = wait.until(
                script_returns_true('''
                    var matches = window.location.pathname.match(/(''' + uuid_regex + ''')/i);
                    if (matches && matches.length === 2){
                        return matches[1];
                    }else{
                        return false;
                    }
                ''')
            )
        except:
            pass

        return graph_id
        #re.compile(uuid_regex).findall(self.driver.current_url)
