<script setup lang="ts">
import {
    computed,
    inject,
    nextTick,
    provide,
    ref,
    useId,
    useTemplateRef,
} from "vue";

import { useGettext } from "vue3-gettext";

import Skeleton from "openvue/skeleton";
import Toast from "openvue/toast";

import FeaturePopup from "@/arches_vue_components/components/MapComponent/components/FeaturePopup.vue";
import FloatingPanel from "@/arches_vue_components/components/MapComponent/components/FloatingPanel.vue";
import GeocoderControls from "@/arches_vue_components/components/MapComponent/components/GeocoderControls.vue";
import MapHeader from "@/arches_vue_components/components/MapComponent/components/MapHeader.vue";
import MapStatusBar from "@/arches_vue_components/components/MapComponent/components/MapStatusBar/MapStatusBar.vue";
import MapToolsPanel from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/MapToolsPanel.vue";

import {
    mapContextKey,
    useMapContext,
} from "@/arches_vue_components/components/MapComponent/composables/useMapContext.ts";
import { useDefaultMapInteractionTools } from "@/arches_vue_components/components/MapComponent/composables/useDefaultMapInteractionTools.ts";
import {
    EXPAND_MAP_ACTION_ID,
    mapExpandTargetKey,
} from "@/arches_vue_components/components/MapComponent/constants.ts";

import type { Component } from "vue";
import type { FeatureCollection } from "geojson";

import type { MapComponentEmit } from "@/arches_vue_components/components/MapComponent/composables/useMapContext.ts";
import type {
    MapHeaderAction,
    MapInteractionTool,
    MapLayer,
    MapSettings,
    MapSource,
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
    resolveMapSources = undefined,
    interactionTools = undefined,
    headerActions = undefined,
    maxFeatures = undefined,
    featurePopupComponent = undefined,
    isReadOnly = false,
    openPopupsInsideDrawnShapes = false,
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
    resolveMapSources?: (candidateMapSources: MapSource[]) => MapSource[];
    interactionTools?: MapInteractionTool[];
    headerActions?: MapHeaderAction[];
    maxFeatures?: number;
    featurePopupComponent?: Component;
    isReadOnly?: boolean;
    openPopupsInsideDrawnShapes?: boolean;
    settings?: Partial<MapSettings>;
}>();

const emit = defineEmits<MapComponentEmit>();

// The root renders beside a popup Teleport, so attrs must be bound explicitly.
defineOptions({ inheritAttrs: false });

const expandTarget = inject(mapExpandTargetKey, null);

const { $gettext } = useGettext();

const mapShell = useTemplateRef<HTMLDivElement>("mapShell");
const mapContainer = useTemplateRef<HTMLDivElement>("mapContainer");
const mapHeader = useTemplateRef<InstanceType<typeof MapHeader>>("mapHeader");

const {
    context,
    popupContainer,
    popupFeatures,
    popupFeatureIndex,
    geocoderControls,
} = useMapContext(
    {
        value: () => value ?? null,
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
        resolveMapSources,
        maxFeatures,
        isReadOnly,
        openPopupsInsideDrawnShapes,
        settings,
    },
    emit,
    mapContainer,
    mapShell,
);
const {
    hosts: geocoderHosts,
    inputText: geocoderInputText,
    isSearching: isGeocoderSearching,
    statusMessage: geocoderStatusMessage,
} = geocoderControls;

const panelId = useId();
const defaultMapInteractionTools = useDefaultMapInteractionTools();

provide(mapContextKey, context);

