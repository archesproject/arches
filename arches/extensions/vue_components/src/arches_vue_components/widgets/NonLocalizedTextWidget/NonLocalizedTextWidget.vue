<script setup lang="ts">
import { computed, onMounted } from "vue";

import NonLocalizedTextWidgetEditor from "@/arches_vue_components/widgets/NonLocalizedTextWidget/components/NonLocalizedTextWidgetEditor.vue";
import NonLocalizedTextWidgetViewer from "@/arches_vue_components/widgets/NonLocalizedTextWidget/components/NonLocalizedTextWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_vue_components/widgets/constants.ts";
import { buildNonLocalizedTextAliasedNodeData } from "@/arches_vue_components/datatypes/non-localized-text/utils.ts";

import type { NonLocalizedTextAliasedNodeData } from "@/arches_vue_components/datatypes/non-localized-text/types.ts";
import type { NonLocalizedTextWidgetProps } from "@/arches_vue_components/widgets/NonLocalizedTextWidget/types.ts";

const { aliasedNodeData, value } = defineProps<NonLocalizedTextWidgetProps>();

const emit = defineEmits<{
    "update:value": [updatedValue: string | null];
    "update:aliasedNodeData": [updatedValue: NonLocalizedTextAliasedNodeData];
    initialized: [updatedValue: NonLocalizedTextAliasedNodeData];
    ready: [];
}>();

const resolvedAliasedNodeData = computed(
    () =>
        aliasedNodeData ?? buildNonLocalizedTextAliasedNodeData(value ?? null),
);

onMounted(() => {
    emit("initialized", resolvedAliasedNodeData.value);
    emit("ready");
});

function onUpdateAliasedNodeData(
    updatedAliasedNodeData: NonLocalizedTextAliasedNodeData,
) {
    emit("update:aliasedNodeData", updatedAliasedNodeData);
    emit("update:value", updatedAliasedNodeData.node_value);
}
</script>

<template>
    <NonLocalizedTextWidgetEditor
        v-if="mode === EDIT"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :aliased-node-data="resolvedAliasedNodeData"
        :render-context="renderContext"
        @update:aliased-node-data="onUpdateAliasedNodeData"
    />
    <NonLocalizedTextWidgetViewer
        v-if="mode === VIEW"
        :aliased-node-data="resolvedAliasedNodeData"
    />
</template>
