<script setup lang="ts">
import InputText from "primevue/inputtext";

import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { NonLocalizedTextValue } from "@/arches_component_lab/datatypes/non-localized-text/types.ts";

const { cardXNodeXWidgetData, aliasedNodeData } = defineProps<{
    cardXNodeXWidgetData: CardXNodeXWidgetData;
    aliasedNodeData: NonLocalizedTextValue;
}>();

const emit = defineEmits<{
    (event: "update:value", updatedValue: NonLocalizedTextValue): void;
}>();

function onUpdateModelValue(updatedValue: string | undefined) {
    if (updatedValue === undefined) {
        updatedValue = "";
    }

    emit("update:value", {
        display_value: updatedValue,
        node_value: updatedValue,
        details: [],
    });
}
</script>

<template>
    <InputText
        type="text"
        :fluid="true"
        :model-value="aliasedNodeData.node_value || ''"
        :placeholder="cardXNodeXWidgetData.config.placeholder"
        :pt="{ root: { id: cardXNodeXWidgetData.node.alias } }"
        @update:model-value="onUpdateModelValue($event)"
    />
</template>
