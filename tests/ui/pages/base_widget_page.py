from base_page import BasePage
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from page_locators import BasePageLocators as locators

class BaseWidgetPage(BasePage):
    """
    Base class to initialize the base page that will be called from all pages

    """

    def __init__(self, driver, live_server_url, base_url=None, wait=20):
        super(BaseWidgetPage, self).__init__(driver, live_server_url, base_url, wait)

    def add_widget(self, widget, location=''):
        return widget(self, location) 
