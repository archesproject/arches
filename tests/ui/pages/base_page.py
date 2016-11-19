from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from page_locators import BasePageLocators as locators

class BasePage(object):
    """
    Base class to initialize the base page that will be called from all pages

    """

    def __init__(self, driver, live_server_url, base_url=None, wait=20):
        self.driver = driver
        self.driver.implicitly_wait(1)
        self.live_server_url = live_server_url
        self.base_url = base_url
        
        self.wait = WebDriverWait(self.driver, wait)

    def open(self, additional_path=''):
        if self.base_url is not None:
            self.driver.get(self.live_server_url + self.base_url + additional_path)
            self.wait.until(
                EC.invisibility_of_element_located(locators.LOADING_MASK)
            )
        else:
            raise Exception("You need to define a base_url when initializing the page class")


class script_returns_true(object):
    """ 
    An Expectation that running a script in the page will return true.

    """

    def __init__(self, script):
        self.script = script

    def __call__(self, driver):
        return driver.execute_script(self.script)
