<script setup lang="ts">
import { computed } from "vue";

import NumberWidgetEditor from "@/arches_component_lab/widgets/NumberWidget/components/NumberWidgetEditor.vue";
import NumberWidgetViewer from "@/arches_component_lab/widgets/NumberWidget/components/NumberWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";
import { buildNumberAliasedNodeData } from "@/arches_component_lab/datatypes/number/utils.ts";

import type { NumberAliasedNodeData } from "@/arches_component_lab/datatypes/number/types.ts";
import type { NumberWidgetProps } from "@/arches_component_lab/widgets/NumberWidget/types.ts";

const { aliasedNodeData, value } = defineProps<NumberWidgetProps>();

const emit = defineEmits<{
    "update:isDirty": [isDirty: boolean];
    "update:value": [updatedValue: number | null];
    "update:aliasedNodeData": [updatedValue: NumberAliasedNodeData];
    initialized: [updatedValue: NumberAliasedNodeData];
}>();

const resolvedAliasedNodeData = computed(
    () => aliasedNodeData ?? buildNumberAliasedNodeData(value ?? null),
);

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
        @initialized="emit('initialized', $event)"
    />
    <NumberWidgetViewer
        v-if="mode === VIEW"
        :aliased-node-data="resolvedAliasedNodeData"
        @initialized="emit('initialized', $event)"
    />
</template>
