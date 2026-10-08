import { ref, shallowRef, watch } from "vue";

import * as maplibregl from "maplibre-gl";

import { uniqBy } from "es-toolkit";

import {
    FEATURE_HIGHLIGHT_COLOR,
    FEATURE_HIGHLIGHT_LINE_WIDTH,
    FEATURE_HIGHLIGHT_OUTLINE_LAYER_ID,
    FEATURE_HIGHLIGHT_POINT_LAYER_ID,
    FEATURE_HIGHLIGHT_POINT_RADIUS,
    FEATURE_HIGHLIGHT_SOURCE_ID,
} from "@/arches_vue_components/components/MapComponent/constants.ts";
import { geometriesToFeatureCollection } from "@/arches_vue_components/components/MapComponent/utils/feature-collection.ts";

import type { ComputedRef, Ref, ShallowRef } from "vue";
import type { Geometry } from "geojson";
import type {
    GeoJSONSource,
    LngLat,
    Map as MaplibreMap,
    MapGeoJSONFeature,
    MapMouseEvent,
    Popup,
} from "maplibre-gl";

import type { MapContext } from "@/arches_vue_components/components/MapComponent/types.ts";

const POINT_GEOMETRY_TYPES = ["Point", "MultiPoint"];

export interface UseFeaturePopupReturn
    extends Pick<MapContext, "showFeatureHighlight" | "clearFeatureHighlight"> {
    popupFeatures: ShallowRef<MapGeoJSONFeature[]>;
    popupContainer: Ref<HTMLElement | null>;
}

export function useFeaturePopup(
    map: ShallowRef<MaplibreMap | null>,
    overlayLayerIds: ComputedRef<string[]>,
    isActivelyDrawingOrEditing: () => boolean,
    isDrawnFeatureOnTop: (point: MapMouseEvent["point"]) => boolean,
): UseFeaturePopupReturn {
    const popupFeatures = shallowRef<MapGeoJSONFeature[]>([]);
    const popupContainer = ref<HTMLElement | null>(null);

    let activePopup: Popup | null = null;

    watch(
        map,
        (createdMap) => {
            if (!createdMap) {
                return;
            }

            createdMap.on("click", handleMapClick);
            createdMap.on("mousemove", handleMapMousemove);
        },
        { once: true },
    );

    function handleMapClick(event: MapMouseEvent): void {
        if (!overlayLayerIds.value.length) {
            return;
        }
        if (isActivelyDrawingOrEditing()) {
            return;
        }

        const features = map.value!.queryRenderedFeatures(event.point, {
            layers: overlayLayerIds.value,
        });

        if (!features.length) {
            return;
        }
        if (isDrawnFeatureOnTop(event.point)) {
            return;
        }

        openFeaturePopup(deduplicateFeatures(features), event.lngLat);
    }

    function deduplicateFeatures(
        features: MapGeoJSONFeature[],
    ): MapGeoJSONFeature[] {
        const identifiableFeatures = features.filter(
            (feature) => feature.properties?.resourceinstanceid || feature.id,
        );

        return uniqBy(identifiableFeatures, (feature) =>
            String(feature.properties?.resourceinstanceid ?? feature.id),
        );
    }

    function openFeaturePopup(
        features: MapGeoJSONFeature[],
        lngLat: LngLat,
    ): void {
        activePopup?.remove();

        const container = document.createElement("div");
        container.style.height = "100%";

        activePopup = new maplibregl.Popup({
            maxWidth: "none",
            className: "feature-info-popup",
        })
            .setDOMContent(container)
            .setLngLat(lngLat)
            .addTo(map.value!);

        popupContainer.value = container;
        popupFeatures.value = features;

        activePopup.on("close", () => {
            popupContainer.value = null;
            popupFeatures.value = [];
            activePopup = null;
            clearFeatureHighlight();
        });
    }

    function handleMapMousemove(event: MapMouseEvent): void {
        const canvas = map.value!.getCanvas();

        if (!overlayLayerIds.value.length) {
            canvas.style.cursor = "";
            return;
        }

        const features = map.value!.queryRenderedFeatures(event.point, {
            layers: overlayLayerIds.value,
        });

        canvas.style.cursor = features.length ? "pointer" : "";
    }

    function ensureHighlightLayers(): void {
        if (!map.value!.getSource(FEATURE_HIGHLIGHT_SOURCE_ID)) {
            map.value!.addSource(FEATURE_HIGHLIGHT_SOURCE_ID, {
                type: "geojson",
                data: geometriesToFeatureCollection([]),
            });
        }
        if (!map.value!.getLayer(FEATURE_HIGHLIGHT_OUTLINE_LAYER_ID)) {
            map.value!.addLayer({
                id: FEATURE_HIGHLIGHT_OUTLINE_LAYER_ID,
                type: "line",
                source: FEATURE_HIGHLIGHT_SOURCE_ID,
                filter: [
                    "!",
                    [
                        "in",
                        ["geometry-type"],
                        ["literal", POINT_GEOMETRY_TYPES],
                    ],
                ],
                paint: {
                    "line-color": FEATURE_HIGHLIGHT_COLOR,
                    "line-width": FEATURE_HIGHLIGHT_LINE_WIDTH,
                },
            });
        }
        if (!map.value!.getLayer(FEATURE_HIGHLIGHT_POINT_LAYER_ID)) {
            map.value!.addLayer({
                id: FEATURE_HIGHLIGHT_POINT_LAYER_ID,
                type: "circle",
                source: FEATURE_HIGHLIGHT_SOURCE_ID,
                filter: [
                    "in",
                    ["geometry-type"],
                    ["literal", POINT_GEOMETRY_TYPES],
                ],
                paint: {
                    "circle-radius": FEATURE_HIGHLIGHT_POINT_RADIUS,
                    "circle-color": "rgba(0, 0, 0, 0)",
                    "circle-stroke-color": FEATURE_HIGHLIGHT_COLOR,
                    "circle-stroke-width": FEATURE_HIGHLIGHT_LINE_WIDTH,
                },
            });
        }
    }

    function showFeatureHighlight(geometries: Geometry[]): void {
        if (!map.value) {
            return;
        }

        ensureHighlightLayers();
        (
            map.value.getSource(FEATURE_HIGHLIGHT_SOURCE_ID) as GeoJSONSource
        ).setData(geometriesToFeatureCollection(geometries));
    }

    function clearFeatureHighlight(): void {
        (
            map.value?.getSource(FEATURE_HIGHLIGHT_SOURCE_ID) as
                | GeoJSONSource
                | undefined
        )?.setData(geometriesToFeatureCollection([]));
    }

    return {
        popupFeatures,
        popupContainer,
        showFeatureHighlight,
        clearFeatureHighlight,
    };
}
