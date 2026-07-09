<script setup lang="ts">
import { onMounted } from "vue";

import type { NonLocalizedTextAliasedNodeData } from "@/arches_component_lab/datatypes/non-localized-text/types.ts";

const { aliasedNodeData } = defineProps<{
    aliasedNodeData: NonLocalizedTextAliasedNodeData;
}>();

const emit = defineEmits<{
    initialized: [updatedValue: NonLocalizedTextAliasedNodeData];
}>();

onMounted(() => {
    emit("initialized", aliasedNodeData);
});
</script>

<template>
    <div>{{ aliasedNodeData?.display_value }}</div>
</template>
