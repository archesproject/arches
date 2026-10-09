import type { InjectionKey } from "vue";

import type { MapSettings } from "@/arches_vue_components/components/MapComponent/types.ts";

export const BUFFER_FILL_COLOR = "#ea7f08";
export const BUFFER_FILL_OPACITY = 0.3;
export const BUFFER_LAYER_ID = "buffer-layer";
export const DEFAULT_FEATURE_COLOR = "#c12";
export const DEFAULT_FEATURE_LINE_WIDTH = 2;
export const DEFAULT_FEATURE_POINT_FILL = "#ffffff";
export const DEFAULT_FEATURE_POINT_SIZE = 6;
export const DIRECT_SELECT = "direct_select";
export const DRAW_CREATE_EVENT = "draw.create";
export const DRAW_DELETE_EVENT = "draw.delete";
export const DRAW_LAYER_ID_PREFIX = "gl-draw-";
export const DRAW_LINE_STRING = "draw_line_string";
export const DRAW_POINT = "draw_point";
export const DRAW_POLYGON = "draw_polygon";
export const DRAW_SELECTION_CHANGE_EVENT = "draw.selectionchange";
export const DRAW_UPDATE_EVENT = "draw.update";
export const FEET = "feet";
export const GEOMETRY_TYPE_LINESTRING = "LineString";
export const GEOMETRY_TYPE_POINT = "Point";
export const GEOMETRY_TYPE_POLYGON = "Polygon";
export const KILOMETERS = "kilometers";
export const LINE = "line";
export const METERS = "meters";
export const MILES = "miles";
export const POINT = "point";
export const POLYGON = "polygon";
export const SIMPLE_SELECT = "simple_select";
export const STYLE_LOAD_EVENT = "style.load";
export const YARDS = "yards";
export const BUFFER_INPUT_DEBOUNCE_MILLISECONDS = 300;
export const DEFAULT_BUFFER_DISTANCE = 100;
export const DEFAULT_OVERLAY_OPACITY_PERCENT = 100;
export const FEATURE_HIGHLIGHT_BUFFER_METERS = 15;
export const FEATURE_HIGHLIGHT_COLOR = "#e08a2b";
export const FEATURE_HIGHLIGHT_LINE_WIDTH = 3;
export const FEATURE_HIGHLIGHT_POINT_RADIUS = 11;
export const FEATURE_HIGHLIGHT_SOURCE_ID = "map-component-feature-highlight";
export const FEATURE_HIGHLIGHT_POINT_LAYER_ID =
    "map-component-feature-highlight-point";
export const FEATURE_HIGHLIGHT_OUTLINE_LAYER_ID =
    "map-component-feature-highlight-outline";
export const COORDINATE_PREVIEW_SOURCE_ID = "map-component-coordinate-preview";
export const VERTEX_HIGHLIGHT_SOURCE_ID = "map-component-vertex-highlight";
export const COMPONENT_LAYER_ID_PREFIX = "map-component-";
export const WGS84_SRID = "4326";
export const THUMBNAIL_WIDTH_PIXELS = 240;
export const THUMBNAIL_HEIGHT_PIXELS = 160;

export const GEOMETRY_ICON_BY_TYPE: Record<string, string> = {
    Point: "pi pi-map-marker",
    MultiPoint: "pi pi-map-marker",
    LineString: "pi pi-minus",
    MultiLineString: "pi pi-minus",
    Polygon: "pi pi-stop",
    MultiPolygon: "pi pi-stop",
};

export const DEFAULT_MAP_SETTINGS: MapSettings = {
    showCursorCoordinates: true,
    coordinateReadoutSrid: WGS84_SRID,
    coordinateReadoutFormat: "dd",
    showMapScale: true,
    mapScaleUnit: "metric",
    showZoomLevel: true,
    geocoderVisible: true,
    showNavigationControl: true,
    showFullscreenControl: true,
    scrollZoomRequiresKey: false,
    allow3d: false,
};

export const panelHeaderActionsIdKey: InjectionKey<string> = Symbol(
    "panelHeaderActionsId",
);
