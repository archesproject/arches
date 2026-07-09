<script setup lang="ts">
import { onMounted } from "vue";
import RadioButton from "primevue/radiobutton";
import RadioButtonGroup from "primevue/radiobuttongroup";

import { buildBooleanAliasedNodeData } from "@/arches_component_lab/datatypes/boolean/utils.ts";

import type { BooleanCardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { BooleanAliasedNodeData } from "@/arches_component_lab/datatypes/boolean/types.ts";

const { cardXNodeXWidgetData, aliasedNodeData } = defineProps<{
    cardXNodeXWidgetData?: BooleanCardXNodeXWidgetData;
    aliasedNodeData: BooleanAliasedNodeData | null;
}>();

const emit = defineEmits<{
    (
        event: "update:aliasedNodeData",
        updatedValue: BooleanAliasedNodeData,
    ): void;
    (event: "initialized", updatedValue: BooleanAliasedNodeData): void;
}>();

onMounted(() => {
    emit(
        "initialized",
        buildBooleanAliasedNodeData(aliasedNodeData?.node_value ?? null),
    );
});

function onUpdateModelValue(updatedValue: string | null) {
    let booleanValue: boolean | null;
    switch (updatedValue) {
        case "true":
            booleanValue = true;
            break;
        case "false":
            booleanValue = false;
            break;
        default:
            booleanValue = null;
            break;
    }
    emit("update:aliasedNodeData", buildBooleanAliasedNodeData(booleanValue));
}
</script>

<template>
    <RadioButtonGroup
        :id="cardXNodeXWidgetData?.node.alias"
        fluid="true"
        class="button-group"
        :model-value="aliasedNodeData?.node_value?.toString() ?? ''"
        tabindex="-1"
        @update:model-value="onUpdateModelValue($event)"
    >
        <div class="radio-options">
            <RadioButton
                :input-id="`${cardXNodeXWidgetData?.node.alias}-true`"
                size="small"
                value="true"
            />
            <label :for="`${cardXNodeXWidgetData?.node.alias}-true`">{{
                cardXNodeXWidgetData?.node.config.trueLabel
            }}</label>
        </div>
        <div class="radio-options">
            <RadioButton
                :input-id="`${cardXNodeXWidgetData?.node.alias}-false`"
                size="small"
                value="false"
            />
            <label :for="`${cardXNodeXWidgetData?.node.alias}-false`">{{
                cardXNodeXWidgetData?.node.config.falseLabel
            }}</label>
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

label {
    all: unset;
}
</style>
