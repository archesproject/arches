<script setup lang="ts">
import InputNumber from "primevue/inputnumber";

import type {
    NumberCardXNodeXWidgetData,
    NumberValue,
} from "@/arches_component_lab/datatypes/number/types.ts";

const { cardXNodeXWidgetData, aliasedNodeData, shouldEmitSimplifiedValue } =
    defineProps<{
        cardXNodeXWidgetData: NumberCardXNodeXWidgetData;
        aliasedNodeData: NumberValue | null;
        shouldEmitSimplifiedValue?: boolean;
    }>();

const emit = defineEmits<{
    (event: "update:value", updatedValue: NumberValue | number | null): void;
}>();

function onUpdateModelValue(updatedValue: number | null) {
    if (shouldEmitSimplifiedValue) {
        emit("update:value", updatedValue);
    } else {
        emit("update:value", {
            display_value: updatedValue !== null ? updatedValue.toString() : "",
            node_value: updatedValue,
            details: [],
        });
    }
}
</script>

<template>
    <InputNumber
        :model-value="aliasedNodeData?.node_value"
        :fluid="true"
        :input-id="cardXNodeXWidgetData.node.alias"
        :placeholder="cardXNodeXWidgetData.config.placeholder"
        :prefix="cardXNodeXWidgetData.config.prefix ?? ''"
        :suffix="cardXNodeXWidgetData.config.suffix ?? ''"
        :min-fraction-digits="
            Number(cardXNodeXWidgetData.config.precision) || 0
        "
        :max-fraction-digits="
            Number(cardXNodeXWidgetData.config.precision) || 0
        "
        :min="Number(cardXNodeXWidgetData.config.min) || -Infinity"
        :max="Number(cardXNodeXWidgetData.config.max) || Infinity"
        @update:model-value="onUpdateModelValue($event)"
    />
</template>
