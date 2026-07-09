<script setup lang="ts">
import { computed } from "vue";

import NodeValueSelectWidgetEditor from "@/arches_component_lab/widgets/NodeValueSelectWidget/components/NodeValueSelectWidgetEditor.vue";
import NodeValueSelectWidgetViewer from "@/arches_component_lab/widgets/NodeValueSelectWidget/components/NodeValueSelectWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";
import { buildNodeValueAliasedNodeData } from "@/arches_component_lab/datatypes/node-value/utils.ts";

import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { NodeValueAliasedNodeData } from "@/arches_component_lab/datatypes/node-value/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

const { aliasedNodeData, value } = defineProps<{
    mode: WidgetMode;
    nodeAlias?: string;
    graphSlug?: string;
    cardXNodeXWidgetData?: CardXNodeXWidgetData;
    aliasedNodeData?: NodeValueAliasedNodeData | null;
    value?: string | null;
}>();

const emit = defineEmits<{
    "update:value": [updatedValue: string | null];
    "update:aliasedNodeData": [updatedValue: NodeValueAliasedNodeData];
    initialized: [updatedValue: NodeValueAliasedNodeData];
}>();

const resolvedAliasedNodeData = computed(
    () => aliasedNodeData ?? buildNodeValueAliasedNodeData(value ?? null),
);

function onUpdateAliasedNodeData(
    updatedAliasedNodeData: NodeValueAliasedNodeData,
) {
    emit("update:aliasedNodeData", updatedAliasedNodeData);
    emit("update:value", updatedAliasedNodeData.node_value);
}
</script>

<template>
    <NodeValueSelectWidgetEditor
        v-if="mode === EDIT"
        :aliased-node-data="resolvedAliasedNodeData"
        @update:aliased-node-data="onUpdateAliasedNodeData"
        @initialized="emit('initialized', $event)"
    />
    <NodeValueSelectWidgetViewer
        v-if="mode === VIEW"
        :aliased-node-data="resolvedAliasedNodeData"
        @initialized="emit('initialized', $event)"
    />
</template>
