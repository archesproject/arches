import re
from base_page import BasePage
from page_locators import NodePageLocators as locators
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class NodePage(BasePage):
    """
    class to initialize the graph/semantics page

    """

    def __init__(self, driver, live_server_url, graph_id):
        super(NodePage, self).__init__(driver, live_server_url, '/graph/' + graph_id)

    def add_new_node(self, appending_graph_id, datatype, is_resource=False, node_id=None):
        """
        Currently creates a node on the top node of a branch and returns the node id and
        nodegroup_id of the new node. If is_resource is True, then
        appends a branch to the top node of the resource. A node id can be passed in
        to specify a target node other than the top node, but this
        is not yet fully implemented.

        """

        self.open()
        self.driver.find_element(*locators.NEW_NODE_BUTTON).click()
        appending_branch_button = (By.XPATH, "//*[@data-arches-graphid='" + appending_graph_id + "']")

        click_steps = [
            appending_branch_button,
            locators.APPEND_BUTTON
        ]

        if is_resource == False:
            click_steps.append(locators.SELECTED_NODE_IN_LEFT_CONTAINER)

        for locator in click_steps:
            self.wait.until(
                EC.element_to_be_clickable(locator)
            ).click()

        if is_resource == False:
            selected_data_type = ''
            for el in self.driver.find_elements_by_class_name('active-result'):
                if el.text == datatype:
                    selected_data_type = el

            selected_data_type.click()
            save_edits = self.driver.find_element(*locators.SAVE_EDITS_BUTTON)
            save_edits.click()
            node_attr_el = self.driver.find_element(*locators.NODE_ELEMENT_IN_SELECTED_NODE_IN_LEFT_CONTAINER)
            node_id = node_attr_el.get_attribute('data-arches-nodeid')
            nodegroup_id = node_attr_el.get_attribute('data-arches-nodegroupid')
            return {'node_id': node_id, 'nodegroup_id': nodegroup_id}
