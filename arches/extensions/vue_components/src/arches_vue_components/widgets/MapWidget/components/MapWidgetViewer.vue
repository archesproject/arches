<script setup lang="ts">
import { computed } from "vue";

import MapComponent from "@/arches_vue_components/components/MapComponent/MapComponent.vue";

import { buildMapSettings } from "@/arches_vue_components/widgets/MapWidget/utils.ts";

import type {
    MapHeaderAction,
    MapInteractionTool,
    MapSettings,
} from "@/arches_vue_components/components/MapComponent/types.ts";
import type { GeoJSONFeatureCollectionAliasedNodeData } from "@/arches_vue_components/datatypes/geojson-feature-collection/types.ts";
import type { MapCardXNodeXWidgetData } from "@/arches_vue_components/widgets/MapWidget/types.ts";

const {
    aliasedNodeData,
    cardXNodeXWidgetData = undefined,
    interactionTools = undefined,
    headerActions = undefined,
    defaultSettings = undefined,
} = defineProps<{
    aliasedNodeData: GeoJSONFeatureCollectionAliasedNodeData;
    cardXNodeXWidgetData?: MapCardXNodeXWidgetData;
    interactionTools?: MapInteractionTool[];
    headerActions?: MapHeaderAction[];
    defaultSettings?: Partial<MapSettings>;
}>();

const emit = defineEmits<{
    "update:isLoading": [isLoading: boolean];
}>();

const mapSettings = computed<Partial<MapSettings>>(() => ({
    ...defaultSettings,
    ...Object.fromEntries(
        Object.entries(buildMapSettings(cardXNodeXWidgetData?.config)).filter(
            ([, settingValue]) => settingValue !== undefined,
        ),
    ),
}));
</script>

<template>
    <MapComponent
        class="map-widget-viewer"
        :value="aliasedNodeData.node_value"
        :zoom="cardXNodeXWidgetData?.config?.zoom"
        :pitch="cardXNodeXWidgetData?.config?.pitch"
        :bearing="cardXNodeXWidgetData?.config?.bearing"
        :center-x="cardXNodeXWidgetData?.config?.centerX"
        :center-y="cardXNodeXWidgetData?.config?.centerY"
        :min-zoom="cardXNodeXWidgetData?.config?.minZoom"
        :max-zoom="cardXNodeXWidgetData?.config?.maxZoom"
        :basemap="cardXNodeXWidgetData?.config?.basemap"
        :is-read-only="true"
        :interaction-tools="interactionTools"
        :header-actions="headerActions"
        :settings="mapSettings"
        @update:is-loading="emit('update:isLoading', $event)"
    />
</template>

<style>
.map-widget-viewer {
    --map-component-min-height: var(--map-component-viewer-block-size, 37.2rem);
}
</style>
