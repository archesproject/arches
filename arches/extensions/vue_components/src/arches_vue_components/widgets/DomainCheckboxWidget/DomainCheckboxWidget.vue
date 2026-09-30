<script setup lang="ts">
import { computed, onMounted } from "vue";

import DomainCheckboxWidgetEditor from "@/arches_vue_components/widgets/DomainCheckboxWidget/components/DomainCheckboxWidgetEditor.vue";
import DomainCheckboxWidgetViewer from "@/arches_vue_components/widgets/DomainCheckboxWidget/components/DomainCheckboxWidgetViewer.vue";

import { buildDomainListAliasedNodeData } from "@/arches_vue_components/datatypes/domain/utils.ts";
import { EDIT, VIEW } from "@/arches_vue_components/widgets/constants.ts";

import type { DomainListAliasedNodeData } from "@/arches_vue_components/datatypes/domain/types.ts";
import type { DomainCheckboxWidgetProps } from "@/arches_vue_components/widgets/DomainCheckboxWidget/types.ts";

const { aliasedNodeData, cardXNodeXWidgetData, value } =
    defineProps<DomainCheckboxWidgetProps>();

const emit = defineEmits<{
    "update:value": [updatedValue: string[] | null];
    "update:aliasedNodeData": [updatedValue: DomainListAliasedNodeData];
    initialized: [updatedValue: DomainListAliasedNodeData];
    ready: [];
}>();

const resolvedAliasedNodeData = computed(
    () =>
        aliasedNodeData ??
        buildDomainListAliasedNodeData(
            value ?? null,
            cardXNodeXWidgetData?.node.config.options ?? [],
        ),
);

onMounted(() => {
    emit("initialized", resolvedAliasedNodeData.value);
    emit("ready");
});

function onUpdateAliasedNodeData(
    updatedAliasedNodeData: DomainListAliasedNodeData,
) {
    emit("update:aliasedNodeData", updatedAliasedNodeData);
    emit("update:value", updatedAliasedNodeData.node_value);
}
</script>

<template>
    <DomainCheckboxWidgetEditor
        v-if="mode === EDIT"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :aliased-node-data="resolvedAliasedNodeData"
        @update:aliased-node-data="onUpdateAliasedNodeData"
    />
    <DomainCheckboxWidgetViewer
        v-if="mode === VIEW"
        :aliased-node-data="resolvedAliasedNodeData"
    />
</template>
