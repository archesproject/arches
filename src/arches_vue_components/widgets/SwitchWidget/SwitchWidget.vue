<script setup lang="ts">
import { computed } from "vue";

import SwitchWidgetEditor from "@/arches_vue_components/widgets/SwitchWidget/components/SwitchWidgetEditor.vue";
import SwitchWidgetViewer from "@/arches_vue_components/widgets/SwitchWidget/components/SwitchWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_vue_components/widgets/constants.ts";
import { buildBooleanAliasedNodeData } from "@/arches_vue_components/datatypes/boolean/utils.ts";

import type { BooleanAliasedNodeData } from "@/arches_vue_components/datatypes/boolean/types.ts";
import type { SwitchWidgetProps } from "@/arches_vue_components/widgets/SwitchWidget/types.ts";

const { aliasedNodeData, value } = defineProps<SwitchWidgetProps>();

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
    <SwitchWidgetEditor
        v-if="mode === EDIT"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :aliased-node-data="resolvedAliasedNodeData"
        @update:aliased-node-data="onUpdateAliasedNodeData"
        @initialized="emit('initialized', $event)"
    />
    <SwitchWidgetViewer
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
