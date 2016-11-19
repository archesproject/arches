from map_widget_page import MapWidgetPage
from page_locators import ResourceEditorPageLocators as locators
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ResourceEditorPage(MapWidgetPage):
    """
    class to initialize the report-editor page

    """

    def __init__(self, driver, live_server_url, target_page, page_id):
        super(ResourceEditorPage, self).__init__(driver, live_server_url, target_page, page_id)
        self.driver.set_window_size(1400,900)

    def create_map_data(self):
        self.open()
        self.open_tools()
        self.open_draw_tools()
        for element in (locators.MAP_DRAW_TOOLS, locators.POINT_DRAW_TOOL):
            self.wait.until(
                EC.element_to_be_clickable(element)
            ).click()

        ac = ActionChains(self.driver)
        map = self.driver.find_element(*locators.MAP_CANVAS)
        ac.click(map).perform()

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
