<script setup lang="ts">
import RadioButton from "primevue/radiobutton";
import RadioButtonGroup from "primevue/radiobuttongroup";

import type {
    DomainDatatypeCardXNodeXWidgetData,
    DomainValue,
    DomainOption,
} from "@/arches_component_lab/datatypes/domain/types.ts";

const {
    cardXNodeXWidgetData,
    aliasedNodeData,
    shouldEmitSimplifiedValue = false,
} = defineProps<{
    cardXNodeXWidgetData: DomainDatatypeCardXNodeXWidgetData;
    aliasedNodeData: DomainValue | null;
    shouldEmitSimplifiedValue?: boolean;
}>();

const options = cardXNodeXWidgetData.node.config.options;

const emit = defineEmits<{
    (event: "update:value", updatedValue: DomainValue | string | null): void;
}>();

function onUpdateModelValue(updatedValue: string | null) {
    if (shouldEmitSimplifiedValue) {
        emit("update:value", updatedValue);
    } else {
        const updatedDisplayValue =
            options.find((option: DomainOption) => option.id === updatedValue)
                ?.text || "";

        emit("update:value", {
            display_value: updatedDisplayValue,
            node_value: updatedValue,
            details: [],
        });
    }
}
</script>

<template>
    <RadioButtonGroup
        :model-value="aliasedNodeData?.node_value"
        class="button-group"
        @update:model-value="onUpdateModelValue($event)"
    >
        <div
            v-for="option in options"
            :key="option.id"
            class="radio-options"
        >
            <RadioButton
                :input-id="option.id"
                :value="option.id"
                size="small"
            />
            <label :for="option.id">{{ option.text }}</label>
        </div>
    </RadioButtonGroup>
</template>
<style scoped>
.button-group {
    display: flex;
    flex-direction: row;
    column-gap: 1.5rem;
    row-gap: 0.5rem;
    flex-wrap: wrap;
}
.radio-options {
    display: flex;
    gap: 0.25rem;
    align-items: center;
}
</style>
