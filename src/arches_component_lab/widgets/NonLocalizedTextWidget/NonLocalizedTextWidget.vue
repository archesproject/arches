<script setup lang="ts">
import { computed } from "vue";

import NonLocalizedTextWidgetEditor from "@/arches_component_lab/widgets/NonLocalizedTextWidget/components/NonLocalizedTextWidgetEditor.vue";
import NonLocalizedTextWidgetViewer from "@/arches_component_lab/widgets/NonLocalizedTextWidget/components/NonLocalizedTextWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";
import { buildNonLocalizedTextAliasedNodeData } from "@/arches_component_lab/datatypes/non-localized-text/utils.ts";

import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { NonLocalizedTextAliasedNodeData } from "@/arches_component_lab/datatypes/non-localized-text/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

const { aliasedNodeData, value } = defineProps<{
    mode: WidgetMode;
    nodeAlias?: string;
    graphSlug?: string;
    cardXNodeXWidgetData?: CardXNodeXWidgetData;
    aliasedNodeData?: NonLocalizedTextAliasedNodeData | null;
    value?: string | null;
    renderContext?: string;
}>();

const emit = defineEmits<{
    "update:value": [updatedValue: string | null];
    "update:aliasedNodeData": [updatedValue: NonLocalizedTextAliasedNodeData];
    initialized: [updatedValue: NonLocalizedTextAliasedNodeData];
}>();

const resolvedAliasedNodeData = computed(
    () =>
        aliasedNodeData ?? buildNonLocalizedTextAliasedNodeData(value ?? null),
);

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
        @initialized="emit('initialized', $event)"
    />
    <NonLocalizedTextWidgetViewer
        v-if="mode === VIEW"
        :aliased-node-data="resolvedAliasedNodeData"
        @initialized="emit('initialized', $event)"
    />
</template>
