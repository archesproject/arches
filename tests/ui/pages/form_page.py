import re
from base_page import BasePage, script_returns_true
from page_locators import FormPageLocators as locators
from selenium.webdriver.support import expected_conditions as EC
from arches.urls import uuid_regex

class FormPage(BasePage):
    """
    class to initialize the form-manager page

    """

    def __init__(self, driver, live_server_url, graph_id):
        super(FormPage, self).__init__(driver, live_server_url, '/graph/' + graph_id + '/form_manager')

    def add_new_form(self):
        """
        Clicks on the add new form button and returns a new form_id

        """

        self.open()
        form_id = None
        self.wait.until(
            EC.element_to_be_clickable(locators.ADD_FORM_BUTTON)
        ).click()
        try:
            form_id = self.wait.until(
                script_returns_true('''
                    try{
                        var matches = window.location.pathname.match(/(''' + uuid_regex + ''')/i);
                        console.log(window.location)
                        if (matches && matches.length === 2){
                            console.log(matches)
                            return matches[1];
                        }else{
                            return false;
                        }
                    }catch(err){
                        return false;
                    }
                ''')
            )
        except:
            pass

        return form_id

    def configure_form(self, form_name):
        self.wait.until(
            EC.element_to_be_clickable(locators.ADD_FORM_CARD_BUTTON)
        ).click()
        form_name_input = self.driver.find_element(*locators.FORM_NAME_INPUT)
        form_name_input.clear()
        form_name_input.send_keys(form_name)
        self.wait.until(
            EC.element_to_be_clickable(locators.SAVE_EDITS_BUTTON)
        ).click()
