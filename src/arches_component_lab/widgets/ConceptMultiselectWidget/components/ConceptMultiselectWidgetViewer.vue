<script setup lang="ts">
import { watch } from "vue";

import type { ConceptListAliasedNodeData } from "@/arches_component_lab/datatypes/concept-list/types.ts";

const { aliasedNodeData } = defineProps<{
    aliasedNodeData?: ConceptListAliasedNodeData | null;
}>();

const emit = defineEmits<{
    initialized: [updatedValue: ConceptListAliasedNodeData];
}>();

watch(
    () => aliasedNodeData,
    (newValue) => {
        if (newValue) {
            emit("initialized", newValue);
        }
    },
    { immediate: true },
);
</script>

<template>
    <div>{{ aliasedNodeData?.display_value }}</div>
</template>
