<script setup lang="ts">
import type { NumberAliasedNodeData } from "@/arches_vue_components/datatypes/number/types.ts";

defineProps<{
    aliasedNodeData: NumberAliasedNodeData;
}>();
</script>

<template>
    <div>{{ aliasedNodeData?.display_value }}</div>
</template>
