import { ref, shallowRef, watch } from "vue";

import * as maplibregl from "maplibre-gl";

import { buffer } from "@turf/turf";
import { partition, uniqBy } from "es-toolkit";

import {
    FEATURE_HIGHLIGHT_BUFFER_METERS,
    FEATURE_HIGHLIGHT_COLOR,
    FEATURE_HIGHLIGHT_LINE_WIDTH,
    FEATURE_HIGHLIGHT_OUTLINE_LAYER_ID,
    FEATURE_HIGHLIGHT_POINT_LAYER_ID,
    FEATURE_HIGHLIGHT_POINT_RADIUS,
    FEATURE_HIGHLIGHT_SOURCE_ID,
} from "@/arches_vue_components/components/MapComponent/constants.ts";
import { fetchClusterResourceIds } from "@/arches_vue_components/components/MapComponent/api.ts";
import { geometriesToFeatureCollection } from "@/arches_vue_components/components/MapComponent/utils/feature-collection.ts";

import type { ComputedRef, Ref, ShallowRef } from "vue";
import type { Feature, Geometry } from "geojson";
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
    extends Pick<
        MapContext,
        "showFeatureHighlight" | "clearFeatureHighlight" | "closeFeaturePopup"
    > {
    popupFeatures: ShallowRef<Feature[]>;
    popupContainer: Ref<HTMLElement | null>;
}

export function useFeaturePopup(
    map: ShallowRef<MaplibreMap | null>,
    overlayLayerIds: ComputedRef<string[]>,
    isActivelyDrawingOrEditing: () => boolean,
    isDrawnFeatureOnTop: (point: MapMouseEvent["point"]) => boolean,
): UseFeaturePopupReturn {
    const popupFeatures = shallowRef<Feature[]>([]);
    const popupContainer = ref<HTMLElement | null>(null);

    let activePopup: Popup | null = null;
    let latestClickToken = 0;

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
        latestClickToken += 1;

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

        if (isClusterFeature(features[0])) {
            openClusterPopup(features[0], event.lngLat);
            return;
        }

        const resourceFeatures = getResourceFeatures(features);
        if (resourceFeatures.length) {
            openFeaturePopup(resourceFeatures, event.lngLat);
        }
    }

    function isClusterFeature(feature: MapGeoJSONFeature): boolean {
        return feature.properties.total > 1;
    }

    async function openClusterPopup(
        clusterFeature: MapGeoJSONFeature,
        lngLat: LngLat,
    ): Promise<void> {
        const clickToken = latestClickToken;

        try {
            const resourceIds = await fetchClusterResourceIds(
                clusterFeature.sourceLayer!,
                clusterFeature.properties.extent,
            );
            if (clickToken !== latestClickToken || !resourceIds.length) {
                return;
            }

            openFeaturePopup(
                resourceIds.map((resourceId) => ({
                    type: "Feature",
                    properties: { resourceinstanceid: resourceId },
                    geometry: clusterFeature.geometry,
                })),
                lngLat,
            );
        } catch (error) {
            console.error("Error fetching cluster resources:", error);
        }
    }

    function getResourceFeatures(
        features: MapGeoJSONFeature[],
    ): MapGeoJSONFeature[] {
        const resourceFeatures = features.filter(
            (feature) => feature.properties.resourceinstanceid,
        );

        return uniqBy(
            resourceFeatures,
            (feature) => feature.properties.resourceinstanceid,
        );
    }

    function openFeaturePopup(features: Feature[], lngLat: LngLat): void {
        activePopup?.remove();

        const container = document.createElement("div");
        container.style.height = "100%";

        activePopup = new maplibregl.Popup({
            maxWidth: "none",
            className: "feature-info-popup",
            closeButton: false,
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

    function closeFeaturePopup(): void {
        activePopup?.remove();
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
        const isOverClickableFeature = features.some(
            (feature) =>
                isClusterFeature(feature) ||
                feature.properties.resourceinstanceid,
        );

        canvas.style.cursor = isOverClickableFeature ? "pointer" : "";
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

        const [pointGeometries, shapeGeometries] = partition(
            geometries,
            (geometry) => POINT_GEOMETRY_TYPES.includes(geometry.type),
        );
        const bufferedShapes = buffer(
            geometriesToFeatureCollection(shapeGeometries),
            FEATURE_HIGHLIGHT_BUFFER_METERS,
            { units: "meters" },
        );

        ensureHighlightLayers();
        (
            map.value.getSource(FEATURE_HIGHLIGHT_SOURCE_ID) as GeoJSONSource
        ).setData({
            type: "FeatureCollection",
            features: [
                ...geometriesToFeatureCollection(pointGeometries).features,
                ...bufferedShapes.features,
            ],
        });
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
        closeFeaturePopup,
    };
}
