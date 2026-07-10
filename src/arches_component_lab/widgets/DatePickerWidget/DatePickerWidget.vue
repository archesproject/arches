<script setup lang="ts">
import { computed } from "vue";

import DatePickerWidgetEditor from "@/arches_component_lab/widgets/DatePickerWidget/components/DatePickerWidgetEditor.vue";
import DatePickerWidgetViewer from "@/arches_component_lab/widgets/DatePickerWidget/components/DatePickerWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";
import { buildDateAliasedNodeData } from "@/arches_component_lab/datatypes/date/utils.ts";

import type { DateAliasedNodeData } from "@/arches_component_lab/datatypes/date/types.ts";
import type { DatePickerWidgetProps } from "@/arches_component_lab/widgets/DatePickerWidget/types.ts";

const { aliasedNodeData, value } = defineProps<DatePickerWidgetProps>();

const emit = defineEmits<{
    "update:value": [updatedValue: string | null];
    "update:aliasedNodeData": [updatedValue: DateAliasedNodeData];
    initialized: [updatedValue: DateAliasedNodeData];
}>();

const resolvedAliasedNodeData = computed(
    () => aliasedNodeData ?? buildDateAliasedNodeData(value ?? null),
);

function onUpdateAliasedNodeData(updatedAliasedNodeData: DateAliasedNodeData) {
    emit("update:aliasedNodeData", updatedAliasedNodeData);
    emit("update:value", updatedAliasedNodeData.node_value);
}
</script>

<template>
    <DatePickerWidgetEditor
        v-if="mode === EDIT"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :aliased-node-data="resolvedAliasedNodeData"
        @update:aliased-node-data="onUpdateAliasedNodeData"
        @initialized="emit('initialized', $event)"
    />
    <DatePickerWidgetViewer
        v-if="mode === VIEW"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :aliased-node-data="resolvedAliasedNodeData"
        @initialized="emit('initialized', $event)"
    />
</template>
