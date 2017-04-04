import re
from base_widget import BaseWidget
from element_locators import MapWidgetLocators as locators
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class MapWidget(BaseWidget):
    """
    class to initialize a map widget element

    """

    def open_tools(self):
        try:
            map_tools_button = self.page.wait.until(
                EC.element_to_be_clickable(locators.MAP_TOOLS_BUTTON)
            ).click()
            result = True
        except:
            result = False
        return result

    def open_draw_tools(self):
        try:
            map_tools_button = self.page.wait.until(
                EC.element_to_be_clickable(locators.MAP_DRAW_TOOLS)
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
                map_tools_button = self.page.wait.until(
                    EC.element_to_be_clickable(element)
                ).click()
            result = True
        except:
            result = False
        return result

    def add_overlay(self, number_of_added_overlays):
        try:
            for element in (
                locators.MAP_TOOLS_OVERLAYS,
                locators.OVERLAY_LIBRARY_BUTTON,
                locators.OVERLAY_TO_ADD
                ):
                map_tools_button = self.page.wait.until(
                    EC.element_to_be_clickable(element)
                ).click()
            result = True if len(self.page.driver.find_elements(*locators.ADDED_OVERLAYS)) == number_of_added_overlays else False
        except:
            result = False
        return result

    def draw_point(self):
        self.open_tools()
        self.open_draw_tools()
        for element in (locators.MAP_DRAW_TOOLS, locators.POINT_DRAW_TOOL):
            self.page.wait.until(
                EC.element_to_be_clickable(element)
            ).click()

        ac = ActionChains(self.page.driver)
        map = self.page.driver.find_element(*locators.MAP_CANVAS)
        ac.click(map).perform()
