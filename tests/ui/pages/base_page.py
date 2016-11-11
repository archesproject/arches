class BasePage(object):
    """
    Base class to initialize the base page that will be called from all pages

    """

    def __init__(self, driver, live_server_url):
        self.driver = driver
        self.live_server_url = live_server_url

class script_returns_true(object):
    """ 
    An Expectation that running a script in the page will return true.

    """

    def __init__(self, script):
        self.script = script

    def __call__(self, driver):
        return driver.execute_script(self.script)
