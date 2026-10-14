<script setup lang="ts">
import MapComponent from "@/arches_vue_components/components/MapComponent/MapComponent.vue";
import MapToolsPanel from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/MapToolsPanel.vue";

import { useDefaultMapInteractionTools } from "@/arches_vue_components/components/MapComponent/composables/useDefaultMapInteractionTools.ts";

import type { GeoJSONFeatureCollectionAliasedNodeData } from "@/arches_vue_components/datatypes/geojson-feature-collection/types.ts";
import type { MapCardXNodeXWidgetData } from "@/arches_vue_components/widgets/MapWidget/types.ts";

const { aliasedNodeData, cardXNodeXWidgetData = undefined } = defineProps<{
    aliasedNodeData: GeoJSONFeatureCollectionAliasedNodeData;
    cardXNodeXWidgetData?: MapCardXNodeXWidgetData;
}>();

const emit = defineEmits<{
    "update:isLoading": [isLoading: boolean];
}>();

const viewerInteractionTools = useDefaultMapInteractionTools().filter(
    (interactionTool) => interactionTool.component !== MapToolsPanel,
);
</script>

<template>
    <MapComponent
        :value="aliasedNodeData.node_value"
        :zoom="cardXNodeXWidgetData?.config?.zoom"
        :pitch="cardXNodeXWidgetData?.config?.pitch"
        :bearing="cardXNodeXWidgetData?.config?.bearing"
        :center-x="cardXNodeXWidgetData?.config?.centerX"
        :center-y="cardXNodeXWidgetData?.config?.centerY"
        :min-zoom="cardXNodeXWidgetData?.config?.minZoom"
        :max-zoom="cardXNodeXWidgetData?.config?.maxZoom"
        :basemap="cardXNodeXWidgetData?.config?.basemap"
        :interaction-tools="viewerInteractionTools"
        :is-read-only="true"
        @update:is-loading="emit('update:isLoading', $event)"
    />
</template>
