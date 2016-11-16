import re
from base_page import BasePage, script_returns_true
from page_locators import ReportManagerPageLocators as locators
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from arches.urls import uuid_regex
from selenium.common.exceptions import StaleElementReferenceException


class ReportManagerPage(BasePage):
    """
    class to initialize the report-manager page

    """

    def __init__(self, driver, live_server_url, graph_id):
        self.driver = driver
        self.live_server_url = live_server_url
        self.graph_id = graph_id
        self.base_url = '/graph/' + self.graph_id + '/report_manager'
        self.wait = WebDriverWait(self.driver, 20)

    def add_new_report(self):
        """
        Clicks on the add new report button and returns a new report_id

        """

        self.wait.until(
            EC.invisibility_of_element_located(locators.LOADING_MASK)
        )
        self.driver.get(self.live_server_url + self.base_url)
        self.driver.implicitly_wait(10)
        report_id = None
        for element in (locators.ADD_REPORT_BUTTON, locators.ADD_REPORT_MAP_HEADER_TEMPLATE):
            self.wait.until(
                EC.element_to_be_clickable(element)
            ).click()

        report_template = self.driver.find_element(*locators.SELECT_REPORT_CARD_BUTTON)
        report_id = report_template.get_attribute('data-arches-reportid')

        return report_id
