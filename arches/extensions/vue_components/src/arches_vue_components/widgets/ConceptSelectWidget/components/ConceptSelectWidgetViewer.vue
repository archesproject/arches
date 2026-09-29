<script setup lang="ts">
import type { ConceptAliasedNodeData } from "@/arches_vue_components/datatypes/concept/types.ts";

defineProps<{
    aliasedNodeData?: ConceptAliasedNodeData | null;
}>();
</script>

<template>
    <div>{{ aliasedNodeData?.display_value }}</div>
</template>
