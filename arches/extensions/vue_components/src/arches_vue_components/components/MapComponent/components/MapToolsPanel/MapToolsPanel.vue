<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";

import { useGettext } from "vue3-gettext";

import CoordinateEditor from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/CoordinateEditor/CoordinateEditor.vue";
import FileDropZone from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/FileDropZone.vue";
import GeometryList from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/GeometryList.vue";
import ToolButtonGroup from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/ToolButtonGroup.vue";

import {
    DRAW_CREATE_EVENT,
    LINE,
    POINT,
    POLYGON,
} from "@/arches_vue_components/components/MapComponent/constants.ts";
import { useGeometryKindOptions } from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/composables/useGeometryKindOptions.ts";
import { useResolvedMapContext } from "@/arches_vue_components/components/MapComponent/composables/useMapContext.ts";
import { onDrawEvent } from "@/arches_vue_components/components/MapComponent/utils/draw-events.ts";

import type { Subscription } from "maplibre-gl";

import type {
    DrawMode,
    MapContext,
} from "@/arches_vue_components/components/MapComponent/types.ts";

const COORDINATES_TOOL = "coordinates" as const;

type MapToolsView = "draw" | "coordinates";

const { context = undefined } = defineProps<{
    context?: MapContext;
}>();

const resolvedContext = useResolvedMapContext(context, "MapToolsPanel");
const {
    map,
    drawnFeatures,
    allowedGeometryTypes,
    setDrawMode,
    deselectDrawnFeature,
} = resolvedContext;

const { $gettext } = useGettext();

const geometryKindOptions = useGeometryKindOptions(allowedGeometryTypes);

const activeView = ref<MapToolsView>("draw");
const activeDrawMode = ref<DrawMode | null>(null);
const editingFeatureId = ref<string | null>(null);

let drawCreateSubscription: Subscription | null = null;

const drawToolOptions = computed(() => [
    ...geometryKindOptions.value,
    {
        value: COORDINATES_TOOL,
        label: $gettext("Coordinates"),
        icon: "pi pi-table",
    },
]);

const drawHint = computed(() => {
    if (activeDrawMode.value === POINT) {
        return $gettext("Click on the map to place a point.");
    }
    if (activeDrawMode.value === LINE) {
        return $gettext("Click to add vertices, double-click to finish.");
    }
    if (activeDrawMode.value === POLYGON) {
        return $gettext(
            "Click to add vertices, click the first point to close the polygon.",
        );
    }
    if (!drawnFeatures.value.length) {
        return $gettext(
            "Select a geometry type above, then click on the map to begin drawing — or use Coordinates to type vertices instead.",
        );
    }
    return $gettext(
        "Select a geometry type above to draw another shape, or select one below to move it or edit its vertices.",
    );
});

onMounted(() => {
    if (map.value) {
        drawCreateSubscription = onDrawEvent(
            map.value,
            DRAW_CREATE_EVENT,
            handleDrawCreate,
        );
    }
});

onUnmounted(() => {
    drawCreateSubscription?.unsubscribe();
    setDrawMode(null);
    deselectDrawnFeature();
});

function selectTool(tool: DrawMode | typeof COORDINATES_TOOL): void {
    if (tool === COORDINATES_TOOL) {
        openCoordinateEditor(null);
        return;
    }
    if (activeDrawMode.value === tool) {
        clearActiveDrawMode();
        setDrawMode(null);
        return;
    }
    deselectDrawnFeature();
    activeDrawMode.value = tool;
    setDrawMode(tool);
}

function clearActiveDrawMode(): void {
    activeDrawMode.value = null;
}

function handleDrawCreate(): void {
    clearActiveDrawMode();
    if (map.value) {
        map.value.getCanvas().style.cursor = "";
    }
}

function openCoordinateEditor(featureId: string | null): void {
    clearActiveDrawMode();
    setDrawMode(null);
    deselectDrawnFeature();
    editingFeatureId.value = featureId;
    activeView.value = "coordinates";
}

function closeCoordinateEditor(): void {
    editingFeatureId.value = null;
    activeView.value = "draw";
}
</script>

<template>
    <div class="map-tools">
        <template v-if="activeView === 'draw'">
            <div class="map-tools-section">
                <span class="map-tools-label">{{
                    $gettext("Geometry type")
                }}</span>
                <ToolButtonGroup
                    :options="drawToolOptions"
                    :active-value="activeDrawMode"
                    @select="selectTool"
                />
                <FileDropZone :context="resolvedContext" />
                <div class="map-tools-hint">
                    <i
                        class="pi pi-info-circle"
                        aria-hidden="true"
                    />
                    <span>{{ drawHint }}</span>
                </div>
            </div>
            <div
                v-if="drawnFeatures.length"
                class="map-tools-section map-tools-scroll-section"
            >
                <GeometryList
                    :context="resolvedContext"
                    @edit-coordinates="openCoordinateEditor"
                />
            </div>
        </template>
        <CoordinateEditor
            v-else
            :context="resolvedContext"
            :editing-feature-id="editingFeatureId"
            @close="closeCoordinateEditor"
        />
    </div>
</template>

<style scoped>
.map-tools {
    display: flex;
    flex-direction: column;
    height: 100%;
    min-height: 0;
}

.map-tools-section {
    display: flex;
    flex: 0 0 auto;
    flex-direction: column;
    gap: 0.8rem;
    padding-block: 1.1rem;
    padding-inline: 1.3rem;
    border-block-end: 0.1rem solid var(--p-content-border-color);
}

.map-tools-scroll-section {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    border-block-end: none;
}

.map-tools-label {
    color: var(--p-text-muted-color);
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: 0.06rem;
    text-transform: uppercase;
}

.map-tools-hint {
    display: flex;
    align-items: baseline;
    gap: 0.65rem;
    padding-block: 0.7rem;
    padding-inline: 0.9rem;
    border-radius: 0.55rem;
    background: var(--p-content-hover-background);
    color: var(--p-text-muted-color);
    font-size: 1.15rem;
    line-height: 1.45;
}

.map-tools-hint .pi {
    flex-shrink: 0;
    color: var(--p-primary-color);
    font-size: 1.15rem;
}
</style>
