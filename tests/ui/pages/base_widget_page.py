from base_page import BasePage

class BaseWidgetPage(BasePage):
    """
    Base class to initialize the base page that will be called from all pages

    """

    def __init__(self, driver, live_server_url, base_url=None, wait=20):
        super(BaseWidgetPage, self).__init__(driver, live_server_url, base_url, wait)

    def add_widget(self, widget, tab_index=0, widget_index=0):
        return widget(self, tab_index=tab_index, widget_index=widget_index) 
