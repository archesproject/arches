<script setup lang="ts">
import {
    computed,
    onMounted,
    onUnmounted,
    provide,
    ref,
    shallowRef,
    useTemplateRef,
    watch,
} from "vue";

import MapboxDraw from "@mapbox/mapbox-gl-draw";
import geojsonExtent from "@mapbox/geojson-extent";
import maplibregl from "maplibre-gl";

import { uniqBy } from "es-toolkit";
import { useGettext } from "vue3-gettext";

import Skeleton from "primevue/skeleton";

import BasemapPanel from "@/arches_component_lab/widgets/MapWidget/components/MapWidgetEditor/components/InteractionsDrawer/components/BasemapPanel.vue";
import DrawPanel from "@/arches_component_lab/widgets/MapWidget/components/MapWidgetEditor/components/InteractionsDrawer/components/DrawPanel/DrawPanel.vue";
import FeaturePopup from "@/arches_component_lab/widgets/MapWidget/components/MapWidgetEditor/components/FeaturePopup.vue";
import InteractionsDrawer from "@/arches_component_lab/widgets/MapWidget/components/MapWidgetEditor/components/InteractionsDrawer/InteractionsDrawer.vue";
import OverlayPanel from "@/arches_component_lab/widgets/MapWidget/components/MapWidgetEditor/components/InteractionsDrawer/components/OverlayPanel.vue";

import {
    fetchMapData,
    fetchDrawnFeaturesBuffer,
    fetchGeoJSONBounds,
} from "@/arches_component_lab/widgets/MapWidget/api.ts";
import { buildGeoJSONFeatureCollectionAliasedNodeData } from "@/arches_component_lab/datatypes/geojson-feature-collection/utils.ts";

import {
    BUFFER_FILL_COLOR,
    BUFFER_FILL_OPACITY,
    BUFFER_LAYER_ID,
    DIRECT_SELECT,
    DRAW_CREATE_EVENT,
    DRAW_DELETE_EVENT,
    DRAW_SELECTION_CHANGE_EVENT,
    DRAW_UPDATE_EVENT,
    GEOMETRY_TYPE_LINESTRING,
    GEOMETRY_TYPE_POINT,
    GEOMETRY_TYPE_POLYGON,
    IDLE,
    METERS,
    SEARCH_RENDER_CONTEXT,
    SIMPLE_SELECT,
    STYLE_LOAD_EVENT,
} from "@/arches_component_lab/widgets/MapWidget/constants.ts";

import type { Ref } from "vue";
import type { Feature, FeatureCollection } from "geojson";
import type { GeoJSONFeatureCollectionAliasedNodeData } from "@/arches_component_lab/datatypes/geojson-feature-collection/types.ts";
import type {
    AddLayerObject,
    GeoJSONSource,
    LngLat,
    Map as MaplibreMap,
    MapGeoJSONFeature,
    MapMouseEvent,
    Popup,
    SourceSpecification,
} from "maplibre-gl";

import type {
    Basemap,
    LayerDefinition,
    MapCardXNodeXWidgetData,
    MapInteractionItem,
    MapLayer,
    MapSource,
    RawBasemap,
} from "@/arches_component_lab/widgets/MapWidget/types.ts";

interface DrawEvent {
    features: Feature[];
}

const { aliasedNodeData, cardXNodeXWidgetData, renderContext } = defineProps<{
    aliasedNodeData: GeoJSONFeatureCollectionAliasedNodeData | null;
    cardXNodeXWidgetData?: MapCardXNodeXWidgetData;
    renderContext?: string;
}>();

const emit = defineEmits<{
    (event: "update:value", value: FeatureCollection): void;
    (event: "update:isLoading", isLoading: boolean): void;
    (event: "update:overlays"): void;
    (
        event: "update:aliasedNodeData",
        updatedValue: GeoJSONFeatureCollectionAliasedNodeData,
    ): void;
    (
        event: "initialized",
        updatedValue: GeoJSONFeatureCollectionAliasedNodeData,
    ): void;
}>();

