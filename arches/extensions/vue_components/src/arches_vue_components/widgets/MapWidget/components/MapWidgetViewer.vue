<script setup lang="ts">
import { computed } from "vue";

import MapComponent from "@/arches_vue_components/components/MapComponent/MapComponent.vue";

import { buildMapSettings } from "@/arches_vue_components/widgets/MapWidget/utils.ts";

import type { GeoJSONFeatureCollectionAliasedNodeData } from "@/arches_vue_components/datatypes/geojson-feature-collection/types.ts";
import type { MapCardXNodeXWidgetData } from "@/arches_vue_components/widgets/MapWidget/types.ts";

const { aliasedNodeData, cardXNodeXWidgetData = undefined } = defineProps<{
    aliasedNodeData: GeoJSONFeatureCollectionAliasedNodeData;
    cardXNodeXWidgetData?: MapCardXNodeXWidgetData;
}>();

const emit = defineEmits<{
    "update:isLoading": [isLoading: boolean];
}>();

const mapSettings = computed(() =>
    buildMapSettings(cardXNodeXWidgetData?.config),
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
        :is-read-only="true"
        :settings="mapSettings"
        @update:is-loading="emit('update:isLoading', $event)"
    />
</template>
