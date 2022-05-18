class PortfolioItemViewModel(object):
    def __init__(self):
        self.category = ""
        self.category_display_name = ""
        self.thumbnail_url = ""
        self.resource_instance_id = ""
        self.display_name = ""

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        self._category = value.lower()