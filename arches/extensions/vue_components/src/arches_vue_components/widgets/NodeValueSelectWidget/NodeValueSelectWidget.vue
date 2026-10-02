<script setup lang="ts">
import { computed, onMounted } from "vue";

import NodeValueSelectWidgetEditor from "@/arches_vue_components/widgets/NodeValueSelectWidget/components/NodeValueSelectWidgetEditor.vue";
import NodeValueSelectWidgetViewer from "@/arches_vue_components/widgets/NodeValueSelectWidget/components/NodeValueSelectWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_vue_components/widgets/constants.ts";
import { buildNodeValueAliasedNodeData } from "@/arches_vue_components/datatypes/node-value/utils.ts";

import type { NodeValueAliasedNodeData } from "@/arches_vue_components/datatypes/node-value/types.ts";
import type { NodeValueSelectWidgetProps } from "@/arches_vue_components/widgets/NodeValueSelectWidget/types.ts";

const { aliasedNodeData, value } = defineProps<NodeValueSelectWidgetProps>();

const emit = defineEmits<{
    "update:value": [updatedValue: string | null];
    "update:aliasedNodeData": [updatedValue: NodeValueAliasedNodeData];
    initialized: [updatedValue: NodeValueAliasedNodeData];
    ready: [];
}>();

const resolvedAliasedNodeData = computed(
    () => aliasedNodeData ?? buildNodeValueAliasedNodeData(value ?? null),
);

onMounted(() => {
    emit("initialized", resolvedAliasedNodeData.value);
    emit("ready");
});

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
    />
    <NodeValueSelectWidgetViewer
        v-if="mode === VIEW"
        :aliased-node-data="resolvedAliasedNodeData"
    />
</template>
