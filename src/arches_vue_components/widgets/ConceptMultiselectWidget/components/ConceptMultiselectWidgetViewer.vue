<script setup lang="ts">
import { watch } from "vue";

import type { ConceptListAliasedNodeData } from "@/arches_vue_components/datatypes/concept-list/types.ts";

const { aliasedNodeData = null } = defineProps<{
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