const activeToolName = ref<string | null>(null);
const isExpanded = ref(false);

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
const resolvedInteractionTools = computed(() => {
    const tools = interactionTools ?? defaultMapInteractionTools;
    if (!isReadOnly) {
        return tools;
    }
    return tools.filter((tool) => tool.component !== MapToolsPanel);
});
const isExpandable = computed(
    () => expandTarget !== null && expandTarget.value !== null,
);
const expandMapAction = computed<MapHeaderAction>(() => {
    if (isExpanded.value) {
        return {
            id: EXPAND_MAP_ACTION_ID,
            label: $gettext("Collapse map"),
            icon: "pi pi-window-minimize",
            isPressed: true,
            onClick: toggleExpanded,
        };
    }
    return {
        id: EXPAND_MAP_ACTION_ID,
        label: $gettext("Expand map"),
        icon: "pi pi-window-maximize",
        isPressed: false,
        onClick: toggleExpanded,
    };
});
const resolvedHeaderActions = computed(() => {
    const actions = headerActions ?? [];
    if (!isExpandable.value) {
        return actions;
    }
    return [...actions, expandMapAction.value];
});
const isHeaderVisible = computed(
    () =>
        resolvedInteractionTools.value.length > 0 ||
        resolvedHeaderActions.value.length > 0,
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

function openPanel(toolName: string): void {
    activeToolName.value = toolName;
}

function toggleExpanded(): void {
    isExpanded.value = !isExpanded.value;
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
</script>

<template>
    <Teleport
        :to="expandTarget"
        :disabled="!isExpanded"
    >
        <div
            ref="mapShell"
            class="map-component"
            :class="{ 'map-component-expanded': isExpanded }"
            v-bind="$attrs"
            @keydown.esc="closePanel"
        >
            <MapHeader
                v-if="isHeaderVisible"
                ref="mapHeader"
                :tools="resolvedInteractionTools"
                :actions="resolvedHeaderActions"
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
                    v-if="$slots.overlay && context.map.value"
                    class="map-overlay-layer"
                >
                    <slot
                        name="overlay"
                        :context="context"
                    />
                </div>
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
    </Teleport>
    <Teleport
        v-if="popupContainer"
        :to="popupContainer"
    >
        <component
            :is="resolvedFeaturePopupComponent"
            v-model:index="popupFeatureIndex"
            :features="popupFeatures"
        />
    </Teleport>
    <GeocoderControls
        v-if="geocoderHosts"
        :hosts="geocoderHosts"
        :hint-id="geocoderControls.hintId"
        :input-text="geocoderInputText"
        :is-searching="isGeocoderSearching"
        :status-message="geocoderStatusMessage"
        @clear="geocoderControls.clear"
    />
</template>

<style>
.feature-info-popup .maplibregl-popup-content {
    display: flex;
    flex-direction: column;
    inline-size: 35rem;
    block-size: var(--map-component-popup-height);
    padding: 0;
    overflow: hidden;
    background: var(--p-content-background);
    color: var(--p-content-color);
}

.feature-info-popup-container {
    block-size: 100%;
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
    --map-component-status-bar-attribution-inset: 0.6rem;
    --map-component-popup-height: 26rem;
    --map-component-panel-inset: 1.6rem;
    --map-component-panel-inset-above-status-bar: 5.2rem;
    position: relative;
    display: flex;
    flex-direction: column;
    inline-size: 100%;
    block-size: 100%;
    flex: 1;
    border: 0.2rem solid var(--p-content-border-color);
    /* Header plus a feature popup between the panel insets */
    min-block-size: var(--map-component-min-height, 37.2rem);
    overflow: hidden;
    background: var(--p-content-background);
    color: var(--p-text-color);
}

.map-component,
.map-component :deep(*),
.map-component :deep(*::before),
.map-component :deep(*::after) {
    box-sizing: border-box;
}

.map-component:fullscreen {
    inline-size: 100%;
    block-size: 100%;
}

.map-component.map-component-expanded {
    position: absolute;
    inset: 0;
    min-block-size: 0;
    pointer-events: auto;
}

.map-body {
    position: relative;
    display: flex;
    flex: 1;
    min-block-size: 0;
}

.map-loading-skeleton {
    position: absolute;
    inset: 0;
    z-index: 1;
    inline-size: 100%;
    block-size: 100%;
    border-radius: 0;
}

.map-container {
    flex: 1;
    min-inline-size: 0;
    min-block-size: 0;
}

.map-overlay-layer {
    position: absolute;
    inset: 0;
    z-index: 2;
    display: flex;
    flex-direction: column;
    pointer-events: none;
}

.map-overlay-layer > :slotted(*) {
    pointer-events: auto;
}

.map-body-with-status-bar .map-overlay-layer {
    inset-block-end: var(--map-component-status-bar-height);
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

.map-body-with-status-bar :deep(.maplibregl-ctrl-bottom-left) {
    inset-block-end: var(--map-component-status-bar-height);
}

.map-body-with-status-bar
    :deep(.maplibregl-ctrl-bottom-right .maplibregl-ctrl-attrib) {
    margin-block-end: var(--map-component-status-bar-attribution-inset);
}

.map-body :deep(.maplibregl-ctrl-attrib.maplibregl-compact) {
    box-sizing: content-box;
}

.map-body-with-status-bar
    :deep(
        .maplibregl-ctrl-bottom-right
            .maplibregl-compact:not(.maplibregl-compact-show)
    ) {
    background-color: transparent;
}

.map-body :deep(.maplibregl-ctrl-geocoder--input) {
    font-size: 1.3rem;
}

.map-body :deep(.map-geocoder) {
    display: flex;
    align-items: stretch;
}

.map-body :deep(.map-geocoder-field) {
    position: relative;
    flex: 1;
    min-inline-size: 0;
}

.map-body :deep(.map-geocoder input::-webkit-search-cancel-button) {
    appearance: none;
}

.map-body :deep(.map-geocoder-field .maplibregl-ctrl-geocoder--input) {
    padding-inline-end: 3.2rem;
}

.map-body :deep(.map-geocoder-clear-host) {
    position: absolute;
    inset-block: 0;
    inset-inline-end: 0.4rem;
    display: flex;
}

.map-body :deep(.map-geocoder-search-host) {
    display: flex;
    flex: 0 0 auto;
    border-start-end-radius: inherit;
    border-end-end-radius: inherit;
}
</style>
