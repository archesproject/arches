<script setup lang="ts">
import { computed, useTemplateRef } from "vue";

import MapWidgetEditor from "@/arches_component_lab/widgets/MapWidget/components/MapWidgetEditor/MapWidgetEditor.vue";
import MapWidgetViewer from "@/arches_component_lab/widgets/MapWidget/components/MapWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";
import { buildGeoJSONFeatureCollectionAliasedNodeData } from "@/arches_component_lab/datatypes/geojson-feature-collection/utils.ts";

import type { FeatureCollection } from "geojson";

import type { GeoJSONFeatureCollectionAliasedNodeData } from "@/arches_component_lab/datatypes/geojson-feature-collection/types.ts";
import type { MapWidgetProps } from "@/arches_component_lab/widgets/MapWidget/types.ts";

const { aliasedNodeData, value } = defineProps<MapWidgetProps>();

const emit = defineEmits<{
    "update:isLoading": [isLoading: boolean];
    "update:value": [updatedValue: FeatureCollection];
    "update:overlays": [];
    "update:aliasedNodeData": [
        updatedValue: GeoJSONFeatureCollectionAliasedNodeData,
    ];
    initialized: [updatedValue: GeoJSONFeatureCollectionAliasedNodeData];
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
});
</script>

<template>
    <MapWidgetEditor
        v-if="mode === EDIT"
        ref="editor"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :aliased-node-data="resolvedAliasedNodeData"
        :render-context="renderContext"
        @update:is-loading="emit('update:isLoading', $event)"
        @update:value="emit('update:value', $event)"
        @update:aliased-node-data="emit('update:aliasedNodeData', $event)"
        @update:overlays="emit('update:overlays')"
        @initialized="emit('initialized', $event)"
    />
    <MapWidgetViewer
        v-if="mode === VIEW"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :aliased-node-data="resolvedAliasedNodeData"
        @update:is-loading="emit('update:isLoading', $event)"
    />
</template>
