import { ref, shallowRef } from "vue";

import MapboxDraw from "@mapbox/mapbox-gl-draw";
import geojsonExtent from "@mapbox/geojson-extent";

import { useToast } from "openvue/usetoast";
import { useGettext } from "vue3-gettext";

import {
    fetchDrawnFeaturesBuffer,
    fetchGeoJSONBounds,
} from "@/arches_vue_components/components/MapComponent/api.ts";

import {
    BUFFER_FILL_COLOR,
    BUFFER_FILL_OPACITY,
    BUFFER_LAYER_ID,
    DIRECT_SELECT,
    DRAW_LAYER_ID_PREFIX,
    DRAW_LINE_STRING,
    DRAW_POINT,
    DRAW_POLYGON,
    DRAW_CREATE_EVENT,
    DRAW_DELETE_EVENT,
    DRAW_SELECTION_CHANGE_EVENT,
    DRAW_UPDATE_EVENT,
    GEOMETRY_TYPE_LINESTRING,
    GEOMETRY_TYPE_POINT,
    GEOMETRY_TYPE_POLYGON,
    IDLE,
    METERS,
    SIMPLE_SELECT,
} from "@/arches_vue_components/components/MapComponent/constants.ts";
import {
    fireDrawEvent,
    onDrawEvent,
} from "@/arches_vue_components/components/MapComponent/utils/draw-events.ts";

import type { Ref, ShallowRef } from "vue";
import type { Feature, FeatureCollection } from "geojson";
import type {
    GeoJSONSource,
    Map as MaplibreMap,
    MapMouseEvent,
} from "maplibre-gl";

import type { DrawEvent } from "@/arches_vue_components/components/MapComponent/utils/draw-events.ts";
import type { MapComponentEmit } from "@/arches_vue_components/components/MapComponent/composables/useMapContext.ts";
import type {
    DrawMode,
    MapContext,
} from "@/arches_vue_components/components/MapComponent/types.ts";

const FIT_TO_FEATURES_MAX_ZOOM = 17;
const FIT_TO_FEATURES_PADDING = 80;

export interface UseDrawnFeaturesReturn
    extends Pick<
        MapContext,
        | "drawnFeatures"
        | "selectedDrawnFeature"
        | "setDrawMode"
        | "selectDrawnFeature"
        | "deselectDrawnFeature"
        | "editDrawnFeature"
        | "deleteDrawnFeature"
        | "deleteSelectedDrawnFeature"
        | "deleteAllDrawnFeatures"
        | "setBufferForSelectedFeature"
        | "setBufferForFeature"
        | "addFeatures"
        | "updateDrawnFeature"
        | "fitToFeatures"
    > {
    setupDraw: () => void;
    addBufferLayer: () => void;
    isActivelyDrawingOrEditing: () => boolean;
    isDrawnFeatureOnTop: (point: MapMouseEvent["point"]) => boolean;
}

