<script setup lang="ts">
import { computed } from "vue";
import { useGettext } from "vue3-gettext";

import type { BooleanCardXNodeXWidgetData } from "@/arches_vue_components/types.ts";
import type { BooleanAliasedNodeData } from "@/arches_vue_components/datatypes/boolean/types.ts";

const { cardXNodeXWidgetData = undefined, aliasedNodeData } = defineProps<{
    cardXNodeXWidgetData?: BooleanCardXNodeXWidgetData;
    aliasedNodeData: BooleanAliasedNodeData;
}>();

const { $gettext } = useGettext();

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
