<script setup lang="ts">
import { watch } from "vue";

import type { LanguageAliasedNodeData } from "@/arches_component_lab/datatypes/language/types.ts";

const { aliasedNodeData } = defineProps<{
    aliasedNodeData?: LanguageAliasedNodeData | null;
}>();

const emit = defineEmits<{
    initialized: [updatedValue: LanguageAliasedNodeData];
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
