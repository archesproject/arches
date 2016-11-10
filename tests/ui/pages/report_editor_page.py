import re
from map_widget_page import MapWidgetPage
from page_locators import ReportEditorPageLocators as locators
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ReportEditorPage(MapWidgetPage):
    """
    Class to initialize a report template page. Inherits functions from
    the map widget page, but could inherit from other widget pages as well

    """

    def __init__(self, driver, live_server_url, target_page, page_id):
        super(MapWidgetPage, self).__init__(target_page, page_id)
        self.driver = driver
        self.live_server_url = live_server_url
        self.page_id = page_id
        self.base_url = '/' + target_page + '/' + self.page_id
        self.wait = WebDriverWait(self.driver, 20)
        self.driver.maximize_window()

    def save_report(self, report_name):
        self.driver.find_element(*locators.ACTIVATE_REPORT_BUTTON).click()
        report_name_input = self.driver.find_element(*locators.REPORT_NAME_INPUT)
        report_name_input.send_keys(report_name)
        self.driver.find_element(*locators.SAVE_EDITS_BUTTON).click()
        print report_name, 'created'
