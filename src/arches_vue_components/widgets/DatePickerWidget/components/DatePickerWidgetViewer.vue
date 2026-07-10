<script setup lang="ts">
import { onMounted } from "vue";

import type { DateAliasedNodeData } from "@/arches_vue_components/datatypes/date/types.ts";

const { aliasedNodeData } = defineProps<{
    aliasedNodeData: DateAliasedNodeData;
}>();

const emit = defineEmits<{
    initialized: [updatedValue: DateAliasedNodeData];
}>();

onMounted(() => {
    emit("initialized", aliasedNodeData);
});
</script>

<template>
    <div>{{ aliasedNodeData?.display_value }}</div>
</template>
