import re
from base_page import BasePage
from page_locators import MapWidgetPageLocators as locators
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from arches.urls import uuid_regex

class MapWidgetPage(BasePage):
    """
    class to initialize the card-manager page

    """

    def __init__(self, driver, live_server_url, target_page, page_id):
        self.driver = driver
        self.live_server_url = live_server_url
        self.page_id = page_id
        self.base_url = '/' + target_page + '/' + self.page_id

    def open_tools(self):
        self.driver.get(self.live_server_url + self.base_url)
        self.driver.implicitly_wait(10)
        wait = WebDriverWait(self.driver, 20)
        wait.until(
            EC.invisibility_of_element_located(locators.LOADING_MASK)
        )
        try:
            map_tools_button = wait.until(
                EC.element_to_be_clickable(locators.MAP_TOOLS_BUTTON)
            )
            map_tools_button.click()
            result = True
        except:
            result = False
        return result
