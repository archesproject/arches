<script setup lang="ts">
import InputText from "primevue/inputtext";

import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { NonLocalizedTextValue } from "@/arches_component_lab/datatypes/non-localized-text/types.ts";

const {
    cardXNodeXWidgetData,
    aliasedNodeData,
    shouldEmitSimplifiedValue = false,
} = defineProps<{
    cardXNodeXWidgetData: CardXNodeXWidgetData;
    aliasedNodeData: NonLocalizedTextValue | null;
    shouldEmitSimplifiedValue?: boolean;
}>();

const emit = defineEmits<{
    (event: "update:value", updatedValue: NonLocalizedTextValue | string): void;
}>();

function onUpdateModelValue(updatedValue: string | undefined) {
    if (updatedValue === undefined) {
        updatedValue = "";
    }

    if (shouldEmitSimplifiedValue) {
        emit("update:value", updatedValue);
    } else {
        emit("update:value", {
            display_value: updatedValue,
            node_value: updatedValue,
            details: [],
        });
    }
}
</script>

<template>
    <InputText
        type="text"
        :fluid="true"
        :model-value="aliasedNodeData?.node_value || ''"
        :placeholder="cardXNodeXWidgetData.config.placeholder"
        :pt="{ root: { id: cardXNodeXWidgetData.node.alias } }"
        @update:model-value="onUpdateModelValue($event)"
    />
</template>
