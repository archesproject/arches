<script setup lang="ts">
import type { DomainListAliasedNodeData } from "@/arches_vue_components/datatypes/domain/types.ts";

defineProps<{
    aliasedNodeData: DomainListAliasedNodeData;
}>();
</script>

<template>
    <div>{{ aliasedNodeData?.display_value }}</div>
</template>
