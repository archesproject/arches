<script setup lang="ts">
import type { ConceptListAliasedNodeData } from "@/arches_vue_components/datatypes/concept-list/types.ts";

defineProps<{
    aliasedNodeData?: ConceptListAliasedNodeData | null;
}>();
</script>

<template>
    <div>{{ aliasedNodeData?.display_value }}</div>
</template>
