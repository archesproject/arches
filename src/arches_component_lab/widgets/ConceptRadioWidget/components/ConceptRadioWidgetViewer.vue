<script setup lang="ts">
import { watch } from "vue";

import type { ConceptAliasedNodeData } from "@/arches_component_lab/datatypes/concept/types.ts";

const { aliasedNodeData } = defineProps<{
    aliasedNodeData?: ConceptAliasedNodeData | null;
}>();

const emit = defineEmits<{
    initialized: [updatedValue: ConceptAliasedNodeData];
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
