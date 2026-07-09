<script setup lang="ts">
import { onMounted } from "vue";

import type { DomainAliasedNodeData } from "@/arches_component_lab/datatypes/domain/types.ts";

const { aliasedNodeData } = defineProps<{
    aliasedNodeData: DomainAliasedNodeData;
}>();

const emit = defineEmits<{
    initialized: [updatedValue: DomainAliasedNodeData];
}>();

onMounted(() => {
    emit("initialized", aliasedNodeData);
});
</script>

<template>
    <div>{{ aliasedNodeData?.display_value }}</div>
</template>
