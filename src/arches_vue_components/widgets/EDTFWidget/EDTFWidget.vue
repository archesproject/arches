<script setup lang="ts">
import { computed } from "vue";

import EDTFWidgetEditor from "@/arches_vue_components/widgets/EDTFWidget/components/EDTFWidgetEditor/EDTFWidgetEditor.vue";
import EDTFWidgetViewer from "@/arches_vue_components/widgets/EDTFWidget/components/EDTFWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_vue_components/widgets/constants.ts";
import { buildEDTFAliasedNodeData } from "@/arches_vue_components/datatypes/edtf/utils.ts";

import type { EDTFAliasedNodeData } from "@/arches_vue_components/datatypes/edtf/types.ts";
import type { EDTFWidgetProps } from "@/arches_vue_components/widgets/EDTFWidget/types.ts";

const { aliasedNodeData, value } = defineProps<EDTFWidgetProps>();

const emit = defineEmits<{
    "update:isDirty": [isDirty: boolean];
    "update:value": [updatedValue: string | null];
    "update:aliasedNodeData": [updatedValue: EDTFAliasedNodeData];
    initialized: [updatedValue: EDTFAliasedNodeData];
}>();

const resolvedAliasedNodeData = computed(
    () => aliasedNodeData ?? buildEDTFAliasedNodeData(value ?? null),
);

function onUpdateAliasedNodeData(updatedAliasedNodeData: EDTFAliasedNodeData) {
    emit("update:aliasedNodeData", updatedAliasedNodeData);
    emit("update:value", updatedAliasedNodeData.node_value);
}
</script>

<template>
    <EDTFWidgetEditor
        v-if="mode === EDIT"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :aliased-node-data="resolvedAliasedNodeData"
        @update:aliased-node-data="onUpdateAliasedNodeData"
        @initialized="emit('initialized', $event)"
    />
    <EDTFWidgetViewer
        v-if="mode === VIEW"
        :aliased-node-data="resolvedAliasedNodeData"
        @initialized="emit('initialized', $event)"
    />
</template>
