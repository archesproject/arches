import re
from base_page import BasePage
from page_locators import MapWidgetPageLocators as locators
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from arches.urls import uuid_regex

class MapWidgetPage(BasePage):
    """
    class to initialize a map widget card page

    """

    def __init__(self, driver, live_server_url, target_page, page_id):
        self.driver = driver
        self.live_server_url = live_server_url
        self.page_id = page_id
        self.base_url = '/' + target_page + '/' + self.page_id
        self.wait = WebDriverWait(self.driver, 20)

    def open_tools(self):
        self.driver.get(self.live_server_url + self.base_url)
        self.driver.implicitly_wait(10)
        self.wait.until(
            EC.invisibility_of_element_located(locators.LOADING_MASK)
        )
        try:
            map_tools_button = self.wait.until(
                EC.element_to_be_clickable(locators.MAP_TOOLS_BUTTON)
            ).click()
            result = True
        except:
            result = False
        return result

    def add_basemap(self):
        try:
            for element in (
                locators.MAP_TOOLS_BASEMAPS,
                locators.SATELLITE_BASE_MAP
                ):
                map_tools_button = self.wait.until(
                    EC.element_to_be_clickable(element)
                ).click()
            result = True
        except:
            result = False
        return result

    def add_basemap(self):
        try:
            for element in (
                locators.MAP_TOOLS_BASEMAPS,
                locators.SATELLITE_BASE_MAP
                ):
                map_tools_button = self.wait.until(
                    EC.element_to_be_clickable(element)
                ).click()
            result = True
        except:
            result = False
        return result

    def add_overlay(self):
        try:
            for element in (
                locators.MAP_TOOLS_OVERLAYS,
                locators.OVERLAY_LIBRARY_BUTTON,
                locators.OVERLAY_TO_ADD
                ):
                map_tools_button = self.wait.until(
                    EC.element_to_be_clickable(element)
                ).click()
            result = True if len(self.driver.find_elements(*locators.ADDED_OVERLAYS)) == 1 else False
        except:
            result = False
        return result
