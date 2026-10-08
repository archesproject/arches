import {
    computed,
    inject,
    onMounted,
    onUnmounted,
    ref,
    shallowRef,
    watch,
} from "vue";

import geojsonExtent from "@mapbox/geojson-extent";
import * as maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

import { fetchMapData } from "@/arches_vue_components/components/MapComponent/api.ts";

import {
    DEFAULT_MAP_SETTINGS,
    STYLE_LOAD_EVENT,
} from "@/arches_vue_components/components/MapComponent/constants.ts";
import { useBasemapStyle } from "@/arches_vue_components/components/MapComponent/composables/useBasemapStyle.ts";
import { useDrawnFeatures } from "@/arches_vue_components/components/MapComponent/composables/useDrawnFeatures.ts";
import { useFeaturePopup } from "@/arches_vue_components/components/MapComponent/composables/useFeaturePopup.ts";
import { useMapControls } from "@/arches_vue_components/components/MapComponent/composables/useMapControls.ts";
import { useOverlayLayers } from "@/arches_vue_components/components/MapComponent/composables/useOverlayLayers.ts";
import { GEOCODER_ATTRIBUTION } from "@/arches_vue_components/components/MapComponent/utils/geocoder-api.ts";
import { registerCoordinateSystems } from "@/arches_vue_components/components/MapComponent/utils/coordinate-systems.ts";

import type { InjectionKey, Ref } from "vue";
import type { FeatureCollection } from "geojson";
import type { Map as MaplibreMap } from "maplibre-gl";

import type { UseFeaturePopupReturn } from "@/arches_vue_components/components/MapComponent/composables/useFeaturePopup.ts";

import type {
    Basemap,
    CoordinateSystem,
    MapContext,
    MapLayer,
    MapSettings,
    MapSource,
    RawBasemap,
} from "@/arches_vue_components/components/MapComponent/types.ts";

// Point maplibre-gl at its worker script as webpack-emitted static assets.
// Without this, maplibre falls back to resolving the worker against its own
// `import.meta.url`, which webpack rewrites to a `file://` URL; maplibre then
// hands `new Worker()` an empty string, which resolves to the current page and
// fails to load as HTML. Mirrors arches' `bindings/maplibre-gl` for Knockout.
maplibregl.setWorkerUrl(
    new URL("maplibre-gl/dist/maplibre-gl-worker.mjs", import.meta.url).href,
);
// Force webpack to also emit the worker's runtime import as a static asset.
new URL("maplibre-gl/dist/maplibre-gl-shared.mjs?asset", import.meta.url);

export interface MapComponentEmit {
    (event: "update:value", value: FeatureCollection): void;
    (event: "update:isLoading", isLoading: boolean): void;
    (event: "update:overlays"): void;
    // Fires once the underlying maplibregl.Map is actually usable. Distinct
    // from the widget-contract "initialized" event fired by *WidgetEditor/
    // *WidgetViewer components, which fires immediately and means "has an
    // initial value," not "is ready."
    (event: "ready"): void;
}

export const mapContextKey: InjectionKey<MapContext> = Symbol("mapContext");

export function useResolvedMapContext(
    context: MapContext | undefined,
    componentName: string,
): MapContext {
    const resolvedContext = context ?? inject(mapContextKey);

    if (!resolvedContext) {
        throw new Error(
            `${componentName} requires a MapContext: pass it via the \`context\` prop, or render this component inside a MapComponent's tree.`,
        );
    }

    return resolvedContext;
}

// MapLibre reads the container's size once, at construction time; building it while the container is still hidden breaks click hit-testing in ways a later resize() doesn't repair.
function waitForNonZeroContainerSize(container: HTMLElement): Promise<void> {
    return new Promise((resolve) => {
        const { width, height } = container.getBoundingClientRect();
        if (width > 0 && height > 0) {
            resolve();
            return;
        }

        const observer = new ResizeObserver((entries) => {
            const entry = entries[0];
            if (
                entry &&
                entry.contentRect.width > 0 &&
                entry.contentRect.height > 0
            ) {
                observer.disconnect();
                resolve();
            }
        });
        observer.observe(container);
    });
}

