<script setup lang="ts">
import { computed, useTemplateRef } from "vue";

import MapWidgetEditor from "@/arches_component_lab/widgets/MapWidget/components/MapWidgetEditor/MapWidgetEditor.vue";
import MapWidgetViewer from "@/arches_component_lab/widgets/MapWidget/components/MapWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";

import type { GeoJSONFeatureCollectionValue } from "@/arches_component_lab/datatypes/geojson-feature-collection/types.ts";
import type { MapCardXNodeXWidgetData } from "@/arches_component_lab/widgets/MapWidget/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

defineProps<{
    mode: WidgetMode;
    renderContext?: string;
    nodeAlias?: string;
    graphSlug?: string;
    cardXNodeXWidgetData?: MapCardXNodeXWidgetData;
    aliasedNodeData: GeoJSONFeatureCollectionValue | null;
    shouldEmitSimplifiedValue?: boolean;
}>();

const emit = defineEmits([
    "update:isLoading",
    "update:value",
    "update:overlays",
]);

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
        :aliased-node-data="aliasedNodeData"
        :render-context="renderContext"
        :should-emit-simplified-value="shouldEmitSimplifiedValue"
        @update:is-loading="emit('update:isLoading', $event)"
        @update:value="emit('update:value', $event)"
        @update:overlays="emit('update:overlays')"
    />
    <MapWidgetViewer
        v-if="mode === VIEW"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :aliased-node-data="aliasedNodeData"
        @update:is-loading="emit('update:isLoading', $event)"
    />
</template>
