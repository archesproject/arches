<script setup lang="ts">
import { onMounted } from "vue";
import InputNumber from "primevue/inputnumber";

import { buildNumberAliasedNodeData } from "@/arches_component_lab/datatypes/number/utils.ts";

import type {
    NumberAliasedNodeData,
    NumberCardXNodeXWidgetData,
} from "@/arches_component_lab/datatypes/number/types.ts";

const { cardXNodeXWidgetData, aliasedNodeData } = defineProps<{
    cardXNodeXWidgetData?: NumberCardXNodeXWidgetData;
    aliasedNodeData: NumberAliasedNodeData | null;
}>();

const emit = defineEmits<{
    (
        event: "update:aliasedNodeData",
        updatedValue: NumberAliasedNodeData,
    ): void;
    (event: "initialized", updatedValue: NumberAliasedNodeData): void;
}>();

onMounted(() => {
    emit("initialized", aliasedNodeData ?? buildNumberAliasedNodeData(null));
});

function onUpdateModelValue(updatedValue: number | null) {
    emit("update:aliasedNodeData", buildNumberAliasedNodeData(updatedValue));
}
</script>

<template>
    <InputNumber
        :model-value="aliasedNodeData?.node_value ?? null"
        :fluid="true"
        :input-id="cardXNodeXWidgetData?.node.alias"
        :placeholder="cardXNodeXWidgetData?.config.placeholder"
        :prefix="cardXNodeXWidgetData?.config.prefix ?? ''"
        :suffix="cardXNodeXWidgetData?.config.suffix ?? ''"
        :min-fraction-digits="
            Number(cardXNodeXWidgetData?.config.precision) || 0
        "
        :max-fraction-digits="
            Number(cardXNodeXWidgetData?.config.precision) || 0
        "
        :min="Number(cardXNodeXWidgetData?.config.min) || -Infinity"
        :max="Number(cardXNodeXWidgetData?.config.max) || Infinity"
        @update:model-value="onUpdateModelValue($event)"
    />
</template>
