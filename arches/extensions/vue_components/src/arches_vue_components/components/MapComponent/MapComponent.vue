<script setup lang="ts">
import { computed, provide, useTemplateRef } from "vue";

import Skeleton from "primevue/skeleton";
import Toast from "primevue/toast";

import FeaturePopup from "@/arches_vue_components/components/MapComponent/components/FeaturePopup.vue";
import InteractionsDrawer from "@/arches_vue_components/components/MapComponent/components/InteractionsDrawer/InteractionsDrawer.vue";

import {
    mapContextKey,
    useMapContext,
} from "@/arches_vue_components/components/MapComponent/composables/useMapContext.ts";
import { useDefaultMapInteractionTools } from "@/arches_vue_components/components/MapComponent/useDefaultMapInteractionTools.ts";

import type { Component } from "vue";
import type { FeatureCollection } from "geojson";

import type { MapComponentEmit } from "@/arches_vue_components/components/MapComponent/composables/useMapContext.ts";
import type {
    MapInteractionTool,
    MapLayer,
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
}>();

const emit = defineEmits<MapComponentEmit>();

const mapContainer = useTemplateRef<HTMLDivElement>("mapContainer");

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
    },
    emit,
    mapContainer,
);

defineExpose({ map: context.map, context });

const resolvedFeaturePopupComponent = computed(
    () => featurePopupComponent ?? FeaturePopup,
);
const defaultMapInteractionTools = useDefaultMapInteractionTools();
const resolvedInteractionTools = computed(
    () => interactionTools ?? defaultMapInteractionTools,
);

provide(mapContextKey, context);
</script>

<template>
    <div class="map-component">
        <div
            ref="mapContainer"
            class="map-container"
        />
        <Skeleton
            v-if="context.isLoading.value"
            class="map-loading-skeleton"
        />
        <InteractionsDrawer
            v-if="context.map.value && resolvedInteractionTools.length"
            position="right"
            :context="context"
            :items="resolvedInteractionTools"
            :default-open-index="0"
        />
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
.map-component {
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
    min-height: 0;
}
</style>
