<script setup lang="ts">
import RadioButton from "primevue/radiobutton";
import RadioButtonGroup from "primevue/radiobuttongroup";
import { useGettext } from "vue3-gettext";

import type { BooleanCardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { BooleanValue } from "@/arches_component_lab/datatypes/boolean/types.ts";

const { $gettext } = useGettext();

const {
    cardXNodeXWidgetData,
    aliasedNodeData,
    shouldEmitSimplifiedValue = false,
} = defineProps<{
    cardXNodeXWidgetData: BooleanCardXNodeXWidgetData;
    aliasedNodeData: BooleanValue | null;
    shouldEmitSimplifiedValue?: boolean;
}>();

const emit = defineEmits<{
    (
        event: "update:value",
        updatedValue: BooleanValue | boolean | undefined | null,
    ): void;
}>();

function getDisplayValue(value: boolean | null | undefined): string {
    if (value === true) {
        return cardXNodeXWidgetData.node.config.trueLabel || $gettext("True");
    } else if (value === false) {
        return cardXNodeXWidgetData.node.config.falseLabel || $gettext("False");
    } else {
        return "";
    }
}

function onUpdateModelValue(updatedValue: string | null) {
    let booleanValue;
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

    if (shouldEmitSimplifiedValue) {
        emit("update:value", booleanValue);
    } else {
        emit("update:value", {
            display_value: getDisplayValue(booleanValue),
            node_value: booleanValue,
            details: [],
        });
    }
}
</script>

<template>
    <RadioButtonGroup
        fluid="true"
        class="button-group"
        :model-value="aliasedNodeData?.node_value?.toString() || ''"
        @update:model-value="onUpdateModelValue($event)"
    >
        <div class="radio-options">
            <RadioButton
                input-id="`${cardXNodeXWidgetData.node.alias}-true`"
                size="small"
                value="true"
            />
            <label for="`${cardXNodeXWidgetData.node.alias}-true`">{{
                cardXNodeXWidgetData.node.config.trueLabel
            }}</label>
        </div>
        <div class="radio-options">
            <RadioButton
                input-id="`${cardXNodeXWidgetData.node.alias}-false`"
                size="small"
                value="false"
            />
            <label for="`${cardXNodeXWidgetData.node.alias}-false`">{{
                cardXNodeXWidgetData.node.config.falseLabel
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
