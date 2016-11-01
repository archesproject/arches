import re
from base_page import BasePage

from graph_page import GraphPage, script_returns_true
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from arches.urls import uuid_regex

class NodePage(BasePage):
    """
    class to initialize the login page

    """

    def __init__(self, driver, live_server_url, graph_id):
        self.driver = driver
        self.live_server_url = live_server_url
        self.graph_id = graph_id
        self.base_url = 'graph/' + self.graph_id

    def get_graph_id(self, graph_id):
        print graph_id
        return graph_id

    def add_new_node(self, data_type_name):
        self.driver.get(self.live_server_url + '/' + self.base_url)

        wait = WebDriverWait(self.driver, 20)

        wait.until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".loading-mask"))
        )

        xpaths = {
            'new_node_button': "//*[@id='node-crud']/ul/li[2]/a",
            'first_in_branch_list': "//div[@id='branch-library']//div//div[@class='library-card']",
            'append_button': "//*[@id='branch-append']",
            'selected_node_in_left_container': "//*[@id='node-form']/div[1]/div/div[2]/div[2]/div/a",
            'save_edits_button': "//*[@id='content-container']/div/div[4]/div[3]/span/button[2]"
        }

        self.driver.find_element_by_xpath(xpaths['new_node_button']).click()

        xpaths_to_wait_on = [
            xpaths['first_in_branch_list'],
            xpaths['append_button'],
            xpaths['selected_node_in_left_container']
        ]

        for xpath in xpaths_to_wait_on:
            wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            ).click()

        selected_data_type = ''
        for el in self.driver.find_elements_by_class_name('active-result'):
            if el.text == data_type_name:
                selected_data_type = el

        selected_data_type.click()

        save_edits = self.driver.find_element_by_xpath(xpaths['save_edits_button'])
        save_edits.click()
