<script setup lang="ts">
import type { ReferenceSelectAliasedNodeData } from "@/arches_controlled_lists/datatypes/reference-select/types";

defineProps<{
    aliasedNodeData?: ReferenceSelectAliasedNodeData | null;
}>();
</script>

<template>
    <span>{{ aliasedNodeData?.display_value }}</span>
</template>