export function useDrawnFeatures(
    map: ShallowRef<MaplibreMap | null>,
    props: {
        value: FeatureCollection | null;
        maxFeatures?: number;
    },
    emit: MapComponentEmit,
): UseDrawnFeaturesReturn {
    const toast = useToast();
    const { $gettext } = useGettext();

    const selectedDrawnFeature: Ref<Feature | null> = ref(null);
    const drawnFeatures = shallowRef<Feature[]>([]);

    let draw: InstanceType<typeof MapboxDraw>;
    let currentBufferData: FeatureCollection = {
        type: "FeatureCollection",
        features: [],
    };
    // Each updateDrawnFeatures() call claims the next token; a call whose
    // async buffer fetch resolves after a newer call has already started
    // (e.g. a stale buffer request outliving a subsequent "clear all") is no
    // longer the latest, so it must not clobber the buffer layer or re-emit
    // its now-outdated feature collection.
    let latestUpdateDrawnFeaturesToken = 0;

    function isActivelyDrawingOrEditing(): boolean {
        return draw && draw.getMode() !== SIMPLE_SELECT;
    }

    function isDrawnFeatureOnTop(point: MapMouseEvent["point"]): boolean {
        const topFeature = map.value!.queryRenderedFeatures(point)[0];
        return topFeature?.layer.id.startsWith(DRAW_LAYER_ID_PREFIX);
    }

    function setupDraw(): void {
        draw = new MapboxDraw({
            displayControlsDefault: false,
            controls: {
                point: false,
                line_string: false,
                polygon: false,
                trash: false,
            },
        });

        map.value!.addControl(draw);

        if (props.value?.features?.length) {
            for (const feature of props.value.features) {
                draw.add(feature);
            }

            updateDrawnFeatures({ shouldEmitValueChange: false });
        }

        onDrawEvent(map.value!, DRAW_CREATE_EVENT, (drawEvent: DrawEvent) => {
            if (
                props.maxFeatures != null &&
                draw.getAll().features.length > props.maxFeatures
            ) {
                const rejectedIds = drawEvent.features.map(
                    (feature) => feature.id as string,
                );
                draw.delete(rejectedIds);
                notifyMaxFeaturesReached();
                updateDrawnFeatures();
                return;
            }

            selectNewlyDrawnFeature(drawEvent);
            updateDrawnFeatures();
        });
        onDrawEvent(map.value!, DRAW_UPDATE_EVENT, (drawEvent: DrawEvent) => {
            selectedDrawnFeature.value = drawEvent.features[0] ?? null;
            updateDrawnFeatures();
        });
        onDrawEvent(map.value!, DRAW_DELETE_EVENT, () => {
            selectedDrawnFeature.value = null;
            updateDrawnFeatures();
        });
        onDrawEvent(map.value!, DRAW_SELECTION_CHANGE_EVENT, () => {
            selectedDrawnFeature.value = draw.getSelected().features[0] ?? null;
        });
    }

    function addBufferLayer(): void {
        if (!map.value!.getSource(BUFFER_LAYER_ID)) {
            map.value!.addSource(BUFFER_LAYER_ID, {
                type: "geojson",
                data: currentBufferData,
            });
        }
        if (!map.value!.getLayer(BUFFER_LAYER_ID)) {
            map.value!.addLayer({
                id: BUFFER_LAYER_ID,
                type: "fill",
                source: BUFFER_LAYER_ID,
                layout: {},
                paint: {
                    "fill-color": BUFFER_FILL_COLOR,
                    "fill-opacity": BUFFER_FILL_OPACITY,
                },
            });
        }
    }

    function selectNewlyDrawnFeature(drawEvent: DrawEvent): void {
        const feature = drawEvent.features[0];
        const featureId = feature.id as string;

        map.value!.once(IDLE, () => {
            if (feature.geometry.type === GEOMETRY_TYPE_POINT) {
                draw.changeMode(SIMPLE_SELECT, { featureIds: [featureId] });
            } else if (
                feature.geometry.type === GEOMETRY_TYPE_LINESTRING ||
                feature.geometry.type === GEOMETRY_TYPE_POLYGON
            ) {
                draw.changeMode(DIRECT_SELECT, { featureId });
            }
        });
    }

    function notifyMaxFeaturesReached(): void {
        toast.add({
            severity: "error",
            summary: $gettext("Feature limit reached"),
            detail: $gettext(
                "Only %{max} feature(s) can be drawn on this map.",
                { max: String(props.maxFeatures) },
            ),
            life: 5000,
            group: "map-component",
        });
    }

    async function updateDrawnFeatures({
        shouldEmitValueChange = true,
        shouldFitBounds = true,
    }: {
        shouldEmitValueChange?: boolean;
        shouldFitBounds?: boolean;
    } = {}): Promise<void> {
        const updateToken = ++latestUpdateDrawnFeaturesToken;

        const drawnFeatureCollection = draw.getAll() as FeatureCollection;
        drawnFeatures.value = drawnFeatureCollection.features as Feature[];

        for (const feature of drawnFeatureCollection.features) {
            feature.properties!.buffer_distance ??= 0;
            feature.properties!.buffer_units ??= METERS;
        }

        try {
            const featuresToBuffer: FeatureCollection = {
                ...drawnFeatureCollection,
                features: drawnFeatureCollection.features.filter(
                    (feature) => feature.properties!.buffer_distance,
                ),
            };

            let bufferedFeatures: FeatureCollection = {
                type: "FeatureCollection",
                features: [],
            };
            if (featuresToBuffer.features.length) {
                bufferedFeatures =
                    await fetchDrawnFeaturesBuffer(featuresToBuffer);
            }

            if (updateToken !== latestUpdateDrawnFeaturesToken) {
                return;
            }

            currentBufferData = bufferedFeatures;
            (map.value!.getSource(BUFFER_LAYER_ID) as GeoJSONSource)?.setData(
                currentBufferData,
            );

            if (shouldFitBounds && drawnFeatureCollection.features.length) {
                const allFeatures: FeatureCollection = {
                    type: "FeatureCollection",
                    features: [
                        ...drawnFeatureCollection.features,
                        ...bufferedFeatures.features,
                    ],
                };

                const [west, south, east, north] =
                    await fetchGeoJSONBounds(allFeatures);

                if (updateToken !== latestUpdateDrawnFeaturesToken) {
                    return;
                }

                map.value!.fitBounds(
                    [
                        [west, south],
                        [east, north],
                    ],
                    {
                        padding: { top: 50, right: 100, bottom: 50, left: 50 },
                    },
                );
            }
        } catch (error) {
            console.error("Error updating drawn features:", error);
        }

        if (shouldEmitValueChange) {
            emit("update:value", drawnFeatureCollection);
        }
    }

    function setDrawMode(mode: DrawMode | null): void {
        if (!mode || !draw) {
            if (map.value) {
                map.value.getCanvas().style.cursor = "";
            }
            draw?.changeMode(SIMPLE_SELECT);
            return;
        }

        map.value!.getCanvas().style.cursor = "crosshair";

        if (mode === "point") {
            draw.changeMode(DRAW_POINT);
        } else if (mode === "line") {
            draw.changeMode(DRAW_LINE_STRING);
        } else if (mode === "polygon") {
            draw.changeMode(DRAW_POLYGON);
        }
    }

    function selectDrawnFeature(feature: Feature): void {
        selectedDrawnFeature.value = feature;
        draw?.changeMode(SIMPLE_SELECT, { featureIds: [String(feature.id)] });
    }

    function deselectDrawnFeature(): void {
        selectedDrawnFeature.value = null;
        draw?.changeMode(SIMPLE_SELECT);
    }

    function editDrawnFeature(feature: Feature): void {
        const featureId = String(feature.id);
        selectedDrawnFeature.value = feature;

        if (feature.geometry.type === GEOMETRY_TYPE_POINT) {
            draw.changeMode(SIMPLE_SELECT, { featureIds: [featureId] });
        } else {
            draw.changeMode(DIRECT_SELECT, { featureId });
        }
    }

    function deleteDrawnFeature(feature: Feature): void {
        draw.delete(String(feature.id));
        fireDrawEvent(map.value!, DRAW_DELETE_EVENT);
    }

    function deleteSelectedDrawnFeature(): void {
        if (!draw) {
            return;
        }

        const selectedFeatures = draw.getSelected();
        if (selectedFeatures.features.length) {
            draw.delete(selectedFeatures.features[0].id as string);
            fireDrawEvent(map.value!, DRAW_DELETE_EVENT);
        }
    }

    function deleteAllDrawnFeatures(): void {
        if (!draw) {
            return;
        }

        draw.deleteAll();
        fireDrawEvent(map.value!, DRAW_DELETE_EVENT);
    }

    function setBufferForSelectedFeature(
        distance: number,
        units: string,
    ): void {
        const feature = selectedDrawnFeature.value;
        if (!feature || !draw) {
            return;
        }

        feature.properties!.buffer_distance = distance;
        feature.properties!.buffer_units = units;

        draw.add(feature);
        fireDrawEvent(map.value!, DRAW_UPDATE_EVENT, { features: [feature] });
    }

    function setBufferForFeature(
        feature: Feature,
        distance: number,
        units: string,
    ): void {
        feature.properties!.buffer_distance = distance;
        feature.properties!.buffer_units = units;

        draw.add(feature);
        updateDrawnFeatures({ shouldFitBounds: false });
    }

    function addFeatures(features: Feature[]): boolean {
        if (!draw || !features.length) {
            return false;
        }

        const projectedCount = draw.getAll().features.length + features.length;
        if (props.maxFeatures != null && projectedCount > props.maxFeatures) {
            notifyMaxFeaturesReached();
            return false;
        }

        for (const feature of features) {
            draw.add(feature);
        }

        updateDrawnFeatures();
        return true;
    }

    function updateDrawnFeature(feature: Feature): void {
        draw.add(feature);
        updateDrawnFeatures();
    }

    function fitToFeatures(features: Feature[]): void {
        if (!features.length) {
            return;
        }

        const [west, south, east, north] = geojsonExtent({
            type: "FeatureCollection",
            features,
        });
        map.value!.fitBounds(
            [
                [west, south],
                [east, north],
            ],
            {
                padding: FIT_TO_FEATURES_PADDING,
                maxZoom: FIT_TO_FEATURES_MAX_ZOOM,
            },
        );
    }

    return {
        drawnFeatures,
        selectedDrawnFeature,
        setupDraw,
        addBufferLayer,
        isActivelyDrawingOrEditing,
        isDrawnFeatureOnTop,
        setDrawMode,
        selectDrawnFeature,
        deselectDrawnFeature,
        editDrawnFeature,
        deleteDrawnFeature,
        deleteSelectedDrawnFeature,
        deleteAllDrawnFeatures,
        setBufferForSelectedFeature,
        setBufferForFeature,
        addFeatures,
        updateDrawnFeature,
        fitToFeatures,
    };
}
