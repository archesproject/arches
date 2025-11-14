<script setup lang="ts">
import Select from "primevue/select";

import type {
    DomainDatatypeCardXNodeXWidgetData,
    DomainValue,
    DomainOption,
} from "@/arches_component_lab/datatypes/domain/types.ts";

const { cardXNodeXWidgetData, aliasedNodeData } = defineProps<{
    cardXNodeXWidgetData: DomainDatatypeCardXNodeXWidgetData;
    aliasedNodeData: DomainValue;
}>();

const options = cardXNodeXWidgetData.node.config.options;

const emit = defineEmits<{
    (event: "update:value", updatedValue: DomainValue): void;
}>();

function onUpdateModelValue(updatedValue: string | null) {
    const updatedDisplayValue =
        options.find((option: DomainOption) => option.id === updatedValue)
            ?.text || "";

    emit("update:value", {
        display_value: updatedDisplayValue,
        node_value: updatedValue,
        details: [],
    });
}
</script>

<template>
    <Select
        option-value="id"
        option-label="text"
        :options="options"
        :placeholder="cardXNodeXWidgetData.config.placeholder"
        :fluid="true"
        :model-value="aliasedNodeData.node_value"
        @update:model-value="onUpdateModelValue($event)"
    />
</template>
