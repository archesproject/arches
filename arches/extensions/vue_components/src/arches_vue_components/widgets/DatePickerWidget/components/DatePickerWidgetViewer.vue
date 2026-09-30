<script setup lang="ts">
import type { DateAliasedNodeData } from "@/arches_vue_components/datatypes/date/types.ts";

defineProps<{
    aliasedNodeData: DateAliasedNodeData;
}>();
</script>

<template>
    <div>{{ aliasedNodeData?.display_value }}</div>
</template>
