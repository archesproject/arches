<script setup lang="ts">
import RadioButton from "primevue/radiobutton";
import RadioButtonGroup from "primevue/radiobuttongroup";

import { buildDomainAliasedNodeData } from "@/arches_vue_components/datatypes/domain/utils.ts";

import type {
    DomainAliasedNodeData,
    DomainCardXNodeXWidgetData,
} from "@/arches_vue_components/datatypes/domain/types.ts";

const { aliasedNodeData, cardXNodeXWidgetData = undefined } = defineProps<{
    cardXNodeXWidgetData?: DomainCardXNodeXWidgetData;
    aliasedNodeData: DomainAliasedNodeData | null;
}>();

const options = cardXNodeXWidgetData?.node.config.options ?? [];

const emit = defineEmits<{
    (
        event: "update:aliasedNodeData",
        updatedValue: DomainAliasedNodeData,
    ): void;
}>();

function onUpdateModelValue(updatedValue: string | null) {
    emit(
        "update:aliasedNodeData",
        buildDomainAliasedNodeData(updatedValue, options),
    );
}
</script>

<template>
    <RadioButtonGroup
        :id="cardXNodeXWidgetData?.node.alias"
        :model-value="aliasedNodeData?.node_value ?? null"
        class="button-group"
        tabindex="-1"
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
