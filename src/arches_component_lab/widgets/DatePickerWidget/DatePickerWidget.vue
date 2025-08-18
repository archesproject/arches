<script setup lang="ts">
import DatePickerWidgetEditor from "@/arches_component_lab/widgets/DatePickerWidget/components/DatePickerWidgetEditor.vue";
import DatePickerWidgetViewer from "@/arches_component_lab/widgets/DatePickerWidget/components/DatePickerWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";

import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";
import type {
    DateValue,
    DateDatatypeCardXNodeXWidgetData,
} from "@/arches_component_lab/datatypes/date/types.ts";

defineProps<{
    mode: WidgetMode;
    nodeAlias: string;
    graphSlug: string;
    cardXNodeXWidgetData: DateDatatypeCardXNodeXWidgetData;
    aliasedNodeData: DateValue;
}>();

const emit = defineEmits(["update:value"]);
</script>

<template>
    <DatePickerWidgetEditor
        v-if="mode === EDIT"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :aliased-node-data="aliasedNodeData"
        @update:value="emit('update:value', $event)"
    />
    <DatePickerWidgetViewer
        v-if="mode === VIEW"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :aliased-node-data="aliasedNodeData"
    />
</template>
