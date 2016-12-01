import re
from base_page import BasePage
from page_locators import ReportManagerPageLocators as locators
from selenium.webdriver.support import expected_conditions as EC


class ReportManagerPage(BasePage):
    """
    class to initialize the report-manager page

    """

    def __init__(self, driver, live_server_url, graph_id):
        super(ReportManagerPage, self).__init__(driver, live_server_url, '/graph/' + graph_id + '/report_manager')

    def add_new_report(self):
        """
        Clicks on the add new report button and returns a new report_id

        """

        self.open()
        report_id = None
        for element in (locators.ADD_REPORT_BUTTON, locators.ADD_REPORT_MAP_HEADER_TEMPLATE):
            self.wait.until(
                EC.element_to_be_clickable(element)
            ).click()

        report_template = self.driver.find_element(*locators.SELECT_REPORT_CARD_BUTTON)
        report_id = report_template.get_attribute('data-arches-reportid')

        return report_id
