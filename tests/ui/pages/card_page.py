import re
from base_page import BasePage
from page_locators import CardPageLocators as locators
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class CardPage(BasePage):
    """
    class to initialize the card-manager page

    """

    def __init__(self, driver, live_server_url, graph_id):
        super(CardPage, self).__init__(driver, live_server_url, '/graph/' + graph_id + '/card_manager')

    def select_card(self, node_ids):
        """
        Clicks on the card in the card-manager with a specified nodegroup_id

        """

        self.open()
        card_xpath = "//*[@data-arches-nodegroupid='" + node_ids['nodegroup_id'] + "']"
        card_id = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, card_xpath))
        ).get_attribute('data-arches-cardid')
        return card_id
