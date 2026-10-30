<script setup lang="ts">
import type { LanguageAliasedNodeData } from "@/arches_vue_components/datatypes/language/types.ts";

defineProps<{
    aliasedNodeData?: LanguageAliasedNodeData | null;
}>();
</script>

<template>
    <div>{{ aliasedNodeData?.display_value }}</div>
</template>
