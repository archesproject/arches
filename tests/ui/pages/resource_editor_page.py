from base_widget_page import BaseWidgetPage
from page_locators import ResourceEditorPageLocators as locators
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class ResourceEditorPage(BaseWidgetPage):
    """
    class to initialize the report-editor page

    """

    def __init__(self, driver, live_server_url, resource_instance_id):
        super(ResourceEditorPage, self).__init__(driver, live_server_url, '/resource/' + resource_instance_id)
        self.driver.set_window_size(1400,900)

    def add_widget(self, widget, tab_index=0, widget_index=0):
        return widget(self, tab_index=tab_index, widget_index=widget_index) 

    def save_edits(self):
        result = []
        
        locator = locators.SAVE_RESOURCE_EDITS_BUTTON
        el = self.driver.find_element(*locator)
        self.driver.execute_script("return arguments[0].scrollIntoView();", el)
        self.wait.until(
            EC.element_to_be_clickable(locator)
        ).click()

        result.append(el.text)
        return result

    def open_report(self):
        locator = locators.MANAGE_MENU
        el = self.driver.find_element(*locator)
        self.driver.execute_script("return arguments[0].scrollIntoView();", el)
        self.wait.until(
            EC.element_to_be_clickable(locator)
        ).click()

        self.wait.until(
            EC.element_to_be_clickable(locators.JUMP_TO_REPORT_BUTTON)
        ).click()

    def select_form_by_index(self, index):
        elements = self.driver.find_elements(*locators.FORM_LIST_ITEMS)
        elements[index].click()
        self.wait_until_loading_mask_is_gone()
        return elements[index]

    def select_form_by_name(self, name):
        for element in self.driver.find_elements(*locators.FORM_LIST_ITEMS):
            el = element.find_element(By.XPATH, "./div[contains(@class, 'crud-card-main')]/a[contains(@class, 'listitem_name')]")
            if el.text == name:
                el.click()
                self.wait_until_loading_mask_is_gone()
                return el
        return None