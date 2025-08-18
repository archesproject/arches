<script setup lang="ts">
import InputText from "primevue/inputtext";

import type { URLValue } from "@/arches_component_lab/datatypes/url/types";
import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";

const { cardXNodeXWidgetData, aliasedNodeData } = defineProps<{
    cardXNodeXWidgetData: CardXNodeXWidgetData;
    aliasedNodeData: URLValue;
}>();

const emit = defineEmits<{
    (event: "update:value", updatedValue: URLValue): void;
}>();

function onUpdateModelValue(updatedValue: string | undefined) {
    const formattedValue = {
        url: updatedValue ?? "",
        url_label: updatedValue ?? "",
    };
    emit("update:value", {
        display_value: JSON.stringify(formattedValue),
        node_value: formattedValue,
        details: [],
    });
}
</script>

<template>
    <InputText
        type="text"
        :fluid="true"
        :model-value="aliasedNodeData.node_value?.url ?? ''"
        :pt="{ root: { id: cardXNodeXWidgetData.node.alias } }"
        @update:model-value="onUpdateModelValue($event)"
    />
</template>
