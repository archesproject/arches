<script setup lang="ts">
import {
    computed,
    nextTick,
    onMounted,
    onUnmounted,
    provide,
    ref,
    useId,
    useTemplateRef,
} from "vue";

import Skeleton from "openvue/skeleton";
import Toast from "openvue/toast";

import FeaturePopup from "@/arches_vue_components/components/MapComponent/components/FeaturePopup.vue";
import FloatingPanel from "@/arches_vue_components/components/MapComponent/components/FloatingPanel.vue";
import MapHeader from "@/arches_vue_components/components/MapComponent/components/MapHeader.vue";
import MapStatusBar from "@/arches_vue_components/components/MapComponent/components/MapStatusBar.vue";

import {
    mapContextKey,
    useMapContext,
} from "@/arches_vue_components/components/MapComponent/composables/useMapContext.ts";
import { useDefaultMapInteractionTools } from "@/arches_vue_components/components/MapComponent/composables/useDefaultMapInteractionTools.ts";

import type { Component } from "vue";
import type { FeatureCollection } from "geojson";

import type { MapComponentEmit } from "@/arches_vue_components/components/MapComponent/composables/useMapContext.ts";
import type {
    MapInteractionTool,
    MapLayer,
    MapSettings,
} from "@/arches_vue_components/components/MapComponent/types.ts";

const {
    value = undefined,
    zoom = undefined,
    pitch = undefined,
    bearing = undefined,
    centerX = undefined,
    centerY = undefined,
    minZoom = undefined,
    maxZoom = undefined,
    basemap = undefined,
    allowedGeometryTypes = undefined,
    resolveOverlayLayers = undefined,
    interactionTools = undefined,
    maxFeatures = undefined,
    featurePopupComponent = undefined,
    settings = undefined,
} = defineProps<{
    value?: FeatureCollection | null;
    zoom?: number;
    pitch?: number;
    bearing?: number;
    centerX?: number;
    centerY?: number;
    minZoom?: number;
    maxZoom?: number;
    basemap?: string;
    allowedGeometryTypes?: string[];
    resolveOverlayLayers?: (candidateOverlayLayers: MapLayer[]) => MapLayer[];
    interactionTools?: MapInteractionTool[];
    maxFeatures?: number;
    featurePopupComponent?: Component;
    settings?: Partial<MapSettings>;
}>();

const emit = defineEmits<MapComponentEmit>();

const mapShell = useTemplateRef<HTMLDivElement>("mapShell");
const mapContainer = useTemplateRef<HTMLDivElement>("mapContainer");
const mapHeader = useTemplateRef<InstanceType<typeof MapHeader>>("mapHeader");

const { context, popupContainer, popupFeatures } = useMapContext(
    {
        value: value ?? null,
        zoom,
        pitch,
        bearing,
        centerX,
        centerY,
        minZoom,
        maxZoom,
        basemap,
        allowedGeometryTypes,
        resolveOverlayLayers,
        maxFeatures,
        settings,
    },
    emit,
    mapContainer,
    mapShell,
);

const panelId = useId();
const defaultMapInteractionTools = useDefaultMapInteractionTools();

provide(mapContextKey, context);

const activeToolName = ref<string | null>(null);

defineExpose({
    map: context.map,
    context,
    activeToolName,
    openPanel,
    closePanel,
});

const resolvedFeaturePopupComponent = computed(
    () => featurePopupComponent ?? FeaturePopup,
);
const resolvedInteractionTools = computed(
    () => interactionTools ?? defaultMapInteractionTools,
);
const isStatusBarVisible = computed(
    () =>
        context.settings.value.showCursorCoordinates ||
        context.settings.value.showMapScale ||
        context.settings.value.showZoomLevel,
);

const activeTool = computed(() =>
    resolvedInteractionTools.value.find(
        (tool) => tool.name === activeToolName.value,
    ),
);

onMounted(() => {
    document.addEventListener("keydown", handleDocumentKeydown);
    document.addEventListener("click", handleDocumentClick);
});

onUnmounted(() => {
    document.removeEventListener("keydown", handleDocumentKeydown);
    document.removeEventListener("click", handleDocumentClick);
});

function openPanel(toolName: string): void {
    activeToolName.value = toolName;
}

function toggleTool(toolName: string): void {
    if (activeToolName.value === toolName) {
        activeToolName.value = null;
    } else {
        activeToolName.value = toolName;
    }
}

