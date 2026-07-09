<script setup lang="ts">
import { onMounted } from "vue";

import type { DomainListAliasedNodeData } from "@/arches_component_lab/datatypes/domain/types.ts";

const { aliasedNodeData } = defineProps<{
    aliasedNodeData: DomainListAliasedNodeData;
}>();

const emit = defineEmits<{
    initialized: [updatedValue: DomainListAliasedNodeData];
}>();

onMounted(() => {
    emit("initialized", aliasedNodeData);
});
</script>

<template>
    <div>{{ aliasedNodeData?.display_value }}</div>
</template>
