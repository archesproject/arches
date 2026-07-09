<script setup lang="ts">
import { onMounted } from "vue";
import ToggleSwitch from "primevue/toggleswitch";

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

function onUpdateModelValue(updatedValue: boolean | null) {
    emit("update:aliasedNodeData", buildBooleanAliasedNodeData(updatedValue));
}
</script>

<template>
    <ToggleSwitch
        :fluid="true"
        :input-id="cardXNodeXWidgetData?.node.alias"
        :model-value="aliasedNodeData?.node_value ?? false"
        @update:model-value="onUpdateModelValue($event)"
    />
</template>