async function closePanel(): Promise<void> {
    const previousToolName = activeToolName.value;
    activeToolName.value = null;

    if (previousToolName) {
        await nextTick();
        mapHeader.value?.focusTool(previousToolName);
    }
}

function handleDocumentKeydown(event: KeyboardEvent): void {
    if (event.key === "Escape" && activeToolName.value) {
        closePanel();
    }
}

function handleDocumentClick(event: MouseEvent): void {
    if (!activeToolName.value || !mapShell.value) {
        return;
    }
    if (event.composedPath().includes(mapShell.value)) {
        return;
    }

    activeToolName.value = null;
}
</script>

<template>
    <div
        ref="mapShell"
        class="map-component"
    >
        <MapHeader
            v-if="resolvedInteractionTools.length"
            ref="mapHeader"
            :tools="resolvedInteractionTools"
            :active-tool-name="activeToolName"
            :panel-id="panelId"
            :context="context"
            @toggle-tool="toggleTool"
        />
        <div
            class="map-body"
            :class="{ 'map-body-with-status-bar': isStatusBarVisible }"
        >
            <div
                ref="mapContainer"
                class="map-container"
            />
            <Skeleton
                v-if="context.isLoading.value"
                class="map-loading-skeleton"
            />
            <div
                v-if="activeTool && context.map.value"
                class="floating-panel-layer"
            >
                <FloatingPanel
                    :title="activeTool.header"
                    :panel-id="panelId"
                    :wide="activeTool.wide === true"
                    @close="closePanel"
                >
                    <component
                        :is="activeTool.component"
                        :context="context"
                        v-bind="activeTool.props"
                    />
                </FloatingPanel>
            </div>
            <MapStatusBar
                v-if="context.map.value"
                :map="context.map.value"
                :settings="context.settings.value"
                :coordinate-systems="context.coordinateSystems.value"
            />
        </div>
        <Toast group="map-component" />
    </div>
    <Teleport
        v-if="popupContainer"
        :to="popupContainer"
    >
        <component
            :is="resolvedFeaturePopupComponent"
            :features="popupFeatures"
        />
    </Teleport>
</template>

<style>
.feature-info-popup .maplibregl-popup-content {
    display: flex;
    flex-direction: column;
    width: 35rem;
    height: var(--map-component-popup-height);
    padding: 0;
    overflow: hidden;
    background: var(--p-content-background);
    color: var(--p-content-color);
}
</style>

<style scoped>
.map-component {
    --map-component-control-font-size: 1.25rem;
    --map-component-badge-size: 1.7rem;
    --p-button-sm-font-size: var(--map-component-control-font-size);
    --p-inputtext-sm-font-size: var(--map-component-control-font-size);
    --p-select-sm-font-size: var(--map-component-control-font-size);
    --p-form-field-sm-font-size: var(--map-component-control-font-size);
    --p-message-text-sm-font-size: var(--map-component-control-font-size);
    --p-badge-font-size: 1.05rem;
    --p-badge-min-width: var(--map-component-badge-size);
    --p-badge-height: var(--map-component-badge-size);
    --p-button-badge-size: var(--map-component-badge-size);
    --map-component-status-bar-height: 3.6rem;
    --map-component-popup-height: 26rem;
    --map-component-panel-inset: 1.6rem;
    --map-component-panel-inset-above-status-bar: 5.2rem;
    position: relative;
    display: flex;
    flex-direction: column;
    width: 100%;
    flex: 1;
    min-height: 25rem;
    overflow: hidden;
    background: var(--p-content-background);
    color: var(--p-text-color);
}

.map-component:fullscreen {
    width: 100%;
    height: 100%;
}

.map-body {
    position: relative;
    display: flex;
    flex: 1;
    min-height: 0;
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
    min-height: 0;
}

.floating-panel-layer {
    position: absolute;
    inset: var(--map-component-panel-inset);
    z-index: 2;
    display: flex;
    align-items: flex-start;
    pointer-events: none;
}

.map-body-with-status-bar .floating-panel-layer {
    inset-block-end: var(--map-component-panel-inset-above-status-bar);
}

.map-body-with-status-bar :deep(.maplibregl-ctrl-bottom-left),
.map-body-with-status-bar :deep(.maplibregl-ctrl-bottom-right) {
    inset-block-end: var(--map-component-status-bar-height);
}
</style>
