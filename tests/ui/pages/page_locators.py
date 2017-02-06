from selenium.webdriver.common.by import By

class BasePageLocators(object):
    LOADING_MASK = (By.CSS_SELECTOR, ".loading-mask")
    MANAGE_MENU = (By.ID, "menu-control")
    SAVE_EDITS_BUTTON = (By.XPATH, "//*[@id='content-container']/div/div[4]/div[3]/span/button[2]")
    ADD_NEW_RESOURCE_NAVBAR_BUTTON = (By.XPATH, "//*[@id='mainnav-menu']/li[3]/a")

class CardPageLocators(BasePageLocators):
    def __init__(self):
        super(BasePageLocators, self).__init__()

class NodePageLocators(BasePageLocators):
    def __init__(self):
        super(BasePageLocators, self).__init__()

    NEW_NODE_BUTTON = (By.XPATH, "//*[@id='node-crud']/ul/li[2]/a")
    ADD_NODE_LIST_BUTTON = (By.XPATH, "//div[@id='branch-library']//div//div[@class='library-card']")
    ADD_BRANCH_LIST_BUTTON = (By.XPATH, "//*[@id='branch-library']/div/div[3]/div[3]")
    APPEND_BUTTON = (By.XPATH, "//*[@id='branch-append']")
    SELECTED_NODE_IN_LEFT_CONTAINER = (By.XPATH, "//*[@id='node-form']/div[1]/div/div[2]/div[2]/div/a")
    SAVE_EDITS_BUTTON = (By.XPATH, "//*[contains(@class, 'ep-form-toolbar-tools')]/span/button[2]")
    NODE_ELEMENT_IN_SELECTED_NODE_IN_LEFT_CONTAINER = (By.XPATH, "//*[@id='node-listing']/div[2]/div[1]/div[2]/a")
    CARD_MANAGER_LINK = (By.XPATH, "//*[@id='card-manager']")

class GraphPageLocators(BasePageLocators):
    def __init__(self):
        super(BasePageLocators, self).__init__()

    ADD_BUTTON = (By.XPATH, "//button[@type='button']")
    STATUS_TAB = (By.XPATH, "//*[@id='xx-meta-tab']")
    ACTIVE_STATUS_BUTTON = (By.XPATH, "//*[@id='meta-card']/div/div/div[2]/div[1]/div/div[2]/div/label[1]")
    SAVE_EDITS_BUTTON = (By.XPATH, "//*[contains(@class, 'ep-form-toolbar-tools')]/button[2]")
    IMPORT_GRAPH_BUTTON = (By.XPATH, "//a[contains(@class, 'arches-tool-item file-upload')]")

class MapWidgetPageLocators(BasePageLocators):
    def __init__(self):
        super(BasePageLocators, self).__init__()

    MAP_TOOLS_BUTTON = (By.ID, "map-tools")
    MAP_TOOLS_BASEMAPS = (By.XPATH, "//*[@id='map-widget-toolbar']/ul/li[1]")
    SATELLITE_BASE_MAP = (By.XPATH, "//*[@id='map-widget-basemaps']/div[3]")
    MAP_TOOLS_OVERLAYS = (By.ID, "btn-overlays")
    OVERLAY_LIBRARY_BUTTON = (By.XPATH, "//*[@id='overlays-panel']/div[1]/h4")
    OVERLAY_TO_ADD = (By.XPATH, "//*[@id='overlay-grid']/div[1]")
    ADDED_OVERLAYS = (By.CSS_SELECTOR, "#overlays-panel .map-widget-overlay-item .map-overlay-name")
    MAP_CANVAS = (By.XPATH, "//*[@id='mapboxgl-map']/div[8]/canvas")
    MAP_DRAW_TOOLS = (By.CSS_SELECTOR, ".drawing-map-tools")
    POINT_DRAW_TOOL = (By.XPATH, "//*[@id='maptools-panel']/div[2]")

class FormPageLocators(BasePageLocators):
    def __init__(self):
        super(BasePageLocators, self).__init__()

    ADD_FORM_BUTTON = (By.XPATH, "//*[@id='report-image-grid']/div[1]")
    ADD_FORM_CARD_BUTTON = (By.XPATH, "//*[@id='report-image-grid']/div/div/div[4]/a")
    FORM_NAME_INPUT = (By.XPATH, "//*[@id='form-id-card']/div/div/div[2]/form/div[1]/div/div[2]/input")
    SAVE_EDITS_BUTTON = (By.XPATH, "//*[contains(@class, 'ep-form-toolbar-tools')]/span/button[2]")

class ReportManagerPageLocators(BasePageLocators):
    def __init__(self):
        super(BasePageLocators, self).__init__()

    ADD_REPORT_BUTTON = (By.ID, "add-card")
    ADD_REPORT_MAP_HEADER_TEMPLATE = (By.XPATH, "//*[@id='report-image-grid']/div[2]/div/div[3]/a")
    SELECT_REPORT_CARD_BUTTON = (By.CSS_SELECTOR, "#report-image-grid > div.card-grid-item")

class ReportEditorPageLocators(MapWidgetPageLocators):
    def __init__(self):
        super(MapWidgetPageLocators, self).__init__()

    REPORT_NAME_INPUT = (By.XPATH, "//*[@id='ep-card-container-crud']/div[2]/div[2]/input")
    ACTIVATE_REPORT_BUTTON = (By.XPATH, "//*[@id='ep-card-container-crud']/div[1]/div/div/span[1]")
    SAVE_EDITS_BUTTON = (By.XPATH, "//*[contains(@class, 'ep-form-toolbar-tools')]/span/button[2]")
    ADD_NEW_RESOURCE_NAVBAR_BUTTON = (By.XPATH, "//*[@id='content-container']/div/div[4]/div[3]/a")

class ResourceManagerPageLocators(BasePageLocators):
    def __init__(self):
        super(BasePageLocators, self).__init__()

class ResourceEditorPageLocators(MapWidgetPageLocators):
    def __init__(self):
        super(BasePageLocators, self).__init__()

    JUMP_TO_REPORT_BUTTON = (By.ID, 'report-manager')
    SAVE_RESOURCE_EDITS_BUTTON = (By.XPATH, "//div[contains(@class, 'install-buttons')]/button[contains(@class, 'btn btn-shim btn-mint btn-labeled btn-lg fa fa-plus')][1]")
    FORM_LIST_ITEMS = (By.XPATH, "//div[contains(@class, 'library-card')]")
