import re
from base_page import BasePage
from page_locators import CardPageLocators as locators
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from arches.urls import uuid_regex

class CardPage(BasePage):
    """
    class to initialize the card-manager page

    """

    def __init__(self, driver, live_server_url, graph_id):
        self.driver = driver
        self.live_server_url = live_server_url
        self.graph_id = graph_id
        self.base_url = '/graph/' + self.graph_id + '/card_manager'

    def select_card(self, node_ids):
        """
        Clicks on the card in the card-manager with a specified nodegroup_id

        """

        self.driver.get(self.live_server_url + self.base_url)
        self.driver.implicitly_wait(10)
        wait = WebDriverWait(self.driver, 20)
        card_xpath = "//*[@data-arches-nodegroupid='" + node_ids['nodegroup_id'] + "']"
        card_id = wait.until(
            EC.element_to_be_clickable((By.XPATH, card_xpath))
        ).get_attribute('data-arches-cardid')
        return card_id
