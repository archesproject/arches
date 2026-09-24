<script setup lang="ts">
import MultiSelect from "primevue/multiselect";

import { buildDomainListAliasedNodeData } from "@/arches_vue_components/datatypes/domain/utils.ts";

import type {
    DomainCardXNodeXWidgetData,
    DomainListAliasedNodeData,
} from "@/arches_vue_components/datatypes/domain/types.ts";

const { aliasedNodeData, cardXNodeXWidgetData = undefined } = defineProps<{
    cardXNodeXWidgetData?: DomainCardXNodeXWidgetData;
    aliasedNodeData: DomainListAliasedNodeData | null;
}>();

const options = cardXNodeXWidgetData?.node.config.options ?? [];

const emit = defineEmits<{
    (
        event: "update:aliasedNodeData",
        updatedValue: DomainListAliasedNodeData,
    ): void;
}>();

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