const { $gettext } = useGettext();

const mapContainer = useTemplateRef<HTMLDivElement>("mapContainer");

const map = shallowRef<MaplibreMap | null>(null);
defineExpose({ map });

const isLoading = ref(false);
const selectedDrawnFeature: Ref<Feature | null> = ref(null);
const drawnFeatures = shallowRef<Feature[]>([]);
const basemaps = ref<Basemap[]>([]);
const overlays = ref<MapLayer[]>([]);
const popupFeatures = ref<MapGeoJSONFeature[]>([]);
const popupContainer = ref<HTMLElement | null>(null);

let activePopup: Popup | null = null;

let draw: InstanceType<typeof MapboxDraw>;
let mapSources: MapSource[] = [];
let defaultBounds: [number, number, number, number] | null = null;
let currentBufferData: FeatureCollection = {
    type: "FeatureCollection",
    features: [],
};

const mapInteractionItems: MapInteractionItem[] = [
    {
        name: $gettext("Draw"),
        header: $gettext("Draw"),
        component: DrawPanel,
        icon: "pi pi-pencil",
    },
    {
        name: $gettext("Basemap"),
        header: $gettext("Basemap"),
        component: BasemapPanel,
        icon: "pi pi-map",
    },
    {
        name: $gettext("Overlays"),
        header: $gettext("Overlays"),
        component: OverlayPanel,
        icon: "pi pi-globe",
    },
];

const overlayLayerIds = computed(() =>
    overlays.value
        .filter((overlay) => overlay.addtomap)
        .flatMap((overlay) =>
            overlay.layerdefinitions.map((layerDef) => layerDef.id),
        ),
);

const geometryTypes = computed(
    () =>
        cardXNodeXWidgetData?.config?.geometryTypes?.map((geometryType) =>
            geometryType.id.toLowerCase(),
        ) ?? null,
);

provide("basemaps", basemaps);
provide("overlays", overlays);
provide("selectedDrawnFeature", selectedDrawnFeature);
provide("drawnFeatures", drawnFeatures);
provide("geometryTypes", geometryTypes);

watch(isLoading, (newValue) => {
    emit("update:isLoading", newValue);
});

watch(
    basemaps,
    (updatedBasemaps) => {
        const activeBasemap = updatedBasemaps.find((basemap) => basemap.active);

        if (activeBasemap && map.value) {
            map.value.setStyle(activeBasemap.url, { diff: false });
        }
    },
    { deep: true },
);

watch(
    overlays,
    (updatedOverlays) => {
        if (map.value?.isStyleLoaded()) {
            updateMapOverlays(updatedOverlays);
        }
    },
    { deep: true },
);

onMounted(async () => {
    const config = cardXNodeXWidgetData?.config;

    map.value = new maplibregl.Map({
        container: mapContainer.value!,
        zoom: config?.zoom ?? 2,
        center: [config?.centerX ?? 0, config?.centerY ?? 0],
        pitch: config?.pitch ?? 0,
        bearing: config?.bearing ?? 0,
        ...(config?.minZoom != null ? { minZoom: config.minZoom } : {}),
        ...(config?.maxZoom != null ? { maxZoom: config.maxZoom } : {}),
        attributionControl: { compact: true },
    });

    map.value.addControl(new maplibregl.NavigationControl(), "top-left");

    map.value.on("click", handleMapClick);
    map.value.on("mousemove", handleMapMousemove);

    map.value.once(STYLE_LOAD_EVENT, () => {
        setupDraw();

        if (defaultBounds) {
            const [west, south, east, north] = defaultBounds;
            map.value!.fitBounds(
                [
                    [west, south],
                    [east, north],
                ],
                { padding: 20 },
            );
        }
    });
    map.value.on(STYLE_LOAD_EVENT, () => {
        map.value!.resize();

        addBufferLayer();
        updateMapOverlays(overlays.value);

        emit("update:overlays");
    });

    await loadMapData();
    emit(
        "initialized",
        buildGeoJSONFeatureCollectionAliasedNodeData(
            aliasedNodeData?.node_value ?? {
                type: "FeatureCollection",
                features: [],
            },
        ),
    );
});

