from base_page import BasePage

class LoginPage(BasePage):
    """
    class to initialize the login page

    """

    base_url = '/auth'

    def login(self, username, password):
        self.driver.get(self.live_server_url + self.base_url)
        self.driver.find_element_by_name("username").clear()
        self.driver.find_element_by_name("username").send_keys(username)
        self.driver.find_element_by_name("password").clear()
        self.driver.find_element_by_name("password").send_keys(password)
        self.driver.find_element_by_xpath("//button[@type='submit']").click()