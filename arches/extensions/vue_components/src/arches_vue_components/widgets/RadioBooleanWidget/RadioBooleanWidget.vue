<script setup lang="ts">
import { computed, onMounted } from "vue";

import RadioBooleanWidgetEditor from "@/arches_vue_components/widgets/RadioBooleanWidget/components/RadioBooleanWidgetEditor.vue";
import RadioBooleanWidgetViewer from "@/arches_vue_components/widgets/RadioBooleanWidget/components/RadioBooleanWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_vue_components/widgets/constants.ts";
import { buildBooleanAliasedNodeData } from "@/arches_vue_components/datatypes/boolean/utils.ts";

import type { BooleanAliasedNodeData } from "@/arches_vue_components/datatypes/boolean/types.ts";
import type { RadioBooleanWidgetProps } from "@/arches_vue_components/widgets/RadioBooleanWidget/types.ts";

const { aliasedNodeData, value } = defineProps<RadioBooleanWidgetProps>();

const emit = defineEmits<{
    "update:value": [updatedValue: boolean | null];
    "update:aliasedNodeData": [updatedValue: BooleanAliasedNodeData];
    initialized: [updatedValue: BooleanAliasedNodeData];
    ready: [];
}>();

const resolvedAliasedNodeData = computed(
    () => aliasedNodeData ?? buildBooleanAliasedNodeData(value ?? null),
);

onMounted(() => {
    emit("initialized", resolvedAliasedNodeData.value);
    emit("ready");
});

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
    />
    <RadioBooleanWidgetViewer
        v-if="mode === VIEW"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :aliased-node-data="resolvedAliasedNodeData"
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
