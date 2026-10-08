<script setup lang="ts">
import {
    computed,
    onMounted,
    onUnmounted,
    ref,
    useTemplateRef,
    watch,
} from "vue";

import * as maplibregl from "maplibre-gl";

import { useGettext } from "vue3-gettext";

import { formatDegreesMinutesSeconds } from "@/arches_vue_components/components/MapComponent/utils/coordinate-format.ts";
import {
    fromWgs84,
    isGeographicCoordinateSystem,
} from "@/arches_vue_components/components/MapComponent/utils/coordinate-systems.ts";

import type {
    LngLat,
    Map as MaplibreMap,
    MapMouseEvent,
    ScaleControl,
} from "maplibre-gl";

import type {
    CoordinateSystem,
    MapSettings,
} from "@/arches_vue_components/components/MapComponent/types.ts";

const ZOOM_DECIMAL_PLACES = 1;
const DECIMAL_DEGREE_PLACES = 4;
const PROJECTED_DECIMAL_PLACES = 2;
const SCALE_MAX_WIDTH_PIXELS = 100;
const NO_COORDINATES_PLACEHOLDER = "—";

const { map, settings, coordinateSystems } = defineProps<{
    map: MaplibreMap;
    settings: MapSettings;
    coordinateSystems: CoordinateSystem[];
}>();

const { $gettext } = useGettext();

const scaleContainer = useTemplateRef<HTMLDivElement>("scaleContainer");
const zoomLevel = ref(map.getZoom());
const cursorLngLat = ref<LngLat | null>(null);

let scaleControl: ScaleControl | null = null;
let scaleElement: HTMLElement | null = null;

const isVisible = computed(
    () =>
        settings.showCursorCoordinates ||
        settings.showMapScale ||
        settings.showZoomLevel,
);

const zoomText = computed(() =>
    $gettext("Zoom %{zoom}", {
        zoom: zoomLevel.value.toFixed(ZOOM_DECIMAL_PLACES),
    }),
);

const readoutCoordinateSystem = computed(() =>
    coordinateSystems.find(
        (coordinateSystem) =>
            coordinateSystem.srid === settings.coordinateReadoutSrid,
    ),
);

const coordinateText = computed(() => {
    const lngLat = cursorLngLat.value;
    if (!lngLat) {
        return NO_COORDINATES_PLACEHOLDER;
    }

    const coordinateSystem = readoutCoordinateSystem.value;
    if (coordinateSystem && !isGeographicCoordinateSystem(coordinateSystem)) {
        const [easting, northing] = fromWgs84(coordinateSystem.srid, [
            lngLat.lng,
            lngLat.lat,
        ]);
        return $gettext("E %{easting}, N %{northing}", {
            easting: easting.toFixed(PROJECTED_DECIMAL_PLACES),
            northing: northing.toFixed(PROJECTED_DECIMAL_PLACES),
        });
    }

    if (settings.coordinateReadoutFormat === "dms") {
        return `${formatDegreesMinutesSeconds(lngLat.lat, "latitude")}, ${formatDegreesMinutesSeconds(lngLat.lng, "longitude")}`;
    }
    return `${lngLat.lat.toFixed(DECIMAL_DEGREE_PLACES)}°, ${lngLat.lng.toFixed(DECIMAL_DEGREE_PLACES)}°`;
});

watch(scaleContainer, (container) => {
    if (container && scaleElement) {
        container.appendChild(scaleElement);
    }
});

watch(
    () => settings.mapScaleUnit,
    (unit) => {
        scaleControl?.setUnit(unit);
    },
);

onMounted(() => {
    scaleControl = new maplibregl.ScaleControl({
        maxWidth: SCALE_MAX_WIDTH_PIXELS,
        unit: settings.mapScaleUnit,
    });
    scaleElement = scaleControl.onAdd(map);
    scaleContainer.value?.appendChild(scaleElement);

    map.on("zoom", handleZoom);
    map.on("mousemove", handleMouseMove);
    map.on("mouseout", handleMouseOut);
});

onUnmounted(() => {
    map.off("zoom", handleZoom);
    map.off("mousemove", handleMouseMove);
    map.off("mouseout", handleMouseOut);
    scaleControl?.onRemove();
});

function handleZoom(): void {
    zoomLevel.value = map.getZoom();
}

function handleMouseMove(event: MapMouseEvent): void {
    cursorLngLat.value = event.lngLat;
}

function handleMouseOut(): void {
    cursorLngLat.value = null;
}
</script>

<template>
    <div
        v-if="isVisible"
        class="map-status-bar"
    >
        <div
            v-if="settings.showMapScale"
            ref="scaleContainer"
            class="map-status-scale"
        />
        <span
            v-if="settings.showZoomLevel"
            class="map-status-item"
        >
            {{ zoomText }}
        </span>
        <span
            v-if="settings.showCursorCoordinates"
            class="map-status-item map-status-coordinates"
        >
            {{ coordinateText }}
        </span>
    </div>
</template>

<style scoped>
.map-status-bar {
    position: absolute;
    inset-inline: 0;
    inset-block-end: 0;
    z-index: 1;
    display: flex;
    align-items: center;
    gap: 1.1rem;
    block-size: var(--map-component-status-bar-height);
    padding-inline: 1.1rem;
    background: var(--p-content-background);
    border-block-start: 0.1rem solid var(--p-content-border-color);
    color: var(--p-text-muted-color);
    font-size: 1.15rem;
    pointer-events: none;
}

.map-status-scale {
    display: flex;
    align-items: center;
}

.map-status-scale :deep(.maplibregl-ctrl-scale) {
    padding-block: 0.5rem 0;
    padding-inline: 0.5rem;
    background: none;
    border: none;
    border-block-start: 0.1rem solid var(--p-text-muted-color);
    color: var(--p-text-muted-color);
    font-size: 1.1rem;
}

.map-status-item {
    flex: 0 0 auto;
    padding-inline-start: 1.1rem;
    border-inline-start: 0.1rem solid var(--p-content-border-color);
    white-space: nowrap;
}

.map-status-coordinates {
    min-width: 21rem;
    font-variant-numeric: tabular-nums;
}
</style>
