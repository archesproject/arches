<script setup lang="ts">
import ToggleSwitch from "primevue/toggleswitch";
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

function onUpdateModelValue(updatedValue: boolean | null) {
    if (shouldEmitSimplifiedValue) {
        emit("update:value", updatedValue);
    } else {
        emit("update:value", {
            display_value: getDisplayValue(updatedValue),
            node_value: updatedValue,
            details: [],
        });
    }
}
</script>

<template>
    <ToggleSwitch
        :fluid="true"
        :input-id="cardXNodeXWidgetData.node.alias"
        :model-value="aliasedNodeData?.node_value || ''"
        @update:model-value="onUpdateModelValue($event)"
    />
</template>
