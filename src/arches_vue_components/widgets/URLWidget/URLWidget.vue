<script setup lang="ts">
import { computed, onMounted } from "vue";

import URLWidgetEditor from "@/arches_vue_components/widgets/URLWidget/components/URLWidgetEditor.vue";
import URLWidgetViewer from "@/arches_vue_components/widgets/URLWidget/components/URLWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_vue_components/widgets/constants.ts";
import { buildURLAliasedNodeData } from "@/arches_vue_components/datatypes/url/utils.ts";

import type {
    URLAliasedNodeData,
    URLNodeValue,
} from "@/arches_vue_components/datatypes/url/types.ts";
import type { URLWidgetProps } from "@/arches_vue_components/widgets/URLWidget/types.ts";

const { aliasedNodeData, value } = defineProps<URLWidgetProps>();

const emit = defineEmits<{
    "update:value": [updatedValue: URLNodeValue | null];
    "update:aliasedNodeData": [updatedValue: URLAliasedNodeData];
    initialized: [updatedValue: URLAliasedNodeData];
    ready: [];
}>();

const resolvedAliasedNodeData = computed(
    () => aliasedNodeData ?? buildURLAliasedNodeData(value ?? null),
);

onMounted(() => {
    emit("initialized", resolvedAliasedNodeData.value);
    emit("ready");
});

function onUpdateAliasedNodeData(updatedAliasedNodeData: URLAliasedNodeData) {
    emit("update:aliasedNodeData", updatedAliasedNodeData);
    emit("update:value", updatedAliasedNodeData.node_value);
}
</script>

<template>
    <URLWidgetEditor
        v-if="mode === EDIT"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :aliased-node-data="resolvedAliasedNodeData"
        @update:aliased-node-data="onUpdateAliasedNodeData"
    />
    <URLWidgetViewer
        v-if="mode === VIEW"
        :aliased-node-data="resolvedAliasedNodeData"
    />
</template>
