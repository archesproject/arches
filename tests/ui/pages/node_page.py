import re
from base_page import BasePage

from graph_page import GraphPage, script_returns_true
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from arches.urls import uuid_regex

class NodePage(BasePage):
    """
    class to initialize the login page

    """

    base_url = '/graph'

    def get_graph(self):
        self.graph_page = Graph()
        return graph_page
