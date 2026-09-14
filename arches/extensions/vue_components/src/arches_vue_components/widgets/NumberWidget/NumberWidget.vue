<script setup lang="ts">
import { computed, onMounted } from "vue";

import NumberWidgetEditor from "@/arches_vue_components/widgets/NumberWidget/components/NumberWidgetEditor.vue";
import NumberWidgetViewer from "@/arches_vue_components/widgets/NumberWidget/components/NumberWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_vue_components/widgets/constants.ts";
import { buildNumberAliasedNodeData } from "@/arches_vue_components/datatypes/number/utils.ts";

import type { NumberAliasedNodeData } from "@/arches_vue_components/datatypes/number/types.ts";
import type { NumberWidgetProps } from "@/arches_vue_components/widgets/NumberWidget/types.ts";

const { aliasedNodeData, value } = defineProps<NumberWidgetProps>();

const emit = defineEmits<{
    "update:value": [updatedValue: number | null];
    "update:aliasedNodeData": [updatedValue: NumberAliasedNodeData];
    initialized: [updatedValue: NumberAliasedNodeData];
    ready: [];
}>();

const resolvedAliasedNodeData = computed(
    () => aliasedNodeData ?? buildNumberAliasedNodeData(value ?? null),
);

onMounted(() => {
    emit("initialized", resolvedAliasedNodeData.value);
    emit("ready");
});

function onUpdateAliasedNodeData(
    updatedAliasedNodeData: NumberAliasedNodeData,
) {
    emit("update:aliasedNodeData", updatedAliasedNodeData);
    emit("update:value", updatedAliasedNodeData.node_value);
}
</script>

<template>
    <NumberWidgetEditor
        v-if="mode === EDIT"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :aliased-node-data="resolvedAliasedNodeData"
        @update:aliased-node-data="onUpdateAliasedNodeData"
    />
    <NumberWidgetViewer
        v-if="mode === VIEW"
        :aliased-node-data="resolvedAliasedNodeData"
    />
</template>
