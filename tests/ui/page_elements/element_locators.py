from selenium.webdriver.common.by import By

class BaseWidgetLocators(object):
    def __init__(self):
        super(BaseWidgetLocators, self).__init

class MapWidgetLocators(BaseWidgetLocators):
    def __init__(self):
        super(MapWidgetLocators, self).__init__()

    MAP_TOOLS_BUTTON = (By.ID, "map-tools")
    MAP_TOOLS_BASEMAPS = (By.XPATH, "//*[@id='map-widget-toolbar']/ul/li[1]")
    SATELLITE_BASE_MAP = (By.XPATH, "//*[@id='map-widget-basemaps']/div[3]")
    MAP_TOOLS_OVERLAYS = (By.ID, "btn-overlays")
    OVERLAY_LIBRARY_BUTTON = (By.XPATH, "//*[@id='overlays-panel']/div[1]/h4")
    OVERLAY_TO_ADD = (By.XPATH, "//*[@id='overlay-grid']/div[1]")
    ADDED_OVERLAYS = (By.CSS_SELECTOR, "#overlays-panel .map-widget-overlay-item .map-overlay-name")
    MAP_CANVAS = (By.CSS_SELECTOR, ".mapboxgl-canvas")
    MAP_DRAW_TOOLS = (By.CSS_SELECTOR, ".drawing-map-tools")
    POINT_DRAW_TOOL = (By.XPATH, "//*[@id='maptools-panel']/div[2]")

class StringWidgetLocators(BaseWidgetLocators):
    def __init__(self):
        super(StringWidgetLocators, self).__init__()

    #INPUT_BOX = (By.XPATH, "//*[@id='content-container']/div[2]/div[4]/div/div[2]/div/div/div[2]/div/div/div/div/div/div[2]/div/form/div/div/div/div/input")
    INPUT_BOX = (By.XPATH, "./div/div/div/input")
