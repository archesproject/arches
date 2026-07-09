<script setup lang="ts">
import { onMounted } from "vue";
import MultiSelect from "primevue/multiselect";

import { buildDomainListAliasedNodeData } from "@/arches_component_lab/datatypes/domain/utils.ts";

import type {
    DomainDatatypeCardXNodeXWidgetData,
    DomainListAliasedNodeData,
} from "@/arches_component_lab/datatypes/domain/types.ts";

const { aliasedNodeData, cardXNodeXWidgetData } = defineProps<{
    cardXNodeXWidgetData?: DomainDatatypeCardXNodeXWidgetData;
    aliasedNodeData: DomainListAliasedNodeData | null;
}>();

const options = cardXNodeXWidgetData?.node.config.options ?? [];

const emit = defineEmits<{
    (
        event: "update:aliasedNodeData",
        updatedValue: DomainListAliasedNodeData,
    ): void;
    (event: "initialized", updatedValue: DomainListAliasedNodeData): void;
}>();

onMounted(() => {
    emit(
        "initialized",
        aliasedNodeData ?? buildDomainListAliasedNodeData(null, options),
    );
});

function onUpdateModelValue(updatedValue: string[] | null) {
    const nodeValues = updatedValue?.length ? updatedValue : null;
    emit(
        "update:aliasedNodeData",
        buildDomainListAliasedNodeData(nodeValues, options),
    );
}
</script>

<template>
    <MultiSelect
        option-value="id"
        option-label="text"
        :input-id="cardXNodeXWidgetData?.node.alias"
        :options="options"
        :placeholder="cardXNodeXWidgetData?.config.placeholder"
        :fluid="true"
        :show-clear="true"
        :model-value="aliasedNodeData?.node_value ?? []"
        @update:model-value="onUpdateModelValue($event)"
    />
</template>
