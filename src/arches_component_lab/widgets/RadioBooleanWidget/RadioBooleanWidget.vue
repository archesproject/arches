<script setup lang="ts">
import { computed } from "vue";

import RadioBooleanWidgetEditor from "@/arches_component_lab/widgets/RadioBooleanWidget/components/RadioBooleanWidgetEditor.vue";
import RadioBooleanWidgetViewer from "@/arches_component_lab/widgets/RadioBooleanWidget/components/RadioBooleanWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";
import { buildBooleanAliasedNodeData } from "@/arches_component_lab/datatypes/boolean/utils.ts";

import type { BooleanCardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { BooleanAliasedNodeData } from "@/arches_component_lab/datatypes/boolean/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

const { aliasedNodeData, value } = defineProps<{
    mode: WidgetMode;
    nodeAlias?: string;
    graphSlug?: string;
    cardXNodeXWidgetData?: BooleanCardXNodeXWidgetData;
    aliasedNodeData?: BooleanAliasedNodeData | null;
    value?: boolean | null;
}>();

const emit = defineEmits<{
    "update:value": [updatedValue: boolean | null];
    "update:aliasedNodeData": [updatedValue: BooleanAliasedNodeData];
    initialized: [updatedValue: BooleanAliasedNodeData];
}>();

const resolvedAliasedNodeData = computed(
    () => aliasedNodeData ?? buildBooleanAliasedNodeData(value ?? null),
);

function onUpdateAliasedNodeData(
    updatedAliasedNodeData: BooleanAliasedNodeData,
) {
    emit("update:aliasedNodeData", updatedAliasedNodeData);
    emit("update:value", updatedAliasedNodeData.node_value);
}
</script>

<template>
    <RadioBooleanWidgetEditor
        v-if="mode === EDIT"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :aliased-node-data="resolvedAliasedNodeData"
        @update:aliased-node-data="onUpdateAliasedNodeData"
        @initialized="emit('initialized', $event)"
    />
    <RadioBooleanWidgetViewer
        v-if="mode === VIEW"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :aliased-node-data="resolvedAliasedNodeData"
        @initialized="emit('initialized', $event)"
    />
</template>

<style scoped>
.widget {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    width: 100%;
}
</style>
