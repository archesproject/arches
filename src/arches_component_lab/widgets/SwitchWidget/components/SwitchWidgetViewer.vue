<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useGettext } from "vue3-gettext";

import type { BooleanCardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { BooleanAliasedNodeData } from "@/arches_component_lab/datatypes/boolean/types.ts";

const { cardXNodeXWidgetData, aliasedNodeData } = defineProps<{
    cardXNodeXWidgetData?: BooleanCardXNodeXWidgetData;
    aliasedNodeData: BooleanAliasedNodeData;
}>();

const emit = defineEmits<{
    initialized: [updatedValue: BooleanAliasedNodeData];
}>();

const { $gettext } = useGettext();

onMounted(() => {
    emit("initialized", aliasedNodeData);
});

const displayValue = computed(() => {
    if (aliasedNodeData?.node_value === true) {
        return cardXNodeXWidgetData?.node.config.trueLabel || $gettext("True");
    } else if (aliasedNodeData?.node_value === false) {
        return (
            cardXNodeXWidgetData?.node.config.falseLabel || $gettext("False")
        );
    }
    return null;
});
</script>

<template>
    <div>{{ displayValue }}</div>
</template>
