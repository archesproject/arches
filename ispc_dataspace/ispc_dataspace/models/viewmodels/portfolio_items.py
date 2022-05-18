from .category import CategoryViewModel

class PortfolioItemsViewModel(object):
    def __init__(self):
        self.items = []
        self.categories = []

    @property
    def categories(self):
        unique_items = { item.category: item for item in self.items }.values()
        unique_categories = [ CategoryViewModel(item.category, item.category_display_name) for item in unique_items ]
        unique_categories.sort(key=lambda item: item.name)
        return unique_categories

    @categories.setter
    def categories(self, value):
        self._categories = value