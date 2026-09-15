<script setup lang="ts">
import { computed, onMounted, useTemplateRef } from "vue";

import MapWidgetEditor from "@/arches_vue_components/widgets/MapWidget/components/MapWidgetEditor.vue";
import MapWidgetViewer from "@/arches_vue_components/widgets/MapWidget/components/MapWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_vue_components/widgets/constants.ts";
import { buildGeoJSONFeatureCollectionAliasedNodeData } from "@/arches_vue_components/datatypes/geojson-feature-collection/utils.ts";

import type { FeatureCollection } from "geojson";

import type { GeoJSONFeatureCollectionAliasedNodeData } from "@/arches_vue_components/datatypes/geojson-feature-collection/types.ts";
import type { MapWidgetProps } from "@/arches_vue_components/widgets/MapWidget/types.ts";

const { aliasedNodeData, value } = defineProps<MapWidgetProps>();

const emit = defineEmits<{
    "update:isLoading": [isLoading: boolean];
    "update:value": [updatedValue: FeatureCollection];
    "update:overlays": [];
    "update:aliasedNodeData": [
        updatedValue: GeoJSONFeatureCollectionAliasedNodeData,
    ];
    initialized: [updatedValue: GeoJSONFeatureCollectionAliasedNodeData];
    ready: [];
}>();

const resolvedAliasedNodeData = computed(
    () =>
        aliasedNodeData ??
        buildGeoJSONFeatureCollectionAliasedNodeData(value ?? null),
);

const editorRef =
    useTemplateRef<InstanceType<typeof MapWidgetEditor>>("editor");

defineExpose({
    map: computed(() => editorRef.value?.map ?? null),
    context: computed(() => editorRef.value?.context ?? null),
});

onMounted(() => {
    emit("initialized", resolvedAliasedNodeData.value);
});
</script>

<template>
    <MapWidgetEditor
        v-if="mode === EDIT"
        ref="editor"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :aliased-node-data="resolvedAliasedNodeData"
        :interaction-tools="interactionTools"
        :feature-popup-component="featurePopupComponent"
        @update:is-loading="emit('update:isLoading', $event)"
        @update:value="emit('update:value', $event)"
        @update:aliased-node-data="emit('update:aliasedNodeData', $event)"
        @update:overlays="emit('update:overlays')"
        @ready="emit('ready')"
    />
    <MapWidgetViewer
        v-if="mode === VIEW"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :aliased-node-data="resolvedAliasedNodeData"
        @update:is-loading="emit('update:isLoading', $event)"
    />
</template>
