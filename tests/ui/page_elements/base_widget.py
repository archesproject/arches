from selenium.webdriver.common.by import By
from tests.ui.pages.resource_editor_page import ResourceEditorPage
from tests.ui.pages.report_editor_page import ReportEditorPage
from tests.ui.pages.card_designer_page import CardDesignerPage

class BaseWidget(object):
    """
    class to initialize a base widget element

    """

    def __init__(self, page_instance, tab_index=0, widget_index=0):
        self.page = page_instance
        self.tab_index = tab_index
        self.widget_index = widget_index

        # self.init_locators()

        if isinstance(page_instance, ResourceEditorPage):
            self.root_element = self.page.driver.find_elements(By.XPATH, "//form")[self.tab_index].find_elements(By.XPATH, "./div")[self.widget_index]

    # def init_locators(self):
    #     pass
