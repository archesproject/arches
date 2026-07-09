<script setup lang="ts">
import { computed } from "vue";

import DomainSelectWidgetEditor from "@/arches_component_lab/widgets/DomainSelectWidget/components/DomainSelectWidgetEditor.vue";
import DomainSelectWidgetViewer from "@/arches_component_lab/widgets/DomainSelectWidget/components/DomainSelectWidgetViewer.vue";

import { buildDomainAliasedNodeData } from "@/arches_component_lab/datatypes/domain/utils.ts";
import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";

import type {
    DomainAliasedNodeData,
    DomainDatatypeCardXNodeXWidgetData,
} from "@/arches_component_lab/datatypes/domain/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

const { aliasedNodeData, value, cardXNodeXWidgetData } = defineProps<{
    mode: WidgetMode;
    nodeAlias?: string;
    graphSlug?: string;
    cardXNodeXWidgetData?: DomainDatatypeCardXNodeXWidgetData;
    aliasedNodeData?: DomainAliasedNodeData | null;
    value?: string | null;
}>();

const emit = defineEmits<{
    "update:value": [updatedValue: string | null];
    "update:aliasedNodeData": [updatedValue: DomainAliasedNodeData];
    initialized: [updatedValue: DomainAliasedNodeData];
}>();

const resolvedAliasedNodeData = computed(
    () =>
        aliasedNodeData ??
        buildDomainAliasedNodeData(
            value ?? null,
            cardXNodeXWidgetData?.node.config.options ?? [],
        ),
);

function onUpdateAliasedNodeData(
    updatedAliasedNodeData: DomainAliasedNodeData,
) {
    emit("update:aliasedNodeData", updatedAliasedNodeData);
    emit("update:value", updatedAliasedNodeData.node_value);
}
</script>

<template>
    <DomainSelectWidgetEditor
        v-if="mode === EDIT"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :aliased-node-data="resolvedAliasedNodeData"
        @update:aliased-node-data="onUpdateAliasedNodeData"
        @initialized="emit('initialized', $event)"
    />
    <DomainSelectWidgetViewer
        v-if="mode === VIEW"
        :aliased-node-data="resolvedAliasedNodeData"
        @initialized="emit('initialized', $event)"
    />
</template>
