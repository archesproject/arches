import re
from base_widget import BaseWidget
from element_locators import StringWidgetLocators as locators

class StringWidget(BaseWidget):
    """
    class to initialize a map widget element

    """

    # def init_locators(self):
    #     self.locators = 

    def set_text(self, text=''):
        input_box = self.root_element.find_element(*locators.INPUT_BOX)
        input_box.send_keys(text)

    def get_text(self):
        input_box = self.root_element.find_element(*locators.INPUT_BOX)
        return input_box.get_attribute('value')