export function resolveDefaultOverlayLayers(
    candidateOverlayLayers: MapLayer[],
): MapLayer[] {
    return candidateOverlayLayers
        .filter(
            (layer) =>
                layer.isoverlay &&
                layer.activated !== false &&
                !layer.searchonly,
        )
        .sort(
            (overlayA, overlayB) =>
                (overlayA.sortorder ?? 0) - (overlayB.sortorder ?? 0),
        );
}

export interface UseMapContextReturn
    extends Pick<UseFeaturePopupReturn, "popupContainer" | "popupFeatures"> {
    context: MapContext;
}

export function useMapContext(
    props: {
        value: FeatureCollection | null;
        zoom?: number;
        pitch?: number;
        bearing?: number;
        centerX?: number;
        centerY?: number;
        minZoom?: number;
        maxZoom?: number;
        basemap?: string;
        allowedGeometryTypes?: string[];
        resolveOverlayLayers?: (
            candidateOverlayLayers: MapLayer[],
        ) => MapLayer[];
        maxFeatures?: number;
        settings?: Partial<MapSettings>;
    },
    emit: MapComponentEmit,
    mapContainer: Readonly<Ref<HTMLDivElement | null>>,
    fullscreenContainer: Readonly<Ref<HTMLElement | null>>,
): UseMapContextReturn {
    const map = shallowRef<MaplibreMap | null>(null);
    const isLoading = ref(false);
    const basemaps = ref<Basemap[]>([]);
    const overlays = ref<MapLayer[]>([]);
    const mapSources = ref<MapSource[]>([]);
    const coordinateSystems = ref<CoordinateSystem[]>([]);
    const settings = ref<MapSettings>({
        ...DEFAULT_MAP_SETTINGS,
        ...Object.fromEntries(
            Object.entries(props.settings ?? {}).filter(
                ([, settingValue]) => settingValue !== undefined,
            ),
        ),
    });

    let defaultBounds: [number, number, number, number] | null = null;

    const allowedGeometryTypes = computed(
        () => props.allowedGeometryTypes ?? null,
    );

    const drawnFeatureControls = useDrawnFeatures(
        map,
        { value: props.value, maxFeatures: props.maxFeatures },
        emit,
    );
    const {
        overlayOpacities,
        overlayLayerIds,
        updateMapOverlays,
        setOverlayOpacity,
        moveOverlay,
    } = useOverlayLayers(map, overlays, mapSources);
    const {
        popupFeatures,
        popupContainer,
        showFeatureHighlight,
        clearFeatureHighlight,
    } = useFeaturePopup(
        map,
        overlayLayerIds,
        drawnFeatureControls.isActivelyDrawingOrEditing,
        drawnFeatureControls.isDrawnFeatureOnTop,
    );
    useBasemapStyle(map, basemaps);
    useMapControls(map, settings, fullscreenContainer);

    watch(isLoading, (newValue) => {
        emit("update:isLoading", newValue);
    });

    onMounted(async () => {
        await waitForNonZeroContainerSize(mapContainer.value!);

        map.value = new maplibregl.Map({
            container: mapContainer.value!,
            zoom: props.zoom ?? 2,
            center: [props.centerX ?? 0, props.centerY ?? 0],
            pitch: props.pitch ?? 0,
            bearing: props.bearing ?? 0,
            ...(props.minZoom != null ? { minZoom: props.minZoom } : {}),
            ...(props.maxZoom != null ? { maxZoom: props.maxZoom } : {}),
            attributionControl: {
                compact: true,
                customAttribution: GEOCODER_ATTRIBUTION,
            },
        });

        map.value.once(STYLE_LOAD_EVENT, () => {
            drawnFeatureControls.setupDraw();

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

            emit("ready");
        });
        map.value.on(STYLE_LOAD_EVENT, () => {
            map.value!.resize();

            drawnFeatureControls.addBufferLayer();
            updateMapOverlays(overlays.value);

            emit("update:overlays");
        });

        await loadMapData();
    });

    onUnmounted(() => {
        map.value?.remove();
    });

    async function loadMapData(): Promise<void> {
        isLoading.value = true;

        try {
            const mapData = await fetchMapData();

            type RawResourceSource = {
                name: string;
                source: MapSource["source"];
            };
            const rawResourceSources = (mapData?.resource_map_sources ??
                []) as RawResourceSource[];
            const resourceSources: MapSource[] = rawResourceSources.map(
                (raw) => ({
                    id: 0,
                    name: raw.name,
                    source: raw.source,
                }),
            );
            mapSources.value = [
                ...((mapData?.map_sources ?? []) as MapSource[]),
                ...resourceSources,
            ];

            coordinateSystems.value = (mapData?.preferred_coordinate_systems ??
                []) as CoordinateSystem[];
            registerCoordinateSystems(coordinateSystems.value);

            const rawBasemaps = (mapData?.basemaps ?? []) as RawBasemap[];
            const hasPreferredBasemap = rawBasemaps.some(
                (layer) => layer.name === props.basemap,
            );

            function isInitiallyActive(layer: RawBasemap): boolean {
                if (hasPreferredBasemap) {
                    return layer.name === props.basemap;
                }
                return layer.addtomap;
            }

            // Folded into `active` rather than a separate setStyle() call, since assigning basemaps.value below already triggers one via watch(basemaps, ...).
            basemaps.value = rawBasemaps.map((layer) => ({
                id: layer.name,
                name: layer.title,
                value: layer.name,
                active: isInitiallyActive(layer),
                url: layer.url,
            }));

            const candidateOverlayLayers = [
                ...((mapData?.map_layers ?? []) as MapLayer[]),
                ...((mapData?.resource_map_layers ?? []) as MapLayer[]),
            ];
            overlays.value = (
                props.resolveOverlayLayers ?? resolveDefaultOverlayLayers
            )(candidateOverlayLayers);

            if (mapData?.default_bounds) {
                defaultBounds = geojsonExtent(mapData.default_bounds);
            }
        } catch (error) {
            console.error("Error loading map data:", error);
        } finally {
            isLoading.value = false;
        }
    }

    const context: MapContext = {
        map,
        isLoading,
        basemaps,
        overlays,
        overlayOpacities,
        settings,
        coordinateSystems,
        drawnFeatures: drawnFeatureControls.drawnFeatures,
        selectedDrawnFeature: drawnFeatureControls.selectedDrawnFeature,
        allowedGeometryTypes,
        setDrawMode: drawnFeatureControls.setDrawMode,
        selectDrawnFeature: drawnFeatureControls.selectDrawnFeature,
        deselectDrawnFeature: drawnFeatureControls.deselectDrawnFeature,
        editDrawnFeature: drawnFeatureControls.editDrawnFeature,
        deleteDrawnFeature: drawnFeatureControls.deleteDrawnFeature,
        deleteSelectedDrawnFeature:
            drawnFeatureControls.deleteSelectedDrawnFeature,
        deleteAllDrawnFeatures: drawnFeatureControls.deleteAllDrawnFeatures,
        setBufferForSelectedFeature:
            drawnFeatureControls.setBufferForSelectedFeature,
        setBufferForFeature: drawnFeatureControls.setBufferForFeature,
        addFeatures: drawnFeatureControls.addFeatures,
        updateDrawnFeature: drawnFeatureControls.updateDrawnFeature,
        fitToFeatures: drawnFeatureControls.fitToFeatures,
        moveOverlay,
        setOverlayOpacity,
        showFeatureHighlight,
        clearFeatureHighlight,
    };

    return { context, popupContainer, popupFeatures };
}
