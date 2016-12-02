from base_widget_page import BaseWidgetPage

class CardDesignerPage(BaseWidgetPage):
    """
    class to initialize the card designer page

    """

    def __init__(self, driver, live_server_url, card_id):
        super(CardDesignerPage, self).__init__(driver, live_server_url, '/card/' + card_id)
