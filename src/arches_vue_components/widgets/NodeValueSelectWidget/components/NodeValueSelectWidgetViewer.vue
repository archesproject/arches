<script setup lang="ts">
import type { NodeValueAliasedNodeData } from "@/arches_vue_components/datatypes/node-value/types.ts";

defineProps<{
    aliasedNodeData: NodeValueAliasedNodeData;
}>();
</script>

<template>
    <div>{{ aliasedNodeData?.display_value }}</div>
</template>
