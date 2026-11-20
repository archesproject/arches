<script setup lang="ts">
import MultiSelect from "openvue/multiselect";

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
        overlay-class="domain-multiselect-widget-overlay"
        :input-id="cardXNodeXWidgetData?.node.alias"
        :options="options"
        :placeholder="cardXNodeXWidgetData?.config.placeholder"
        :fluid="true"
        :show-clear="true"
        :model-value="aliasedNodeData?.node_value ?? []"
        @update:model-value="onUpdateModelValue($event)"
    />
</template>

<style>
.domain-multiselect-widget-overlay .p-checkbox,
.domain-multiselect-widget-overlay .p-checkbox-box {
    inline-size: 1.8rem;
    block-size: 1.8rem;
}

.domain-multiselect-widget-overlay .p-checkbox-icon {
    inline-size: 1.2rem;
    block-size: 1.2rem;
    font-size: 1.2rem;
}
</style>