onUnmounted(() => {
    map.value?.remove();
});

function handleMapClick(event: MapMouseEvent) {
    if (!overlayLayerIds.value.length) return;

    const features = map.value!.queryRenderedFeatures(event.point, {
        layers: overlayLayerIds.value,
    });

    if (!features.length) return;

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

function openFeaturePopup(features: MapGeoJSONFeature[], lngLat: LngLat) {
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
    });
}

function handleMapMousemove(event: MapMouseEvent) {
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

async function loadMapData() {
    isLoading.value = true;

    const config = cardXNodeXWidgetData?.config;

    try {
        const mapData = await fetchMapData();

        type RawResourceSource = { name: string; source: MapSource["source"] };
        const rawResourceSources = (mapData?.resource_map_sources ??
            []) as RawResourceSource[];
        const resourceSources: MapSource[] = rawResourceSources.map((raw) => ({
            id: 0,
            name: raw.name,
            source: raw.source,
        }));
        mapSources = [
            ...((mapData?.map_sources ?? []) as MapSource[]),
            ...resourceSources,
        ];

        basemaps.value = ((mapData?.basemaps ?? []) as RawBasemap[]).map(
            (layer) => ({
                id: layer.name,
                name: layer.title,
                value: layer.name,
                active: layer.addtomap,
                url: layer.url,
            }),
        );

        const configuredOverlays = (
            (mapData?.map_layers ?? []) as MapLayer[]
        ).filter(
            (layer) =>
                layer.isoverlay &&
                layer.activated !== false &&
                (!layer.searchonly || renderContext === SEARCH_RENDER_CONTEXT),
        );
        const resourceLayers = (mapData?.resource_map_layers ??
            []) as MapLayer[];
        const fetchedOverlays = [...configuredOverlays, ...resourceLayers].sort(
            (overlayA, overlayB) =>
                (overlayA.sortorder ?? 0) - (overlayB.sortorder ?? 0),
        );
        overlays.value = fetchedOverlays;

        if (mapData?.default_bounds) {
            defaultBounds = geojsonExtent(mapData.default_bounds);
        }

        const preferredBasemap =
            basemaps.value.find(
                (basemap) => basemap.value === config?.basemap,
            ) ?? null;
        const activeBasemap =
            preferredBasemap ??
            basemaps.value.find((basemap) => basemap.active);
        if (activeBasemap?.url) {
            map.value!.setStyle(activeBasemap.url);
        }
    } catch (error) {
        console.error("Error loading map data:", error);
    } finally {
        isLoading.value = false;
    }
}

function setupDraw() {
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

    if (aliasedNodeData?.node_value?.features?.length) {
        for (const feature of aliasedNodeData.node_value.features) {
            draw.add(feature);
        }

        updateDrawnFeatures();
    }

    map.value!.on(DRAW_CREATE_EVENT, (drawEvent: DrawEvent) => {
        selectNewlyDrawnFeature(drawEvent);
        updateDrawnFeatures();
    });
    map.value!.on(DRAW_UPDATE_EVENT, (drawEvent: DrawEvent) => {
        selectedDrawnFeature.value = drawEvent.features[0] ?? null;
        updateDrawnFeatures();
    });
    map.value!.on(DRAW_DELETE_EVENT, () => {
        selectedDrawnFeature.value = null;
        updateDrawnFeatures();
    });
    map.value!.on(DRAW_SELECTION_CHANGE_EVENT, () => {
        selectedDrawnFeature.value = draw.getSelected().features[0] ?? null;
    });
}

function addBufferLayer() {
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

function selectNewlyDrawnFeature(drawEvent: DrawEvent) {
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

async function updateDrawnFeatures() {
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
            bufferedFeatures = await fetchDrawnFeaturesBuffer(featuresToBuffer);
        }

        currentBufferData = bufferedFeatures;
        (map.value!.getSource(BUFFER_LAYER_ID) as GeoJSONSource)?.setData(
            currentBufferData,
        );

        if (drawnFeatureCollection.features.length) {
            const allFeatures: FeatureCollection = {
                type: "FeatureCollection",
                features: [
                    ...drawnFeatureCollection.features,
                    ...bufferedFeatures.features,
                ],
            };

            const [west, south, east, north] =
                await fetchGeoJSONBounds(allFeatures);
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

    emit("update:value", drawnFeatureCollection);
    emit(
        "update:aliasedNodeData",
        buildGeoJSONFeatureCollectionAliasedNodeData(drawnFeatureCollection),
    );
}

function addOverlayToMap(overlay: MapLayer) {
    for (const layerDef of overlay.layerdefinitions) {
        try {
            if (layerDef.source && !map.value!.getSource(layerDef.source)) {
                const sourceSpec = mapSources.find(
                    (mapSource) => mapSource.name === layerDef.source,
                );
                if (sourceSpec) {
                    map.value!.addSource(
                        layerDef.source,
                        sourceSpec.source as SourceSpecification,
                    );
                }
            }
            if (!map.value!.getLayer(layerDef.id)) {
                map.value!.addLayer(layerDef as AddLayerObject);
            }
        } catch (error) {
            console.error(error);
        }
    }
}

function removeOverlayFromMap(overlay: MapLayer) {
    const sourcesToRemove: Record<string, boolean> = {};

    for (const layerDef of overlay.layerdefinitions) {
        if (map.value!.getLayer(layerDef.id)) {
            map.value!.removeLayer(layerDef.id);
            if (layerDef.source) {
                sourcesToRemove[layerDef.source] = true;
            }
        }
    }

    for (const layer of (map.value!.getStyle()?.layers ??
        []) as LayerDefinition[]) {
        const layerSource = layer.source;
        if (layerSource && sourcesToRemove[layerSource]) {
            delete sourcesToRemove[layerSource];
        }
    }

    for (const source of Object.keys(sourcesToRemove)) {
        if (map.value!.getSource(source)) {
            map.value!.removeSource(source);
        }
    }
}

function updateMapOverlays(overlays: MapLayer[]) {
    for (const overlay of overlays) {
        for (const layerDef of overlay.layerdefinitions) {
            if (map.value!.getLayer(layerDef.id)) {
                map.value!.removeLayer(layerDef.id);
            }
        }
    }
    for (const overlay of overlays) {
        if (overlay.addtomap) {
            addOverlayToMap(overlay);
        } else {
            removeOverlayFromMap(overlay);
        }
    }
}
</script>

<template>
    <div class="map-widget-editor">
        <div
            ref="mapContainer"
            class="map-container"
        />
        <Skeleton
            v-if="isLoading"
            class="map-loading-skeleton"
        />
        <InteractionsDrawer
            v-if="map"
            position="right"
            :map="map"
            :items="mapInteractionItems"
            :default-open-index="0"
        />
    </div>
    <Teleport
        v-if="popupContainer"
        :to="popupContainer"
    >
        <FeaturePopup :features="popupFeatures" />
    </Teleport>
</template>

<style>
.feature-info-popup .maplibregl-popup-content {
    display: flex;
    flex-direction: column;
    width: 30rem;
    min-height: 10rem;
    padding: 0;
    background: var(--p-content-background);
    color: var(--p-content-color);
}

.feature-info-popup .maplibregl-popup-close-button {
    color: var(--p-content-color);
    font-size: 1.75rem;
    padding: 0.375rem 0.75rem;
    line-height: 1;
}
</style>

<style scoped>
.map-widget-editor {
    position: relative;
    display: flex;
    flex-direction: row;
    width: 100%;
    flex: 1;
    min-height: 25rem;
    overflow: hidden;
}

.map-loading-skeleton {
    position: absolute;
    inset: 0;
    z-index: 1;
    width: 100%;
    height: 100%;
    border-radius: 0;
}

.map-container {
    flex: 1;
    min-width: 0;
}
</style>
