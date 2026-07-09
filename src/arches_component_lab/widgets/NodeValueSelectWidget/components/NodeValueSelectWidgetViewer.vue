<script setup lang="ts">
import { onMounted } from "vue";

import type { NodeValueAliasedNodeData } from "@/arches_component_lab/datatypes/node-value/types.ts";

const { aliasedNodeData } = defineProps<{
    aliasedNodeData: NodeValueAliasedNodeData;
}>();

const emit = defineEmits<{
    initialized: [updatedValue: NodeValueAliasedNodeData];
}>();

onMounted(() => {
    emit("initialized", aliasedNodeData);
});
</script>

<template>
    <div>{{ aliasedNodeData?.display_value }}</div>
</template>
