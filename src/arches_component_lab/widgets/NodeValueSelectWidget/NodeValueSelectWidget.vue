<script setup lang="ts">
import NodeValueSelectWidgetEditor from "@/arches_component_lab/widgets/NodeValueSelectWidget/components/NodeValueSelectWidgetEditor.vue";
import NodeValueSelectWidgetViewer from "@/arches_component_lab/widgets/NodeValueSelectWidget/components/NodeValueSelectWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";

import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { NodeValueValue } from "@/arches_component_lab/datatypes/node-value/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

defineProps<{
    mode: WidgetMode;
    nodeAlias: string;
    graphSlug: string;
    cardXNodeXWidgetData: CardXNodeXWidgetData;
    aliasedNodeData: NodeValueValue | null;
    shouldEmitSimplifiedValue?: boolean;
}>();

const emit = defineEmits(["update:value"]);
</script>

<template>
    <NodeValueSelectWidgetEditor
        v-if="mode === EDIT"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :aliased-node-data="aliasedNodeData"
        :should-emit-simplified-value="shouldEmitSimplifiedValue"
        @update:value="emit('update:value', $event)"
    />
    <NodeValueSelectWidgetViewer
        v-if="mode === VIEW"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :aliased-node-data="aliasedNodeData"
    />
</template>
