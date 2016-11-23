from base_widget_page import BaseWidgetPage
from page_locators import ResourceEditorPageLocators as locators
from selenium.webdriver.support import expected_conditions as EC

class ResourceEditorPage(BaseWidgetPage):
    """
    class to initialize the report-editor page

    """

    def __init__(self, driver, live_server_url, resource_instance_id):
        super(ResourceEditorPage, self).__init__(driver, live_server_url, '/resource/' + resource_instance_id)
        self.driver.set_window_size(1400,900)

    def save_edits(self):
        result = []
        for locator in (locators.SAVE_RESOURCE_EDITS_BUTTON, locators.MANAGE_MENU):
            el = self.driver.find_element(*locator)
            self.driver.execute_script("return arguments[0].scrollIntoView();", el)
            self.wait.until(
                EC.element_to_be_clickable(locator)
            ).click()
            result.append(el.text)
        self.wait.until(
            EC.element_to_be_clickable(locators.JUMP_TO_REPORT_BUTTON)
        ).click()
        
        return result

    def select_form_by_index(self, index):
        return locators.FORM_LIST_ITEMS[index]

    def select_form_by_name(self, name):
        for locator in locators.FORM_LIST_ITEMS:
            if locator + "/div[contains(@class, 'crud-card-main')]/a[contains(@class, 'listitem_name')]" == name:
                print 'found'
                return locator
