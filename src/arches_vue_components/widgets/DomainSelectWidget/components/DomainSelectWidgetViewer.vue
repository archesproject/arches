<script setup lang="ts">
import type { DomainAliasedNodeData } from "@/arches_vue_components/datatypes/domain/types.ts";

defineProps<{
    aliasedNodeData: DomainAliasedNodeData;
}>();
</script>

<template>
    <div>{{ aliasedNodeData?.display_value }}</div>
</template>
